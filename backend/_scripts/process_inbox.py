#!/usr/bin/env python3
"""
Fetch new Slack messages, classify with local LLM, write to Obsidian vault.

Usage:
    python process_inbox.py          # Process once and exit
    python process_inbox.py --daemon # Run continuously with 2-minute polling
"""

import argparse
import os
import json
import signal
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

# Use shared Slack client with retry logic
from slack_client import fetch_messages, reply_to_message, send_dm

# State management for message tracking
from state import (
    set_file_for_message,
    is_message_processed,
    mark_message_processed,
    cleanup_old_processed_messages,
    record_successful_run,
    record_failed_run,
    log_to_dead_letter,
    get_failed_count_today,
)

# Multi-level classification with local LLM
from message_classifier import MessageClassifier, ClassificationResult
from ollama_client import OllamaError, OllamaServerNotRunning, OllamaTimeout

# PARA-aware file creation
from file_writer import create_note_file, append_attachments_section, safe_attachment_filename
# Task indicators (todo:, kanban:)
from task_parser import parse_task_indicators
# Slack file attachments
from slack_client import get_message_files, download_file
# Optional Veritas Kanban push
from veritas_client import is_push_enabled, create_task as veritas_create_task

# Alert threshold - send DM if this many failures in one day
FAILURE_ALERT_THRESHOLD = 3

# Vault path (matches vault_scanner.py)
VAULT_PATH = Path.home() / "PARA"
LAST_TS_FILE = Path(__file__).parent / ".state" / ".last_processed_ts"

# Lazy-initialized classifier
_classifier: Optional[MessageClassifier] = None

# Polling configuration
POLL_INTERVAL_SECONDS = 120  # 2 minutes

# Graceful shutdown flag
_shutdown_requested = False


def _signal_handler(sig, frame):
    """Handle shutdown signals gracefully."""
    global _shutdown_requested
    sig_name = signal.Signals(sig).name if hasattr(signal, 'Signals') else str(sig)
    print(f"\nShutdown signal received ({sig_name}), finishing current cycle...")
    _shutdown_requested = True


# Register signal handlers
signal.signal(signal.SIGTERM, _signal_handler)
signal.signal(signal.SIGINT, _signal_handler)


def get_classifier() -> MessageClassifier:
    """Get or create the MessageClassifier instance."""
    global _classifier
    if _classifier is None:
        _classifier = MessageClassifier()
    return _classifier


def fetch_new_messages():
    """Get messages since last processed timestamp."""
    LAST_TS_FILE.parent.mkdir(parents=True, exist_ok=True)
    last_ts = LAST_TS_FILE.read_text().strip() if LAST_TS_FILE.exists() else "0"
    return fetch_messages(oldest=last_ts)


def _process_attachments(msg: dict, filepath: Path) -> None:
    """
    Download Slack message attachments to the note's folder and append markdown links.

    Uses 1:1 mirrored structure: attachments live in the same folder as the note.
    Skips files over max size or with disallowed extensions.
    """
    files = get_message_files(msg)
    if not files:
        return
    dest_dir = filepath.parent
    existing = set()
    links = []
    for file_info in files:
        name = file_info.get("name") or file_info.get("title") or "attachment"
        safe_name = safe_attachment_filename(name, existing)
        dest_path = dest_dir / safe_name
        downloaded = download_file(file_info, dest_path)
        if downloaded:
            existing.add(safe_name)
            links.append((name, safe_name))
    if links:
        append_attachments_section(filepath, links)


# --- Main Loop ---

def process_message(msg: dict) -> bool:
    """
    Process a single message using local LLM classification.

    Returns True if successful, False if failed (logged to dead letter).
    """
    text = msg["text"]
    ts = msg["ts"]
    timestamp = datetime.fromtimestamp(float(ts)).isoformat()

    # Skip fix: commands - handled by fix_handler.py
    if text.lower().startswith("fix:"):
        return True  # Not a failure, just skipped

    # Skip status commands (done:, progress:, etc.)
    if text.lower().split(":")[0] in ["done", "progress", "blocked", "backlog"]:
        return True  # Handled by status_handler.py

    # Idempotency check - skip already processed messages
    if is_message_processed(ts):
        return True  # Already processed

    # Parse task indicators (todo:, kanban:) for task notes
    task_indicators = parse_task_indicators(text)
    text_for_classification = task_indicators["clean_text"] if task_indicators["is_task"] else text

    try:
        # Classify using local LLM
        classifier = get_classifier()
        result = classifier.classify(text_for_classification)

        if result.confidence >= 0.6:
            # Build task_info when user used todo: or kanban:
            task_info = None
            if task_indicators["is_task"]:
                board = task_indicators.get("domain") or result.domain
                task_info = {
                    "type": "task",
                    "status": "backlog",
                    "board": board,
                    "priority": task_indicators.get("priority", "medium"),
                    "project": task_indicators.get("project"),
                    "view": task_indicators.get("view"),
                }

            filepath = create_note_file(
                classification=result,
                message_text=text,
                vault_path=VAULT_PATH,
                task_info=task_info,
            )

            # Download attachments (1:1 mirrored) and append links to note
            _process_attachments(msg, filepath)

            # Optional: push task to Veritas Kanban when todo:/kanban: and VERITAS_PUSH_ENABLED
            if task_info and is_push_enabled():
                title = (task_indicators.get("clean_text") or text).strip()[:500]
                veritas_create_task(
                    title=title or "Untitled task",
                    status=task_info.get("status", "backlog"),
                    task_type="task",
                    priority=task_info.get("priority"),
                    project=task_info.get("project"),
                )

            # Record message-to-file mapping for fix commands and status_handler
            set_file_for_message(ts, filepath)

            path_display = f"{result.domain}/{result.para_type}/{result.subject}"
            task_line = " (task → backlog)\n" if task_info else "\n"
            reply_to_message(
                ts,
                f"✓ Filed to *{path_display}*{task_line}"
                f"Category: {result.category}\n"
                f"Confidence: {result.confidence:.0%}\n"
                f"_Reply `fix: <domain>` to correct_"
                + ("\n_Reply `!done` to mark done_" if task_info else "")
            )
        else:
            # Low confidence - notify but don't file
            reply_to_message(
                ts,
                f"⚠️ Low confidence ({result.confidence:.0%})\n"
                f"Best guess: {result.domain}/{result.para_type}\n"
                f"Reasoning: {result.reasoning[:100]}\n"
                f"_Please repost with more context_"
            )

        # Mark message as processed (prevents duplicate processing)
        mark_message_processed(ts)

        # Update last processed timestamp
        LAST_TS_FILE.parent.mkdir(parents=True, exist_ok=True)
        LAST_TS_FILE.write_text(ts)

        return True

    except (OllamaServerNotRunning, OllamaTimeout) as e:
        # Ollama-specific errors - log but don't alert (transient)
        print(f"Ollama error for message {ts}: {e}")
        log_to_dead_letter(ts, text, str(e), error_type="ollama")
        return False

    except Exception as e:
        # Log to dead letter queue
        import traceback
        error_details = traceback.format_exc()
        log_to_dead_letter(ts, text, error_details, error_type="processing")
        print(f"Error processing message {ts}: {e}")
        return False


def process_all():
    """Main processing loop with error handling."""
    try:
        messages = fetch_new_messages()

        if not messages:
            print("No new messages to process")
            record_successful_run()
            return

        processed_count = 0
        failed_count = 0

        for msg in reversed(messages):  # Process oldest first
            if process_message(msg):
                processed_count += 1
            else:
                failed_count += 1

        # Periodically clean up old processed message entries
        cleanup_old_processed_messages()

        # Record run status
        if failed_count == 0:
            record_successful_run()
        else:
            record_failed_run(f"{failed_count} messages failed processing")

        # Alert if too many failures today
        total_failures_today = get_failed_count_today()
        if total_failures_today >= FAILURE_ALERT_THRESHOLD:
            try:
                send_dm(
                    f"⚠️ *Second Brain Alert*\n\n"
                    f"{total_failures_today} messages failed processing today.\n"
                    f"Check `_inbox_log/FAILED-{datetime.now().strftime('%Y-%m-%d')}.md` for details."
                )
            except Exception as alert_error:
                print(f"Failed to send alert: {alert_error}")

        print(f"Processed {processed_count} messages, {failed_count} failures")

    except Exception as e:
        # Catastrophic failure - record and alert
        import traceback
        error_details = traceback.format_exc()
        record_failed_run(str(e))
        print(f"Catastrophic error in process_all: {e}")

        try:
            send_dm(
                f"🚨 *Second Brain Critical Error*\n\n"
                f"Processing failed completely:\n```{str(e)[:500]}```"
            )
        except Exception:
            pass  # Can't even send alert

        raise


def main_loop():
    """
    Run continuous processing loop with 2-minute polling interval.
    
    Handles graceful shutdown on SIGTERM/SIGINT.
    Used when running in daemon mode (--daemon flag).
    """
    global _shutdown_requested
    print(f"Starting processing loop (polling every {POLL_INTERVAL_SECONDS}s)...")
    print("Press Ctrl+C to stop gracefully.")
    
    while not _shutdown_requested:
        try:
            process_all()
        except Exception as e:
            print(f"Error in processing cycle: {e}")
            # Continue running despite errors
        
        # Sleep in small increments to check shutdown flag
        for _ in range(POLL_INTERVAL_SECONDS):
            if _shutdown_requested:
                break
            time.sleep(1)
    
    print("Graceful shutdown complete")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Process Slack inbox messages with local LLM classification"
    )
    parser.add_argument(
        "--daemon", "-d",
        action="store_true",
        help="Run in daemon mode with 2-minute polling"
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Process once and exit (default behavior)"
    )
    args = parser.parse_args()
    
    if args.daemon:
        main_loop()
    else:
        process_all()
