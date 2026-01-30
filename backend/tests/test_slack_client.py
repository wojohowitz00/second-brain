"""
Integration tests for Slack API client.

These tests require real Slack credentials and are marked with @pytest.mark.integration.
They will be skipped automatically if SLACK_BOT_TOKEN is not set.

To run: Set up backend/_scripts/.env with credentials, then:
    cd backend
    source _scripts/.env
    uv run pytest tests/test_slack_client.py -v -m integration
"""

import os
import pytest
from unittest.mock import patch, Mock

# Import the module under test
import slack_client
from slack_client import (
    SlackAPIError,
    SlackRateLimitError,
    fetch_messages,
    fetch_thread_replies,
    _get_token,
    _get_channel_id,
)


# --- Fixtures ---

@pytest.fixture
def has_slack_credentials():
    """Check if Slack credentials are available."""
    return os.environ.get("SLACK_BOT_TOKEN") and os.environ.get("SLACK_CHANNEL_ID")


def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line(
        "markers", "integration: mark test as integration test requiring real Slack API"
    )


# --- Integration Tests ---

@pytest.mark.integration
def test_fetch_messages_with_real_credentials(has_slack_credentials):
    """Test fetching messages from real Slack channel."""
    if not has_slack_credentials:
        pytest.skip("SLACK_BOT_TOKEN and SLACK_CHANNEL_ID not set")

    # Fetch recent messages (may be empty, that's OK)
    messages = fetch_messages(limit=10)

    # Should return a list (may be empty if no recent messages)
    assert isinstance(messages, list)

    # If there are messages, validate structure
    for msg in messages:
        assert isinstance(msg, dict)
        assert "ts" in msg  # All messages have timestamp
        assert "type" in msg
        assert msg["type"] == "message"
        # Should have filtered out bot messages
        assert "bot_id" not in msg


@pytest.mark.integration
def test_fetch_messages_filters_bot_messages(has_slack_credentials):
    """Test that bot messages are filtered out."""
    if not has_slack_credentials:
        pytest.skip("SLACK_BOT_TOKEN and SLACK_CHANNEL_ID not set")

    messages = fetch_messages(limit=50)

    # All returned messages should NOT be from bots
    for msg in messages:
        assert "bot_id" not in msg, "Bot messages should be filtered out"


@pytest.mark.integration
def test_fetch_messages_respects_oldest_parameter(has_slack_credentials):
    """Test that oldest parameter filters messages correctly."""
    if not has_slack_credentials:
        pytest.skip("SLACK_BOT_TOKEN and SLACK_CHANNEL_ID not set")

    # Use a very recent timestamp (now minus 1 hour)
    import time
    one_hour_ago = str(time.time() - 3600)

    messages = fetch_messages(oldest=one_hour_ago, limit=20)

    # All messages should have timestamp >= oldest
    for msg in messages:
        assert float(msg["ts"]) >= float(one_hour_ago)


@pytest.mark.integration
def test_fetch_thread_replies_with_nonexistent_thread(has_slack_credentials):
    """Test that fetch_thread_replies handles non-existent threads gracefully."""
    if not has_slack_credentials:
        pytest.skip("SLACK_BOT_TOKEN and SLACK_CHANNEL_ID not set")

    # Use a clearly invalid thread timestamp
    fake_ts = "0000000000.000000"

    # Should not raise - Slack API returns empty or errors gracefully
    try:
        replies = fetch_thread_replies(fake_ts)
        # If it doesn't error, should return empty list or list with error
        assert isinstance(replies, list)
    except SlackAPIError as e:
        # Expected - invalid thread
        assert e.error in ["thread_not_found", "message_not_found", "channel_not_found"]


# --- Unit Tests (no real API calls) ---

def test_get_token_raises_when_missing(monkeypatch):
    """Test that _get_token raises ValueError when SLACK_BOT_TOKEN not set."""
    monkeypatch.delenv("SLACK_BOT_TOKEN", raising=False)

    with pytest.raises(ValueError, match="SLACK_BOT_TOKEN"):
        _get_token()


def test_get_token_returns_value(monkeypatch):
    """Test that _get_token returns the environment variable value."""
    monkeypatch.setenv("SLACK_BOT_TOKEN", "xoxb-test-token")

    token = _get_token()
    assert token == "xoxb-test-token"


def test_get_channel_id_raises_when_missing(monkeypatch):
    """Test that _get_channel_id raises ValueError when SLACK_CHANNEL_ID not set."""
    monkeypatch.delenv("SLACK_CHANNEL_ID", raising=False)

    with pytest.raises(ValueError, match="SLACK_CHANNEL_ID"):
        _get_channel_id()


def test_get_channel_id_returns_value(monkeypatch):
    """Test that _get_channel_id returns the environment variable value."""
    monkeypatch.setenv("SLACK_CHANNEL_ID", "C123456")

    channel_id = _get_channel_id()
    assert channel_id == "C123456"


def test_slack_api_error_with_invalid_token(monkeypatch):
    """Test that invalid token raises SlackAPIError."""
    monkeypatch.setenv("SLACK_BOT_TOKEN", "xoxb-invalid")
    monkeypatch.setenv("SLACK_CHANNEL_ID", "C123456")

    # Mock requests to return invalid_auth error
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"ok": False, "error": "invalid_auth"}

    with patch("requests.get", return_value=mock_response):
        with pytest.raises(SlackAPIError, match="invalid_auth"):
            fetch_messages()


def test_rate_limit_error_handling(monkeypatch):
    """Test that 429 rate limit is handled correctly."""
    monkeypatch.setenv("SLACK_BOT_TOKEN", "xoxb-test")
    monkeypatch.setenv("SLACK_CHANNEL_ID", "C123456")

    # Mock requests to return 429 on all retry attempts
    mock_response = Mock()
    mock_response.status_code = 429
    mock_response.headers = {"Retry-After": "1"}

    with patch("requests.get", return_value=mock_response):
        with patch("time.sleep"):  # Don't actually sleep in tests
            with pytest.raises(SlackRateLimitError, match="Rate limited"):
                fetch_messages()


def test_fetch_messages_returns_empty_list_when_no_messages(monkeypatch):
    """Test that fetch_messages returns empty list when no messages."""
    monkeypatch.setenv("SLACK_BOT_TOKEN", "xoxb-test")
    monkeypatch.setenv("SLACK_CHANNEL_ID", "C123456")

    # Mock successful response with no messages
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"ok": True, "messages": []}

    with patch("requests.get", return_value=mock_response):
        messages = fetch_messages()
        assert messages == []
