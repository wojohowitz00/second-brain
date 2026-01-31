#!/usr/bin/env python3
"""
Tests for message_classifier module.

TDD approach: Tests written FIRST, implementation follows.
Tests use mocks for unit tests, real Ollama for integration tests.
"""

import pytest
from unittest.mock import Mock, patch
import json


def make_mock_response(domain, para_type, subject, category, confidence, reasoning):
    """Helper to create mock LLM response dict."""
    return {
        "message": {
            "content": json.dumps({
                "domain": domain,
                "para_type": para_type,
                "subject": subject,
                "category": category,
                "confidence": confidence,
                "reasoning": reasoning
            })
        }
    }


class TestClassificationResult:
    """Test cases for ClassificationResult dataclass."""
    
    def test_result_has_all_fields(self):
        """ClassificationResult has domain, para_type, subject, category, confidence, reasoning."""
        from message_classifier import ClassificationResult
        
        result = ClassificationResult(
            domain="Personal",
            para_type="1_Projects",
            subject="apps",
            category="task",
            confidence=0.85,
            reasoning="Test reasoning"
        )
        
        assert result.domain == "Personal"
        assert result.para_type == "1_Projects"
        assert result.subject == "apps"
        assert result.category == "task"
        assert result.confidence == 0.85
        assert result.reasoning == "Test reasoning"
    
    def test_result_optional_raw_response(self):
        """ClassificationResult can include raw_response."""
        from message_classifier import ClassificationResult
        
        result = ClassificationResult(
            domain="Personal",
            para_type="1_Projects",
            subject="apps",
            category="task",
            confidence=0.85,
            reasoning="Test",
            raw_response='{"domain": "Personal"}'
        )
        
        assert result.raw_response == '{"domain": "Personal"}'


class TestDomainClassification:
    """Test cases for domain classification."""
    
    def test_personal_message_returns_personal(self):
        """Message about personal tasks returns domain=Personal."""
        from message_classifier import MessageClassifier
        
        classifier = MessageClassifier()
        mock_response = make_mock_response("Personal", "1_Projects", "apps", "task", 0.9, "Personal task")
        mock_vocab = {"domains": ["Personal", "Just-Value", "CCBH"], "para_types": [], "subjects": ["apps"]}
        mock_structure = {"Personal": {"1_Projects": ["apps"]}}
        
        with patch.object(classifier._ollama_client, 'chat', return_value=mock_response):
            with patch.object(classifier._vault_scanner, 'get_vocabulary', return_value=mock_vocab):
                with patch.object(classifier._vault_scanner, 'get_structure', return_value=mock_structure):
                    result = classifier.classify("Set up my home office")
                    assert result.domain == "Personal"
    
    def test_just_value_message_returns_just_value(self):
        """Message about properties returns domain=Just-Value."""
        from message_classifier import MessageClassifier
        
        classifier = MessageClassifier()
        mock_response = make_mock_response("Just-Value", "2_Areas", "properties", "task", 0.85, "JV properties")
        mock_vocab = {"domains": ["Personal", "Just-Value", "CCBH"], "para_types": [], "subjects": ["properties"]}
        mock_structure = {"Just-Value": {"2_Areas": ["properties"]}}
        
        with patch.object(classifier._ollama_client, 'chat', return_value=mock_response):
            with patch.object(classifier._vault_scanner, 'get_vocabulary', return_value=mock_vocab):
                with patch.object(classifier._vault_scanner, 'get_structure', return_value=mock_structure):
                    result = classifier.classify("Review Q4 rental income for Newark")
                    assert result.domain == "Just-Value"
    
    def test_ccbh_message_returns_ccbh(self):
        """Message about CCBH work returns domain=CCBH."""
        from message_classifier import MessageClassifier
        
        classifier = MessageClassifier()
        mock_response = make_mock_response("CCBH", "2_Areas", "clients", "meeting", 0.9, "CCBH work")
        mock_vocab = {"domains": ["Personal", "Just-Value", "CCBH"], "para_types": [], "subjects": ["clients"]}
        mock_structure = {"CCBH": {"2_Areas": ["clients"]}}
        
        with patch.object(classifier._ollama_client, 'chat', return_value=mock_response):
            with patch.object(classifier._vault_scanner, 'get_vocabulary', return_value=mock_vocab):
                with patch.object(classifier._vault_scanner, 'get_structure', return_value=mock_structure):
                    result = classifier.classify("CCBH board meeting")
                    assert result.domain == "CCBH"
    
    def test_unknown_domain_normalizes_to_personal(self):
        """Unknown domain in LLM response normalizes to Personal."""
        from message_classifier import MessageClassifier
        
        classifier = MessageClassifier()
        mock_response = make_mock_response("InvalidDomain", "2_Areas", "general", "reference", 0.5, "Unknown")
        mock_vocab = {"domains": ["Personal", "Just-Value", "CCBH"], "para_types": [], "subjects": []}
        mock_structure = {}
        
        with patch.object(classifier._ollama_client, 'chat', return_value=mock_response):
            with patch.object(classifier._vault_scanner, 'get_vocabulary', return_value=mock_vocab):
                with patch.object(classifier._vault_scanner, 'get_structure', return_value=mock_structure):
                    result = classifier.classify("Some message")
                    assert result.domain == "Personal"


class TestParaClassification:
    """Test cases for PARA type classification."""
    
    def test_project_message_returns_1_projects(self):
        """Project-related message returns para_type=1_Projects."""
        from message_classifier import MessageClassifier
        
        classifier = MessageClassifier()
        mock_response = make_mock_response("Personal", "1_Projects", "apps", "task", 0.9, "Project work")
        mock_vocab = {"domains": ["Personal"], "para_types": [], "subjects": ["apps"]}
        mock_structure = {"Personal": {"1_Projects": ["apps"]}}
        
        with patch.object(classifier._ollama_client, 'chat', return_value=mock_response):
            with patch.object(classifier._vault_scanner, 'get_vocabulary', return_value=mock_vocab):
                with patch.object(classifier._vault_scanner, 'get_structure', return_value=mock_structure):
                    result = classifier.classify("Build new feature for the app")
                    assert result.para_type == "1_Projects"
    
    def test_area_message_returns_2_areas(self):
        """Ongoing area message returns para_type=2_Areas."""
        from message_classifier import MessageClassifier
        
        classifier = MessageClassifier()
        mock_response = make_mock_response("Personal", "2_Areas", "health", "journal", 0.85, "Health area")
        mock_vocab = {"domains": ["Personal"], "para_types": [], "subjects": ["health"]}
        mock_structure = {"Personal": {"2_Areas": ["health"]}}
        
        with patch.object(classifier._ollama_client, 'chat', return_value=mock_response):
            with patch.object(classifier._vault_scanner, 'get_vocabulary', return_value=mock_vocab):
                with patch.object(classifier._vault_scanner, 'get_structure', return_value=mock_structure):
                    result = classifier.classify("Weekly health check-in")
                    assert result.para_type == "2_Areas"
    
    def test_invalid_para_normalizes_to_3_resources(self):
        """Invalid PARA type normalizes to 3_Resources."""
        from message_classifier import MessageClassifier
        
        classifier = MessageClassifier()
        mock_response = make_mock_response("Personal", "InvalidPARA", "general", "reference", 0.5, "Unknown")
        mock_vocab = {"domains": ["Personal"], "para_types": [], "subjects": []}
        mock_structure = {}
        
        with patch.object(classifier._ollama_client, 'chat', return_value=mock_response):
            with patch.object(classifier._vault_scanner, 'get_vocabulary', return_value=mock_vocab):
                with patch.object(classifier._vault_scanner, 'get_structure', return_value=mock_structure):
                    result = classifier.classify("Some message")
                    assert result.para_type == "3_Resources"


class TestSubjectClassification:
    """Test cases for subject classification."""
    
    def test_known_subject_returns_subject(self):
        """Message about known subject returns that subject."""
        from message_classifier import MessageClassifier
        
        classifier = MessageClassifier()
        mock_response = make_mock_response("Personal", "1_Projects", "apps", "idea", 0.9, "App project")
        mock_vocab = {"domains": ["Personal"], "para_types": [], "subjects": ["apps", "writing"]}
        mock_structure = {"Personal": {"1_Projects": ["apps", "writing"]}}
        
        with patch.object(classifier._ollama_client, 'chat', return_value=mock_response):
            with patch.object(classifier._vault_scanner, 'get_vocabulary', return_value=mock_vocab):
                with patch.object(classifier._vault_scanner, 'get_structure', return_value=mock_structure):
                    result = classifier.classify("New app feature idea")
                    assert result.subject == "apps"
    
    def test_unknown_subject_returns_general(self):
        """Unknown subject returns 'general'."""
        from message_classifier import MessageClassifier
        
        classifier = MessageClassifier()
        mock_response = make_mock_response("Personal", "1_Projects", "nonexistent_topic", "reference", 0.6, "Unknown")
        mock_vocab = {"domains": ["Personal"], "para_types": [], "subjects": ["apps"]}
        mock_structure = {"Personal": {"1_Projects": ["apps"]}}
        
        with patch.object(classifier._ollama_client, 'chat', return_value=mock_response):
            with patch.object(classifier._vault_scanner, 'get_vocabulary', return_value=mock_vocab):
                with patch.object(classifier._vault_scanner, 'get_structure', return_value=mock_structure):
                    result = classifier.classify("Random unknown topic")
                    assert result.subject == "general"


class TestCategoryClassification:
    """Test cases for category classification."""
    
    def test_meeting_message_returns_meeting(self):
        """Meeting notes return category=meeting."""
        from message_classifier import MessageClassifier
        
        classifier = MessageClassifier()
        mock_response = make_mock_response("CCBH", "2_Areas", "clients", "meeting", 0.9, "Meeting notes")
        mock_vocab = {"domains": ["CCBH"], "para_types": [], "subjects": ["clients"]}
        mock_structure = {"CCBH": {"2_Areas": ["clients"]}}
        
        with patch.object(classifier._ollama_client, 'chat', return_value=mock_response):
            with patch.object(classifier._vault_scanner, 'get_vocabulary', return_value=mock_vocab):
                with patch.object(classifier._vault_scanner, 'get_structure', return_value=mock_structure):
                    result = classifier.classify("Notes from client meeting")
                    assert result.category == "meeting"
    
    def test_task_message_returns_task(self):
        """Action items return category=task."""
        from message_classifier import MessageClassifier
        
        classifier = MessageClassifier()
        mock_response = make_mock_response("Personal", "1_Projects", "apps", "task", 0.85, "Action item")
        mock_vocab = {"domains": ["Personal"], "para_types": [], "subjects": ["apps"]}
        mock_structure = {"Personal": {"1_Projects": ["apps"]}}
        
        with patch.object(classifier._ollama_client, 'chat', return_value=mock_response):
            with patch.object(classifier._vault_scanner, 'get_vocabulary', return_value=mock_vocab):
                with patch.object(classifier._vault_scanner, 'get_structure', return_value=mock_structure):
                    result = classifier.classify("TODO: Fix the login bug")
                    assert result.category == "task"
    
    def test_idea_message_returns_idea(self):
        """Brainstorm returns category=idea."""
        from message_classifier import MessageClassifier
        
        classifier = MessageClassifier()
        mock_response = make_mock_response("Personal", "1_Projects", "apps", "idea", 0.8, "Brainstorm")
        mock_vocab = {"domains": ["Personal"], "para_types": [], "subjects": ["apps"]}
        mock_structure = {"Personal": {"1_Projects": ["apps"]}}
        
        with patch.object(classifier._ollama_client, 'chat', return_value=mock_response):
            with patch.object(classifier._vault_scanner, 'get_vocabulary', return_value=mock_vocab):
                with patch.object(classifier._vault_scanner, 'get_structure', return_value=mock_structure):
                    result = classifier.classify("What if we added voice control?")
                    assert result.category == "idea"
    
    def test_invalid_category_normalizes_to_reference(self):
        """Invalid category normalizes to 'reference'."""
        from message_classifier import MessageClassifier
        
        classifier = MessageClassifier()
        mock_response = make_mock_response("Personal", "3_Resources", "general", "invalid_cat", 0.5, "Unknown")
        mock_vocab = {"domains": ["Personal"], "para_types": [], "subjects": []}
        mock_structure = {}
        
        with patch.object(classifier._ollama_client, 'chat', return_value=mock_response):
            with patch.object(classifier._vault_scanner, 'get_vocabulary', return_value=mock_vocab):
                with patch.object(classifier._vault_scanner, 'get_structure', return_value=mock_structure):
                    result = classifier.classify("Some message")
                    assert result.category == "reference"


class TestResponseParsing:
    """Test cases for LLM response parsing."""
    
    def test_valid_json_parses_correctly(self):
        """Valid JSON response parses correctly."""
        from message_classifier import MessageClassifier
        
        classifier = MessageClassifier()
        mock_response = make_mock_response("Personal", "1_Projects", "apps", "task", 0.85, "Clear reasoning")
        mock_vocab = {"domains": ["Personal"], "para_types": [], "subjects": ["apps"]}
        mock_structure = {"Personal": {"1_Projects": ["apps"]}}
        
        with patch.object(classifier._ollama_client, 'chat', return_value=mock_response):
            with patch.object(classifier._vault_scanner, 'get_vocabulary', return_value=mock_vocab):
                with patch.object(classifier._vault_scanner, 'get_structure', return_value=mock_structure):
                    result = classifier.classify("Test message")
                    assert result.confidence == 0.85
                    assert result.reasoning == "Clear reasoning"
    
    def test_invalid_json_uses_regex_fallback(self):
        """Invalid JSON falls back to regex extraction."""
        from message_classifier import MessageClassifier
        
        classifier = MessageClassifier()
        # Malformed JSON with extra text
        mock_response = {
            "message": {
                "content": '''Here's the classification:
        {"domain": "Personal", "para_type": "1_Projects", "subject": "apps", "category": "task", "confidence": 0.8, "reasoning": "test"}
        Hope that helps!'''
            }
        }
        mock_vocab = {"domains": ["Personal"], "para_types": [], "subjects": ["apps"]}
        mock_structure = {"Personal": {"1_Projects": ["apps"]}}
        
        with patch.object(classifier._ollama_client, 'chat', return_value=mock_response):
            with patch.object(classifier._vault_scanner, 'get_vocabulary', return_value=mock_vocab):
                with patch.object(classifier._vault_scanner, 'get_structure', return_value=mock_structure):
                    result = classifier.classify("Test message")
                    # Should still parse the domain
                    assert result.domain == "Personal"


class TestErrorHandling:
    """Test cases for error handling."""
    
    def test_empty_message_returns_defaults(self):
        """Empty message returns defaults with low confidence."""
        from message_classifier import MessageClassifier
        
        classifier = MessageClassifier()
        mock_response = make_mock_response("Personal", "3_Resources", "general", "reference", 0.1, "Empty")
        mock_vocab = {"domains": ["Personal"], "para_types": [], "subjects": []}
        mock_structure = {}
        
        with patch.object(classifier._ollama_client, 'chat', return_value=mock_response):
            with patch.object(classifier._vault_scanner, 'get_vocabulary', return_value=mock_vocab):
                with patch.object(classifier._vault_scanner, 'get_structure', return_value=mock_structure):
                    result = classifier.classify("")
                    assert result.confidence <= 0.5
    
    def test_ollama_timeout_raises(self):
        """OllamaTimeout exception propagates."""
        from message_classifier import MessageClassifier
        from ollama_client import OllamaTimeout
        
        classifier = MessageClassifier()
        mock_vocab = {"domains": ["Personal"], "para_types": [], "subjects": []}
        
        with patch.object(classifier._ollama_client, 'chat', side_effect=OllamaTimeout("Timeout")):
            with patch.object(classifier._vault_scanner, 'get_vocabulary', return_value=mock_vocab):
                with pytest.raises(OllamaTimeout):
                    classifier.classify("Test message")
    
    def test_ollama_server_not_running_raises(self):
        """OllamaServerNotRunning exception propagates."""
        from message_classifier import MessageClassifier
        from ollama_client import OllamaServerNotRunning
        
        classifier = MessageClassifier()
        mock_vocab = {"domains": ["Personal"], "para_types": [], "subjects": []}
        
        with patch.object(classifier._ollama_client, 'chat', side_effect=OllamaServerNotRunning("Not running")):
            with patch.object(classifier._vault_scanner, 'get_vocabulary', return_value=mock_vocab):
                with pytest.raises(OllamaServerNotRunning):
                    classifier.classify("Test message")
    
    def test_confidence_clamped_to_0_1(self):
        """Confidence is always between 0.0 and 1.0."""
        from message_classifier import MessageClassifier
        
        classifier = MessageClassifier()
        # Invalid confidence > 1.0
        mock_response = {
            "message": {
                "content": json.dumps({
                    "domain": "Personal",
                    "para_type": "1_Projects",
                    "subject": "apps",
                    "category": "task",
                    "confidence": 1.5,
                    "reasoning": "Test"
                })
            }
        }
        mock_vocab = {"domains": ["Personal"], "para_types": [], "subjects": ["apps"]}
        mock_structure = {"Personal": {"1_Projects": ["apps"]}}
        
        with patch.object(classifier._ollama_client, 'chat', return_value=mock_response):
            with patch.object(classifier._vault_scanner, 'get_vocabulary', return_value=mock_vocab):
                with patch.object(classifier._vault_scanner, 'get_structure', return_value=mock_structure):
                    result = classifier.classify("Test message")
                    assert 0.0 <= result.confidence <= 1.0


class TestConvenienceFunction:
    """Test cases for classify_message convenience function."""
    
    def test_classify_message_returns_result(self):
        """classify_message() returns ClassificationResult."""
        from message_classifier import classify_message, ClassificationResult
        
        with patch('message_classifier.MessageClassifier') as MockClassifier:
            mock_instance = Mock()
            mock_instance.classify.return_value = ClassificationResult(
                domain="Personal",
                para_type="1_Projects",
                subject="apps",
                category="task",
                confidence=0.8,
                reasoning="Test"
            )
            MockClassifier.return_value = mock_instance
            
            result = classify_message("Test message")
            assert isinstance(result, ClassificationResult)


# Integration tests (require real Ollama)
@pytest.mark.integration
class TestMessageClassifierIntegration:
    """Integration tests with real Ollama server."""
    
    def test_real_classification(self):
        """Test classification against real Ollama server."""
        from message_classifier import MessageClassifier
        from ollama_client import OllamaClient
        
        client = OllamaClient()
        status = client.health_check()
        
        if not status.ready:
            pytest.skip(f"Ollama not ready: {status.error}")
        
        classifier = MessageClassifier()
        result = classifier.classify("Set up my home office workspace for productivity")
        
        # Domain should be a non-empty string (actual validation depends on vault structure)
        assert isinstance(result.domain, str) and len(result.domain) > 0
        assert result.para_type in ["1_Projects", "2_Areas", "3_Resources", "4_Archive"]
        assert result.category in ["meeting", "task", "idea", "reference", "journal", "question"]
        assert 0.0 <= result.confidence <= 1.0
        assert len(result.reasoning) > 0
    
    def test_performance_within_bounds(self):
        """Classification completes within acceptable time."""
        import time
        from message_classifier import MessageClassifier
        from ollama_client import OllamaClient
        
        client = OllamaClient()
        status = client.health_check()
        
        if not status.ready:
            pytest.skip(f"Ollama not ready: {status.error}")
        
        classifier = MessageClassifier()
        
        start = time.time()
        result = classifier.classify("Quick test message")
        elapsed = time.time() - start
        
        # Should complete within 30 seconds even on cold start
        assert elapsed < 30, f"Classification took {elapsed:.1f}s, expected < 30s"
