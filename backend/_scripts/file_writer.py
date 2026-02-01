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
from typing import TYPE_CHECKING, List, Optional, Tuple

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


def build_frontmatter(
    classification: "ClassificationResult",
    timestamp: str,
    task_info: Optional[dict] = None,
) -> str:
    """
    Build YAML frontmatter string from classification result.

    Args:
        classification: ClassificationResult with domain, para_type, etc.
        timestamp: ISO format timestamp string
        task_info: Optional dict with type, status, board, priority, project for task notes.

    Returns:
        Complete YAML frontmatter including --- delimiters
    """
    # Quote reasoning if it contains special characters
    reasoning = classification.reasoning
    if ":" in reasoning or '"' in reasoning or "\n" in reasoning:
        reasoning = '"' + reasoning.replace('"', '\\"') + '"'

    frontmatter = f"""---
domain: {classification.domain}
para_type: {classification.para_type}
subject: {classification.subject}
category: {classification.category}
confidence: {classification.confidence:.2f}
reasoning: {reasoning}
created: {timestamp}
tags: []"""

    if task_info:
        frontmatter += "\ntype: task"
        frontmatter += f"\nstatus: {task_info.get('status', 'backlog')}"
        if task_info.get("board"):
            frontmatter += f"\nboard: {task_info['board']}"
        if task_info.get("priority"):
            frontmatter += f"\npriority: {task_info['priority']}"
        if task_info.get("project"):
            frontmatter += f"\nproject: {task_info['project']}"
        if task_info.get("view"):
            frontmatter += f"\nview: {task_info['view']}"

    frontmatter += "\n---"
    return frontmatter


def create_note_file(
    classification: "ClassificationResult",
    message_text: str,
    vault_path: Path,
    timestamp: str = None,
    task_info: Optional[dict] = None,
) -> Path:
    """
    Create a .md file in the vault with proper structure.

    Args:
        classification: ClassificationResult with classification details
        message_text: Original message text to include in body
        vault_path: Root path of the Obsidian vault
        timestamp: Optional timestamp (defaults to now)
        task_info: Optional dict for task notes (type, status, board, priority, project, view).

    Returns:
        Path to the created file.

    File structure:
        vault_path / domain / para_type / subject / {timestamp}-{title}.md
    """
    if timestamp is None:
        timestamp = datetime.now().isoformat()

    folder = vault_path / classification.domain / classification.para_type / classification.subject
    folder.mkdir(parents=True, exist_ok=True)

    file_timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    sanitized_title = sanitize_filename(message_text)
    filename = f"{file_timestamp}-{sanitized_title}.md"
    filepath = folder / filename

    frontmatter = build_frontmatter(classification, timestamp, task_info=task_info)
    
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


def safe_attachment_filename(original_name: str, existing: Optional[set] = None) -> str:
    """
    Return a safe filename for an attachment (kebab-case stem + original extension).
    If existing set provided and name collides, append _1, _2, etc.
    """
    existing = existing or set()
    path = Path(original_name)
    stem = sanitize_filename(path.stem) if path.stem else "attachment"
    ext = path.suffix.lower() if path.suffix else ""
    name = stem + ext
    if name not in existing:
        return name
    i = 1
    while f"{stem}_{i}{ext}" in existing:
        i += 1
    return f"{stem}_{i}{ext}"


def append_attachments_section(note_path: Path, links: List[Tuple[str, str]]) -> None:
    """
    Append an "## Attachments" section with markdown links to the note file.

    Args:
        note_path: Path to the .md note file
        links: List of (display_name, relative_path) for each attachment (path relative to note)
    """
    if not links:
        return
    section = "\n\n## Attachments\n\n" + "\n".join(f"- [{name}]({path})" for name, path in links)
    content = note_path.read_text()
    if "## Attachments" in content:
        return  # Already has attachments, avoid duplicate
    note_path.write_text(content.rstrip() + section + "\n")


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
