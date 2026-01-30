#!/usr/bin/env python3
"""
Wikilink generation for Obsidian integration.

Transforms entity mentions to [[wikilinks]] and creates stub files
for new entities not yet in the vault.
"""

import re
import yaml
from pathlib import Path
from datetime import datetime
from typing import Optional

VAULT_PATH = Path.home() / "SecondBrain"


def normalize_to_filename(name: str) -> str:
    """
    Convert a display name to a kebab-case filename.

    "John Smith" -> "john-smith"
    "Project: Alpha" -> "project-alpha"
    """
    # Lowercase
    filename = name.lower()
    # Replace common separators with hyphens
    filename = re.sub(r"[:\s_]+", "-", filename)
    # Remove non-alphanumeric except hyphens
    filename = re.sub(r"[^a-z0-9-]", "", filename)
    # Collapse multiple hyphens
    filename = re.sub(r"-+", "-", filename)
    # Strip leading/trailing hyphens
    filename = filename.strip("-")
    return filename or "unnamed"


def find_existing_entity(name: str, entity_type: str) -> Optional[Path]:
    """
    Check if an entity already exists in the vault.

    Searches by:
    1. Exact filename match
    2. Match against 'name' field in frontmatter
    3. Match against 'aliases' list in frontmatter

    Args:
        name: Display name to search for
        entity_type: "people" or "projects"

    Returns:
        Path to existing file, or None if not found
    """
    folder = VAULT_PATH / entity_type
    if not folder.exists():
        return None

    target_filename = normalize_to_filename(name)
    name_lower = name.lower()

    # Check for exact filename match
    exact_match = folder / f"{target_filename}.md"
    if exact_match.exists():
        return exact_match

    # Check name and aliases in existing files
    for filepath in folder.glob("*.md"):
        try:
            content = filepath.read_text()
            if "---" not in content:
                continue

            # Parse frontmatter
            parts = content.split("---", 2)
            if len(parts) < 3:
                continue

            frontmatter = yaml.safe_load(parts[1])
            if not frontmatter:
                continue

            # Check 'name' field
            fm_name = frontmatter.get("name", "")
            if fm_name and fm_name.lower() == name_lower:
                return filepath

            # Check 'aliases' list
            aliases = frontmatter.get("aliases", [])
            if aliases:
                for alias in aliases:
                    if isinstance(alias, str) and alias.lower() == name_lower:
                        return filepath

        except Exception:
            continue

    return None


def create_stub_file(name: str, entity_type: str, context: str = "") -> Path:
    """
    Create a stub file for a newly mentioned entity.

    Args:
        name: Display name for the entity
        entity_type: "people" or "projects"
        context: Optional context about why this was created

    Returns:
        Path to the created file
    """
    folder = VAULT_PATH / entity_type
    folder.mkdir(parents=True, exist_ok=True)

    filename = normalize_to_filename(name)
    filepath = folder / f"{filename}.md"

    # Don't overwrite existing files
    if filepath.exists():
        return filepath

    today = datetime.now().strftime("%Y-%m-%d")

    if entity_type == "people":
        content = f"""---
type: person
name: {name}
aliases: []
context: {context}
follow_ups: []
last_touched: {today}
tags:
  - stub
---

## Notes

_This is a stub file created automatically when {name} was mentioned._
_Add details as you learn more about this person._
"""
    else:  # projects
        content = f"""---
type: project
name: {name}
status: mentioned
next_action: ""
created: {today}
tags:
  - stub
---

## Notes

_This is a stub file created automatically when {name} was mentioned._
_Add project details when you start working on it._
"""

    filepath.write_text(content)
    return filepath


def process_linked_entities(entities: list, create_stubs: bool = True) -> dict:
    """
    Process a list of linked entities, creating stubs for new ones.

    Args:
        entities: List of dicts with "name" and "type" keys
        create_stubs: Whether to create stub files for new entities

    Returns:
        Dict mapping original names to their wikilink filenames
    """
    links = {}

    for entity in entities:
        name = entity.get("name", "").strip()
        entity_type = entity.get("type", "").lower()

        if not name or entity_type not in ("people", "projects", "person", "project"):
            continue

        # Normalize type
        folder = "people" if entity_type in ("people", "person") else "projects"

        # Check if entity exists
        existing = find_existing_entity(name, folder)

        if existing:
            # Use existing filename (without .md)
            links[name] = existing.stem
        elif create_stubs:
            # Create stub and use its filename
            stub = create_stub_file(name, folder, context="Mentioned in capture")
            links[name] = stub.stem
        else:
            # Just use normalized name
            links[name] = normalize_to_filename(name)

    return links


def insert_wikilinks(text: str, entity_links: dict) -> str:
    """
    Replace entity mentions in text with [[wikilinks]].

    Args:
        text: Original text
        entity_links: Dict mapping names to wikilink targets

    Returns:
        Text with [[wikilinks]] inserted
    """
    result = text

    # Sort by length (longest first) to handle overlapping names
    sorted_names = sorted(entity_links.keys(), key=len, reverse=True)

    for name in sorted_names:
        target = entity_links[name]
        # Case-insensitive replacement, preserving original case in display
        pattern = re.compile(re.escape(name), re.IGNORECASE)

        def replace_with_link(match):
            original = match.group(0)
            # Use display text if different from target
            if normalize_to_filename(original) == target:
                return f"[[{target}]]"
            else:
                return f"[[{target}|{original}]]"

        result = pattern.sub(replace_with_link, result)

    return result
