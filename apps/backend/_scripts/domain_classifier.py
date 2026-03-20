#!/usr/bin/env python3
"""
Domain classifier for message classification using local LLM.

Uses OllamaClient for LLM calls and VaultScanner vocabulary for valid domains.
Classifies messages into domains: Personal, Just-Value, CCBH.
"""

import json
import logging
import re
from dataclasses import dataclass, field
from typing import Optional, List

from ollama_client import (
    OllamaClient,
    OllamaError,
    OllamaServerNotRunning,
    OllamaTimeout,
    get_ollama_client,
)
from vault_scanner import VaultScanner

# Configure module logger
logger = logging.getLogger(__name__)


@dataclass
class ClassificationResult:
    """Result of domain classification."""
    domain: str
    confidence: float
    reasoning: str
    raw_response: Optional[str] = None


# Prompt template for domain classification
CLASSIFICATION_PROMPT = """You are a message classification assistant. Classify the following message into ONE of these domains:
{domains}

Message: {message}

Respond in this exact JSON format, with no additional text:
{{"domain": "<domain>", "confidence": <0.0-1.0>, "reasoning": "<brief explanation>"}}

IMPORTANT:
- Only use domains from the list above
- confidence should be between 0.0 and 1.0
- If unsure, use a lower confidence value
- Respond ONLY with valid JSON"""


class DomainClassifier:
    """
    Classifier for routing messages to domains.
    
    Uses LLM to classify messages into domains discovered by VaultScanner.
    """
    
    def __init__(self, ollama_client: OllamaClient, vault_scanner: VaultScanner):
        """
        Initialize classifier.
        
        Args:
            ollama_client: Client for LLM operations
            vault_scanner: Scanner for vault vocabulary
        """
        self.ollama = ollama_client
        self.scanner = vault_scanner
        self._vocabulary = None
    
    @property
    def vocabulary(self) -> dict:
        """Get cached vocabulary from vault scanner."""
        if self._vocabulary is None:
            self._vocabulary = self.scanner.get_vocabulary()
        return self._vocabulary
    
    @property
    def valid_domains(self) -> List[str]:
        """Get list of valid domain names."""
        return self.vocabulary.get("domains", [])
    
    def _build_prompt(self, message: str, domains: List[str]) -> str:
        """Build classification prompt with vocabulary."""
        domain_list = ", ".join(domains)
        return CLASSIFICATION_PROMPT.format(
            domains=domain_list,
            message=message
        )
    
    def _normalize_domain(self, domain: str) -> Optional[str]:
        """
        Normalize domain name to match vocabulary.
        
        Returns None if domain doesn't match any valid domain.
        """
        domain_lower = domain.lower().strip()
        
        for valid_domain in self.valid_domains:
            if valid_domain.lower() == domain_lower:
                return valid_domain
        
        return None
    
    def _parse_response(self, response: str, valid_domains: List[str]) -> ClassificationResult:
        """
        Parse LLM response into ClassificationResult.
        
        Handles both valid JSON and malformed responses.
        """
        try:
            # Try JSON parse first
            data = json.loads(response)
            
            raw_domain = data.get("domain", "unknown")
            raw_confidence = data.get("confidence", 0.5)
            reasoning = data.get("reasoning", "")
            
            # Normalize domain
            normalized_domain = self._normalize_domain(raw_domain)
            if normalized_domain is None:
                normalized_domain = "unknown"
                reasoning = f"Invalid domain '{raw_domain}' - not in vocabulary"
            
            # Clamp confidence
            confidence = max(0.0, min(1.0, float(raw_confidence)))
            
            return ClassificationResult(
                domain=normalized_domain,
                confidence=confidence,
                reasoning=reasoning,
                raw_response=response
            )
            
        except (json.JSONDecodeError, ValueError, TypeError) as e:
            logger.warning(f"Failed to parse LLM response as JSON: {e}")
            
            # Try regex extraction as fallback
            domain = self._extract_domain_fallback(response)
            
            return ClassificationResult(
                domain=domain if domain else "unknown",
                confidence=0.3 if domain else 0.0,
                reasoning="Extracted from malformed response" if domain else "Failed to parse response",
                raw_response=response
            )
    
    def _extract_domain_fallback(self, response: str) -> Optional[str]:
        """Try to extract domain from malformed response using regex."""
        response_lower = response.lower()
        
        for domain in self.valid_domains:
            if domain.lower() in response_lower:
                return domain
        
        return None
    
    def classify(self, message: str) -> ClassificationResult:
        """
        Classify a message into a domain.
        
        Args:
            message: The message text to classify
            
        Returns:
            ClassificationResult with domain, confidence, and reasoning
        """
        # Handle empty message
        if not message or not message.strip():
            return ClassificationResult(
                domain="unknown",
                confidence=0.0,
                reasoning="Empty message cannot be classified"
            )
        
        try:
            # Get domains from vocabulary
            domains = self.valid_domains
            if not domains:
                return ClassificationResult(
                    domain="unknown",
                    confidence=0.0,
                    reasoning="No domains available in vocabulary"
                )
            
            # Build prompt
            prompt = self._build_prompt(message, domains)
            
            # Call LLM
            messages = [{"role": "user", "content": prompt}]
            response = self.ollama.chat(messages)
            
            # Extract response content
            content = response.get("message", {}).get("content", "")
            
            # Parse response
            return self._parse_response(content, domains)
            
        except OllamaServerNotRunning as e:
            logger.error(f"Ollama server not running: {e}")
            return ClassificationResult(
                domain="unknown",
                confidence=0.0,
                reasoning="Error: Ollama server not running"
            )
            
        except OllamaTimeout as e:
            logger.error(f"Ollama timeout: {e}")
            return ClassificationResult(
                domain="unknown",
                confidence=0.0,
                reasoning="Error: Ollama request timed out"
            )
            
        except OllamaError as e:
            logger.error(f"Ollama error: {e}")
            return ClassificationResult(
                domain="unknown",
                confidence=0.0,
                reasoning=f"Error: {str(e)}"
            )


# Convenience function
def classify_domain(message: str) -> ClassificationResult:
    """
    Classify a message into a domain using default clients.
    
    This is a convenience function that creates temporary clients.
    For repeated classifications, create a DomainClassifier instance.
    
    Args:
        message: The message text to classify
        
    Returns:
        ClassificationResult with domain, confidence, and reasoning
    """
    ollama = get_ollama_client()
    scanner = VaultScanner()
    
    classifier = DomainClassifier(ollama, scanner)
    return classifier.classify(message)
