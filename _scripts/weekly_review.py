#!/usr/bin/env python3
"""Generate weekly review from Obsidian vault, send to Slack DM."""

from pathlib import Path
from datetime import datetime, timedelta
import yaml
import os
import requests

VAULT_PATH = Path.home() / "SecondBrain"
SLACK_TOKEN = os.environ.get("SLACK_BOT_TOKEN")
SLACK_USER_ID = os.environ.get("SLACK_USER_ID")


def send_dm(text):
    """Send digest to user DM."""
    if not SLACK_TOKEN or not SLACK_USER_ID:
        raise ValueError("SLACK_BOT_TOKEN and SLACK_USER_ID must be set")
    
    resp = requests.post(
        "https://slack.com/api/conversations.open",
        headers={"Authorization": f"Bearer {SLACK_TOKEN}"},
        json={"users": SLACK_USER_ID}
    )
    resp.raise_for_status()
    data = resp.json()
    
    if not data.get("ok"):
        raise ValueError(f"Failed to open DM: {data.get('error')}")
    
    dm_channel = data["channel"]["id"]
    
    resp = requests.post(
        "https://slack.com/api/chat.postMessage",
        headers={"Authorization": f"Bearer {SLACK_TOKEN}"},
        json={"channel": dm_channel, "text": text}
    )
    resp.raise_for_status()
    return resp.json()


def gather_week_data():
    """Collect all items from past 7 days."""
    week_ago = datetime.now() - timedelta(days=7)
    
    # Read inbox logs from past week
    inbox_logs = []
    log_dir = VAULT_PATH / "_inbox_log"
    if log_dir.exists():
        for log_file in log_dir.glob("*.md"):
            try:
                date_str = log_file.stem
                log_date = datetime.strptime(date_str, "%Y-%m-%d")
                if log_date >= week_ago:
                    inbox_logs.append(log_file.read_text())
            except (ValueError, Exception) as e:
                print(f"Error reading log {log_file}: {e}")
    
    # Gather all active projects
    projects = []
    projects_dir = VAULT_PATH / "projects"
    if projects_dir.exists():
        for f in projects_dir.glob("*.md"):
            try:
                content = f.read_text()
                if "---" in content:
                    parts = content.split("---")
                    if len(parts) >= 2:
                        fm = yaml.safe_load(parts[1])
                        if fm:
                            projects.append(fm)
            except Exception as e:
                print(f"Error reading {f}: {e}")
    
    # Count items by type from logs
    stats = {"people": 0, "projects": 0, "ideas": 0, "admin": 0, "review": 0}
    for log_text in inbox_logs:
        for line in log_text.split("\n"):
            if "|" in line and "Destination" not in line:
                parts = [p.strip() for p in line.split("|")]
                if len(parts) >= 4:
                    dest = parts[3].lower()
                    if "review" in dest:
                        stats["review"] += 1
                    elif dest in stats:
                        stats[dest] += 1
    
    return inbox_logs, projects, stats


REVIEW_PROMPT = """
Generate a weekly review under 250 words.

Items captured this week:
{stats}

Active projects:
{projects}

Structure:
1. **What you captured** (breakdown by type)
2. **Progress made** (projects moved forward)
3. **What's stuck** (projects with no recent activity)
4. **One insight** (pattern or theme from the week)

Keep it reflective and actionable.
"""


def generate_review(inbox_logs, projects, stats):
    """
    Generate review text. In practice, Claude Code would call Claude API here.
    """
    # Placeholder - Claude Code fills this in
    lines = [
        f"*Weekly Review - Week of {datetime.now().strftime('%B %d, %Y')}*\n"
    ]
    
    # What you captured
    total = sum(stats.values())
    lines.append(f"*Captured {total} items this week:*")
    for dest, count in stats.items():
        if count > 0:
            lines.append(f"• {dest.title()}: {count}")
    
    # Progress
    active = [p for p in projects if p.get("status") == "active"]
    lines.append(f"\n*Active projects: {len(active)}*")
    for proj in active[:5]:
        name = proj.get("name", "Unnamed")
        next_action = proj.get("next_action", "")
        if next_action:
            lines.append(f"• {name}: {next_action}")
    
    # Stuck items
    stalled = [p for p in projects if p.get("status") == "active" and not p.get("next_action")]
    if stalled:
        lines.append(f"\n*Projects needing attention: {len(stalled)}*")
        for proj in stalled[:3]:
            lines.append(f"• {proj.get('name', 'Unnamed')}")
    
    return "\n".join(lines)


def main():
    """Main review generation."""
    inbox_logs, projects, stats = gather_week_data()
    
    review_text = generate_review(inbox_logs, projects, stats)
    
    # In actual use, Claude Code would call Claude API with REVIEW_PROMPT
    
    send_dm(review_text)
    print("Weekly review sent to Slack DM")


if __name__ == "__main__":
    main()
