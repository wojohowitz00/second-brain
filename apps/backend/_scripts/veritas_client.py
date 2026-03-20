#!/usr/bin/env python3
"""
Optional Veritas Kanban REST client for push-on-capture.

When VERITAS_PUSH_ENABLED is set, Second Brain creates a task in Veritas
when the user posts todo: or kanban: to Slack. Vault note remains source of truth.
"""

import os
from typing import Optional

import requests

# Config from env
VERITAS_BASE_URL_ENV = "VERITAS_BASE_URL"
VERITAS_API_KEY_ENV = "VERITAS_API_KEY"
VERITAS_PUSH_ENABLED_ENV = "VERITAS_PUSH_ENABLED"
DEFAULT_BASE_URL = "http://localhost:3001"

# Second Brain status -> Veritas status
STATUS_MAP = {
    "backlog": "todo",
    "in_progress": "in-progress",
    "blocked": "blocked",
    "done": "done",
}


class VeritasAPIError(Exception):
    """Raised when Veritas API returns an error."""
    pass


def is_push_enabled() -> bool:
    """Return True if VERITAS_PUSH_ENABLED is set to a truthy value."""
    val = os.environ.get(VERITAS_PUSH_ENABLED_ENV, "").strip().lower()
    return val in ("true", "1", "yes", "on")


def _get_base_url() -> str:
    return os.environ.get(VERITAS_BASE_URL_ENV, DEFAULT_BASE_URL).rstrip("/")


def _get_api_key() -> Optional[str]:
    return os.environ.get(VERITAS_API_KEY_ENV) or None


def create_task(
    title: str,
    status: str = "todo",
    task_type: str = "task",
    priority: Optional[str] = None,
    project: Optional[str] = None,
    description: Optional[str] = None,
) -> Optional[dict]:
    """
    Create a task in Veritas Kanban via REST API.

    Args:
        title: Task title
        status: backlog -> todo, in_progress -> in-progress, blocked -> blocked, done -> done
        task_type: Veritas type (e.g. task, code)
        priority: Optional (high, medium, low)
        project: Optional project name
        description: Optional body/description

    Returns:
        Veritas task object (dict) on success, None if push disabled or API key missing/failure
    """
    if not is_push_enabled():
        return None
    api_key = _get_api_key()
    if not api_key:
        return None
    base = _get_base_url()
    url = f"{base}/api/tasks"
    veritas_status = STATUS_MAP.get(status, "todo")
    payload = {
        "title": title[:500],  # reasonable max
        "status": veritas_status,
        "type": task_type,
    }
    if priority:
        payload["priority"] = priority
    if project:
        payload["project"] = project
    if description:
        payload["description"] = description[:2000]
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": api_key,
    }
    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=10)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.RequestException:
        return None
