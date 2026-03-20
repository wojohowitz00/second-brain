# External Integrations

**Analysis Date:** 2026-01-30

## APIs & External Services

**Slack:**
- Primary messaging platform for knowledge capture
- SDK/Client: `slack_client.py` wraps raw `requests` library (no SDK)
- Auth: Bearer token via `SLACK_BOT_TOKEN` environment variable
- Scopes required:
  - `channels:history` - Read messages from channels
  - `channels:read` - Access channel info
  - `chat:write` - Post replies and DMs
  - `im:write` - Send direct messages
- Key endpoints:
  - `conversations.history` - Fetch messages from inbox channel
  - `conversations.replies` - Fetch thread replies
  - `chat.postMessage` - Post messages and replies
  - `conversations.open` - Open DM channels for alerts

**Claude API:**
- Classification of thoughts (destinaton: people/projects/ideas/admin)
- Note: Called via Claude Code invocation layer (not direct API call from scripts)
- Classification prompt defined in `backend/_scripts/process_inbox.py` (lines 48-80)

## Data Storage

**Databases:**
- None - System uses local file storage only

**File Storage:**
- **Local Obsidian Vault** - Primary storage
  - Location: `~/SecondBrain/`
  - Format: Markdown files with YAML frontmatter
  - Directories:
    - `people/` - Person notes
    - `projects/` - Project notes
    - `ideas/` - Ideas and insights
    - `admin/` - Tasks and errands
    - `daily/` - Daily notes (YYYY-MM-DD.md)
    - `_inbox_log/` - Processing logs and dead letter queue

**Caching:**
- None - Stateless on each run

## State Management

**State Persistence:**
- Location: `~/SecondBrain/_scripts/.state/` (atomic JSON files with fcntl locking)
- `message_mapping.json` - Maps Slack message TS to created file path
- `processed_messages.json` - Tracks processed message timestamps (idempotency)
- `last_run.json` - Last success/failure timestamps and status
- YAML frontmatter stored in Markdown files (timestamps, metadata)

## Authentication & Identity

**Auth Provider:**
- Custom token-based (Slack Bot Token)
- Environment-sourced: `SLACK_BOT_TOKEN`
- No identity federation or OAuth flow

**User Identification:**
- Slack User ID: `SLACK_USER_ID` for DM alerts
- Channel ID: `SLACK_CHANNEL_ID` for inbox monitoring

## Monitoring & Observability

**Error Tracking:**
- Dead letter queue: `~/SecondBrain/_inbox_log/FAILED-{date}.md`
- Failed messages logged with timestamp, text, error details, and traceback
- Implementation: `state.log_to_dead_letter()` in `backend/_scripts/state.py` (lines 228-275)

**Logs:**
- File-based logs (no centralized service)
- Locations:
  - `/tmp/wry_sb.log` - process_inbox.py output (cron redirect)
  - `/tmp/sb-health.log` - health_check.py output (cron redirect)
  - `/tmp/sb-fix.log` - fix_handler.py output (cron redirect)
- Daily inbox logs: `~/SecondBrain/_inbox_log/{date}.md` (markdown table format)
- Health check via `backend/_scripts/health_check.py` monitors last successful run

**Alerts:**
- Slack DMs when failures exceed threshold (3+ in one day)
- Critical error alerts sent via `send_dm()` on catastrophic failures
- Implementation: `backend/_scripts/process_inbox.py` lines 354-362, 373-379

## CI/CD & Deployment

**Hosting:**
- Local macOS deployment (no cloud hosting)
- Runs via user's crontab

**CI Pipeline:**
- None configured

**Deployment:**
- Local shell setup script: `backend/setup.sh`
- Manual installation via bash script or directory copying
- Cron job scheduling for automation

## Environment Configuration

**Required env vars:**
- `SLACK_BOT_TOKEN` - Slack bot OAuth token (xoxb-...)
- `SLACK_CHANNEL_ID` - Inbox channel ID (C...)
- `SLACK_USER_ID` - User ID for alerts (U...)

**Secrets location:**
- `.env` file in `backend/_scripts/` (git-ignored, must be manually created from `.env.example`)
- Sourced before each cron job execution: `source .env`
- Never committed to version control

## Webhooks & Callbacks

**Incoming:**
- None - System polls Slack API rather than using webhooks

**Outgoing:**
- Slack channel replies (in-thread confirmations)
- Slack DMs (user alerts)
- No external webhooks

## Slack API Integration Details

**Rate Limiting:**
- Handled by `_request_with_retry()` in `backend/_scripts/slack_client.py`
- Exponential backoff: starts at 1.0s, caps at 30.0s
- Max retries: 3 attempts
- Respects Slack 429 Retry-After header
- Implementation: lines 49-116

**Error Handling:**
- Custom exceptions: `SlackAPIError`, `SlackRateLimitError`
- All API calls wrap response in retry logic
- Timeout: 30 seconds per request
- HTTP 5xx errors trigger automatic retry

**Message Filtering:**
- Excludes bot messages (checks `bot_id` field)
- Excludes system messages
- Only processes messages with `type == "message"`

## Obsidian Integration

**File Writing:**
- YAML frontmatter generation based on destination type (people/projects/ideas/admin)
- Wikilinks auto-generated for mentioned entities via `process_linked_entities()`
- Daily note appended with capture reference
- Inbox log updated with classification result and confidence
- Implementation: `backend/_scripts/process_inbox.py` lines 103-186

**Required Obsidian Plugin:**
- Dataview (community plugin for dashboard queries)

---

*Integration audit: 2026-01-30*
