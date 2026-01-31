#!/usr/bin/env python3
"""
Task parser for extracting task indicators from Slack messages.

Parses messages with task prefixes (todo:, kanban:) and extracts:
- Task view type (todo/kanban)
- Domain indicator (Just-Value, Personal, CCBH)
- Project indicator
- Priority level (p1/p2/p3 → high/medium/low)
- Status commands (!done, !progress, !blocked, !backlog)
"""

import re
from typing import Dict, List, Optional

# Priority mapping
PRIORITY_MAP: Dict[str, str] = {
    "p1": "high",
    "p2": "medium",
    "p3": "low"
}

# Status commands
STATUS_COMMANDS: List[str] = ["!done", "!progress", "!blocked", "!backlog"]

# Status command to status value mapping
STATUS_MAP: Dict[str, str] = {
    "!done": "done",
    "!progress": "in_progress",
    "!blocked": "blocked",
    "!backlog": "backlog"
}

# Domain normalization aliases
DOMAIN_ALIASES: Dict[str, str] = {
    "just-value": "Just-Value",
    "justvalue": "Just-Value",
    "jv": "Just-Value",
    "personal": "Personal",
    "ccbh": "CCBH",
}

# Regex patterns
TASK_PREFIX_PATTERN = re.compile(r"^(todo|kanban):\s*", re.IGNORECASE)
DOMAIN_PATTERN = re.compile(r"\bdomain:(\S+)", re.IGNORECASE)
PROJECT_PATTERN = re.compile(r"\bproject:(\S+)", re.IGNORECASE)
PRIORITY_PATTERN = re.compile(r"\b(p[123])\b", re.IGNORECASE)


def parse_task_indicators(text: str) -> Dict:
    """
    Parse Slack message for task indicators.
    
    Args:
        text: Raw message text
        
    Returns:
        Dict with keys:
        - is_task: bool - Whether message is a task
        - view: str - "todo" or "kanban" (if is_task)
        - domain: str | None - Normalized domain name
        - project: str | None - Project name
        - priority: str - "high", "medium", or "low"
        - clean_text: str - Message with indicators removed
    """
    result = {
        "is_task": False,
        "view": None,
        "domain": None,
        "project": None,
        "priority": "medium",  # Default
        "clean_text": text
    }
    
    # Check for task prefix
    prefix_match = TASK_PREFIX_PATTERN.match(text)
    if not prefix_match:
        return result
    
    result["is_task"] = True
    result["view"] = prefix_match.group(1).lower()
    
    # Remove prefix from text
    working_text = TASK_PREFIX_PATTERN.sub("", text).strip()
    
    # Parse domain
    domain_match = DOMAIN_PATTERN.search(working_text)
    if domain_match:
        raw_domain = domain_match.group(1).lower()
        result["domain"] = DOMAIN_ALIASES.get(raw_domain, raw_domain.title())
        working_text = DOMAIN_PATTERN.sub("", working_text)
    
    # Parse project
    project_match = PROJECT_PATTERN.search(working_text)
    if project_match:
        result["project"] = project_match.group(1).lower()
        working_text = PROJECT_PATTERN.sub("", working_text)
    
    # Parse priority
    priority_match = PRIORITY_PATTERN.search(working_text)
    if priority_match:
        priority_key = priority_match.group(1).lower()
        result["priority"] = PRIORITY_MAP.get(priority_key, "medium")
        working_text = PRIORITY_PATTERN.sub("", working_text)
    
    # Clean up remaining text
    result["clean_text"] = " ".join(working_text.split()).strip()
    
    return result


def is_status_command(text: str) -> bool:
    """
    Check if text is a status command.
    
    Args:
        text: Message text
        
    Returns:
        True if text matches a status command
    """
    normalized = text.strip().lower()
    return normalized in [cmd.lower() for cmd in STATUS_COMMANDS]


def parse_status_command(text: str) -> Optional[str]:
    """
    Parse status command to status value.
    
    Args:
        text: Status command text (e.g., "!done")
        
    Returns:
        Status value (e.g., "done") or None if not a command
    """
    normalized = text.strip().lower()
    for cmd, status in STATUS_MAP.items():
        if normalized == cmd.lower():
            return status
    return None
