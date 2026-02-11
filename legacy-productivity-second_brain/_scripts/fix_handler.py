#!/usr/bin/env python3
"""Handle fix: commands in Slack thread replies."""

import re
from datetime import datetime
from pathlib import Path
import yaml

# Use shared Slack client with retry logic
from slack_client import (
    fetch_messages,
    fetch_thread_replies,
    reply_to_message,
)

# State management for message-to-file mapping
from state import get_file_for_message, update_file_location

VAULT_PATH = Path.home() / "SecondBrain"


def move_file(filepath, new_destination):
    """
    Move file to new destination folder.

    Returns:
        New filepath if successful, None otherwise.
    """
    if not filepath.exists():
        return None

    new_folder = VAULT_PATH / new_destination
    new_folder.mkdir(parents=True, exist_ok=True)

    new_filepath = new_folder / filepath.name

    # Handle conflicts
    if new_filepath.exists():
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        stem = filepath.stem
        new_filepath = new_folder / f"{stem}-moved-{timestamp}.md"

    filepath.rename(new_filepath)

    # Update frontmatter to record the move
    try:
        content = new_filepath.read_text()
        if "---" in content:
            parts = content.split("---")
            if len(parts) >= 2:
                fm = yaml.safe_load(parts[1])
                if fm:
                    fm["type"] = _get_type_for_destination(new_destination)
                    fm["moved_from"] = filepath.parent.name
                    fm["moved_at"] = datetime.now().isoformat()

                    # Rewrite with updated frontmatter
                    new_content = "---\n"
                    for k, v in fm.items():
                        if isinstance(v, list):
                            new_content += f"{k}:\n"
                            for item in v:
                                new_content += f"  - {item}\n"
                        else:
                            new_content += f"{k}: {v}\n"
                    new_content += "---\n" + "---".join(parts[2:])
                    new_filepath.write_text(new_content)
    except Exception as e:
        print(f"Error updating frontmatter: {e}")

    return new_filepath


def _get_type_for_destination(destination: str) -> str:
    """Get the frontmatter type for a destination folder."""
    type_map = {
        "people": "person",
        "projects": "project",
        "ideas": "idea",
        "admin": "admin"
    }
    return type_map.get(destination, destination)


def process_fix_commands():
    """Check for fix: commands in all recent threads."""
    messages = fetch_messages(limit=50)
    processed = 0

    for msg in messages:
        # Check if message has thread replies
        if msg.get("thread_ts") or msg.get("reply_count", 0) > 0:
            thread_ts = msg.get("thread_ts") or msg.get("ts")
            original_ts = msg.get("ts")
            replies = fetch_thread_replies(thread_ts)

            for reply in replies:
                text = reply.get("text", "").strip()
                if text.lower().startswith("fix:"):
                    # Extract destination
                    match = re.match(r"fix:\s*(\w+)", text.lower())
                    if match:
                        new_dest = match.group(1)
                        if new_dest in ["people", "projects", "ideas", "admin"]:
                            # Find original file using message mapping
                            filepath = get_file_for_message(original_ts)

                            if filepath:
                                # Move file
                                new_filepath = move_file(filepath, new_dest)
                                if new_filepath:
                                    # Update the message mapping with new location
                                    update_file_location(original_ts, new_filepath)

                                    reply_to_message(
                                        thread_ts,
                                        f"✓ Moved to *{new_dest}* as `{new_filepath.name}`"
                                    )
                                    processed += 1
                                else:
                                    reply_to_message(
                                        thread_ts,
                                        "⚠️ Failed to move file"
                                    )
                            else:
                                reply_to_message(
                                    thread_ts,
                                    "⚠️ Could not find original file (message not in mapping)"
                                )

    print(f"Processed {processed} fix commands")


if __name__ == "__main__":
    process_fix_commands()
