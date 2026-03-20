# Technology Stack

**Analysis Date:** 2026-01-30

## Languages

**Primary:**
- Python 3.9+ - Backend automation scripts, message processing, classification validation
- Swift - iOS app (initial development phase)

**Secondary:**
- Markdown - Obsidian vault files (output format)
- Bash - Setup and cron scripts

## Runtime

**Environment:**
- Python 3.13 (active development environment)
- macOS 10.15+ (primary deployment target)

**Package Manager:**
- `uv` (Astral's modern Python package manager) - Primary management
- Lockfile: `uv.lock` (present, ensures reproducible builds)

## Frameworks

**Core:**
- No web framework - Pure Python CLI scripts
- `requests` 2.28.0+ - HTTP client for Slack API with connection pooling
- `pyyaml` 6.0+ - YAML parsing for Obsidian frontmatter

**Testing:**
- Not yet implemented (no test framework configured)

**Build/Dev:**
- `hatchling` - Build backend (defined in `pyproject.toml`)
- `uv` - Environment and dependency management

## Key Dependencies

**Critical:**
- `requests` - Core HTTP library for Slack API integration, retry logic, rate limit handling
- `pyyaml` - YAML frontmatter parsing in Obsidian files

**Standard Library Only:**
- `os` - Environment variable access
- `pathlib` - File system operations
- `json` - State file serialization
- `fcntl` - File locking for atomic state operations
- `datetime` - Timestamp handling
- `re` - Text validation and sanitization
- `typing` - Type hints

## Configuration

**Environment:**
- Sourced via `source _scripts/.env` (bash)
- Three required variables:
  - `SLACK_BOT_TOKEN` - Bot user OAuth token (xoxb-*)
  - `SLACK_CHANNEL_ID` - Target channel ID (C*)
  - `SLACK_USER_ID` - User ID for DMs (U*)
- Reference: `.env.example` in `backend/_scripts/`

**Build:**
- `pyproject.toml` - Single source of truth for dependencies and build config
- No separate requirements.txt (deprecated in favor of pyproject.toml)
- Historical reference: `backend/_scripts/requirements.txt` (for pip compatibility)

## Platform Requirements

**Development:**
- macOS 10.15+
- Python 3.9+ (tested with 3.13)
- `uv` package manager installed
- Obsidian (free) for vault visualization

**Production:**
- macOS deployment (local cron jobs)
- Slack workspace with bot token
- Local filesystem with SecondBrain vault at `~/SecondBrain/`

**iOS Development:**
- Xcode 15+
- iOS 15+ target deployment

## Runtime Configuration

**Scripts Location:**
- `backend/_scripts/*.py` - All automation scripts

**State Location:**
- `~/SecondBrain/_scripts/.state/` - Atomic JSON state files
  - `message_mapping.json` - Message TS to file path mapping
  - `processed_messages.json` - Idempotency tracking
  - `last_run.json` - Health check data

**Vault Location:**
- `~/SecondBrain/` - Obsidian vault root

## Cron Execution

All scripts run via `uv run` from `backend/` directory with `source _scripts/.env`:

```
*/2 * * * * cd ~/second-brain-setup/backend && source _scripts/.env && uv run _scripts/process_inbox.py
*/5 * * * * cd ~/second-brain-setup/backend && source _scripts/.env && uv run _scripts/fix_handler.py
0 * * * * cd ~/second-brain-setup/backend && source _scripts/.env && uv run _scripts/health_check.py
```

---

*Stack analysis: 2026-01-30*
