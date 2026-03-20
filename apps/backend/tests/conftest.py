"""
Pytest configuration and shared fixtures for Second Brain tests.
"""

import sys
from pathlib import Path
import pytest

# Add _scripts directory to sys.path so tests can import modules
BACKEND_DIR = Path(__file__).parent.parent
SCRIPTS_DIR = BACKEND_DIR / "_scripts"
sys.path.insert(0, str(SCRIPTS_DIR))


@pytest.fixture
def temp_state_dir(tmp_path, monkeypatch):
    """
    Fixture that creates a temporary state directory for tests.

    Monkeypatches the STATE_DIR in state.py to use tmp_path,
    isolating tests from real state files.

    Args:
        tmp_path: Pytest's temporary directory fixture
        monkeypatch: Pytest's monkeypatch fixture

    Returns:
        Path to temporary state directory
    """
    state_dir = tmp_path / ".state"
    state_dir.mkdir(parents=True, exist_ok=True)

    # Monkeypatch the STATE_DIR constant in state module
    import state
    monkeypatch.setattr(state, "STATE_DIR", state_dir)

    # Also update the file paths that depend on STATE_DIR
    monkeypatch.setattr(state, "MESSAGE_MAPPING_FILE", state_dir / "message_mapping.json")
    monkeypatch.setattr(state, "PROCESSED_MESSAGES_FILE", state_dir / "processed_messages.json")
    monkeypatch.setattr(state, "LAST_RUN_FILE", state_dir / "last_run.json")

    return state_dir


@pytest.fixture
def sample_classification():
    """
    Fixture providing a valid classification data dict.

    Returns:
        Dict with all required and optional classification fields
    """
    return {
        "destination": "ideas",
        "confidence": 0.85,
        "filename": "my-awesome-idea",
        "extracted": {
            "title": "My Awesome Idea",
            "oneliner": "A really great thought"
        },
        "linked_entities": [
            {"name": "Alice", "type": "person"},
            {"name": "Project X", "type": "project"}
        ]
    }


@pytest.fixture
def sample_thought():
    """
    Fixture providing sample thought text for testing.

    Returns:
        Sample thought string
    """
    return "This is a test thought that needs to be classified and stored"
