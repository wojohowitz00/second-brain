#!/usr/bin/env python3
"""
Message classifier for multi-level classification.

Classifies messages into four levels using local LLM:
- Domain (Personal, Just-Value, CCBH)
- PARA type (1_Projects, 2_Areas, 3_Resources, 4_Archive)
- Subject (from vault structure)
- Category (meeting, task, idea, reference, journal, question)

Uses vocabulary from VaultScanner to constrain classifications.
"""

import json
import re
from dataclasses import dataclass
from typing import Dict, List, Optional

from ollama_client import OllamaClient, OllamaError
from vault_scanner import VaultScanner


# Valid categories for message classification
VALID_CATEGORIES = ["meeting", "task", "idea", "reference", "journal", "question"]

# Valid PARA types
VALID_PARA_TYPES = ["1_Projects", "2_Areas", "3_Resources", "4_Archive"]

# Defaults for normalization
DEFAULT_DOMAIN = "Personal"
DEFAULT_PARA_TYPE = "3_Resources"
DEFAULT_CATEGORY = "reference"
DEFAULT_SUBJECT = "general"
DEFAULT_CONFIDENCE = 0.5


@dataclass
class ClassificationResult:
    """Result of message classification."""
    domain: str
    para_type: str
    subject: str
    category: str
    confidence: float
    reasoning: str
    raw_response: Optional[str] = None


class MessageClassifier:
    """
    Classifies messages into domain, PARA type, subject, and category.
    
    Uses single-shot LLM classification for performance (avoids multiple
    round trips which compound cold start latency).
    
    Usage:
        classifier = MessageClassifier()
        result = classifier.classify("Set up my home office workspace")
        print(f"{result.domain}/{result.para_type}/{result.subject} [{result.category}]")
    """
    
    def __init__(
        self,
        ollama_client: Optional[OllamaClient] = None,
        vault_scanner: Optional[VaultScanner] = None
    ):
        """
        Initialize classifier with optional custom clients.
        
        Args:
            ollama_client: OllamaClient instance (default: new OllamaClient())
            vault_scanner: VaultScanner instance (default: new VaultScanner())
        """
        self._ollama_client = ollama_client or OllamaClient()
        self._vault_scanner = vault_scanner or VaultScanner()
    
    def classify(self, message: str) -> ClassificationResult:
        """
        Classify a message into domain, PARA type, subject, and category.
        
        Args:
            message: The message text to classify
            
        Returns:
            ClassificationResult with all four classification levels
            
        Raises:
            OllamaServerNotRunning: Ollama server is not reachable
            OllamaTimeout: Request timed out
            OllamaModelNotFound: Configured model not available
        """
        # Get vocabulary from vault scanner
        vocabulary = self._vault_scanner.get_vocabulary()
        structure = self._vault_scanner.get_structure()
        
        # Build prompt
        prompt = self._build_prompt(message, vocabulary, structure)
        
        # Call LLM
        response = self._ollama_client.chat([
            {"role": "user", "content": prompt}
        ])
        
        # Extract response content
        raw_response = response.get("message", {}).get("content", "")
        
        # Parse and validate response
        return self._parse_response(raw_response, vocabulary, structure)
    
    def _build_prompt(
        self,
        message: str,
        vocabulary: Dict[str, List[str]],
        structure: Dict[str, Dict[str, List[str]]]
    ) -> str:
        """Build the classification prompt."""
        domains = ", ".join(vocabulary.get("domains", [DEFAULT_DOMAIN]))
        
        # Build subjects by domain for context
        subjects_by_domain = []
        for domain, para_dict in structure.items():
            all_subjects = []
            for para, subjects in para_dict.items():
                all_subjects.extend(subjects)
            if all_subjects:
                subjects_by_domain.append(f"  {domain}: {', '.join(sorted(set(all_subjects)))}")
        subjects_section = "\n".join(subjects_by_domain) if subjects_by_domain else "  (no subjects discovered)"
        
        return f"""You are a classification assistant for a personal knowledge management system.

VOCABULARY (use ONLY these values):
Domains: {domains}
PARA Types: 1_Projects, 2_Areas, 3_Resources, 4_Archive
Categories: meeting, task, idea, reference, journal, question

SUBJECTS by domain:
{subjects_section}

MESSAGE TO CLASSIFY:
"{message}"

Respond with ONLY this JSON (no other text):
{{"domain": "...", "para_type": "...", "subject": "...", "category": "...", "confidence": 0.0-1.0, "reasoning": "..."}}

RULES:
- domain MUST be one from the Domains list
- para_type MUST be one from PARA Types
- subject should be from the domain's subjects, or "general" if none fit
- category MUST be one from Categories
- confidence between 0.0 and 1.0 based on certainty
- reasoning should be a brief explanation"""
    
    def _parse_response(
        self,
        raw_response: str,
        vocabulary: Dict[str, List[str]],
        structure: Dict[str, Dict[str, List[str]]]
    ) -> ClassificationResult:
        """Parse LLM response and validate fields."""
        # Try JSON parse first
        parsed = None
        try:
            # Try to find JSON in the response (handle extra text)
            json_match = re.search(r'\{[^{}]*\}', raw_response, re.DOTALL)
            if json_match:
                parsed = json.loads(json_match.group())
        except json.JSONDecodeError:
            pass
        
        # Fallback to regex extraction if JSON fails
        if parsed is None:
            parsed = self._extract_with_regex(raw_response)
        
        # Validate and normalize each field
        valid_domains = vocabulary.get("domains", [DEFAULT_DOMAIN])
        
        domain = self._validate_domain(parsed.get("domain", ""), valid_domains)
        para_type = self._validate_para(parsed.get("para_type", ""))
        subject = self._validate_subject(parsed.get("subject", ""), structure, domain, para_type)
        category = self._validate_category(parsed.get("category", ""))
        confidence = self._validate_confidence(parsed.get("confidence", DEFAULT_CONFIDENCE))
        reasoning = parsed.get("reasoning", "Classification by LLM")
        
        return ClassificationResult(
            domain=domain,
            para_type=para_type,
            subject=subject,
            category=category,
            confidence=confidence,
            reasoning=reasoning,
            raw_response=raw_response
        )
    
    def _extract_with_regex(self, raw_response: str) -> Dict:
        """Extract fields using regex as fallback."""
        result = {}
        
        # Try to extract each field
        patterns = {
            "domain": r'"domain"\s*:\s*"([^"]+)"',
            "para_type": r'"para_type"\s*:\s*"([^"]+)"',
            "subject": r'"subject"\s*:\s*"([^"]+)"',
            "category": r'"category"\s*:\s*"([^"]+)"',
            "confidence": r'"confidence"\s*:\s*([0-9.]+)',
            "reasoning": r'"reasoning"\s*:\s*"([^"]+)"',
        }
        
        for field, pattern in patterns.items():
            match = re.search(pattern, raw_response)
            if match:
                value = match.group(1)
                if field == "confidence":
                    try:
                        value = float(value)
                    except ValueError:
                        value = DEFAULT_CONFIDENCE
                result[field] = value
        
        return result
    
    def _validate_domain(self, domain: str, valid_domains: List[str]) -> str:
        """Validate domain against vocabulary."""
        if not domain:
            return DEFAULT_DOMAIN
        
        # Case-insensitive match
        domain_lower = domain.lower()
        for valid in valid_domains:
            if valid.lower() == domain_lower:
                return valid
        
        # Check for partial match
        for valid in valid_domains:
            if domain_lower in valid.lower() or valid.lower() in domain_lower:
                return valid
        
        return DEFAULT_DOMAIN
    
    def _validate_para(self, para_type: str) -> str:
        """Validate PARA type."""
        if not para_type:
            return DEFAULT_PARA_TYPE
        
        # Case-insensitive match
        para_lower = para_type.lower()
        for valid in VALID_PARA_TYPES:
            if valid.lower() == para_lower:
                return valid
        
        # Check for partial match (e.g., "Projects" -> "1_Projects")
        for valid in VALID_PARA_TYPES:
            if para_lower in valid.lower() or valid.lower().split("_")[-1] in para_lower:
                return valid
        
        return DEFAULT_PARA_TYPE
    
    def _validate_subject(
        self,
        subject: str,
        structure: Dict[str, Dict[str, List[str]]],
        domain: str,
        para_type: str
    ) -> str:
        """Validate subject against vault structure."""
        if not subject or subject.lower() == "general":
            return DEFAULT_SUBJECT
        
        subject_lower = subject.lower()
        
        # First, check if subject exists in the specific domain/para
        if domain in structure and para_type in structure[domain]:
            for valid in structure[domain][para_type]:
                if valid.lower() == subject_lower:
                    return valid
        
        # Then check if subject exists anywhere in the domain
        if domain in structure:
            for para_dict in structure[domain].values():
                for valid in para_dict:
                    if valid.lower() == subject_lower:
                        return valid
        
        # Finally check if subject exists anywhere
        for domain_dict in structure.values():
            for para_dict in domain_dict.values():
                for valid in para_dict:
                    if valid.lower() == subject_lower:
                        return valid
        
        return DEFAULT_SUBJECT
    
    def _validate_category(self, category: str) -> str:
        """Validate category."""
        if not category:
            return DEFAULT_CATEGORY
        
        category_lower = category.lower()
        for valid in VALID_CATEGORIES:
            if valid.lower() == category_lower:
                return valid
        
        return DEFAULT_CATEGORY
    
    def _validate_confidence(self, confidence) -> float:
        """Validate and clamp confidence to 0.0-1.0."""
        try:
            conf = float(confidence)
            return max(0.0, min(1.0, conf))
        except (TypeError, ValueError):
            return DEFAULT_CONFIDENCE


# Convenience functions
def classify_message(message: str) -> ClassificationResult:
    """
    Classify a message using default clients.
    
    Args:
        message: The message text to classify
        
    Returns:
        ClassificationResult with all four classification levels
    """
    classifier = MessageClassifier()
    return classifier.classify(message)


def get_classifier() -> MessageClassifier:
    """Get a configured MessageClassifier instance."""
    return MessageClassifier()
