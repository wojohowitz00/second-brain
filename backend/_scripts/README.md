# Second Brain Scripts

Scripts for processing Slack inbox messages and managing Obsidian vault.

## Setup

1. **Create Slack App:**
   - Go to https://api.slack.com/apps
   - Create new app, install to workspace
   - Add bot scopes: `channels:history`, `chat:write`, `im:write`
   - Copy bot token (starts with `xoxb-`)

2. **Get Channel and User IDs:**
   - Create private channel `#sb-inbox`
   - Right-click channel → View channel details → Copy channel ID (starts with `C`)
   - Right-click your profile → Copy user ID (starts with `U`)

3. **Set Environment Variables:**
```bash
export SLACK_BOT_TOKEN="xoxb-your-token"
export SLACK_CHANNEL_ID="C0123..."
export SLACK_USER_ID="U0123..."
```

4. **Move vault to home directory:**
```bash
mv second_brain ~/SecondBrain
```

5. **Install dependencies:**
```bash
pip install requests pyyaml
```

## Scripts

### `process_inbox.py`
Fetches new Slack messages, classifies them, writes to Obsidian.

**Usage:**
```bash
python3 ~/SecondBrain/_scripts/process_inbox.py
```

**Note:** The `classify_thought()` function is a placeholder. In Claude Code, replace it with actual Claude API call using the `CLASSIFICATION_PROMPT`.

### `daily_digest.py`
Generates morning digest from active projects/people, sends to Slack DM.

**Usage:**
```bash
python3 ~/SecondBrain/_scripts/daily_digest.py
```

**Schedule:** Run at 7 AM daily via cron or Claude Code.

### `weekly_review.py`
Generates weekly summary, sends to Slack DM.

**Usage:**
```bash
python3 ~/SecondBrain/_scripts/weekly_review.py
```

**Schedule:** Run Sunday at 4 PM.

### `fix_handler.py`
Processes `fix:` commands in thread replies to reclassify items.

**Usage:**
```bash
python3 ~/SecondBrain/_scripts/fix_handler.py
```

## Cron Setup

Add to `crontab -e`:

```cron
# Process inbox every 15 minutes
*/15 * * * * cd ~/SecondBrain && python3 _scripts/process_inbox.py >> _scripts/logs.txt 2>&1

# Daily digest at 7 AM
0 7 * * * cd ~/SecondBrain && python3 _scripts/daily_digest.py >> _scripts/logs.txt 2>&1

# Weekly review Sunday at 4 PM
0 16 * * 0 cd ~/SecondBrain && python3 _scripts/weekly_review.py >> _scripts/logs.txt 2>&1

# Process fix commands every hour
0 * * * * cd ~/SecondBrain && python3 _scripts/fix_handler.py >> _scripts/logs.txt 2>&1
```

## Claude Code Integration

Create `~/.claude/skills/second-brain/SKILL.md` (see `SKILL.md` in this directory).

Then use:
```bash
claude "Process my second brain inbox"
claude "Generate my daily digest"
claude "Run weekly review"
```

## Classification

The classification prompt expects Claude to return JSON:
```json
{
  "destination": "people" | "projects" | "ideas" | "admin",
  "confidence": 0.0-1.0,
  "filename": "kebab-case-name",
  "extracted": {
    // Type-specific fields
  }
}
```

## Troubleshooting

- **"Operation not permitted"**: Make sure vault is in `~/SecondBrain` (home directory)
- **Slack API errors**: Check token and channel/user IDs are correct
- **Classification fails**: Replace `classify_thought()` placeholder with actual Claude API call
- **Files not found**: Check that Obsidian vault folders exist
