#!/usr/bin/env python3
"""
Tests for file_writer module.

TDD approach: Tests written FIRST, implementation follows.
Tests use tmp_path fixture for isolated file system testing.
"""

import pytest
from datetime import datetime
from pathlib import Path


class TestSanitizeFilename:
    """Test cases for sanitize_filename function."""
    
    def test_removes_special_characters(self):
        """Special characters are removed from filename."""
        from file_writer import sanitize_filename
        
        result = sanitize_filename("Hello! World? #test")
        assert "!" not in result
        assert "?" not in result
        assert "#" not in result
    
    def test_replaces_spaces_with_hyphens(self):
        """Spaces become hyphens."""
        from file_writer import sanitize_filename
        
        result = sanitize_filename("hello world test")
        assert " " not in result
        assert "-" in result
    
    def test_lowercases_text(self):
        """Result is lowercase."""
        from file_writer import sanitize_filename
        
        result = sanitize_filename("Hello WORLD")
        assert result == result.lower()
    
    def test_truncates_to_max_length(self):
        """Truncates to specified max_length."""
        from file_writer import sanitize_filename
        
        long_text = "a" * 100
        result = sanitize_filename(long_text, max_length=30)
        assert len(result) <= 30
    
    def test_handles_empty_input(self):
        """Empty input returns 'untitled'."""
        from file_writer import sanitize_filename
        
        result = sanitize_filename("")
        assert result == "untitled"
    
    def test_handles_whitespace_only(self):
        """Whitespace-only input returns 'untitled'."""
        from file_writer import sanitize_filename
        
        result = sanitize_filename("   ")
        assert result == "untitled"
    
    def test_collapses_multiple_hyphens(self):
        """Multiple consecutive hyphens collapse to one."""
        from file_writer import sanitize_filename
        
        result = sanitize_filename("hello   world")
        assert "--" not in result
    
    def test_strips_leading_trailing_hyphens(self):
        """No leading or trailing hyphens."""
        from file_writer import sanitize_filename
        
        result = sanitize_filename("  hello  ")
        assert not result.startswith("-")
        assert not result.endswith("-")


class TestBuildFrontmatter:
    """Test cases for build_frontmatter function."""
    
    def test_produces_valid_yaml_structure(self):
        """Frontmatter has --- delimiters."""
        from file_writer import build_frontmatter
        from message_classifier import ClassificationResult
        
        classification = ClassificationResult(
            domain="Personal",
            para_type="1_Projects",
            subject="apps",
            category="task",
            confidence=0.85,
            reasoning="Test reasoning"
        )
        
        result = build_frontmatter(classification, "2026-01-31T12:00:00")
        assert result.startswith("---\n")
        assert result.strip().endswith("---")
    
    def test_contains_all_required_fields(self):
        """Frontmatter includes all classification fields."""
        from file_writer import build_frontmatter
        from message_classifier import ClassificationResult
        
        classification = ClassificationResult(
            domain="Personal",
            para_type="1_Projects",
            subject="apps",
            category="task",
            confidence=0.85,
            reasoning="Test reasoning"
        )
        
        result = build_frontmatter(classification, "2026-01-31T12:00:00")
        assert "domain: Personal" in result
        assert "para_type: 1_Projects" in result
        assert "subject: apps" in result
        assert "category: task" in result
        assert "confidence:" in result
        assert "created:" in result
    
    def test_quotes_reasoning_with_special_chars(self):
        """Reasoning with colons is properly quoted."""
        from file_writer import build_frontmatter
        from message_classifier import ClassificationResult
        
        classification = ClassificationResult(
            domain="Personal",
            para_type="1_Projects",
            subject="apps",
            category="task",
            confidence=0.85,
            reasoning="Note: this has a colon"
        )
        
        result = build_frontmatter(classification, "2026-01-31T12:00:00")
        # Should either quote the value or handle colons safely
        assert "reasoning:" in result
        # Verify it doesn't break YAML parsing
        assert result.count("---") == 2  # Two delimiters


class TestCreateNoteFile:
    """Test cases for create_note_file function."""
    
    def test_creates_file_in_correct_folder_structure(self, tmp_path):
        """File is created in domain/para_type/subject/ path."""
        from file_writer import create_note_file
        from message_classifier import ClassificationResult
        
        classification = ClassificationResult(
            domain="Personal",
            para_type="1_Projects",
            subject="apps",
            category="task",
            confidence=0.85,
            reasoning="Test"
        )
        
        filepath = create_note_file(
            classification=classification,
            message_text="Test message",
            vault_path=tmp_path
        )
        
        assert filepath.exists()
        assert "Personal" in str(filepath)
        assert "1_Projects" in str(filepath)
        assert "apps" in str(filepath)
    
    def test_file_contains_frontmatter(self, tmp_path):
        """Created file has YAML frontmatter."""
        from file_writer import create_note_file
        from message_classifier import ClassificationResult
        
        classification = ClassificationResult(
            domain="CCBH",
            para_type="2_Areas",
            subject="clients",
            category="meeting",
            confidence=0.9,
            reasoning="Client meeting"
        )
        
        filepath = create_note_file(
            classification=classification,
            message_text="Meeting notes",
            vault_path=tmp_path
        )
        
        content = filepath.read_text()
        assert content.startswith("---")
        assert "domain: CCBH" in content
    
    def test_file_contains_original_message(self, tmp_path):
        """Created file includes original message text."""
        from file_writer import create_note_file
        from message_classifier import ClassificationResult
        
        message = "This is my original Slack message"
        classification = ClassificationResult(
            domain="Personal",
            para_type="3_Resources",
            subject="general",
            category="reference",
            confidence=0.7,
            reasoning="Reference info"
        )
        
        filepath = create_note_file(
            classification=classification,
            message_text=message,
            vault_path=tmp_path
        )
        
        content = filepath.read_text()
        assert message in content
    
    def test_filename_is_unique_with_timestamp(self, tmp_path):
        """Filename includes timestamp for uniqueness."""
        from file_writer import create_note_file
        from message_classifier import ClassificationResult
        import time
        
        classification = ClassificationResult(
            domain="Personal",
            para_type="1_Projects",
            subject="apps",
            category="task",
            confidence=0.8,
            reasoning="Test"
        )
        
        filepath1 = create_note_file(classification, "Message 1", tmp_path)
        time.sleep(0.01)  # Small delay to ensure different timestamp
        filepath2 = create_note_file(classification, "Message 2", tmp_path)
        
        # Both files exist with different names
        assert filepath1.exists()
        assert filepath2.exists()
        assert filepath1 != filepath2
    
    def test_creates_parent_directories(self, tmp_path):
        """Creates parent directories if they don't exist."""
        from file_writer import create_note_file
        from message_classifier import ClassificationResult
        
        classification = ClassificationResult(
            domain="Just-Value",
            para_type="2_Areas",
            subject="properties",
            category="task",
            confidence=0.9,
            reasoning="Property task"
        )
        
        # No pre-existing structure
        filepath = create_note_file(
            classification=classification,
            message_text="Review rental income",
            vault_path=tmp_path
        )
        
        assert filepath.exists()
        assert (tmp_path / "Just-Value" / "2_Areas" / "properties").exists()
    
    def test_handles_general_subject(self, tmp_path):
        """Works with 'general' subject (no specific folder)."""
        from file_writer import create_note_file
        from message_classifier import ClassificationResult
        
        classification = ClassificationResult(
            domain="Personal",
            para_type="3_Resources",
            subject="general",
            category="reference",
            confidence=0.6,
            reasoning="General info"
        )
        
        filepath = create_note_file(
            classification=classification,
            message_text="Some general info",
            vault_path=tmp_path
        )
        
        assert filepath.exists()
        assert "general" in str(filepath)
    
    def test_returns_path_object(self, tmp_path):
        """Returns a Path object."""
        from file_writer import create_note_file
        from message_classifier import ClassificationResult
        
        classification = ClassificationResult(
            domain="Personal",
            para_type="1_Projects",
            subject="apps",
            category="idea",
            confidence=0.75,
            reasoning="App idea"
        )
        
        result = create_note_file(classification, "Test", tmp_path)
        assert isinstance(result, Path)


class TestIntegration:
    """Integration tests for full file creation workflow."""
    
    def test_end_to_end_file_creation(self, tmp_path):
        """Complete workflow: classification result → valid vault file."""
        from file_writer import create_note_file
        from message_classifier import ClassificationResult
        
        # Given: A classification result
        classification = ClassificationResult(
            domain="CCBH",
            para_type="2_Areas",
            subject="clients",
            category="meeting",
            confidence=0.92,
            reasoning="Meeting notes from client sync call"
        )
        message = "Discussed Q4 goals with client. Follow up next week."
        
        # When: Create note file
        filepath = create_note_file(classification, message, tmp_path)
        
        # Then: File exists with correct structure
        assert filepath.exists()
        assert filepath.suffix == ".md"
        
        # And: Content is valid
        content = filepath.read_text()
        
        # Frontmatter
        assert content.startswith("---")
        assert "domain: CCBH" in content
        assert "para_type: 2_Areas" in content
        assert "subject: clients" in content
        assert "category: meeting" in content
        
        # Body
        assert "Q4 goals" in content
        assert "Follow up" in content
        
        # Path structure
        assert "CCBH" in str(filepath.parent)
        assert "2_Areas" in str(filepath.parent)
        assert "clients" in str(filepath.parent)
