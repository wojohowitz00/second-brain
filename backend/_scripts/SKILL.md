# Second Brain Skill

## Purpose
Process Slack inbox, classify thoughts, write to Obsidian vault.

## Scripts Location
`~/SecondBrain/_scripts/`

## Commands

### Process Inbox
```bash
python3 ~/SecondBrain/_scripts/process_inbox.py
```
Fetches new Slack messages from `#sb-inbox`, classifies with Claude, writes to Obsidian vault.

**What it does:**
1. Fetches messages since last run
2. Classifies each message (people/projects/ideas/admin)
3. Writes markdown file to appropriate folder
4. Logs to `_inbox_log/YYYY-MM-DD.md`
5. Replies in Slack thread with confirmation

**Classification:**
Uses Claude API with this prompt:
```
You are a classifier for a personal knowledge system.

INPUT: {thought}

OUTPUT: Return ONLY valid JSON:
{
  "destination": "people" | "projects" | "ideas" | "admin",
  "confidence": 0.0-1.0,
  "filename": "suggested-filename-kebab-case",
  "extracted": {
    // For people: name, context, follow_ups[]
    // For projects: name, status, next_action, notes
    // For ideas: title, oneliner
    // For admin: task, due_date (if mentioned), status
  }
}

RULES:
- "people": Mentions a specific person or follow-up with someone
- "projects": Multi-step work with a next action
- "ideas": Insights, possibilities, explorations
- "admin": One-off tasks, errands
- Always extract concrete next_action for projects (verb + object)
- If confidence < 0.6, still classify but it will be flagged for review
```

### Daily Digest
```bash
python3 ~/SecondBrain/_scripts/daily_digest.py
```
Generates morning summary from active projects and people with follow-ups, sends to Slack DM.

**What it does:**
1. Gathers active projects (status: active)
2. Finds people with follow_ups
3. Identifies stalled items
4. Generates digest (< 150 words)
5. Sends to user's Slack DM

**Digest structure:**
1. Top 3 actions for today (from projects)
2. One thing you might be avoiding (oldest/stalled)
3. People follow-ups (time-sensitive)

### Weekly Review
```bash
python3 ~/SecondBrain/_scripts/weekly_review.py
```
Generates weekly summary, sends to Slack DM on Sunday.

**What it does:**
1. Reads inbox logs from past 7 days
2. Gathers all active projects
3. Calculates stats by type
4. Generates review (< 250 words)
5. Sends to Slack DM

**Review structure:**
1. What you captured (breakdown by type)
2. Progress made (projects moved forward)
3. What's stuck (no recent activity)
4. One insight (pattern/theme)

### Fix Handler
```bash
python3 ~/SecondBrain/_scripts/fix_handler.py
```
Processes `fix:` commands in thread replies to reclassify items.

**Usage:**
Reply to any confirmation message in Slack thread:
```
fix: projects
```
Moves the file to the specified destination.

## Vault Structure

```
~/SecondBrain/
├── _inbox_log/              # Daily audit trail
│   └── YYYY-MM-DD.md
├── _templates/              # YAML templates
├── people/                  # Person notes
│   └── name.md
├── projects/                # Project notes
│   └── project-name.md
├── ideas/                   # Idea notes
│   └── idea-title.md
├── admin/                   # Task notes
│   └── task-name.md
├── daily/                   # Daily digests (optional)
└── weekly/                  # Weekly reviews (optional)
```

## File Format

All files use YAML frontmatter:

**People:**
```yaml
---
type: person
name: John Doe
context: Met at conference
follow_ups:
  - Send follow-up email about project
last_touched: 2024-01-15
tags: []
---
```

**Projects:**
```yaml
---
type: project
name: Website Redesign
status: active
next_action: Review mockups with team
tags: []
created: 2024-01-10
---
```

**Ideas:**
```yaml
---
type: idea
title: Mobile App Concept
oneliner: App for tracking daily habits
tags: []
created: 2024-01-12
---
```

**Admin:**
```yaml
---
type: admin
task: Schedule dentist appointment
due_date: 2024-01-20
status: pending
created: 2024-01-15
---
```

## Environment Variables

Required:
- `SLACK_BOT_TOKEN`: Bot token from Slack app
- `SLACK_CHANNEL_ID`: Channel ID for `#sb-inbox`
- `SLACK_USER_ID`: Your user ID for DMs

## Integration Notes

- Replace `classify_thought()` placeholder in `process_inbox.py` with actual Claude API call
- Replace `generate_digest()` placeholder in `daily_digest.py` with Claude API call
- Replace `generate_review()` placeholder in `weekly_review.py` with Claude API call
- All scripts log to `_scripts/logs.txt` when run via cron

## Quick Reference

```bash
# Process inbox
claude "Run process_inbox.py to classify new Slack messages"

# Daily digest
claude "Generate my daily digest from SecondBrain vault"

# Weekly review
claude "Generate my weekly review"

# Fix handler
claude "Process fix commands in Slack threads"
```
