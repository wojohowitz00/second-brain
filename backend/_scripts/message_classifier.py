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
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

from ollama_client import OllamaClient, OllamaError
from vault_scanner import VaultScanner


def _load_sop(sop_root: Optional[Path] = None) -> str:
    """
    Load SOP markdown files from docs/sop/ and return concatenated content.
    Used to inject agent rules into the classifier prompt.
    """
    if sop_root is None:
        env_path = os.environ.get("SOP_PATH")
        if env_path:
            sop_root = Path(env_path)
        else:
            # Default: repo docs/sop relative to this script (backend/_scripts -> repo root)
            repo_root = Path(__file__).resolve().parent.parent.parent
            sop_root = repo_root / "docs" / "sop"
    if not sop_root.is_dir():
        return ""
    order = ("naming.md", "folder-rules.md", "tasks.md")
    parts = []
    for name in order:
        path = sop_root / name
        if path.is_file():
            parts.append(path.read_text().strip())
    return "\n\n".join(parts) if parts else ""


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

# Classification mode: "single" (one shot) or "pipeline" (domain → para → subject+category)
CLASSIFICATION_MODE_ENV = "CLASSIFICATION_MODE"
OLLAMA_MODEL_DOMAIN_ENV = "OLLAMA_MODEL_DOMAIN"
OLLAMA_MODEL_PARA_ENV = "OLLAMA_MODEL_PARA"
OLLAMA_MODEL_FULL_ENV = "OLLAMA_MODEL_FULL"


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
    
    def _get_classification_mode(self) -> str:
        """Return 'single' or 'pipeline' from env (default: single)."""
        mode = (os.environ.get(CLASSIFICATION_MODE_ENV) or "single").strip().lower()
        return mode if mode in ("single", "pipeline") else "single"

    def _get_model_for_step(self, step: str) -> Optional[str]:
        """Return model name for pipeline step (domain, para, subject_category) or None for default."""
        env_map = {
            "domain": OLLAMA_MODEL_DOMAIN_ENV,
            "para": OLLAMA_MODEL_PARA_ENV,
            "subject_category": OLLAMA_MODEL_FULL_ENV,
        }
        return os.environ.get(env_map.get(step, ""))

    def classify(self, message: str) -> ClassificationResult:
        """
        Classify a message into domain, PARA type, subject, and category.

        Uses single-shot or pipeline mode based on CLASSIFICATION_MODE env.
        """
        if self._get_classification_mode() == "pipeline":
            return self._classify_pipeline(message)

        vocabulary = self._vault_scanner.get_vocabulary()
        structure = self._vault_scanner.get_structure()
        prompt = self._build_prompt(message, vocabulary, structure)
        response = self._ollama_client.chat([{"role": "user", "content": prompt}])
        raw_response = response.get("message", {}).get("content", "")
        return self._parse_response(raw_response, vocabulary, structure)

    def _classify_pipeline(self, message: str) -> ClassificationResult:
        """Run domain → para → subject+category pipeline and return combined result."""
        vocabulary = self._vault_scanner.get_vocabulary()
        structure = self._vault_scanner.get_structure()
        valid_domains = vocabulary.get("domains", [DEFAULT_DOMAIN])
        sop_text = _load_sop()
        sop_section = f"\nSOP (follow when classifying):\n{sop_text}\n" if sop_text else ""

        # Step 1: Domain only
        domain_prompt = f"""You classify messages into ONE domain. Domains: {", ".join(valid_domains)}.{sop_section}

MESSAGE: "{message}"

Respond with ONLY this JSON: {{"domain": "...", "confidence": 0.0-1.0, "reasoning": "..."}}
domain MUST be one of: {", ".join(valid_domains)}."""
        model_domain = self._get_model_for_step("domain")
        resp1 = self._ollama_client.chat([{"role": "user", "content": domain_prompt}], model=model_domain)
        raw1 = resp1.get("message", {}).get("content", "")
        domain, conf1, reason1 = self._parse_domain_step(raw1, valid_domains)
        if domain is None:
            domain = DEFAULT_DOMAIN
            conf1 = DEFAULT_CONFIDENCE
            reason1 = "fallback default"

        # Step 2: PARA only (given domain)
        para_prompt = f"""You classify messages into ONE PARA type. Message: "{message}". Domain (already chosen): {domain}.{sop_section}

PARA Types: 1_Projects, 2_Areas, 3_Resources, 4_Archive.

Respond with ONLY this JSON: {{"para_type": "...", "confidence": 0.0-1.0, "reasoning": "..."}}
para_type MUST be one of: 1_Projects, 2_Areas, 3_Resources, 4_Archive."""
        model_para = self._get_model_for_step("para")
        resp2 = self._ollama_client.chat([{"role": "user", "content": para_prompt}], model=model_para)
        raw2 = resp2.get("message", {}).get("content", "")
        para_type, conf2, reason2 = self._parse_para_step(raw2)
        if para_type is None:
            para_type = DEFAULT_PARA_TYPE
            conf2 = DEFAULT_CONFIDENCE
            reason2 = "fallback default"

        # Step 3: Subject + category (given domain, para)
        subjects_for_domain = []
        if domain in structure:
            for para, subjects in structure[domain].items():
                subjects_for_domain.extend(subjects)
        subjects_str = ", ".join(sorted(set(subjects_for_domain))) if subjects_for_domain else "general"
        step3_prompt = f"""You classify message into subject and category. Message: "{message}". Domain: {domain}. PARA: {para_type}.{sop_section}

Subjects for this domain: {subjects_str}. Use one of these or "general".
Categories: meeting, task, idea, reference, journal, question.

Respond with ONLY this JSON: {{"subject": "...", "category": "...", "confidence": 0.0-1.0, "reasoning": "..."}}"""
        model_full = self._get_model_for_step("subject_category")
        resp3 = self._ollama_client.chat([{"role": "user", "content": step3_prompt}], model=model_full)
        raw3 = resp3.get("message", {}).get("content", "")
        subject, category, conf3, reason3 = self._parse_subject_category_step(raw3, structure, domain, para_type)
        if subject is None:
            subject = DEFAULT_SUBJECT
        if category is None:
            category = DEFAULT_CATEGORY
        if conf3 is None:
            conf3 = DEFAULT_CONFIDENCE
            reason3 = "fallback default"

        confidence = min(conf1, conf2, conf3) if all(x is not None for x in (conf1, conf2, conf3)) else DEFAULT_CONFIDENCE
        reasoning = f"Pipeline: domain={reason1}; para={reason2}; subject+cat={reason3}"

        return ClassificationResult(
            domain=domain,
            para_type=para_type,
            subject=subject,
            category=category,
            confidence=confidence,
            reasoning=reasoning,
            raw_response=f"domain: {raw1}\npara: {raw2}\nsubject_category: {raw3}",
        )

    def _parse_domain_step(self, raw: str, valid_domains: List[str]) -> tuple:
        """Parse domain step JSON; return (domain, confidence, reasoning)."""
        parsed = self._parse_json_single(raw)
        if not parsed:
            return (None, None, None)
        domain = self._validate_domain(parsed.get("domain", ""), valid_domains)
        conf = self._validate_confidence(parsed.get("confidence", DEFAULT_CONFIDENCE))
        reason = parsed.get("reasoning", "") or "Pipeline step"
        return (domain, conf, reason)

    def _parse_para_step(self, raw: str) -> tuple:
        """Parse para_type step response; return (para_type, confidence, reasoning)."""
        parsed = self._parse_json_single(raw)
        if not parsed:
            return (None, None, None)
        para = self._validate_para(parsed.get("para_type", ""))
        conf = self._validate_confidence(parsed.get("confidence", DEFAULT_CONFIDENCE))
        reason = parsed.get("reasoning", "") or "Pipeline step"
        return (para, conf, reason)

    def _parse_subject_category_step(
        self, raw: str, structure: Dict, domain: str, para_type: str
    ) -> tuple:
        """Parse subject+category step; return (subject, category, confidence, reasoning)."""
        parsed = self._parse_json_single(raw)
        if not parsed:
            return (None, None, None, None)
        subject = self._validate_subject(parsed.get("subject", ""), structure, domain, para_type)
        category = self._validate_category(parsed.get("category", ""))
        conf = self._validate_confidence(parsed.get("confidence", DEFAULT_CONFIDENCE))
        reason = parsed.get("reasoning", "") or "Pipeline step"
        return (subject, category, conf, reason)

    def _parse_json_single(self, raw: str) -> Optional[Dict]:
        """Extract single JSON object from raw response."""
        try:
            json_match = re.search(r"\{[^{}]*\}", raw, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except json.JSONDecodeError:
            pass
        return None

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
        sop_text = _load_sop()
        sop_section = f"\nSOP (follow when classifying):\n{sop_text}\n" if sop_text else ""

        return f"""You are a classification assistant for a personal knowledge management system.

VOCABULARY (use ONLY these values):
Domains: {domains}
PARA Types: 1_Projects, 2_Areas, 3_Resources, 4_Archive
Categories: meeting, task, idea, reference, journal, question

SUBJECTS by domain:
{subjects_section}
{sop_section}

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
