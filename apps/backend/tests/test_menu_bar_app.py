#!/usr/bin/env python3
"""
Tests for menu_bar_app module.

Tests MenuBarCore (business logic) and MenuBarApp (wrapper).
Core tests don't require rumps, making them runnable in any environment.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import json


class TestMenuBarCoreInit:
    """Tests for MenuBarCore initialization."""
    
    def test_creates_with_default_status(self):
        """Core initializes with idle status."""
        from menu_bar_app import MenuBarCore
        
        core = MenuBarCore()
        
        assert core.status == "idle"
    
    def test_accepts_custom_state_dir(self, tmp_path):
        """Core accepts custom state directory."""
        from menu_bar_app import MenuBarCore
        
        core = MenuBarCore(state_dir=tmp_path)
        
        assert core._state_dir == tmp_path


class TestStatusManagement:
    """Tests for status updates."""
    
    def test_set_status_idle(self):
        """Setting status to idle works."""
        from menu_bar_app import MenuBarCore
        
        core = MenuBarCore()
        core.set_status("idle")
        
        assert core.status == "idle"
    
    def test_set_status_syncing(self):
        """Setting status to syncing works."""
        from menu_bar_app import MenuBarCore
        
        core = MenuBarCore()
        core.set_status("syncing")
        
        assert core.status == "syncing"
    
    def test_set_status_error_with_message(self):
        """Setting status to error stores message."""
        from menu_bar_app import MenuBarCore
        
        core = MenuBarCore()
        core.set_status("error", "Ollama not running")
        
        assert core.status == "error"
        assert core.error_message == "Ollama not running"
    
    def test_set_status_clears_error_message_on_non_error(self):
        """Non-error status clears error message."""
        from menu_bar_app import MenuBarCore
        
        core = MenuBarCore()
        core.set_status("error", "Some error")
        core.set_status("idle")
        
        assert core.error_message is None
    
    def test_invalid_status_raises_value_error(self):
        """Invalid status raises ValueError."""
        from menu_bar_app import MenuBarCore
        
        core = MenuBarCore()
        
        with pytest.raises(ValueError) as exc_info:
            core.set_status("invalid_status")
        
        assert "invalid_status" in str(exc_info.value)
    
    def test_get_status_icon_returns_correct_icon(self):
        """get_status_icon returns correct emoji."""
        from menu_bar_app import MenuBarCore, STATUS_ICONS
        
        core = MenuBarCore()
        
        for status, icon in STATUS_ICONS.items():
            core.set_status(status)
            assert core.get_status_icon() == icon


class TestRecentActivity:
    """Tests for recent activity tracking."""
    
    def test_get_recent_activity_returns_empty_list_initially(self, tmp_path):
        """get_recent_activity returns empty list when no activity."""
        from menu_bar_app import MenuBarCore
        
        core = MenuBarCore(state_dir=tmp_path)
        activity = core.get_recent_activity()
        
        assert isinstance(activity, list)
        assert len(activity) == 0
    
    def test_add_recent_activity_adds_item(self, tmp_path):
        """add_recent_activity adds item to list."""
        from menu_bar_app import MenuBarCore
        
        core = MenuBarCore(state_dir=tmp_path)
        
        core.add_recent_activity(
            title="Test Note",
            domain="Personal",
            path="/path/to/note.md"
        )
        
        activity = core.get_recent_activity()
        assert len(activity) == 1
        assert activity[0]["title"] == "Test Note"
        assert activity[0]["domain"] == "Personal"
        assert activity[0]["path"] == "/path/to/note.md"
    
    def test_recent_activity_newest_first(self, tmp_path):
        """Most recent activity is first in list."""
        from menu_bar_app import MenuBarCore
        
        core = MenuBarCore(state_dir=tmp_path)
        
        core.add_recent_activity("First", "Personal", "/path/1.md")
        core.add_recent_activity("Second", "Personal", "/path/2.md")
        
        activity = core.get_recent_activity()
        assert activity[0]["title"] == "Second"
        assert activity[1]["title"] == "First"
    
    def test_recent_activity_caps_at_five(self, tmp_path):
        """Recent activity is capped at 5 items."""
        from menu_bar_app import MenuBarCore
        
        core = MenuBarCore(state_dir=tmp_path)
        
        for i in range(7):
            core.add_recent_activity(f"Note {i}", "Personal", f"/path/{i}.md")
        
        activity = core.get_recent_activity()
        assert len(activity) == 5
        # Most recent should be first
        assert activity[0]["title"] == "Note 6"
    
    def test_recent_activity_persists(self, tmp_path):
        """Recent activity persists across instances."""
        from menu_bar_app import MenuBarCore
        
        core1 = MenuBarCore(state_dir=tmp_path)
        core1.add_recent_activity("Test", "Personal", "/path/test.md")
        
        # New instance should see the activity
        core2 = MenuBarCore(state_dir=tmp_path)
        activity = core2.get_recent_activity()
        
        assert len(activity) == 1
        assert activity[0]["title"] == "Test"


class TestSync:
    """Tests for sync operations."""
    
    @patch("menu_bar_app.process_all")
    def test_do_sync_calls_process_all(self, mock_process, tmp_path):
        """do_sync calls process_all."""
        from menu_bar_app import MenuBarCore
        
        core = MenuBarCore(state_dir=tmp_path)
        result = core.do_sync()
        
        assert result is True
        mock_process.assert_called_once()
    
    @patch("menu_bar_app.process_all")
    def test_do_sync_sets_syncing_status(self, mock_process, tmp_path):
        """do_sync sets status to syncing during sync."""
        from menu_bar_app import MenuBarCore
        
        statuses_seen = []
        
        def capture_status():
            statuses_seen.append(core.status)
        
        mock_process.side_effect = capture_status
        
        core = MenuBarCore(state_dir=tmp_path)
        core.do_sync()
        
        assert "syncing" in statuses_seen
    
    @patch("menu_bar_app.process_all")
    def test_do_sync_sets_idle_on_success(self, mock_process, tmp_path):
        """do_sync sets status to idle after successful sync."""
        from menu_bar_app import MenuBarCore
        
        core = MenuBarCore(state_dir=tmp_path)
        core.do_sync()
        
        assert core.status == "idle"
    
    @patch("menu_bar_app.process_all")
    def test_do_sync_sets_error_on_failure(self, mock_process, tmp_path):
        """do_sync sets error status on exception."""
        from menu_bar_app import MenuBarCore
        
        mock_process.side_effect = Exception("Sync failed")
        
        core = MenuBarCore(state_dir=tmp_path)
        result = core.do_sync()
        
        assert result is False
        assert core.status == "error"
        assert "Sync failed" in core.error_message


class TestHealthCheck:
    """Tests for health checks."""
    
    @patch("menu_bar_app.OllamaClient")
    def test_health_check_returns_dict(self, mock_client_class, tmp_path):
        """health_check returns status dict."""
        from menu_bar_app import MenuBarCore
        
        mock_client = Mock()
        mock_client.health_check.return_value = Mock(ready=True, error=None)
        mock_client_class.return_value = mock_client
        
        core = MenuBarCore(state_dir=tmp_path)
        health = core.health_check()
        
        assert isinstance(health, dict)
        assert "ollama" in health
        assert "vault" in health
    
    @patch("menu_bar_app.OllamaClient")
    def test_health_check_ollama_ready(self, mock_client_class, tmp_path):
        """health_check reports Ollama ready."""
        from menu_bar_app import MenuBarCore
        
        mock_client = Mock()
        mock_client.health_check.return_value = Mock(ready=True, error=None)
        mock_client_class.return_value = mock_client
        
        core = MenuBarCore(state_dir=tmp_path)
        health = core.health_check()
        
        assert health["ollama"]["ready"] is True
    
    @patch("menu_bar_app.OllamaClient")
    def test_health_check_ollama_down(self, mock_client_class, tmp_path):
        """health_check reports Ollama down."""
        from menu_bar_app import MenuBarCore
        
        mock_client = Mock()
        mock_client.health_check.return_value = Mock(ready=False, error="Connection refused")
        mock_client_class.return_value = mock_client
        
        core = MenuBarCore(state_dir=tmp_path)
        health = core.health_check()
        
        assert health["ollama"]["ready"] is False
        assert health["ollama"]["error"] == "Connection refused"


class TestMenuBarApp:
    """Tests for MenuBarApp wrapper."""
    
    def test_app_creates_with_core(self, tmp_path):
        """App can be created with custom core."""
        from menu_bar_app import MenuBarApp, MenuBarCore
        
        core = MenuBarCore(state_dir=tmp_path)
        app = MenuBarApp(core=core)
        
        assert app._core is core
    
    def test_app_status_delegates_to_core(self, tmp_path):
        """App status property delegates to core."""
        from menu_bar_app import MenuBarApp, MenuBarCore
        
        core = MenuBarCore(state_dir=tmp_path)
        app = MenuBarApp(core=core)
        
        assert app.status == "idle"
        
        core.set_status("syncing")
        assert app.status == "syncing"
    
    def test_app_set_status_delegates_to_core(self, tmp_path):
        """App set_status delegates to core."""
        from menu_bar_app import MenuBarApp, MenuBarCore
        
        core = MenuBarCore(state_dir=tmp_path)
        app = MenuBarApp(core=core)
        
        app.set_status("error", "Test error")
        
        assert core.status == "error"
        assert core.error_message == "Test error"
    
    def test_app_get_recent_activity_delegates(self, tmp_path):
        """App get_recent_activity delegates to core."""
        from menu_bar_app import MenuBarApp, MenuBarCore
        
        core = MenuBarCore(state_dir=tmp_path)
        core.add_recent_activity("Test", "Personal", "/path/test.md")
        
        app = MenuBarApp(core=core)
        activity = app.get_recent_activity()
        
        assert len(activity) == 1
        assert activity[0]["title"] == "Test"


class TestOpenNote:
    """Tests for open_note function."""
    
    @patch("menu_bar_app.subprocess.run")
    def test_open_note_calls_subprocess(self, mock_run):
        """open_note calls subprocess to open URL."""
        from menu_bar_app import open_note
        
        open_note("/Users/test/PARA/Personal/1_Projects/apps/note.md")
        
        mock_run.assert_called_once()
        call_args = mock_run.call_args[0][0]
        assert call_args[0] == "open"
        assert "obsidian://" in call_args[1]
    
    @patch("menu_bar_app.subprocess.run")
    def test_open_note_builds_correct_url(self, mock_run):
        """open_note builds correct Obsidian URL."""
        from menu_bar_app import open_note
        
        open_note("/Users/test/PARA/Personal/1_Projects/note.md")
        
        call_args = mock_run.call_args[0][0]
        url = call_args[1]
        
        assert "vault=PARA" in url
        # Should not have .md extension
        assert ".md" not in url or "file=" in url
