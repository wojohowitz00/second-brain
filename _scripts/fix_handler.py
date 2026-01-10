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

VAULT_PATH = Path.home() / "SecondBrain"


def find_original_message_file(original_ts):
    """Find the file created from a message timestamp."""
    # Search inbox logs for this timestamp
    log_dir = VAULT_PATH / "_inbox_log"
    if not log_dir.exists():
        return None
    
    # Convert timestamp to datetime
    try:
        msg_time = datetime.fromtimestamp(float(original_ts))
        date_str = msg_time.strftime("%Y-%m-%d")
        log_file = log_dir / f"{date_str}.md"
        
        if not log_file.exists():
            return None
        
        # Read log and find matching entry
        content = log_file.read_text()
        for line in content.split("\n"):
            if original_ts[:10] in line or msg_time.strftime("%H:%M") in line:
                # Extract filename from log entry
                parts = [p.strip() for p in line.split("|")]
                if len(parts) >= 5:
                    filename = parts[4].strip()
                    if filename and filename != "—":
                        # Search all folders for this file
                        for folder in ["people", "projects", "ideas", "admin"]:
                            folder_path = VAULT_PATH / folder
                            if folder_path.exists():
                                filepath = folder_path / filename
                                if filepath.exists():
                                    return filepath
        
        return None
    except Exception as e:
        print(f"Error finding file for {original_ts}: {e}")
        return None


def move_file(filepath, new_destination):
    """Move file to new destination folder."""
    if not filepath.exists():
        return False
    
    new_folder = VAULT_PATH / new_destination
    new_folder.mkdir(parents=True, exist_ok=True)
    
    new_filepath = new_folder / filepath.name
    
    # Handle conflicts
    if new_filepath.exists():
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        stem = filepath.stem
        new_filepath = new_folder / f"{stem}-moved-{timestamp}.md"
    
    filepath.rename(new_filepath)
    
    # Update frontmatter destination if needed
    try:
        content = new_filepath.read_text()
        if "---" in content:
            parts = content.split("---")
            if len(parts) >= 2:
                fm = yaml.safe_load(parts[1])
                if fm:
                    fm["moved_to"] = new_destination
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
    
    return True


def process_fix_commands():
    """Check for fix: commands in all recent threads."""
    messages = fetch_messages(limit=50)
    processed = 0
    
    for msg in messages:
        # Check if message has thread replies
        if msg.get("thread_ts") or msg.get("reply_count", 0) > 0:
            thread_ts = msg.get("thread_ts") or msg.get("ts")
            replies = fetch_thread_replies(thread_ts)
            
            for reply in replies:
                text = reply.get("text", "").strip()
                if text.lower().startswith("fix:"):
                    # Extract destination
                    match = re.match(r"fix:\s*(\w+)", text.lower())
                    if match:
                        new_dest = match.group(1)
                        if new_dest in ["people", "projects", "ideas", "admin"]:
                            # Find original file
                            original_ts = msg.get("ts")
                            filepath = find_original_message_file(original_ts)
                            
                            if filepath:
                                # Move file
                                if move_file(filepath, new_dest):
                                    reply_to_message(
                                        thread_ts,
                                        f"✓ Moved to *{new_dest}* as `{filepath.name}`"
                                    )
                                    processed += 1
                                else:
                                    reply_to_message(
                                        thread_ts,
                                        f"⚠️ Failed to move file"
                                    )
                            else:
                                reply_to_message(
                                    thread_ts,
                                    f"⚠️ Could not find original file"
                                )
    
    print(f"Processed {processed} fix commands")


if __name__ == "__main__":
    process_fix_commands()
