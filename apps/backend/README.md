# Second Brain System

A personal knowledge capture system that automatically classifies thoughts from Slack and stores them in Obsidian with full knowledge graph integration.

## How It Works

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   Slack     │────▶│  Processing  │────▶│  Obsidian   │
│  #wry_sb  │     │   Scripts    │     │   Vault     │
└─────────────┘     └──────────────┘     └─────────────┘
      │                    │                    │
      │                    ▼                    │
      │            ┌──────────────┐             │
      │            │    Claude    │             │
      │            │Classification│             │
      │            └──────────────┘             │
      │                    │                    │
      └────────────────────┴────────────────────┘
             Slack replies with confirmation
```

1. Post thoughts to `#wry_sb` Slack channel
2. Scripts poll for new messages every 2 minutes
3. Claude classifies each thought (people/projects/ideas/admin)
4. Markdown file created in Obsidian with frontmatter
5. Wikilinks auto-generated for mentioned entities
6. Slack reply confirms filing with confidence score

## Requirements

### macOS
- macOS 10.15 or later
- Python 3.9+
- uv (install with: `curl -LsSf https://astral.sh/uv/install.sh | sh`)
- Obsidian (free download from obsidian.md)

### Slack App
You'll need to create a Slack app with these OAuth scopes:
- `channels:history` - Read messages from channels
- `channels:read` - Access channel info
- `chat:write` - Post replies
- `im:write` - Send DM alerts

### Obsidian Plugins
- **Dataview** (required for dashboard) - Install from Community Plugins

## Installation

### Quick Start

```bash
# Clone or download this repository
git clone <repo-url> ~/second-brain-setup
cd ~/second-brain-setup

# Run setup script
chmod +x setup.sh
./setup.sh
```

### Manual Installation

1. **Create vault structure**
   ```bash
   mkdir -p ~/SecondBrain/{people,projects,ideas,admin,daily,_inbox_log,_scripts/.state}
   ```

2. **Copy scripts**
   ```bash
   cp _scripts/*.py ~/SecondBrain/_scripts/
   cp _scripts/requirements.txt ~/SecondBrain/_scripts/
   ```

3. **Install dependencies**
   ```bash
   cd ~/second-brain-setup/backend
   uv sync
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your Slack credentials
   ```

## Slack App Setup

1. Go to [api.slack.com/apps](https://api.slack.com/apps)
2. Click "Create New App" → "From scratch"
3. Name it "Second Brain" and select your workspace
4. Go to **OAuth & Permissions** and add these scopes:
   - `channels:history`
   - `channels:read`
   - `chat:write`
   - `im:write`
5. Click "Install to Workspace"
6. Copy the **Bot User OAuth Token** (starts with `xoxb-`)
7. Create a channel called `#wry_sb`
8. Invite your bot to the channel: `/invite @SecondBrain`

### Finding Your IDs

**Channel ID:**
- Right-click `#wry_sb` → "View channel details"
- Scroll to bottom, copy the ID (starts with `C`)

**User ID:**
- Click your profile picture → "Profile"
- Click "..." → "Copy member ID" (starts with `U`)

## Configuration

Edit `~/SecondBrain/_scripts/.env`:

```bash
export SLACK_BOT_TOKEN="xoxb-your-token-here"
export SLACK_CHANNEL_ID="C0123456789"
export SLACK_USER_ID="U0123456789"
```

## Automation (Cron Jobs)

Add these to your crontab (`crontab -e`):

```cron
# Process inbox every 2 minutes
*/2 * * * * cd ~/second-brain-setup/backend && source _scripts/.env && uv run _scripts/process_inbox.py >> /tmp/wry_sb.log 2>&1

# Health check every hour
0 * * * * cd ~/second-brain-setup/backend && source _scripts/.env && uv run _scripts/health_check.py --quiet >> /tmp/sb-health.log 2>&1

# Process fix commands every 5 minutes
*/5 * * * * cd ~/second-brain-setup/backend && source _scripts/.env && uv run _scripts/fix_handler.py >> /tmp/sb-fix.log 2>&1
```

## Usage

### Capturing Thoughts

Post to `#wry_sb`:
```
Had a great call with Sarah about the Q2 roadmap.
She mentioned we should prioritize the mobile app.
Next step: Schedule follow-up for next Tuesday.
```

The system will:
1. Classify this as "people" (mentions Sarah)
2. Create `~/SecondBrain/people/sarah.md`
3. Extract follow-ups and next actions
4. Create wikilinks: `[[sarah]]`, `[[q2-roadmap]]`
5. Reply in Slack with confirmation

### Correcting Mistakes

If the classification is wrong, reply in the thread:
```
fix: projects
```

This moves the file to the correct folder and updates the mapping.

### Prefixes (Optional)

For explicit classification, use prefixes:
```
person: Met John at the conference
project: Website redesign - need to finalize colors
idea: What if we automated the reporting?
admin: Renew domain name before Friday
```

## File Structure

```
~/SecondBrain/
├── dashboard.md          # Dataview dashboard (open in Obsidian)
├── people/               # Person notes
│   ├── sarah.md
│   └── john-smith.md
├── projects/             # Project notes
│   ├── website-redesign.md
│   └── q2-roadmap.md
├── ideas/                # Ideas and insights
├── admin/                # Tasks and errands
├── daily/                # Daily notes with captures
│   └── 2026-01-09.md
├── _inbox_log/           # Processing logs
│   ├── 2026-01-09.md
│   └── FAILED-2026-01-09.md
└── _scripts/             # Processing scripts
    ├── .state/           # State files (don't edit)
    ├── .env              # Your credentials
    ├── process_inbox.py  # Main processing
    ├── fix_handler.py    # Handle corrections
    ├── health_check.py   # Monitoring
    ├── slack_client.py   # Slack API wrapper
    ├── state.py          # State management
    ├── schema.py         # Validation
    └── wikilinks.py      # Link generation
```

## Obsidian Setup

1. Open Obsidian
2. "Open folder as vault" → Select `~/SecondBrain`
3. Go to Settings → Community Plugins → Browse
4. Search "Dataview" and install it
5. Enable Dataview in Community Plugins
6. Open `dashboard.md` for your live overview

### Recommended Plugins

- **Dataview** (required) - Live queries for your dashboard
- **Calendar** - Navigate daily notes by date
- **Graph Analysis** - Enhanced graph view

## Dashboard

The dashboard (`dashboard.md`) shows:
- Active projects with next actions
- Stale projects (not touched in 14+ days)
- People with pending follow-ups
- Recent captures (last 7 days)
- Stub files needing details
- Orphan notes (no backlinks)
- Pending admin tasks

## Troubleshooting

### Check Logs
```bash
# Recent processing
tail -50 /tmp/wry_sb.log

# Health check output
tail -20 /tmp/sb-health.log

# Fix command processing
tail -20 /tmp/sb-fix.log
```

### Manual Health Check
```bash
cd ~/second-brain-setup/backend
source _scripts/.env
uv run _scripts/health_check.py
```

### Common Issues

**"No new messages"**
- Check cron is running: `crontab -l`
- Verify bot is in channel: `/invite @SecondBrain`
- Check token in `.env`

**"Slack API error: not_in_channel"**
- Invite bot to channel: `/invite @SecondBrain`

**Dashboard not working**
- Install Dataview plugin in Obsidian
- Enable it in Settings → Community Plugins

**Files not linking**
- Check `aliases` field in person files
- Aliases are case-insensitive

## Security Notes

- Never commit `.env` to version control
- Bot token gives access to channel history
- State files contain message timestamps (not content)
- All data stays local on your Mac

## Scripts Reference

| Script | Purpose | Run Frequency |
|--------|---------|---------------|
| `process_inbox.py` | Fetch and classify new messages | Every 2 min |
| `fix_handler.py` | Process "fix:" corrections | Every 5 min |
| `health_check.py` | Monitor system health | Every hour |
| `daily_digest.py` | Generate morning summary | Manual/daily |
| `weekly_review.py` | Generate weekly review | Manual/weekly |

## License

MIT License - Use freely for personal knowledge management.
