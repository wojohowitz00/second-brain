"""Tests for veritas_client (optional Veritas Kanban push)."""

import pytest
from unittest.mock import patch


class TestIsPushEnabled:
    def test_disabled_when_unset(self):
        with patch.dict("os.environ", {}, clear=True):
            from veritas_client import is_push_enabled
            assert is_push_enabled() is False

    def test_enabled_when_true(self):
        with patch.dict("os.environ", {"VERITAS_PUSH_ENABLED": "true"}, clear=False):
            from veritas_client import is_push_enabled
            assert is_push_enabled() is True

    def test_enabled_when_1(self):
        with patch.dict("os.environ", {"VERITAS_PUSH_ENABLED": "1"}, clear=False):
            from veritas_client import is_push_enabled
            assert is_push_enabled() is True


class TestCreateTask:
    def test_returns_none_when_push_disabled(self):
        with patch.dict("os.environ", {"VERITAS_PUSH_ENABLED": "false"}, clear=False):
            from veritas_client import create_task
            assert create_task("My task") is None

    def test_returns_none_when_no_api_key(self):
        with patch.dict("os.environ", {"VERITAS_PUSH_ENABLED": "true"}, clear=False):
            with patch.dict("os.environ", {"VERITAS_API_KEY": ""}, clear=False):
                from veritas_client import create_task
                assert create_task("My task") is None

    @patch("veritas_client.requests.post")
    def test_creates_task_when_enabled_and_key_set(self, mock_post):
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"id": "task_123", "title": "My task"}
        with patch.dict("os.environ", {
            "VERITAS_PUSH_ENABLED": "true",
            "VERITAS_API_KEY": "test-key",
            "VERITAS_BASE_URL": "http://localhost:3001",
        }, clear=False):
            from veritas_client import create_task
            result = create_task("My task", status="backlog", priority="high", project="apps")
            assert result == {"id": "task_123", "title": "My task"}
            mock_post.assert_called_once()
            call_args = mock_post.call_args
            assert call_args[0][0] == "http://localhost:3001/api/tasks"
            assert call_args[1]["json"]["title"] == "My task"
            assert call_args[1]["json"]["status"] == "todo"
            assert call_args[1]["json"]["priority"] == "high"
            assert call_args[1]["json"]["project"] == "apps"
            assert call_args[1]["headers"]["X-API-Key"] == "test-key"

    @patch("veritas_client.requests.post")
    def test_returns_none_on_request_error(self, mock_post):
        import requests
        mock_post.side_effect = requests.exceptions.RequestException("timeout")
        with patch.dict("os.environ", {
            "VERITAS_PUSH_ENABLED": "true",
            "VERITAS_API_KEY": "test-key",
        }, clear=False):
            from veritas_client import create_task
            assert create_task("My task") is None
