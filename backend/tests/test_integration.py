"""
Integration tests for Second Brain backend.

Tests the complete flow of:
1. Writing .md files with frontmatter to Obsidian vault (Success Criteria #2)
2. Processing fix: corrections to move files (Success Criteria #3)
3. State tracking idempotency (Success Criteria #4)

These tests use tmp_path for isolation and don't require real Slack API.
"""

import pytest
from pathlib import Path
from datetime import datetime
import yaml

# Modules under test
from process_inbox import write_to_obsidian
from fix_handler import move_file, _get_type_for_destination
from state import (
    is_message_processed,
    mark_message_processed,
    set_file_for_message,
    get_file_for_message,
)


# --- Fixtures ---

@pytest.fixture
def temp_vault(tmp_path, monkeypatch):
    """
    Create a temporary Obsidian vault for testing.

    Monkeypatches VAULT_PATH in both process_inbox and fix_handler modules.

    Args:
        tmp_path: Pytest's temporary directory fixture
        monkeypatch: Pytest's monkeypatch fixture

    Returns:
        Path to temporary vault directory
    """
    vault = tmp_path / "TestVault"
    vault.mkdir(parents=True, exist_ok=True)

    # Monkeypatch VAULT_PATH in both modules
    import process_inbox
    import fix_handler
    monkeypatch.setattr(process_inbox, "VAULT_PATH", vault)
    monkeypatch.setattr(fix_handler, "VAULT_PATH", vault)

    return vault


# --- Test File Creation (Success Criteria #2) ---

def test_write_to_obsidian_creates_file_in_correct_folder(temp_vault, sample_classification):
    """
    Test that write_to_obsidian() creates file in the correct destination folder.

    Success Criteria #2: Backend can create .md files in test vault.
    """
    timestamp = datetime.now().isoformat()

    filepath = write_to_obsidian(sample_classification, "Original thought text", timestamp)

    # Verify file was created
    assert filepath.exists()

    # Verify file is in correct folder
    expected_folder = temp_vault / sample_classification["destination"]
    assert filepath.parent == expected_folder

    # Verify filename matches
    expected_name = sample_classification["filename"] + ".md"
    assert filepath.name == expected_name


def test_write_to_obsidian_has_valid_yaml_frontmatter(temp_vault, sample_classification):
    """
    Test that created files have valid YAML frontmatter with proper delimiters.

    Success Criteria #2: .md files have frontmatter.
    """
    timestamp = datetime.now().isoformat()

    filepath = write_to_obsidian(sample_classification, "Original thought", timestamp)

    content = filepath.read_text()

    # Verify file starts with ---
    assert content.startswith("---\n"), "File should start with YAML frontmatter delimiter"

    # Verify frontmatter closes with ---
    parts = content.split("---")
    assert len(parts) >= 3, "File should have opening and closing --- delimiters"

    # Verify frontmatter is valid YAML
    frontmatter_text = parts[1]
    frontmatter = yaml.safe_load(frontmatter_text)
    assert isinstance(frontmatter, dict)


def test_write_to_obsidian_frontmatter_has_required_fields(temp_vault, sample_classification):
    """
    Test that frontmatter includes required fields based on destination type.

    Success Criteria #2: Frontmatter includes required fields.
    """
    timestamp = datetime.now().isoformat()

    filepath = write_to_obsidian(sample_classification, "Original thought", timestamp)

    content = filepath.read_text()
    parts = content.split("---")
    frontmatter = yaml.safe_load(parts[1])

    # All files should have type field
    assert "type" in frontmatter

    # For ideas destination
    if sample_classification["destination"] == "ideas":
        assert frontmatter["type"] == "idea"
        assert "created" in frontmatter
        # YAML may load date as datetime.date object or string
        created = str(frontmatter["created"])
        assert created == timestamp[:10]


def test_write_to_obsidian_includes_original_capture_text(temp_vault, sample_classification):
    """
    Test that original capture text appears in the file.

    Success Criteria #2: Original capture text preserved.
    """
    timestamp = datetime.now().isoformat()
    original_text = "This is my original thought that should be preserved"

    filepath = write_to_obsidian(sample_classification, original_text, timestamp)

    content = filepath.read_text()

    # Verify original text appears in file
    assert original_text in content

    # Verify it's in the "Original Capture" section
    assert "## Original Capture" in content


def test_write_to_obsidian_creates_different_frontmatter_per_type(temp_vault):
    """
    Test that different destination types get appropriate frontmatter structures.
    """
    timestamp = datetime.now().isoformat()

    # Test "people" destination
    people_classification = {
        "destination": "people",
        "confidence": 0.9,
        "filename": "john-doe",
        "extracted": {
            "name": "John Doe",
            "aliases": ["JD"],
            "context": "Met at conference",
            "follow_ups": ["Send article"]
        },
        "linked_entities": []
    }

    filepath = write_to_obsidian(people_classification, "Met John at conference", timestamp)
    content = filepath.read_text()
    parts = content.split("---")
    frontmatter = yaml.safe_load(parts[1])

    # People-specific fields
    assert frontmatter["type"] == "person"
    assert frontmatter["name"] == "John Doe"
    assert "aliases" in frontmatter
    assert "context" in frontmatter
    assert "follow_ups" in frontmatter
    assert "last_touched" in frontmatter


def test_write_to_obsidian_handles_duplicate_filenames(temp_vault, sample_classification):
    """
    Test that duplicate filenames get timestamp appended.
    """
    timestamp = datetime.now().isoformat()

    # Create first file
    filepath1 = write_to_obsidian(sample_classification, "First thought", timestamp)

    # Create second file with same classification (same filename)
    filepath2 = write_to_obsidian(sample_classification, "Second thought", timestamp)

    # Files should be different
    assert filepath1 != filepath2

    # Both should exist
    assert filepath1.exists()
    assert filepath2.exists()

    # Second filename should have timestamp suffix
    assert timestamp[:10] in filepath2.stem


# --- Test Fix Handler (Success Criteria #3) ---

def test_move_file_moves_to_new_destination(temp_vault, temp_state_dir):
    """
    Test that move_file() moves file to new destination folder.

    Success Criteria #3: Backend can process fix: corrections.
    """
    # Create a test file in "ideas" folder
    ideas_folder = temp_vault / "ideas"
    ideas_folder.mkdir(parents=True, exist_ok=True)
    test_file = ideas_folder / "my-idea.md"
    test_file.write_text("---\ntype: idea\n---\n\nOriginal content")

    # Move to "projects"
    new_filepath = move_file(test_file, "projects")

    # Verify file was moved
    assert new_filepath is not None
    assert new_filepath.exists()
    assert new_filepath.parent == temp_vault / "projects"

    # Verify original file no longer exists
    assert not test_file.exists()


def test_move_file_updates_frontmatter(temp_vault, temp_state_dir):
    """
    Test that move_file() updates frontmatter with moved_from and moved_at.

    Success Criteria #3: Frontmatter updated with move metadata.
    """
    # Create a test file with frontmatter
    ideas_folder = temp_vault / "ideas"
    ideas_folder.mkdir(parents=True, exist_ok=True)
    test_file = ideas_folder / "my-idea.md"
    test_file.write_text("---\ntype: idea\ntitle: My Idea\n---\n\nContent here")

    # Move to "admin"
    new_filepath = move_file(test_file, "admin")

    # Read new file and check frontmatter
    content = new_filepath.read_text()
    parts = content.split("---")
    frontmatter = yaml.safe_load(parts[1])

    # Verify frontmatter was updated
    assert frontmatter["type"] == "admin"  # Type changed to match destination
    assert frontmatter["moved_from"] == "ideas"
    assert "moved_at" in frontmatter

    # Verify moved_at is a valid ISO timestamp (convert to string first if needed)
    moved_at = str(frontmatter["moved_at"])
    datetime.fromisoformat(moved_at)  # Should not raise


def test_move_file_preserves_content(temp_vault, temp_state_dir):
    """
    Test that move_file() preserves file content when moving.
    """
    # Create a test file
    ideas_folder = temp_vault / "ideas"
    ideas_folder.mkdir(parents=True, exist_ok=True)
    test_file = ideas_folder / "my-idea.md"
    original_content_section = "\n\nThis is my important content that should not be lost"
    test_file.write_text("---\ntype: idea\n---" + original_content_section)

    # Move to another folder
    new_filepath = move_file(test_file, "projects")

    # Verify content is preserved
    new_content = new_filepath.read_text()
    assert "This is my important content that should not be lost" in new_content


def test_move_file_returns_none_if_file_doesnt_exist(temp_vault):
    """
    Test that move_file() returns None for non-existent files.
    """
    nonexistent_file = temp_vault / "ideas" / "doesnt-exist.md"

    result = move_file(nonexistent_file, "projects")

    assert result is None


def test_move_file_handles_name_conflicts(temp_vault, temp_state_dir):
    """
    Test that move_file() handles conflicts when target file already exists.
    """
    # Create file in ideas
    ideas_folder = temp_vault / "ideas"
    ideas_folder.mkdir(parents=True, exist_ok=True)
    test_file = ideas_folder / "duplicate.md"
    test_file.write_text("---\ntype: idea\n---\n\nOriginal")

    # Create file with same name in projects
    projects_folder = temp_vault / "projects"
    projects_folder.mkdir(parents=True, exist_ok=True)
    existing_file = projects_folder / "duplicate.md"
    existing_file.write_text("---\ntype: project\n---\n\nExisting")

    # Move should rename to avoid conflict
    new_filepath = move_file(test_file, "projects")

    # Verify both files exist
    assert new_filepath.exists()
    assert existing_file.exists()

    # New file should have different name (with timestamp)
    assert new_filepath != existing_file
    assert "moved" in new_filepath.stem


# --- Test State Idempotency (Success Criteria #4) ---

def test_is_message_processed_returns_false_for_new_message(temp_state_dir):
    """
    Test that is_message_processed() returns False for unprocessed messages.

    Success Criteria #4: State tracking prevents duplicate processing.
    """
    message_ts = "1234567890.123456"

    assert is_message_processed(message_ts) is False


def test_mark_message_processed_and_check(temp_state_dir):
    """
    Test that marking a message as processed makes it return True on next check.

    Success Criteria #4: State tracking idempotency.
    """
    message_ts = "1234567890.123456"

    # Initially not processed
    assert is_message_processed(message_ts) is False

    # Mark as processed
    mark_message_processed(message_ts)

    # Now should be processed
    assert is_message_processed(message_ts) is True


def test_message_processed_persists_across_checks(temp_state_dir):
    """
    Test that processed status persists across multiple checks.
    """
    message_ts = "1234567890.123456"

    mark_message_processed(message_ts)

    # Check multiple times
    assert is_message_processed(message_ts) is True
    assert is_message_processed(message_ts) is True
    assert is_message_processed(message_ts) is True


def test_different_messages_tracked_independently(temp_state_dir):
    """
    Test that different messages are tracked independently.
    """
    msg1 = "1111111111.111111"
    msg2 = "2222222222.222222"

    # Mark only msg1
    mark_message_processed(msg1)

    # msg1 should be processed, msg2 should not
    assert is_message_processed(msg1) is True
    assert is_message_processed(msg2) is False


def test_message_to_file_mapping(temp_vault, temp_state_dir):
    """
    Test that message-to-file mapping works for fix: command support.

    Success Criteria #3 dependency: fix: needs to find original file.
    """
    message_ts = "1234567890.123456"
    test_file = temp_vault / "ideas" / "test-idea.md"
    test_file.parent.mkdir(parents=True, exist_ok=True)
    test_file.write_text("---\ntype: idea\n---\n\nContent")

    # Initially no mapping
    assert get_file_for_message(message_ts) is None

    # Set mapping
    set_file_for_message(message_ts, test_file)

    # Should now return the file
    result = get_file_for_message(message_ts)
    assert result == test_file


def test_get_type_for_destination():
    """
    Test helper function that maps destination folder to frontmatter type.
    """
    assert _get_type_for_destination("people") == "person"
    assert _get_type_for_destination("projects") == "project"
    assert _get_type_for_destination("ideas") == "idea"
    assert _get_type_for_destination("admin") == "admin"

    # Unknown destinations return themselves
    assert _get_type_for_destination("unknown") == "unknown"
