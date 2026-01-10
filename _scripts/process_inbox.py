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
from state import set_file_for_message

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
    // For people: name, context, follow_ups[]
    // For projects: name, status, next_action, notes
    // For ideas: title, oneliner
    // For admin: task, due_date (if mentioned), status
  }}
}}

RULES:
- "people": Mentions a specific person or follow-up with someone
- "projects": Multi-step work with a next action
- "ideas": Insights, possibilities, explorations
- "admin": One-off tasks, errands
- Always extract concrete next_action for projects (verb + object)
- If confidence < 0.6, still classify but it will be flagged for review
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
        "extracted": {}
    }


# --- Obsidian Writing ---

def write_to_obsidian(classification: dict, original_text: str, timestamp: str):
    """Write classified item to appropriate Obsidian folder."""
    dest = classification["destination"]
    conf = classification["confidence"]
    extracted = classification["extracted"]
    filename = classification["filename"] + ".md"
    
    folder = VAULT_PATH / dest
    folder.mkdir(parents=True, exist_ok=True)
    
    # Build frontmatter based on type
    if dest == "people":
        frontmatter = {
            "type": "person",
            "name": extracted.get("name", ""),
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
        content += f"{body}\n\n"
    
    content += f"## Original Capture\n\n> {original_text}\n"
    
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


# --- Main Loop ---

def process_all():
    """Main processing loop."""
    messages = fetch_new_messages()
    
    if not messages:
        print("No new messages to process")
        return
    
    processed_count = 0
    
    for msg in reversed(messages):  # Process oldest first
        text = msg["text"]
        ts = msg["ts"]
        timestamp = datetime.fromtimestamp(float(ts)).isoformat()

        # Skip fix: commands - handled by fix_handler.py
        if text.lower().startswith("fix:"):
            continue

        # Classify
        classification = classify_thought(text)
        conf = classification["confidence"]
        dest = classification["destination"]
        
        if conf >= 0.6:
            # File it
            filepath = write_to_obsidian(classification, text, timestamp)
            log_to_inbox_log(text, dest, filepath.name, conf)

            # Record message-to-file mapping for fix commands
            set_file_for_message(ts, filepath)

            reply_to_message(
                ts,
                f"✓ Filed to *{dest}* as `{filepath.name}`\n"
                f"Confidence: {conf:.0%}\n"
                f"_Reply `fix: people|projects|ideas|admin` if wrong_"
            )
            processed_count += 1
        else:
            # Low confidence - log but don't file
            log_to_inbox_log(text, "NEEDS REVIEW", "—", conf)
            
            reply_to_message(
                ts,
                f"⚠️ Not sure where this goes (confidence: {conf:.0%})\n"
                f"Please repost with a prefix like:\n"
                f"• `person: ...`\n• `project: ...`\n• `idea: ...`\n• `admin: ...`"
            )
        
        # Update last processed timestamp
        LAST_TS_FILE.parent.mkdir(parents=True, exist_ok=True)
        LAST_TS_FILE.write_text(ts)
    
    print(f"Processed {processed_count} messages")


if __name__ == "__main__":
    process_all()
