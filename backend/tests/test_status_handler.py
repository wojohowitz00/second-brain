#!/usr/bin/env python3
"""
Tests for status_handler module.

TDD approach: Tests written FIRST, implementation follows.
"""

import pytest
from pathlib import Path


class TestUpdateStatusInFile:
    """Test update_status_in_file() function."""

    def test_updates_status_in_frontmatter(self, tmp_path):
        """Updates status field in YAML frontmatter."""
        from status_handler import update_status_in_file
        
        task_file = tmp_path / "task.md"
        task_file.write_text("""---
type: task
status: backlog
priority: high
---

# Task content
""")
        
        update_status_in_file(task_file, "done")
        
        content = task_file.read_text()
        assert "status: done" in content

    def test_preserves_other_frontmatter_fields(self, tmp_path):
        """Preserves all other frontmatter fields."""
        from status_handler import update_status_in_file
        
        task_file = tmp_path / "task.md"
        task_file.write_text("""---
type: task
status: backlog
priority: high
project: rvm
domain: Just-Value
---

# Task content
""")
        
        update_status_in_file(task_file, "in_progress")
        
        content = task_file.read_text()
        assert "type: task" in content
        assert "priority: high" in content
        assert "project: rvm" in content
        assert "domain: Just-Value" in content
        assert "status: in_progress" in content

    def test_preserves_content_after_frontmatter(self, tmp_path):
        """Preserves content after frontmatter."""
        from status_handler import update_status_in_file
        
        original_content = """---
type: task
status: backlog
---

# Important Task

This is the task description with details.
- Item 1
- Item 2
"""
        task_file = tmp_path / "task.md"
        task_file.write_text(original_content)
        
        update_status_in_file(task_file, "done")
        
        content = task_file.read_text()
        assert "# Important Task" in content
        assert "This is the task description" in content
        assert "- Item 1" in content

    def test_returns_true_on_success(self, tmp_path):
        """Returns True when update succeeds."""
        from status_handler import update_status_in_file
        
        task_file = tmp_path / "task.md"
        task_file.write_text("""---
status: backlog
---
""")
        
        result = update_status_in_file(task_file, "done")
        
        assert result is True

    def test_returns_false_for_missing_file(self, tmp_path):
        """Returns False for missing file."""
        from status_handler import update_status_in_file
        
        missing_file = tmp_path / "missing.md"
        
        result = update_status_in_file(missing_file, "done")
        
        assert result is False

    def test_returns_false_for_no_frontmatter(self, tmp_path):
        """Returns False for file without frontmatter."""
        from status_handler import update_status_in_file
        
        task_file = tmp_path / "no_fm.md"
        task_file.write_text("# Just content, no frontmatter")
        
        result = update_status_in_file(task_file, "done")
        
        assert result is False


class TestProcessStatusCommand:
    """Test process_status_command() function."""

    def test_updates_file_on_valid_command(self, tmp_path, monkeypatch):
        """Updates file when command is valid."""
        from status_handler import process_status_command
        import status_handler
        
        task_file = tmp_path / "task.md"
        task_file.write_text("""---
status: backlog
---
""")
        
        # Mock get_file_for_message to return our test file
        monkeypatch.setattr(status_handler, "get_file_for_message", 
                           lambda msg_id: task_file)
        
        result = process_status_command("msg123", "!done")
        
        assert result["success"] is True
        assert result["new_status"] == "done"

    def test_returns_error_for_unknown_message(self, monkeypatch):
        """Returns error when message not found."""
        from status_handler import process_status_command
        import status_handler
        
        monkeypatch.setattr(status_handler, "get_file_for_message", 
                           lambda msg_id: None)
        
        result = process_status_command("unknown_msg", "!done")
        
        assert result["success"] is False
        assert "not found" in result["error"].lower()

    def test_returns_error_for_invalid_command(self, tmp_path, monkeypatch):
        """Returns error for invalid status command."""
        from status_handler import process_status_command
        import status_handler
        
        task_file = tmp_path / "task.md"
        task_file.write_text("""---
status: backlog
---
""")
        
        monkeypatch.setattr(status_handler, "get_file_for_message", 
                           lambda msg_id: task_file)
        
        result = process_status_command("msg123", "not a command")
        
        assert result["success"] is False


class TestGetFileForMessage:
    """Test get_file_for_message() function."""

    def test_returns_path_for_known_message(self, tmp_path, monkeypatch):
        """Returns file path for known message ID."""
        from status_handler import get_file_for_message
        import status_handler
        import json
        
        # Create mock mapping file
        mapping_file = tmp_path / "message_mapping.json"
        mapping_file.write_text(json.dumps({
            "msg123": str(tmp_path / "task.md")
        }))
        
        monkeypatch.setattr(status_handler, "MESSAGE_MAPPING_FILE", mapping_file)
        
        result = get_file_for_message("msg123")
        
        assert result == tmp_path / "task.md"

    def test_returns_none_for_unknown_message(self, tmp_path, monkeypatch):
        """Returns None for unknown message ID."""
        from status_handler import get_file_for_message
        import status_handler
        import json
        
        mapping_file = tmp_path / "message_mapping.json"
        mapping_file.write_text(json.dumps({}))
        
        monkeypatch.setattr(status_handler, "MESSAGE_MAPPING_FILE", mapping_file)
        
        result = get_file_for_message("unknown")
        
        assert result is None
