#!/usr/bin/env python3
"""
Fetch new Slack messages, classify with Claude, write to Obsidian.
Run via Claude Code or cron.
"""

import os
import json
from datetime import datetime
from pathlib import Path

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

# Schema validation for classification responses
from schema import validate_classification, create_fallback_classification, ValidationError

# Wikilink generation for Obsidian integration
from wikilinks import process_linked_entities, insert_wikilinks

# Alert threshold - send DM if this many failures in one day
FAILURE_ALERT_THRESHOLD = 3

VAULT_PATH = Path.home() / "SecondBrain"
LAST_TS_FILE = VAULT_PATH / "_scripts/.last_processed_ts"


def fetch_new_messages():
    """Get messages since last processed timestamp."""
    last_ts = LAST_TS_FILE.read_text().strip() if LAST_TS_FILE.exists() else "0"
    return fetch_messages(oldest=last_ts)


# --- Classification (called by Claude Code) ---

CLASSIFICATION_PROMPT = """
You are a classifier for a personal knowledge system.

INPUT: {thought}

OUTPUT: Return ONLY valid JSON:
{{
  "destination": "people" | "projects" | "ideas" | "admin",
  "confidence": 0.0-1.0,
  "filename": "suggested-filename-kebab-case",
  "extracted": {{
    // For people: name, aliases[] (nicknames), context, follow_ups[]
    // For projects: name, status, next_action, notes
    // For ideas: title, oneliner
    // For admin: task, due_date (if mentioned), status
  }},
  "linked_entities": [
    // People and projects mentioned in the text that should be linked
    {{"name": "Person Name", "type": "person"}},
    {{"name": "Project Name", "type": "project"}}
  ]
}}

RULES:
- "people": Mentions a specific person or follow-up with someone
- "projects": Multi-step work with a next action
- "ideas": Insights, possibilities, explorations
- "admin": One-off tasks, errands
- Always extract concrete next_action for projects (verb + object)
- If confidence < 0.6, still classify but it will be flagged for review
- Extract ALL people and project names mentioned for linked_entities
- Include the primary subject in linked_entities if it's a person/project
"""


def classify_thought(thought: str) -> dict:
    """
    This function should be replaced with actual Claude Code invocation.
    In practice, Claude Code runs this script and handles the AI call.

    For now, returns a placeholder structure.
    """
    # Placeholder - Claude Code fills this in
    # In actual use, this would call Claude API via Claude Code
    return {
        "destination": "ideas",
        "confidence": 0.5,
        "filename": "placeholder",
        "extracted": {},
        "linked_entities": []
    }


# --- Obsidian Writing ---

def write_to_obsidian(classification: dict, original_text: str, timestamp: str):
    """Write classified item to appropriate Obsidian folder."""
    dest = classification["destination"]
    conf = classification["confidence"]
    extracted = classification["extracted"]
    filename = classification["filename"] + ".md"
    linked_entities = classification.get("linked_entities", [])

    folder = VAULT_PATH / dest
    folder.mkdir(parents=True, exist_ok=True)

    # Process linked entities (creates stubs for new ones)
    entity_links = process_linked_entities(linked_entities, create_stubs=True)

    # Build frontmatter based on type
    if dest == "people":
        frontmatter = {
            "type": "person",
            "name": extracted.get("name", ""),
            "aliases": extracted.get("aliases", []),
            "context": extracted.get("context", ""),
            "follow_ups": extracted.get("follow_ups", []),
            "last_touched": timestamp[:10],
            "tags": []
        }
        body = ""
    elif dest == "projects":
        frontmatter = {
            "type": "project",
            "name": extracted.get("name", ""),
            "status": extracted.get("status", "active"),
            "next_action": extracted.get("next_action", ""),
            "tags": [],
            "created": timestamp[:10]
        }
        body = extracted.get("notes", "")
    elif dest == "ideas":
        frontmatter = {
            "type": "idea",
            "title": extracted.get("title", ""),
            "oneliner": extracted.get("oneliner", ""),
            "tags": [],
            "created": timestamp[:10]
        }
        body = ""
    else:  # admin
        frontmatter = {
            "type": "admin",
            "task": extracted.get("task", ""),
            "due_date": extracted.get("due_date", ""),
            "status": "pending",
            "created": timestamp[:10]
        }
        body = ""

    # Write file
    filepath = folder / filename

    # Handle existing files (append timestamp if exists)
    if filepath.exists():
        base = filepath.stem
        filepath = folder / f"{base}-{timestamp[:10]}.md"

    content = "---\n"
    for k, v in frontmatter.items():
        if isinstance(v, list):
            content += f"{k}:\n"
            for item in v:
                content += f"  - {item}\n"
        else:
            content += f"{k}: {v}\n"
    content += "---\n\n"

    if body:
        # Insert wikilinks into body text
        linked_body = insert_wikilinks(body, entity_links)
        content += f"{linked_body}\n\n"

    # Insert wikilinks into original capture
    linked_original = insert_wikilinks(original_text, entity_links)
    content += f"## Original Capture\n\n> {linked_original}\n"

    filepath.write_text(content)
    return filepath


def log_to_inbox_log(original: str, destination: str, filename: str, confidence: float):
    """Append to daily inbox log."""
    today = datetime.now().strftime("%Y-%m-%d")
    log_file = VAULT_PATH / "_inbox_log" / f"{today}.md"
    log_file.parent.mkdir(parents=True, exist_ok=True)

    if not log_file.exists():
        log_file.write_text(
            f"## Inbox Processing Log - {today}\n\n"
            "| Time | Original | Destination | Filed As | Confidence |\n"
            "|------|----------|-------------|----------|------------|\n"
        )

    time_now = datetime.now().strftime("%H:%M")
    status = "**NEEDS REVIEW**" if confidence < 0.6 else destination

    with open(log_file, "a") as f:
        f.write(
            f"| {time_now} | {original[:40]}... | {status} | {filename} | {confidence:.2f} |\n"
        )


def append_to_daily_note(destination: str, filename: str, summary: str):
    """
    Append a capture entry to today's daily note.

    Creates the daily note if it doesn't exist, using Obsidian's
    standard daily note format.
    """
    today = datetime.now().strftime("%Y-%m-%d")
    daily_folder = VAULT_PATH / "daily"
    daily_folder.mkdir(parents=True, exist_ok=True)

    daily_note = daily_folder / f"{today}.md"
    time_now = datetime.now().strftime("%H:%M")

    # Remove .md extension for wikilink
    link_name = filename.replace(".md", "")

    if not daily_note.exists():
        # Create daily note with header
        daily_note.write_text(
            f"---\n"
            f"type: daily\n"
            f"date: {today}\n"
            f"---\n\n"
            f"# {today}\n\n"
            f"## Captured\n\n"
        )

    # Append the capture entry with wikilink
    with open(daily_note, "a") as f:
        f.write(f"- {time_now} - [[{link_name}]] ({destination}): {summary[:60]}\n")


# --- Main Loop ---

def process_message(msg: dict) -> bool:
    """
    Process a single message.

    Returns True if successful, False if failed (logged to dead letter).
    """
    text = msg["text"]
    ts = msg["ts"]
    timestamp = datetime.fromtimestamp(float(ts)).isoformat()

    # Skip fix: commands - handled by fix_handler.py
    if text.lower().startswith("fix:"):
        return True  # Not a failure, just skipped

    # Idempotency check - skip already processed messages
    if is_message_processed(ts):
        return True  # Already processed

    try:
        # Classify and validate
        try:
            raw_classification = classify_thought(text)
            classification = validate_classification(raw_classification)
        except ValidationError as e:
            # Fallback to ideas with low confidence if validation fails
            print(f"Validation error for message {ts}: {e}")
            classification = create_fallback_classification(text, error=str(e))

        conf = classification["confidence"]
        dest = classification["destination"]

        if conf >= 0.6:
            # File it
            filepath = write_to_obsidian(classification, text, timestamp)
            log_to_inbox_log(text, dest, filepath.name, conf)

            # Append to daily note for Obsidian integration
            summary = text[:60] if len(text) <= 60 else text[:57] + "..."
            append_to_daily_note(dest, filepath.name, summary)

            # Record message-to-file mapping for fix commands
            set_file_for_message(ts, filepath)

            reply_to_message(
                ts,
                f"✓ Filed to *{dest}* as `{filepath.name}`\n"
                f"Confidence: {conf:.0%}\n"
                f"_Reply `fix: people|projects|ideas|admin` if wrong_"
            )
        else:
            # Low confidence - log but don't file
            log_to_inbox_log(text, "NEEDS REVIEW", "—", conf)

            reply_to_message(
                ts,
                f"⚠️ Not sure where this goes (confidence: {conf:.0%})\n"
                f"Please repost with a prefix like:\n"
                f"• `person: ...`\n• `project: ...`\n• `idea: ...`\n• `admin: ...`"
            )

        # Mark message as processed (prevents duplicate processing)
        mark_message_processed(ts)

        # Update last processed timestamp
        LAST_TS_FILE.parent.mkdir(parents=True, exist_ok=True)
        LAST_TS_FILE.write_text(ts)

        return True

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


if __name__ == "__main__":
    process_all()
