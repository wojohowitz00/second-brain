#!/usr/bin/env python3
"""
Tests for domain_classifier module.

TDD approach: Tests written FIRST, implementation follows.
"""

import pytest
from unittest.mock import Mock, patch
from dataclasses import dataclass


class TestClassificationResult:
    """Test ClassificationResult dataclass."""

    def test_has_required_fields(self):
        """ClassificationResult has domain, confidence, reasoning fields."""
        from domain_classifier import ClassificationResult
        
        result = ClassificationResult(
            domain="Personal",
            confidence=0.85,
            reasoning="Personal task"
        )
        
        assert result.domain == "Personal"
        assert result.confidence == 0.85
        assert result.reasoning == "Personal task"

    def test_optional_raw_response(self):
        """ClassificationResult can include raw_response."""
        from domain_classifier import ClassificationResult
        
        result = ClassificationResult(
            domain="Personal",
            confidence=0.85,
            reasoning="Personal task",
            raw_response='{"domain": "Personal"}'
        )
        
        assert result.raw_response == '{"domain": "Personal"}'


class TestDomainClassifier:
    """Test DomainClassifier class."""

    @pytest.fixture
    def mock_ollama(self):
        """Mock OllamaClient."""
        client = Mock()
        client.chat.return_value = {
            "message": {
                "content": '{"domain": "Personal", "confidence": 0.85, "reasoning": "Personal task"}'
            }
        }
        return client

    @pytest.fixture
    def mock_scanner(self, tmp_path):
        """Mock VaultScanner with vocabulary."""
        scanner = Mock()
        scanner.get_vocabulary.return_value = {
            "domains": ["CCBH", "Just-Value", "Personal"],
            "para_types": ["1_Projects", "2_Areas"],
            "subjects": ["apps", "finance"]
        }
        return scanner

    def test_classifies_personal_message(self, mock_ollama, mock_scanner):
        """Personal task message classified correctly."""
        from domain_classifier import DomainClassifier
        
        mock_ollama.chat.return_value = {
            "message": {
                "content": '{"domain": "Personal", "confidence": 0.9, "reasoning": "Personal productivity"}'
            }
        }
        
        classifier = DomainClassifier(mock_ollama, mock_scanner)
        result = classifier.classify("Set up my home office")
        
        assert result.domain == "Personal"
        assert result.confidence >= 0.8

    def test_classifies_just_value_message(self, mock_ollama, mock_scanner):
        """Just Value real estate message classified correctly."""
        from domain_classifier import DomainClassifier
        
        mock_ollama.chat.return_value = {
            "message": {
                "content": '{"domain": "Just-Value", "confidence": 0.95, "reasoning": "Real estate financials"}'
            }
        }
        
        classifier = DomainClassifier(mock_ollama, mock_scanner)
        result = classifier.classify("Review Q4 rental income for Newark properties")
        
        assert result.domain == "Just-Value"

    def test_classifies_ccbh_message(self, mock_ollama, mock_scanner):
        """CCBH work message classified correctly."""
        from domain_classifier import DomainClassifier
        
        mock_ollama.chat.return_value = {
            "message": {
                "content": '{"domain": "CCBH", "confidence": 0.88, "reasoning": "CCBH organization"}'
            }
        }
        
        classifier = DomainClassifier(mock_ollama, mock_scanner)
        result = classifier.classify("Schedule CCBH board meeting")
        
        assert result.domain == "CCBH"

    def test_ambiguous_message_lower_confidence(self, mock_ollama, mock_scanner):
        """Ambiguous message returns lower confidence."""
        from domain_classifier import DomainClassifier
        
        mock_ollama.chat.return_value = {
            "message": {
                "content": '{"domain": "Personal", "confidence": 0.45, "reasoning": "Could be work or personal"}'
            }
        }
        
        classifier = DomainClassifier(mock_ollama, mock_scanner)
        result = classifier.classify("Send email about taxes")
        
        assert result.confidence < 0.6

    def test_invalid_domain_returns_unknown(self, mock_ollama, mock_scanner):
        """LLM returning invalid domain results in 'unknown'."""
        from domain_classifier import DomainClassifier
        
        mock_ollama.chat.return_value = {
            "message": {
                "content": '{"domain": "InvalidDomain", "confidence": 0.9, "reasoning": "Made up"}'
            }
        }
        
        classifier = DomainClassifier(mock_ollama, mock_scanner)
        result = classifier.classify("Random message")
        
        assert result.domain == "unknown"

    def test_normalizes_domain_case(self, mock_ollama, mock_scanner):
        """Domain with wrong case is normalized to vocabulary."""
        from domain_classifier import DomainClassifier
        
        mock_ollama.chat.return_value = {
            "message": {
                "content": '{"domain": "personal", "confidence": 0.85, "reasoning": "Personal task"}'
            }
        }
        
        classifier = DomainClassifier(mock_ollama, mock_scanner)
        result = classifier.classify("Personal task")
        
        assert result.domain == "Personal"  # Normalized

    def test_empty_message_returns_unknown(self, mock_ollama, mock_scanner):
        """Empty message returns unknown with error."""
        from domain_classifier import DomainClassifier
        
        classifier = DomainClassifier(mock_ollama, mock_scanner)
        result = classifier.classify("")
        
        assert result.domain == "unknown"
        assert result.confidence == 0.0

    def test_handles_ollama_server_not_running(self, mock_scanner):
        """Handles OllamaServerNotRunning gracefully."""
        from domain_classifier import DomainClassifier
        from ollama_client import OllamaServerNotRunning
        
        mock_ollama = Mock()
        mock_ollama.chat.side_effect = OllamaServerNotRunning("Server not running")
        
        classifier = DomainClassifier(mock_ollama, mock_scanner)
        result = classifier.classify("Some message")
        
        assert result.domain == "unknown"
        assert "server" in result.reasoning.lower() or "error" in result.reasoning.lower()

    def test_handles_ollama_timeout(self, mock_scanner):
        """Handles OllamaTimeout gracefully."""
        from domain_classifier import DomainClassifier
        from ollama_client import OllamaTimeout
        
        mock_ollama = Mock()
        mock_ollama.chat.side_effect = OllamaTimeout("Timed out")
        
        classifier = DomainClassifier(mock_ollama, mock_scanner)
        result = classifier.classify("Some message")
        
        assert result.domain == "unknown"
        assert "timeout" in result.reasoning.lower() or "error" in result.reasoning.lower()

    def test_confidence_between_zero_and_one(self, mock_ollama, mock_scanner):
        """Confidence is always between 0.0 and 1.0."""
        from domain_classifier import DomainClassifier
        
        # Test confidence > 1 gets clamped
        mock_ollama.chat.return_value = {
            "message": {
                "content": '{"domain": "Personal", "confidence": 1.5, "reasoning": "Very sure"}'
            }
        }
        
        classifier = DomainClassifier(mock_ollama, mock_scanner)
        result = classifier.classify("Test message")
        
        assert 0.0 <= result.confidence <= 1.0

    def test_reasoning_explains_classification(self, mock_ollama, mock_scanner):
        """Reasoning field provides explanation."""
        from domain_classifier import DomainClassifier
        
        mock_ollama.chat.return_value = {
            "message": {
                "content": '{"domain": "Personal", "confidence": 0.85, "reasoning": "Home office setup is a personal productivity task"}'
            }
        }
        
        classifier = DomainClassifier(mock_ollama, mock_scanner)
        result = classifier.classify("Set up home office")
        
        assert len(result.reasoning) > 0

    def test_uses_vault_vocabulary_in_prompt(self, mock_ollama, mock_scanner):
        """Prompt includes domains from vault vocabulary."""
        from domain_classifier import DomainClassifier
        
        classifier = DomainClassifier(mock_ollama, mock_scanner)
        classifier.classify("Test message")
        
        # Check that chat was called with messages containing vocabulary
        call_args = mock_ollama.chat.call_args
        messages = call_args[0][0] if call_args[0] else call_args[1].get("messages", [])
        
        prompt_content = str(messages)
        assert "Personal" in prompt_content
        assert "Just-Value" in prompt_content
        assert "CCBH" in prompt_content

    def test_handles_malformed_json_response(self, mock_ollama, mock_scanner):
        """Handles malformed JSON from LLM."""
        from domain_classifier import DomainClassifier
        
        mock_ollama.chat.return_value = {
            "message": {
                "content": "I think this is Personal domain"  # Not JSON
            }
        }
        
        classifier = DomainClassifier(mock_ollama, mock_scanner)
        result = classifier.classify("Test message")
        
        # Should try to extract domain or return unknown
        assert result.domain in ["Personal", "unknown"]


class TestConvenienceFunction:
    """Test module-level convenience function."""

    def test_classify_domain_function_exists(self):
        """classify_domain convenience function is exported."""
        from domain_classifier import classify_domain
        
        assert callable(classify_domain)
