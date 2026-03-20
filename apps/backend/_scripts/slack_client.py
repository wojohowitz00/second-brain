#!/usr/bin/env python3
"""
Slack API client with retry logic and rate limit handling.
All Slack interactions should go through this module.
"""

import os
import time
import requests
from pathlib import Path
from typing import List, Optional

# Retry configuration
MAX_RETRIES = 3
INITIAL_BACKOFF = 1.0  # seconds
MAX_BACKOFF = 30.0  # seconds


class SlackAPIError(Exception):
    """Raised when Slack API returns an error."""
    def __init__(self, error: str, response: dict = None):
        self.error = error
        self.response = response or {}
        super().__init__(f"Slack API error: {error}")


class SlackRateLimitError(SlackAPIError):
    """Raised when rate limited by Slack."""
    def __init__(self, retry_after: int):
        self.retry_after = retry_after
        super().__init__(f"Rate limited. Retry after {retry_after}s")


def _get_token() -> str:
    """Get Slack token from environment."""
    token = os.environ.get("SLACK_BOT_TOKEN")
    if not token:
        raise ValueError("SLACK_BOT_TOKEN environment variable not set")
    return token


def _get_channel_id() -> str:
    """Get channel ID from environment."""
    channel_id = os.environ.get("SLACK_CHANNEL_ID")
    if not channel_id:
        raise ValueError("SLACK_CHANNEL_ID environment variable not set")
    return channel_id


def _request_with_retry(
    method: str,
    url: str,
    headers: dict,
    retries: int = MAX_RETRIES,
    **kwargs
) -> dict:
    """
    Make HTTP request with exponential backoff retry.

    Handles:
    - Network errors (retry)
    - 429 rate limits (wait and retry)
    - 5xx server errors (retry)
    - Slack API errors (raise)
    """
    backoff = INITIAL_BACKOFF
    last_exception = None

    for attempt in range(retries + 1):
        try:
            if method.upper() == "GET":
                resp = requests.get(url, headers=headers, timeout=30, **kwargs)
            else:
                resp = requests.post(url, headers=headers, timeout=30, **kwargs)

            # Handle rate limiting
            if resp.status_code == 429:
                retry_after = int(resp.headers.get("Retry-After", backoff))
                if attempt < retries:
                    time.sleep(retry_after)
                    backoff = min(backoff * 2, MAX_BACKOFF)
                    continue
                raise SlackRateLimitError(retry_after)

            # Handle server errors with retry
            if resp.status_code >= 500:
                if attempt < retries:
                    time.sleep(backoff)
                    backoff = min(backoff * 2, MAX_BACKOFF)
                    continue
                resp.raise_for_status()

            # Raise for other HTTP errors
            resp.raise_for_status()

            # Parse response
            data = resp.json()

            # Check Slack API-level errors
            if not data.get("ok"):
                error = data.get("error", "unknown_error")
                raise SlackAPIError(error, data)

            return data

        except requests.exceptions.RequestException as e:
            last_exception = e
            if attempt < retries:
                time.sleep(backoff)
                backoff = min(backoff * 2, MAX_BACKOFF)
                continue
            raise

    # Should not reach here, but just in case
    if last_exception:
        raise last_exception
    raise RuntimeError("Unexpected retry loop exit")


def fetch_messages(oldest: str = "0", limit: int = 100) -> list:
    """
    Fetch messages from the inbox channel.

    Args:
        oldest: Only return messages after this timestamp
        limit: Maximum number of messages to return (max 100)

    Returns:
        List of message dicts, filtered to exclude bot messages
    """
    token = _get_token()
    channel_id = _get_channel_id()

    data = _request_with_retry(
        "GET",
        "https://slack.com/api/conversations.history",
        headers={"Authorization": f"Bearer {token}"},
        params={"channel": channel_id, "oldest": oldest, "limit": min(limit, 100)},
    )

    messages = data.get("messages", [])

    # Filter out bot messages and system messages
    return [m for m in messages if m.get("type") == "message" and "bot_id" not in m]


def fetch_thread_replies(thread_ts: str) -> list:
    """
    Fetch all replies in a thread.

    Args:
        thread_ts: Timestamp of the parent message

    Returns:
        List of message dicts (including parent)
    """
    token = _get_token()
    channel_id = _get_channel_id()

    data = _request_with_retry(
        "GET",
        "https://slack.com/api/conversations.replies",
        headers={"Authorization": f"Bearer {token}"},
        params={"channel": channel_id, "ts": thread_ts}
    )

    return data.get("messages", [])


def post_message(channel: str, text: str, thread_ts: Optional[str] = None) -> dict:
    """
    Post a message to a channel or thread.

    Args:
        channel: Channel ID to post to
        text: Message text
        thread_ts: Optional thread timestamp for replies

    Returns:
        Slack API response dict
    """
    token = _get_token()

    payload = {"channel": channel, "text": text}
    if thread_ts:
        payload["thread_ts"] = thread_ts

    return _request_with_retry(
        "POST",
        "https://slack.com/api/chat.postMessage",
        headers={"Authorization": f"Bearer {token}"},
        json=payload
    )


def reply_to_message(thread_ts: str, text: str) -> dict:
    """
    Reply to a message in the inbox channel.

    Args:
        thread_ts: Timestamp of the message to reply to
        text: Reply text

    Returns:
        Slack API response dict
    """
    channel_id = _get_channel_id()
    return post_message(channel_id, text, thread_ts)


def get_message_files(msg: dict) -> List[dict]:
    """
    Return list of file dicts for a message (attachments).

    Each file dict has at least: id, name, url_private or url_private_download, size, mimetype.
    If message has "files" with only IDs, fetches full file info via files.info.
    """
    files = msg.get("files") or []
    if not files:
        return []
    token = _get_token()
    result = []
    for f in files:
        if isinstance(f, dict) and (f.get("url_private") or f.get("url_private_download")):
            result.append(f)
            continue
        file_id = f.get("id") if isinstance(f, dict) else f
        if file_id:
            try:
                info = files_info(file_id, token)
                if info and (info.get("url_private") or info.get("url_private_download")):
                    result.append(info)
            except SlackAPIError:
                continue
    return result


def files_info(file_id: str, token: Optional[str] = None) -> Optional[dict]:
    """Get file metadata from Slack (files.info). Returns file object or None."""
    token = token or _get_token()
    data = _request_with_retry(
        "GET",
        "https://slack.com/api/files.info",
        headers={"Authorization": f"Bearer {token}"},
        params={"file": file_id},
    )
    return data.get("file")


def download_file(
    file_info: dict,
    dest_path: Path,
    token: Optional[str] = None,
    max_size_bytes: int = 50 * 1024 * 1024,
    allowed_extensions: tuple = (".pdf", ".png", ".jpg", ".jpeg", ".gif", ".webp", ".mp3", ".m4a", ".wav", ".mp4", ".mov", ".txt", ".md", ".csv"),
) -> Optional[Path]:
    """
    Download a Slack file to dest_path. Uses url_private_download with Bearer token.

    Returns dest_path on success, None on skip/failure.
    Skips if size > max_size_bytes or extension not in allowed_extensions.
    """
    token = token or _get_token()
    url = file_info.get("url_private_download") or file_info.get("url_private")
    if not url:
        return None
    size = file_info.get("size", 0)
    if size > max_size_bytes:
        return None
    name = file_info.get("name") or file_info.get("title") or "attachment"
    ext = Path(name).suffix.lower()
    if ext and ext not in allowed_extensions:
        return None
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        resp = requests.get(url, headers={"Authorization": f"Bearer {token}"}, timeout=60, stream=True)
        resp.raise_for_status()
        dest_path.write_bytes(resp.content)
        return dest_path
    except Exception:
        return None


def send_dm(text: str, user_id: Optional[str] = None) -> dict:
    """
    Send a direct message to a user.

    Args:
        text: Message text
        user_id: User ID to DM (defaults to SLACK_USER_ID env var)

    Returns:
        Slack API response dict
    """
    token = _get_token()
    user_id = user_id or os.environ.get("SLACK_USER_ID")

    if not user_id:
        raise ValueError("SLACK_USER_ID environment variable not set")

    # Open DM channel
    data = _request_with_retry(
        "POST",
        "https://slack.com/api/conversations.open",
        headers={"Authorization": f"Bearer {token}"},
        json={"users": user_id}
    )

    dm_channel = data["channel"]["id"]

    # Send message
    return post_message(dm_channel, text)
