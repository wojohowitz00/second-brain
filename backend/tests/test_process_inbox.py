#!/usr/bin/env python3
"""
Integration tests for process_inbox module.

Tests the end-to-end flow from Slack message to vault file.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch
from datetime import datetime


class TestProcessMessage:
    """Tests for process_message function."""
    
    def test_skips_fix_commands(self):
        """fix: commands should be skipped (handled by fix_handler)."""
        from process_inbox import process_message
        
        msg = {"text": "fix: Personal", "ts": "1234567890.123456"}
        result = process_message(msg)
        assert result is True  # Skipped, not failed
    
    def test_skips_status_commands(self):
        """Status commands (done:, progress:) should be skipped."""
        from process_inbox import process_message
        
        for cmd in ["done:", "progress:", "blocked:", "backlog:"]:
            msg = {"text": f"{cmd} task completed", "ts": "1234567890.123456"}
            result = process_message(msg)
            assert result is True  # Skipped, not failed
    
    def test_skips_already_processed(self, temp_state_dir):
        """Already processed messages should be skipped."""
        from process_inbox import process_message
        from state import mark_message_processed
        
        ts = "1234567890.123456"
        mark_message_processed(ts)
        
        msg = {"text": "Test message", "ts": ts}
        result = process_message(msg)
        assert result is True  # Skipped, not failed
    
    @patch("process_inbox.get_classifier")
    @patch("process_inbox.create_note_file")
    @patch("process_inbox.reply_to_message")
    @patch("process_inbox.set_file_for_message")
    @patch("process_inbox.mark_message_processed")
    def test_processes_new_message_high_confidence(
        self, mock_mark, mock_set_file, mock_reply, mock_create, mock_get_classifier, 
        temp_state_dir, tmp_path
    ):
        """New messages with high confidence should be classified and filed."""
        from process_inbox import process_message
        from message_classifier import ClassificationResult
        
        # Setup mock classifier
        mock_classifier = Mock()
        mock_classifier.classify.return_value = ClassificationResult(
            domain="Personal",
            para_type="1_Projects",
            subject="apps",
            category="task",
            confidence=0.85,
            reasoning="Test"
        )
        mock_get_classifier.return_value = mock_classifier
        
        # Setup mock file creation
        mock_file = tmp_path / "test.md"
        mock_file.write_text("test")
        mock_create.return_value = mock_file
        
        msg = {"text": "Work on the app", "ts": "9999999999.999999"}  # Unique ts
        result = process_message(msg)
        
        assert result is True
        mock_classifier.classify.assert_called_once_with("Work on the app")
        mock_create.assert_called_once()
        mock_reply.assert_called_once()
        # Reply should mention the path
        reply_text = mock_reply.call_args[0][1]
        assert "Personal" in reply_text
    
    @patch("process_inbox.get_classifier")
    @patch("process_inbox.reply_to_message")
    @patch("process_inbox.mark_message_processed")
    def test_low_confidence_not_filed(
        self, mock_mark, mock_reply, mock_get_classifier, temp_state_dir
    ):
        """Low confidence messages should not be filed but should be acknowledged."""
        from process_inbox import process_message
        from message_classifier import ClassificationResult
        
        mock_classifier = Mock()
        mock_classifier.classify.return_value = ClassificationResult(
            domain="Personal",
            para_type="3_Resources",
            subject="general",
            category="reference",
            confidence=0.4,  # Below 0.6 threshold
            reasoning="Uncertain"
        )
        mock_get_classifier.return_value = mock_classifier
        
        msg = {"text": "Ambiguous message", "ts": "8888888888.888888"}
        result = process_message(msg)
        
        assert result is True
        # Should reply with low confidence warning
        mock_reply.assert_called_once()
        call_text = mock_reply.call_args[0][1]
        assert "confidence" in call_text.lower()


class TestProcessAll:
    """Tests for process_all function."""
    
    @patch("process_inbox.fetch_new_messages")
    @patch("process_inbox.process_message")
    @patch("process_inbox.record_successful_run")
    @patch("process_inbox.cleanup_old_processed_messages")
    def test_processes_messages_oldest_first(
        self, mock_cleanup, mock_record, mock_process, mock_fetch, temp_state_dir
    ):
        """Messages should be processed oldest first (reversed order)."""
        from process_inbox import process_all
        
        mock_fetch.return_value = [
            {"text": "newer", "ts": "1234567892.0"},
            {"text": "older", "ts": "1234567890.0"},
        ]
        mock_process.return_value = True
        
        process_all()
        
        # Verify oldest processed first (reversed)
        calls = mock_process.call_args_list
        assert len(calls) == 2
        assert calls[0][0][0]["text"] == "older"
        assert calls[1][0][0]["text"] == "newer"
    
    @patch("process_inbox.fetch_new_messages")
    @patch("process_inbox.record_successful_run")
    def test_handles_empty_inbox(self, mock_record, mock_fetch, temp_state_dir):
        """Empty inbox should record successful run."""
        from process_inbox import process_all
        
        mock_fetch.return_value = []
        
        process_all()
        
        mock_record.assert_called_once()


class TestPollingConfig:
    """Tests for polling configuration."""
    
    def test_poll_interval_is_two_minutes(self):
        """Poll interval should be 120 seconds (2 minutes)."""
        from process_inbox import POLL_INTERVAL_SECONDS
        assert POLL_INTERVAL_SECONDS == 120


class TestGetClassifier:
    """Tests for lazy classifier initialization."""
    
    @patch("process_inbox.MessageClassifier")
    def test_creates_classifier_once(self, mock_class):
        """Classifier should be created once and reused."""
        import process_inbox
        from process_inbox import get_classifier
        
        process_inbox._classifier = None  # Reset singleton
        
        mock_instance = Mock()
        mock_class.return_value = mock_instance
        
        c1 = get_classifier()
        c2 = get_classifier()
        
        assert c1 is c2
        mock_class.assert_called_once()
        
        # Cleanup
        process_inbox._classifier = None


class TestMainLoop:
    """Tests for main_loop daemon mode."""
    
    def test_main_loop_exists(self):
        """main_loop function should exist."""
        from process_inbox import main_loop
        assert callable(main_loop)
    
    def test_shutdown_flag_exists(self):
        """Shutdown flag should exist for graceful termination."""
        import process_inbox
        assert hasattr(process_inbox, '_shutdown_requested')


class TestSignalHandling:
    """Tests for signal handling."""
    
    def test_signal_handler_sets_shutdown_flag(self):
        """Signal handler should set shutdown flag."""
        import process_inbox
        from process_inbox import _signal_handler
        
        # Reset flag
        process_inbox._shutdown_requested = False
        
        # Simulate signal
        _signal_handler(2, None)  # 2 = SIGINT
        
        assert process_inbox._shutdown_requested is True
        
        # Cleanup
        process_inbox._shutdown_requested = False
