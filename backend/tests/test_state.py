"""
Unit tests for state management module.

Tests message processing idempotency, message-to-file mapping,
and cleanup operations.

All tests use temp_state_dir fixture to isolate from real state files.
"""

import pytest
from pathlib import Path
from datetime import datetime, timedelta
import state


class TestMessageProcessingIdempotency:
    """Test cases for message processing idempotency tracking."""

    def test_mark_then_check_returns_true(self, temp_state_dir):
        """mark_message_processed() then is_message_processed() returns True."""
        message_ts = "1234567890.123456"

        # Initially should not be processed
        assert state.is_message_processed(message_ts) is False

        # Mark as processed
        state.mark_message_processed(message_ts)

        # Now should be processed
        assert state.is_message_processed(message_ts) is True

    def test_unknown_message_returns_false(self, temp_state_dir):
        """is_message_processed() for unknown message returns False."""
        message_ts = "9999999999.999999"

        assert state.is_message_processed(message_ts) is False

    def test_duplicate_mark_is_idempotent(self, temp_state_dir):
        """Duplicate mark_message_processed() is idempotent (no error)."""
        message_ts = "1234567890.123456"

        # Mark twice
        state.mark_message_processed(message_ts)
        state.mark_message_processed(message_ts)

        # Should still be processed
        assert state.is_message_processed(message_ts) is True

    def test_multiple_messages_tracked_independently(self, temp_state_dir):
        """Multiple messages are tracked independently."""
        msg1 = "1111111111.111111"
        msg2 = "2222222222.222222"
        msg3 = "3333333333.333333"

        state.mark_message_processed(msg1)
        state.mark_message_processed(msg3)

        assert state.is_message_processed(msg1) is True
        assert state.is_message_processed(msg2) is False
        assert state.is_message_processed(msg3) is True


class TestMessageToFileMapping:
    """Test cases for message-to-file mapping."""

    def test_set_then_get_returns_path(self, temp_state_dir):
        """set_file_for_message() then get_file_for_message() returns path."""
        message_ts = "1234567890.123456"
        filepath = temp_state_dir / "test-file.md"

        # Create the file so it exists
        filepath.write_text("test content")

        # Set mapping
        state.set_file_for_message(message_ts, filepath)

        # Get mapping
        result = state.get_file_for_message(message_ts)

        assert result == filepath

    def test_get_for_unknown_message_returns_none(self, temp_state_dir):
        """get_file_for_message() for unknown message returns None."""
        message_ts = "9999999999.999999"

        result = state.get_file_for_message(message_ts)

        assert result is None

    def test_get_for_nonexistent_file_returns_none(self, temp_state_dir):
        """get_file_for_message() returns None if mapped file doesn't exist."""
        message_ts = "1234567890.123456"
        filepath = temp_state_dir / "nonexistent.md"

        # Set mapping for file that doesn't exist
        state.set_file_for_message(message_ts, filepath)

        # Get should return None because file doesn't exist
        result = state.get_file_for_message(message_ts)

        assert result is None

    def test_update_file_location_changes_path(self, temp_state_dir):
        """update_file_location() changes the stored path."""
        message_ts = "1234567890.123456"
        old_path = temp_state_dir / "old-file.md"
        new_path = temp_state_dir / "new-file.md"

        # Create both files
        old_path.write_text("old content")
        new_path.write_text("new content")

        # Set initial mapping
        state.set_file_for_message(message_ts, old_path)
        assert state.get_file_for_message(message_ts) == old_path

        # Update location
        state.update_file_location(message_ts, new_path)

        # Should now return new path
        assert state.get_file_for_message(message_ts) == new_path

    def test_remove_message_mapping_clears_mapping(self, temp_state_dir):
        """remove_message_mapping() clears the mapping."""
        message_ts = "1234567890.123456"
        filepath = temp_state_dir / "test-file.md"

        # Create file and set mapping
        filepath.write_text("test content")
        state.set_file_for_message(message_ts, filepath)
        assert state.get_file_for_message(message_ts) == filepath

        # Remove mapping
        state.remove_message_mapping(message_ts)

        # Should now return None
        assert state.get_file_for_message(message_ts) is None

    def test_remove_nonexistent_mapping_no_error(self, temp_state_dir):
        """remove_message_mapping() on nonexistent mapping doesn't error."""
        message_ts = "9999999999.999999"

        # Should not raise error
        state.remove_message_mapping(message_ts)


class TestCleanupOldProcessedMessages:
    """Test cases for cleanup_old_processed_messages()."""

    def test_old_entries_removed(self, temp_state_dir, monkeypatch):
        """Old entries (>30 days) are removed."""
        # Create entries with different ages
        old_date = (datetime.now() - timedelta(days=35)).isoformat()
        recent_date = (datetime.now() - timedelta(days=5)).isoformat()

        # Manually write to processed messages file
        processed_file = temp_state_dir / "processed_messages.json"
        import json
        data = {
            "old_msg_1": old_date,
            "old_msg_2": old_date,
            "recent_msg": recent_date,
        }
        processed_file.write_text(json.dumps(data, indent=2))

        # Run cleanup
        state.cleanup_old_processed_messages()

        # Check what remains
        assert state.is_message_processed("old_msg_1") is False
        assert state.is_message_processed("old_msg_2") is False
        assert state.is_message_processed("recent_msg") is True

    def test_recent_entries_preserved(self, temp_state_dir):
        """Recent entries are preserved."""
        msg1 = "1111111111.111111"
        msg2 = "2222222222.222222"

        # Mark messages as processed
        state.mark_message_processed(msg1)
        state.mark_message_processed(msg2)

        # Run cleanup
        state.cleanup_old_processed_messages()

        # Both should still be processed
        assert state.is_message_processed(msg1) is True
        assert state.is_message_processed(msg2) is True

    def test_cleanup_on_empty_file_no_error(self, temp_state_dir):
        """cleanup_old_processed_messages() on empty file doesn't error."""
        # Should not raise error even if file doesn't exist
        state.cleanup_old_processed_messages()

    def test_entries_exactly_at_ttl_boundary(self, temp_state_dir):
        """Entries exactly at TTL boundary (30 days) are removed."""
        # Entry exactly 30 days old
        boundary_date = (datetime.now() - timedelta(days=30)).isoformat()

        processed_file = temp_state_dir / "processed_messages.json"
        import json
        data = {"boundary_msg": boundary_date}
        processed_file.write_text(json.dumps(data, indent=2))

        # Run cleanup
        state.cleanup_old_processed_messages()

        # Should be removed (implementation uses >, not >=)
        assert state.is_message_processed("boundary_msg") is False


class TestAtomicJSONOperations:
    """Test cases for atomic JSON read/write operations."""

    def test_concurrent_reads_dont_corrupt_data(self, temp_state_dir):
        """Basic smoke test: multiple reads work correctly."""
        message_ts = "1234567890.123456"
        state.mark_message_processed(message_ts)

        # Multiple reads should all return True
        results = [state.is_message_processed(message_ts) for _ in range(10)]

        assert all(results)

    def test_nonexistent_file_returns_empty_dict(self, temp_state_dir):
        """_atomic_json_read on nonexistent file returns empty dict."""
        nonexistent = temp_state_dir / "nonexistent.json"

        result = state._atomic_json_read(nonexistent)

        assert result == {}

    def test_corrupted_json_returns_empty_dict(self, temp_state_dir):
        """_atomic_json_read on corrupted JSON returns empty dict."""
        corrupted_file = temp_state_dir / "corrupted.json"
        corrupted_file.write_text("{ invalid json }")

        result = state._atomic_json_read(corrupted_file)

        assert result == {}


class TestYouTubeRegistry:
    """Test cases for YouTube URL registry."""

    def test_normalize_youtube_url_variants(self):
        assert (
            state.normalize_youtube_url("https://youtu.be/abc123")
            == "https://www.youtube.com/watch?v=abc123"
        )
        assert (
            state.normalize_youtube_url("https://www.youtube.com/watch?v=abc123&feature=youtu.be")
            == "https://www.youtube.com/watch?v=abc123"
        )
        assert (
            state.normalize_youtube_url("https://www.youtube.com/shorts/abc123?feature=share")
            == "https://www.youtube.com/watch?v=abc123"
        )

    def test_record_success_and_lookup(self, temp_state_dir, monkeypatch):
        monkeypatch.setattr(state, "YOUTUBE_URLS_FILE", temp_state_dir / "youtube_urls.json")

        url = "https://youtu.be/abc123"
        note_path = temp_state_dir / "note.md"
        note_path.write_text("content")

        state.record_youtube_url_success(url, note_path)

        assert state.is_youtube_url_processed(url) is True
        entry = state.get_youtube_url_entry(url)
        assert entry["status"] == "success"
        assert entry["note_path"] == str(note_path)

    def test_record_failed_increments_attempts(self, temp_state_dir, monkeypatch):
        monkeypatch.setattr(state, "YOUTUBE_URLS_FILE", temp_state_dir / "youtube_urls.json")

        url = "https://www.youtube.com/watch?v=abc123"
        state.record_youtube_url_failed(url, error="first")
        entry = state.get_youtube_url_entry(url)
        assert entry["status"] == "failed"
        assert entry["attempts"] == 1

        state.record_youtube_url_failed(url, error="second")
        entry = state.get_youtube_url_entry(url)
        assert entry["attempts"] == 2
        assert entry["last_error"] == "second"

    def test_file_locking_basic_smoke_test(self, temp_state_dir):
        """Basic smoke test that file locking doesn't break operations."""
        # This is a basic test - full concurrency testing would need threading
        msg1 = "1111111111.111111"
        msg2 = "2222222222.222222"

        # Interleaved operations
        state.mark_message_processed(msg1)
        filepath1 = temp_state_dir / "file1.md"
        filepath1.write_text("test")
        state.set_file_for_message(msg1, filepath1)

        state.mark_message_processed(msg2)
        filepath2 = temp_state_dir / "file2.md"
        filepath2.write_text("test")
        state.set_file_for_message(msg2, filepath2)

        # Verify both operations succeeded
        assert state.is_message_processed(msg1) is True
        assert state.is_message_processed(msg2) is True
        assert state.get_file_for_message(msg1) == filepath1
        assert state.get_file_for_message(msg2) == filepath2
