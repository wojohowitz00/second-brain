"""
Unit tests for schema validation module.

Tests validate_classification(), sanitize_filename(), validate_linked_entity(),
and create_fallback_classification() functions.
"""

import pytest
from schema import (
    validate_classification,
    sanitize_filename,
    validate_linked_entity,
    create_fallback_classification,
    ValidationError,
    VALID_DESTINATIONS,
)


class TestValidateClassification:
    """Test cases for validate_classification()."""

    def test_valid_classification_with_all_fields(self, sample_classification):
        """Valid classification with all fields returns cleaned data."""
        result = validate_classification(sample_classification)

        assert result["destination"] == "ideas"
        assert result["confidence"] == 0.85
        assert result["filename"] == "my-awesome-idea"
        assert result["extracted"]["title"] == "My Awesome Idea"
        assert len(result["linked_entities"]) == 2

    def test_missing_confidence_defaults_to_half(self):
        """Missing confidence defaults to 0.5."""
        data = {
            "destination": "projects",
            "filename": "test"
        }
        result = validate_classification(data)

        assert result["confidence"] == 0.5

    def test_invalid_destination_raises_validation_error(self):
        """Invalid destination raises ValidationError."""
        data = {
            "destination": "invalid-category",
            "confidence": 0.8,
            "filename": "test"
        }

        with pytest.raises(ValidationError) as exc_info:
            validate_classification(data)

        assert "Invalid destination" in str(exc_info.value)
        assert "invalid-category" in str(exc_info.value)

    @pytest.mark.parametrize("confidence,expected", [
        (-0.5, 0.0),      # Below range gets clamped to 0
        (1.5, 1.0),       # Above range gets clamped to 1
        (2.0, 1.0),       # Well above range gets clamped to 1
        (-1.0, 0.0),      # Well below range gets clamped to 0
        (0.0, 0.0),       # Edge: exactly 0
        (1.0, 1.0),       # Edge: exactly 1
        (0.5, 0.5),       # Middle of range is unchanged
    ])
    def test_confidence_outside_range_gets_clamped(self, confidence, expected):
        """Confidence outside 0-1 gets clamped to valid range."""
        data = {
            "destination": "ideas",
            "confidence": confidence,
            "filename": "test"
        }
        result = validate_classification(data)

        assert result["confidence"] == expected

    def test_missing_filename_generates_fallback(self):
        """Missing filename generates fallback based on destination."""
        data = {
            "destination": "people",
            "confidence": 0.7
        }
        result = validate_classification(data)

        assert result["filename"] == "untitled-people"

    def test_empty_filename_generates_fallback(self):
        """Empty filename generates fallback based on destination."""
        data = {
            "destination": "admin",
            "confidence": 0.6,
            "filename": ""
        }
        result = validate_classification(data)

        assert result["filename"] == "untitled-admin"

    def test_empty_extracted_becomes_empty_dict(self):
        """Missing or non-dict extracted becomes empty dict."""
        # Missing extracted
        data1 = {"destination": "ideas", "filename": "test"}
        result1 = validate_classification(data1)
        assert result1["extracted"] == {}

        # Non-dict extracted
        data2 = {"destination": "ideas", "filename": "test", "extracted": "not a dict"}
        result2 = validate_classification(data2)
        assert result2["extracted"] == {}

    def test_invalid_linked_entities_filtered_out(self):
        """Invalid linked entities are filtered out during validation."""
        data = {
            "destination": "projects",
            "filename": "test",
            "linked_entities": [
                {"name": "Valid Person", "type": "person"},
                {"name": "", "type": "person"},          # Invalid: empty name
                {"name": "Valid Project", "type": "project"},
                {"type": "person"},                       # Invalid: missing name
                {"name": "Unknown Type", "type": "unknown"},  # Invalid: unknown type
            ]
        }
        result = validate_classification(data)

        assert len(result["linked_entities"]) == 2
        assert result["linked_entities"][0]["name"] == "Valid Person"
        assert result["linked_entities"][1]["name"] == "Valid Project"

    def test_non_dict_input_raises_validation_error(self):
        """Non-dict input raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            validate_classification("not a dict")

        assert "must be a dict" in str(exc_info.value)

    def test_non_number_confidence_raises_validation_error(self):
        """Non-number confidence raises ValidationError."""
        data = {
            "destination": "ideas",
            "confidence": "high",
            "filename": "test"
        }

        with pytest.raises(ValidationError) as exc_info:
            validate_classification(data)

        assert "Confidence must be a number" in str(exc_info.value)


class TestSanitizeFilename:
    """Test cases for sanitize_filename()."""

    def test_converts_spaces_and_underscores_to_hyphens(self):
        """Converts spaces and underscores to hyphens."""
        assert sanitize_filename("My Great Idea") == "my-great-idea"
        assert sanitize_filename("my_great_idea") == "my-great-idea"
        assert sanitize_filename("My Great_Idea") == "my-great-idea"

    def test_removes_path_traversal_attempts(self):
        """Removes path traversal attempts (../, /, backslash)."""
        assert sanitize_filename("../etc/passwd") == "etc-passwd"
        assert sanitize_filename("../../dangerous") == "dangerous"
        assert sanitize_filename("folder/file") == "folder-file"
        assert sanitize_filename("folder\\file") == "folder-file"

    def test_handles_unicode_and_special_characters(self):
        """Removes unicode and special characters."""
        # Unicode removed
        assert sanitize_filename("café") == "caf"
        assert sanitize_filename("naïve") == "nave"

        # Special characters removed
        assert sanitize_filename("hello@world!") == "helloworld"
        assert sanitize_filename("test#123$") == "test123"
        assert sanitize_filename("a&b*c") == "abc"

    def test_collapses_multiple_hyphens(self):
        """Collapses multiple consecutive hyphens into one."""
        assert sanitize_filename("hello---world") == "hello-world"
        assert sanitize_filename("a--b--c") == "a-b-c"

    def test_removes_leading_trailing_hyphens(self):
        """Removes leading and trailing hyphens."""
        assert sanitize_filename("-leading") == "leading"
        assert sanitize_filename("trailing-") == "trailing"
        assert sanitize_filename("-both-") == "both"

    def test_truncates_at_100_characters(self):
        """Truncates filename at 100 characters."""
        long_name = "a" * 150
        result = sanitize_filename(long_name)

        assert len(result) == 100
        assert result == "a" * 100

    def test_truncates_and_removes_trailing_hyphen(self):
        """Truncates and removes trailing hyphen if truncation creates one."""
        # Create a string where truncation at 100 would end with hyphen
        long_name = "a" * 99 + "-" + "b" * 50
        result = sanitize_filename(long_name)

        assert len(result) <= 100
        assert not result.endswith("-")

    def test_empty_input_returns_untitled(self):
        """Empty input returns 'untitled'."""
        assert sanitize_filename("") == "untitled"
        assert sanitize_filename("   ") == "untitled"
        assert sanitize_filename("!!!") == "untitled"  # All special chars removed

    def test_converts_to_lowercase(self):
        """Converts all text to lowercase."""
        assert sanitize_filename("UPPERCASE") == "uppercase"
        assert sanitize_filename("MixedCase") == "mixedcase"


class TestValidateLinkedEntity:
    """Test cases for validate_linked_entity()."""

    def test_valid_person_entity_returns_normalized(self):
        """Valid person entity returns normalized dict."""
        entity = {"name": "Alice Smith", "type": "person"}
        result = validate_linked_entity(entity)

        assert result == {"name": "Alice Smith", "type": "people"}

    def test_valid_project_entity_returns_normalized(self):
        """Valid project entity returns normalized dict."""
        entity = {"name": "Project X", "type": "project"}
        result = validate_linked_entity(entity)

        assert result == {"name": "Project X", "type": "projects"}

    def test_plural_types_normalized_correctly(self):
        """Plural types (people, projects) are normalized correctly."""
        entity1 = {"name": "Bob", "type": "people"}
        result1 = validate_linked_entity(entity1)
        assert result1["type"] == "people"

        entity2 = {"name": "Project Y", "type": "projects"}
        result2 = validate_linked_entity(entity2)
        assert result2["type"] == "projects"

    def test_missing_name_returns_none(self):
        """Missing or empty name returns None."""
        assert validate_linked_entity({"type": "person"}) is None
        assert validate_linked_entity({"name": "", "type": "person"}) is None
        assert validate_linked_entity({"name": "   ", "type": "person"}) is None

    def test_unknown_type_returns_none(self):
        """Unknown entity type returns None."""
        assert validate_linked_entity({"name": "Something", "type": "unknown"}) is None
        assert validate_linked_entity({"name": "Something", "type": "idea"}) is None

    def test_non_dict_input_returns_none(self):
        """Non-dict input returns None."""
        assert validate_linked_entity("not a dict") is None
        assert validate_linked_entity(None) is None
        assert validate_linked_entity([]) is None

    def test_case_insensitive_type_matching(self):
        """Entity type matching is case-insensitive."""
        entity1 = {"name": "Alice", "type": "PERSON"}
        result1 = validate_linked_entity(entity1)
        assert result1["type"] == "people"

        entity2 = {"name": "Project", "type": "PROJECT"}
        result2 = validate_linked_entity(entity2)
        assert result2["type"] == "projects"


class TestCreateFallbackClassification:
    """Test cases for create_fallback_classification()."""

    def test_returns_ideas_with_low_confidence(self):
        """Returns 'ideas' destination with low confidence (0.3)."""
        thought = "This is a test thought"
        result = create_fallback_classification(thought)

        assert result["destination"] == "ideas"
        assert result["confidence"] == 0.3

    def test_includes_error_in_extracted_metadata(self):
        """Includes error message in extracted metadata."""
        thought = "Test thought"
        error = "JSON parse error: unexpected token"
        result = create_fallback_classification(thought, error)

        assert "_validation_error" in result["extracted"]
        assert result["extracted"]["_validation_error"] == error

    def test_generates_filename_from_thought(self):
        """Generates filename from first few words of thought."""
        thought = "This is a really long thought about many things"
        result = create_fallback_classification(thought)

        # Should use first 5 words, sanitized
        assert result["filename"] == "this-is-a-really-long"

    def test_empty_linked_entities(self):
        """Fallback has empty linked_entities list."""
        thought = "Test"
        result = create_fallback_classification(thought)

        assert result["linked_entities"] == []

    def test_truncates_title_at_50_chars(self):
        """Truncates title in extracted metadata at 50 characters."""
        long_thought = "a" * 100
        result = create_fallback_classification(long_thought)

        assert len(result["extracted"]["title"]) == 53  # 50 + "..."
        assert result["extracted"]["title"].endswith("...")

    def test_includes_oneliner_about_validation_error(self):
        """Includes oneliner explaining auto-classification."""
        thought = "Test"
        result = create_fallback_classification(thought)

        assert "oneliner" in result["extracted"]
        assert "validation error" in result["extracted"]["oneliner"].lower()
