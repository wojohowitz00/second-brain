#!/usr/bin/env python3
"""
State management for Second Brain processing.

Handles:
- Message-to-file mapping (which Slack message created which file)
- Processed message tracking (idempotency)
- Last successful run tracking (health checks)
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional
from urllib.parse import parse_qs, urlparse
import fcntl

# State files location
SCRIPTS_DIR = Path(__file__).parent
STATE_DIR = SCRIPTS_DIR / ".state"


def _ensure_state_dir():
    """Ensure state directory exists."""
    STATE_DIR.mkdir(parents=True, exist_ok=True)


def _atomic_json_read(filepath: Path) -> dict:
    """Read JSON file with locking."""
    if not filepath.exists():
        return {}

    with open(filepath, "r") as f:
        fcntl.flock(f.fileno(), fcntl.LOCK_SH)
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}
        finally:
            fcntl.flock(f.fileno(), fcntl.LOCK_UN)


def _atomic_json_write(filepath: Path, data: dict):
    """Write JSON file with locking."""
    _ensure_state_dir()

    # Write to temp file first, then rename (atomic on POSIX)
    temp_path = filepath.with_suffix(".tmp")
    with open(temp_path, "w") as f:
        fcntl.flock(f.fileno(), fcntl.LOCK_EX)
        try:
            json.dump(data, f, indent=2, default=str)
        finally:
            fcntl.flock(f.fileno(), fcntl.LOCK_UN)

    temp_path.rename(filepath)


# --- Message-to-File Mapping ---

MESSAGE_MAPPING_FILE = STATE_DIR / "message_mapping.json"


def get_file_for_message(message_ts: str) -> Optional[Path]:
    """
    Get the file path for a given message timestamp.

    Returns None if message hasn't been processed.
    """
    mapping = _atomic_json_read(MESSAGE_MAPPING_FILE)
    filepath_str = mapping.get(message_ts)

    if filepath_str:
        filepath = Path(filepath_str)
        if filepath.exists():
            return filepath

    return None


def set_file_for_message(message_ts: str, filepath: Path):
    """
    Record which file was created from a message.
    """
    mapping = _atomic_json_read(MESSAGE_MAPPING_FILE)
    mapping[message_ts] = str(filepath)
    _atomic_json_write(MESSAGE_MAPPING_FILE, mapping)


def remove_message_mapping(message_ts: str):
    """
    Remove a message from the mapping (e.g., after file deletion).
    """
    mapping = _atomic_json_read(MESSAGE_MAPPING_FILE)
    if message_ts in mapping:
        del mapping[message_ts]
        _atomic_json_write(MESSAGE_MAPPING_FILE, mapping)


def update_file_location(message_ts: str, new_filepath: Path):
    """
    Update the file location for a message (e.g., after move).
    """
    set_file_for_message(message_ts, new_filepath)


# --- Processed Messages (Idempotency) ---

PROCESSED_MESSAGES_FILE = STATE_DIR / "processed_messages.json"
PROCESSED_MESSAGE_TTL_DAYS = 30


def is_message_processed(message_ts: str) -> bool:
    """
    Check if a message has already been processed.
    """
    processed = _atomic_json_read(PROCESSED_MESSAGES_FILE)
    return message_ts in processed


def mark_message_processed(message_ts: str):
    """
    Mark a message as processed.
    """
    processed = _atomic_json_read(PROCESSED_MESSAGES_FILE)
    processed[message_ts] = datetime.now().isoformat()
    _atomic_json_write(PROCESSED_MESSAGES_FILE, processed)


def cleanup_old_processed_messages():
    """
    Remove entries older than TTL to prevent unbounded growth.
    Call periodically (e.g., daily).
    """
    processed = _atomic_json_read(PROCESSED_MESSAGES_FILE)
    cutoff = datetime.now() - timedelta(days=PROCESSED_MESSAGE_TTL_DAYS)

    cleaned = {}
    for ts, processed_at_str in processed.items():
        try:
            processed_at = datetime.fromisoformat(processed_at_str)
            if processed_at > cutoff:
                cleaned[ts] = processed_at_str
        except (ValueError, TypeError):
            # Keep entries with invalid dates (shouldn't happen)
            cleaned[ts] = processed_at_str

    if len(cleaned) != len(processed):
        _atomic_json_write(PROCESSED_MESSAGES_FILE, cleaned)


# --- Last Run Tracking (Health Checks) ---

LAST_RUN_FILE = STATE_DIR / "last_run.json"


def record_successful_run():
    """
    Record that a processing run completed successfully.
    """
    data = {
        "last_success": datetime.now().isoformat(),
        "status": "success"
    }
    _atomic_json_write(LAST_RUN_FILE, data)


def record_failed_run(error: str):
    """
    Record that a processing run failed.
    """
    existing = _atomic_json_read(LAST_RUN_FILE)
    data = {
        "last_success": existing.get("last_success"),
        "last_failure": datetime.now().isoformat(),
        "last_error": error,
        "status": "failed"
    }
    _atomic_json_write(LAST_RUN_FILE, data)


def get_last_run_status() -> dict:
    """
    Get the last run status.

    Returns:
        Dict with keys: last_success, last_failure, last_error, status
    """
    return _atomic_json_read(LAST_RUN_FILE)


def is_system_healthy(max_age_minutes: int = 60) -> tuple[bool, str]:
    """
    Check if the system is healthy.

    Args:
        max_age_minutes: Maximum age of last successful run

    Returns:
        Tuple of (is_healthy, message)
    """
    status = get_last_run_status()

    if not status:
        return False, "No runs recorded yet"

    last_success_str = status.get("last_success")
    if not last_success_str:
        return False, "No successful runs recorded"

    try:
        last_success = datetime.fromisoformat(last_success_str)
        age = datetime.now() - last_success

        if age > timedelta(minutes=max_age_minutes):
            return False, f"Last success was {age.total_seconds() / 60:.0f} minutes ago"

        return True, f"Healthy - last success {age.total_seconds() / 60:.0f} minutes ago"

    except (ValueError, TypeError) as e:
        return False, f"Invalid last_success timestamp: {e}"


# --- Dead Letter Queue ---

from vault_scanner import VAULT_ROOT
VAULT_PATH = VAULT_ROOT


def log_to_dead_letter(
    message_ts: str,
    message_text: str,
    error: str,
    error_type: str = "processing"
):
    """
    Log a failed message to the dead letter queue.

    Creates/appends to _inbox_log/FAILED-{date}.md

    Args:
        message_ts: Slack message timestamp
        message_text: Original message text
        error: Error message/traceback
        error_type: Type of error (processing, classification, network, etc.)
    """
    today = datetime.now().strftime("%Y-%m-%d")
    failed_log = VAULT_PATH / "_inbox_log" / f"FAILED-{today}.md"
    failed_log.parent.mkdir(parents=True, exist_ok=True)

    if not failed_log.exists():
        failed_log.write_text(
            f"# Failed Messages - {today}\n\n"
            "Messages that failed processing and need manual review.\n\n"
            "---\n\n"
        )

    time_now = datetime.now().strftime("%H:%M:%S")
    entry = f"""## {time_now} - {error_type.upper()}

**Message TS:** `{message_ts}`

**Original:**
> {message_text[:200]}{"..." if len(message_text) > 200 else ""}

**Error:**
```
{error}
```

---

"""

    with open(failed_log, "a") as f:
        f.write(entry)


def get_failed_count_today() -> int:
    """Get the count of failed messages today."""
    today = datetime.now().strftime("%Y-%m-%d")
    failed_log = VAULT_PATH / "_inbox_log" / f"FAILED-{today}.md"

    if not failed_log.exists():
        return 0

    content = failed_log.read_text()
    # Count error entries by counting "## " headers (excluding the title)
    return content.count("\n## ") - content.count("# Failed")


# --- YouTube URL Registry (Idempotency) ---

YOUTUBE_URLS_FILE = STATE_DIR / "youtube_urls.json"


def normalize_youtube_url(url: str) -> str:
    """
    Normalize YouTube URLs to a canonical form for idempotency tracking.

    If a video id is detected, return: https://www.youtube.com/watch?v=<id>
    Otherwise, return a sanitized URL (no fragment).
    """
    if not url:
        return url

    url = url.strip()
    if "://" not in url and ("youtube.com" in url or "youtu.be" in url):
        url = f"https://{url}"

    try:
        parsed = urlparse(url)
    except Exception:
        return url

    host = (parsed.netloc or "").lower()
    path = parsed.path or ""
    video_id = None

    if host in {"youtu.be", "www.youtu.be"}:
        video_id = path.strip("/") or None
    elif "youtube.com" in host:
        qs = parse_qs(parsed.query)
        if "v" in qs and qs["v"]:
            video_id = qs["v"][0]
        else:
            parts = [p for p in path.split("/") if p]
            if len(parts) >= 2 and parts[0] in {"shorts", "embed", "v"}:
                video_id = parts[1]

    if video_id:
        return f"https://www.youtube.com/watch?v={video_id}"

    if parsed.fragment:
        parsed = parsed._replace(fragment="")
    return parsed.geturl() or url


def get_youtube_url_entry(url: str) -> Optional[dict]:
    """
    Get registry entry for a YouTube URL, if present.
    """
    if not url:
        return None
    key = normalize_youtube_url(url)
    registry = _atomic_json_read(YOUTUBE_URLS_FILE)
    return registry.get(key)


def is_youtube_url_processed(url: str) -> bool:
    """
    Return True if the URL was successfully processed before.
    """
    entry = get_youtube_url_entry(url)
    return bool(entry and entry.get("status") == "success")


def should_process_youtube_url(url: str, force: bool = False) -> bool:
    """
    Decide whether a URL should be processed.

    Returns False when a successful entry exists, unless force=True.
    """
    if force:
        return True
    return not is_youtube_url_processed(url)


def record_youtube_url_status(
    url: str,
    status: str,
    note_path: Optional[Path] = None,
    error: Optional[str] = None,
    metadata: Optional[dict] = None,
    increment_attempts: bool = False,
) -> dict:
    """
    Create or update a URL registry entry.
    """
    if not url:
        return {}
    key = normalize_youtube_url(url)
    registry = _atomic_json_read(YOUTUBE_URLS_FILE)
    entry = registry.get(key, {})

    if not entry.get("first_seen"):
        entry["first_seen"] = datetime.now().isoformat()

    if increment_attempts:
        entry["attempts"] = int(entry.get("attempts", 0)) + 1

    entry["status"] = status
    entry["last_updated"] = datetime.now().isoformat()

    if note_path:
        entry["note_path"] = str(note_path)
    if error:
        entry["last_error"] = error
    if metadata:
        entry["metadata"] = metadata

    registry[key] = entry
    _atomic_json_write(YOUTUBE_URLS_FILE, registry)
    return entry


def record_youtube_url_queued(url: str, metadata: Optional[dict] = None) -> dict:
    """Record URL as queued for ingestion."""
    return record_youtube_url_status(url, "queued", metadata=metadata)


def record_youtube_url_processing(url: str, metadata: Optional[dict] = None) -> dict:
    """Record URL as in-progress."""
    return record_youtube_url_status(url, "processing", metadata=metadata)


def record_youtube_url_success(
    url: str,
    note_path: Path,
    metadata: Optional[dict] = None,
) -> dict:
    """Record URL as successfully processed."""
    return record_youtube_url_status(
        url,
        "success",
        note_path=note_path,
        metadata=metadata,
    )


def record_youtube_url_failed(
    url: str,
    error: str,
    metadata: Optional[dict] = None,
) -> dict:
    """Record URL as failed and increment attempts."""
    return record_youtube_url_status(
        url,
        "failed",
        error=error,
        metadata=metadata,
        increment_attempts=True,
    )
