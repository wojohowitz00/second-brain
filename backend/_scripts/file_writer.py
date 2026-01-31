#!/usr/bin/env python3
"""
File writer for PARA-structured Obsidian vault.

Creates .md files with YAML frontmatter in the correct folder hierarchy:
domain / para_type / subject / {timestamp}-{sanitized-title}.md

Uses pathlib for all path operations and manual YAML generation
(no external dependencies).
"""

import re
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from message_classifier import ClassificationResult


def sanitize_filename(text: str, max_length: int = 30) -> str:
    """
    Convert text to a safe, kebab-case filename.
    
    Args:
        text: Input text to sanitize
        max_length: Maximum length of output (default 30)
        
    Returns:
        Lowercase, hyphenated, safe filename string
        
    Examples:
        >>> sanitize_filename("Hello World!")
        'hello-world'
        >>> sanitize_filename("Test: Something")
        'test-something'
    """
    if not text or not text.strip():
        return "untitled"
    
    # Lowercase
    result = text.lower()
    
    # Remove special characters, keep alphanumeric and spaces
    result = re.sub(r'[^a-z0-9\s-]', '', result)
    
    # Replace spaces with hyphens
    result = re.sub(r'\s+', '-', result)
    
    # Collapse multiple hyphens
    result = re.sub(r'-+', '-', result)
    
    # Strip leading/trailing hyphens
    result = result.strip('-')
    
    # Handle empty result after sanitization
    if not result:
        return "untitled"
    
    # Truncate to max_length
    if len(result) > max_length:
        result = result[:max_length].rstrip('-')
    
    return result


def build_frontmatter(classification: "ClassificationResult", timestamp: str) -> str:
    """
    Build YAML frontmatter string from classification result.
    
    Args:
        classification: ClassificationResult with domain, para_type, etc.
        timestamp: ISO format timestamp string
        
    Returns:
        Complete YAML frontmatter including --- delimiters
        
    Example output:
        ---
        domain: Personal
        para_type: 1_Projects
        subject: apps
        category: task
        confidence: 0.85
        reasoning: "Project work on app feature"
        created: 2026-01-31T12:00:00
        tags: []
        ---
    """
    # Quote reasoning if it contains special characters
    reasoning = classification.reasoning
    if ':' in reasoning or '"' in reasoning or '\n' in reasoning:
        # Escape quotes and wrap in quotes
        reasoning = '"' + reasoning.replace('"', '\\"') + '"'
    
    frontmatter = f"""---
domain: {classification.domain}
para_type: {classification.para_type}
subject: {classification.subject}
category: {classification.category}
confidence: {classification.confidence:.2f}
reasoning: {reasoning}
created: {timestamp}
tags: []
---"""
    
    return frontmatter


def create_note_file(
    classification: "ClassificationResult",
    message_text: str,
    vault_path: Path,
    timestamp: str = None
) -> Path:
    """
    Create a .md file in the vault with proper structure.
    
    Args:
        classification: ClassificationResult with classification details
        message_text: Original message text to include in body
        vault_path: Root path of the Obsidian vault
        timestamp: Optional timestamp (defaults to now)
        
    Returns:
        Path to the created file
        
    File structure:
        vault_path / domain / para_type / subject / {timestamp}-{title}.md
        
    Example:
        ~/PARA/Personal/1_Projects/apps/20260131-120000-fix-login-bug.md
    """
    # Generate timestamp if not provided
    if timestamp is None:
        timestamp = datetime.now().isoformat()
    
    # Create folder path: domain / para_type / subject
    folder = vault_path / classification.domain / classification.para_type / classification.subject
    folder.mkdir(parents=True, exist_ok=True)
    
    # Generate unique filename with timestamp
    file_timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    sanitized_title = sanitize_filename(message_text)
    filename = f"{file_timestamp}-{sanitized_title}.md"
    
    filepath = folder / filename
    
    # Build file content
    frontmatter = build_frontmatter(classification, timestamp)
    
    body = f"""
## Original Capture

{message_text}

## Classification

- **Domain:** {classification.domain}
- **PARA Type:** {classification.para_type}
- **Subject:** {classification.subject}
- **Category:** {classification.category}
- **Confidence:** {classification.confidence:.0%}
- **Reasoning:** {classification.reasoning}
"""
    
    content = frontmatter + body
    
    # Write file
    filepath.write_text(content)
    
    return filepath


# Convenience function for simple file creation
def write_classified_note(
    classification: "ClassificationResult",
    message: str,
    vault_root: Path = None
) -> Path:
    """
    Convenience function to write a classified note to the vault.
    
    Args:
        classification: ClassificationResult from MessageClassifier
        message: Original message text
        vault_root: Vault root path (defaults to ~/PARA)
        
    Returns:
        Path to created file
    """
    if vault_root is None:
        vault_root = Path.home() / "PARA"
    
    return create_note_file(
        classification=classification,
        message_text=message,
        vault_path=vault_root
    )
