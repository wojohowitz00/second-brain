#!/usr/bin/env python3
"""
Schema definitions and validation for Second Brain.

Validates classification responses from Claude to prevent crashes
from malformed or unexpected data.
"""

import re
from typing import Optional

# Valid destinations
VALID_DESTINATIONS = {"people", "projects", "ideas", "admin"}


class ValidationError(Exception):
    """Raised when classification validation fails."""
    pass


def validate_classification(data: dict) -> dict:
    """
    Validate a classification response from Claude.

    Args:
        data: The parsed JSON response

    Returns:
        The validated data (possibly with defaults filled in)

    Raises:
        ValidationError: If data is invalid and can't be recovered
    """
    if not isinstance(data, dict):
        raise ValidationError(f"Classification must be a dict, got {type(data).__name__}")

    # Required fields
    destination = data.get("destination")
    if destination not in VALID_DESTINATIONS:
        raise ValidationError(
            f"Invalid destination '{destination}'. Must be one of: {VALID_DESTINATIONS}"
        )

    # Confidence: must be a number between 0 and 1
    confidence = data.get("confidence")
    if confidence is None:
        confidence = 0.5  # Default if missing
    elif not isinstance(confidence, (int, float)):
        raise ValidationError(f"Confidence must be a number, got {type(confidence).__name__}")
    elif not 0 <= confidence <= 1:
        # Clamp to valid range rather than reject
        confidence = max(0, min(1, confidence))

    # Filename: must be a valid kebab-case string
    filename = data.get("filename", "")
    if not filename:
        # Generate fallback filename
        filename = f"untitled-{destination}"
    else:
        # Sanitize filename
        filename = sanitize_filename(filename)

    # Extracted: must be a dict
    extracted = data.get("extracted", {})
    if not isinstance(extracted, dict):
        extracted = {}

    return {
        "destination": destination,
        "confidence": confidence,
        "filename": filename,
        "extracted": extracted
    }


def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename to be safe and kebab-case.

    - Removes path traversal attempts
    - Converts to lowercase
    - Replaces invalid characters with hyphens
    - Collapses multiple hyphens
    """
    # Remove any path components
    filename = filename.replace("/", "-").replace("\\", "-")
    filename = filename.replace("..", "-")

    # Convert to lowercase
    filename = filename.lower()

    # Replace spaces and underscores with hyphens
    filename = filename.replace(" ", "-").replace("_", "-")

    # Remove any characters that aren't alphanumeric or hyphens
    filename = re.sub(r"[^a-z0-9-]", "", filename)

    # Collapse multiple hyphens
    filename = re.sub(r"-+", "-", filename)

    # Remove leading/trailing hyphens
    filename = filename.strip("-")

    # Ensure not empty
    if not filename:
        filename = "untitled"

    # Limit length
    if len(filename) > 100:
        filename = filename[:100].rstrip("-")

    return filename


def create_fallback_classification(
    thought: str,
    error: Optional[str] = None
) -> dict:
    """
    Create a fallback classification when Claude's response is invalid.

    Defaults to 'ideas' category with low confidence so user can review.
    """
    # Generate filename from first few words
    words = thought.split()[:5]
    filename = "-".join(words).lower()
    filename = sanitize_filename(filename) or "unclassified"

    return {
        "destination": "ideas",
        "confidence": 0.3,  # Low confidence triggers review
        "filename": filename,
        "extracted": {
            "title": thought[:50] + ("..." if len(thought) > 50 else ""),
            "oneliner": "Auto-classified due to validation error",
            "_validation_error": error
        }
    }


def parse_and_validate_classification(json_str: str) -> dict:
    """
    Parse JSON string and validate as classification.

    Args:
        json_str: Raw JSON string from Claude

    Returns:
        Validated classification dict

    Note:
        Returns fallback classification if parsing/validation fails
        (does not raise - caller should check confidence)
    """
    import json

    try:
        data = json.loads(json_str)
        return validate_classification(data)
    except json.JSONDecodeError as e:
        return create_fallback_classification(
            json_str[:100],
            error=f"JSON parse error: {e}"
        )
    except ValidationError as e:
        return create_fallback_classification(
            json_str[:100],
            error=str(e)
        )
