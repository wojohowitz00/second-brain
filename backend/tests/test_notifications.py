#!/usr/bin/env python3
"""
Tests for notifications module.

Tests notification functionality using mocks to avoid
actual macOS notification popups during testing.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path


class TestNotifyNoteFiled:
    """Tests for notify_note_filed function."""
    
    @patch("notifications.subprocess.run")
    def test_sends_notification(self, mock_run):
        """notify_note_filed sends a macOS notification."""
        from notifications import notify_note_filed
        
        notify_note_filed(
            title="Test Note",
            domain="Personal",
            para_type="1_Projects",
            path="/path/to/note.md"
        )
        
        mock_run.assert_called_once()
    
    @patch("notifications.subprocess.run")
    def test_notification_includes_title(self, mock_run):
        """Notification includes note title."""
        from notifications import notify_note_filed
        
        notify_note_filed(
            title="My Important Note",
            domain="Personal",
            para_type="1_Projects",
            path="/path/to/note.md"
        )
        
        call_args = mock_run.call_args[0][0]
        script = call_args[-1]  # osascript script is last arg
        
        assert "My Important Note" in script
    
    @patch("notifications.subprocess.run")
    def test_notification_includes_domain(self, mock_run):
        """Notification includes domain."""
        from notifications import notify_note_filed
        
        notify_note_filed(
            title="Test Note",
            domain="CCBH",
            para_type="2_Areas",
            path="/path/to/note.md"
        )
        
        call_args = mock_run.call_args[0][0]
        script = call_args[-1]
        
        assert "CCBH" in script
    
    @patch("notifications.subprocess.run")
    def test_truncates_long_title(self, mock_run):
        """Long titles are truncated to 50 chars."""
        from notifications import notify_note_filed
        
        long_title = "A" * 100
        notify_note_filed(
            title=long_title,
            domain="Personal",
            para_type="1_Projects",
            path="/path/to/note.md"
        )
        
        call_args = mock_run.call_args[0][0]
        script = call_args[-1]
        
        # Should be truncated
        assert long_title not in script
        assert "A" * 47 + "..." in script or len(script) < len(long_title) + 100


class TestNotificationSettings:
    """Tests for notification settings."""
    
    @patch("notifications.subprocess.run")
    def test_notifications_enabled_by_default(self, mock_run):
        """Notifications are enabled by default."""
        from notifications import notify_note_filed, notifications_enabled
        
        assert notifications_enabled() is True
    
    @patch("notifications.subprocess.run")
    def test_can_disable_notifications(self, mock_run, tmp_path):
        """Notifications can be disabled."""
        from notifications import (
            notify_note_filed, 
            set_notifications_enabled,
            notifications_enabled
        )
        
        # Disable
        set_notifications_enabled(False, config_dir=tmp_path)
        
        # Verify disabled
        assert notifications_enabled(config_dir=tmp_path) is False
    
    @patch("notifications.subprocess.run")
    def test_disabled_notifications_dont_send(self, mock_run, tmp_path):
        """When disabled, no notification is sent."""
        from notifications import (
            notify_note_filed,
            set_notifications_enabled
        )
        
        set_notifications_enabled(False, config_dir=tmp_path)
        
        notify_note_filed(
            title="Test",
            domain="Personal",
            para_type="1_Projects",
            path="/path/test.md",
            config_dir=tmp_path
        )
        
        mock_run.assert_not_called()


class TestBuildNotificationScript:
    """Tests for osascript generation."""
    
    def test_builds_valid_applescript(self):
        """Builds valid AppleScript for notification."""
        from notifications import _build_notification_script
        
        script = _build_notification_script(
            title="Test Note",
            subtitle="Filed to Personal/1_Projects"
        )
        
        assert "display notification" in script
        assert "Test Note" in script
        assert "Second Brain" in script
