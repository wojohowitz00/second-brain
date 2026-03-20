# Architecture

**Analysis Date:** 2026-01-30

## Pattern Overview

**Overall:** Event-driven pipeline with classification, routing, and state management. A unified codebase supporting multiple client platforms (backend processing, iOS app) connected through Slack webhook ingestion and Obsidian vault output.

**Key Characteristics:**
- Event-driven processing triggered by Slack messages
- Polling-based collection with cron-scheduled workers
- Three-stage pipeline: fetch → classify → write
- Decoupled layers with clear separation of concerns
- State management for idempotency and message tracking
- Local-first (macOS) with no central server

## Layers

**Slack Integration Layer:**
- Purpose: Fetch messages from Slack and send replies/DMs
- Location: `backend/_scripts/slack_client.py`
- Contains: HTTP client with retry logic, rate limit handling, API wrappers for conversation history/replies/DMs
- Depends on: `requests` library, environment variables for credentials
- Used by: `process_inbox.py`, `fix_handler.py`, `health_check.py`, `daily_digest.py`, `weekly_review.py`

**Processing/Classification Layer:**
- Purpose: Classify thoughts and determine routing destination
- Location: `backend/_scripts/process_inbox.py` (main orchestrator)
- Contains: Message processing loop, Claude classification invocation, Obsidian writing, logging
- Depends on: `slack_client`, `state`, `schema`, `wikilinks`, Claude API (via Claude Code runtime)
- Used by: Cron scheduling

**State Management Layer:**
- Purpose: Track processed messages, maintain idempotency, map messages to files
- Location: `backend/_scripts/state.py`
- Contains: Atomic JSON read/write with file locking, message-to-file mapping, processed message tracking, run health records
- Depends on: `fcntl` (file locking), filesystem operations
- Used by: `process_inbox.py`, `fix_handler.py`, `health_check.py`

**Validation Layer:**
- Purpose: Validate classification responses from Claude and provide fallbacks
- Location: `backend/_scripts/schema.py`
- Contains: Classification schema validation, entity type validation, fallback classification generation
- Depends on: `typing` module, regex
- Used by: `process_inbox.py`

**Wikilink Generation Layer:**
- Purpose: Extract and auto-link entities (people, projects) mentioned in text
- Location: `backend/_scripts/wikilinks.py`
- Contains: Entity extraction, stub file creation, wikilink insertion into markdown
- Depends on: filesystem operations, Path utilities
- Used by: `process_inbox.py`

**Correction Layer:**
- Purpose: Handle user corrections via "fix:" replies in Slack threads
- Location: `backend/_scripts/fix_handler.py`
- Contains: Thread monitoring, file relocation, metadata update logic
- Depends on: `slack_client`, `state`, filesystem operations
- Used by: Cron scheduling

**Health Monitoring Layer:**
- Purpose: Track system health and alert on failures
- Location: `backend/_scripts/health_check.py`
- Contains: Run history checking, failure detection, DM alerting
- Depends on: `state`, `slack_client`
- Used by: Cron scheduling

**Digest/Review Layer:**
- Purpose: Generate summaries and weekly reviews
- Location: `backend/_scripts/daily_digest.py`, `weekly_review.py`
- Contains: Obsidian vault scanning, markdown aggregation, Slack DM sending
- Depends on: `slack_client`, filesystem operations
- Used by: Cron scheduling (or manual invocation)

**iOS Application Layer:**
- Purpose: Native iOS client for Second Brain (initial development)
- Location: `ios/SecondBrain/`
- Contains: SwiftUI UI components, app lifecycle management
- Depends on: SwiftUI framework, iOS SDK
- Used by: iOS users

## Data Flow

**Inbound Processing (Every 2 minutes):**

1. **Slack Poll** (`fetch_messages`) → Query `conversations.history` API since last processed timestamp
2. **Idempotency Check** (`is_message_processed`) → Skip if message already processed via state mapping
3. **Skip Corrections** → Filter out "fix:" commands (handled separately by `fix_handler.py`)
4. **Classification** (`classify_thought`) → Invoke Claude to classify thought into destination category
5. **Validation** (`validate_classification`) → Ensure response matches schema, apply fallback if invalid
6. **Obsidian Write** (`write_to_obsidian`) → Create markdown file with YAML frontmatter in appropriate folder
7. **Entity Linking** (`process_linked_entities`) → Create stub files for mentioned people/projects
8. **Wikilink Insertion** (`insert_wikilinks`) → Replace entity names with `[[wikilinks]]` in body text
9. **Daily Note Append** (`append_to_daily_note`) → Add entry to `daily/{YYYY-MM-DD}.md` with timestamp
10. **Inbox Log** (`log_to_inbox_log`) → Append row to `_inbox_log/{YYYY-MM-DD}.md` for audit trail
11. **State Update** (`mark_message_processed`, `set_file_for_message`) → Record message TS and mapped file path
12. **Slack Reply** (`reply_to_message`) → Send confirmation with destination, filename, and confidence score
13. **Last TS Update** → Store `ts` in `.last_processed_ts` to avoid re-polling

**Correction Flow (Every 5 minutes):**

1. **Fetch Corrections** → Query threads in channel for messages starting with "fix:"
2. **Lookup Original** (`get_file_for_message`) → Find file created from the original message
3. **Move File** → Relocate file to corrected destination folder
4. **Update Mapping** (`update_file_location`) → Record new file path in state
5. **Update Frontmatter** → Rewrite YAML with new type/context
6. **Slack Reply** → Confirm reclassification

**Health Check Flow (Every hour):**

1. **Check Last Run** (`get_last_successful_run`) → Compare timestamp to threshold (5 minutes)
2. **Count Failures** (`get_failed_count_today`) → Look at failed run log for today
3. **Send Alert** → DM user if system hasn't run recently or too many failures
4. **Log Results** → Append to state's run history

**State Management:**

- **Processed Messages:** Stored in `.state/processed_messages.json` with TTL (cleanup after 30 days)
- **Message-to-File Mapping:** `.state/message_mapping.json` tracks which Slack TS maps to which vault file
- **Run History:** `.state/run_history.json` logs success/failure with timestamps for health checks
- **Dead Letter Queue:** `_inbox_log/FAILED-{YYYY-MM-DD}.md` stores messages that failed processing

## Key Abstractions

**Message:**
- Represents: Single Slack message from `#wry_sb`
- Examples: Text posts, threaded replies, corrections
- Pattern: Fetched as dict with `text`, `ts` (timestamp), `user` fields

**Classification:**
- Represents: Routing decision and extracted metadata
- Examples: `{"destination": "people", "confidence": 0.95, "filename": "sarah", "extracted": {...}, "linked_entities": [...]}`
- Pattern: Validated dict with required fields for YAML frontmatter generation

**Entity:**
- Represents: A person or project mentioned in text
- Examples: `{"name": "Sarah Chen", "type": "people"}` or `{"name": "Q2 Roadmap", "type": "projects"}`
- Pattern: Used for automatic wikilink generation, stub creation

**Vault File:**
- Represents: Markdown file written to Obsidian vault
- Examples: `~/SecondBrain/people/sarah.md`, `~/SecondBrain/projects/q2-roadmap.md`
- Pattern: YAML frontmatter (type, metadata) + body content with wikilinks

## Entry Points

**process_inbox.py:**
- Location: `backend/_scripts/process_inbox.py`
- Triggers: Cron job every 2 minutes, manual invocation via `uv run`
- Responsibilities: Main processing loop, orchestrates all downstream operations, handles errors with dead letter logging

**fix_handler.py:**
- Location: `backend/_scripts/fix_handler.py`
- Triggers: Cron job every 5 minutes
- Responsibilities: Monitor threads for "fix:" corrections, move files, update state

**health_check.py:**
- Location: `backend/_scripts/health_check.py`
- Triggers: Cron job every hour
- Responsibilities: Monitor system health, send alerts for failures

**daily_digest.py:**
- Location: `backend/_scripts/daily_digest.py`
- Triggers: Manual (morning ritual) or scheduled daily
- Responsibilities: Scan vault, generate morning summary, send via Slack DM

**weekly_review.py:**
- Location: `backend/_scripts/weekly_review.py`
- Triggers: Manual (weekly ritual) or scheduled weekly
- Responsibilities: Scan week's captures, generate insights, send via Slack DM

**SecondBrainApp.swift:**
- Location: `ios/SecondBrain/SecondBrainApp.swift`
- Triggers: User launches iOS app
- Responsibilities: App lifecycle, scene setup, initial navigation

## Error Handling

**Strategy:** Fail-safe with logging and alerts. Low confidence messages are held for review rather than auto-filed. Catastrophic failures trigger DM alerts.

**Patterns:**

1. **Validation Errors** → Caught by `try/except ValidationError`, fallback to ideas classification with low confidence (0.5)
2. **Slack API Errors** → Caught by `try/except SlackAPIError`, retry with exponential backoff (max 3 retries), log to dead letter
3. **File Write Errors** → Caught by exception handler in `process_message`, appends timestamp to filename if file exists
4. **Network Errors** → Handled by `_request_with_retry` with exponential backoff (1s → 30s max)
5. **Rate Limiting (429)** → Extracted from response headers, sleep and retry
6. **Catastrophic Failure** → Caught by outer exception handler in `process_all`, records to run history, sends DM alert

**Dead Letter Queue:** Failed messages are logged to `_inbox_log/FAILED-{YYYY-MM-DD}.md` with full error traceback for manual review.

**Fallback Classification:**
```python
{
    "destination": "ideas",
    "confidence": 0.5,
    "filename": "needs-review-{timestamp}",
    "extracted": {"title": "[Original text]", "oneliner": "[Error details]"},
    "linked_entities": []
}
```

## Cross-Cutting Concerns

**Logging:**
- Console output from scripts (captured by cron to `/tmp/wry_sb.log`)
- Markdown audit logs: `_inbox_log/{YYYY-MM-DD}.md` (table format), `_inbox_log/FAILED-{YYYY-MM-DD}.md` (traceback)
- State logs: `run_history.json` tracks all runs with timestamps

**Validation:**
- Schema validation in `schema.py` prevents crashes from malformed Claude responses
- Fallback classification for validation failures
- Atomic JSON operations with file locking in `state.py` prevent corruption from concurrent access

**Authentication:**
- Environment variables: `SLACK_BOT_TOKEN`, `SLACK_CHANNEL_ID`, `SLACK_USER_ID`
- Loaded from `.env` file in `_scripts/` directory (not committed)
- All Slack API calls use Bearer token from `SLACK_BOT_TOKEN`

**Idempotency:**
- Message timestamps used as unique identifiers
- `processed_messages.json` tracks which timestamps have been handled
- Re-running script doesn't duplicate files or messages
- State cleanup removes entries older than 30 days

**Concurrency:**
- File locking (fcntl) used in atomic JSON operations to prevent race conditions
- Cron jobs run independently with separate entry points (no shared state issues)
- Last processed timestamp prevents re-polling old messages

---

*Architecture analysis: 2026-01-30*
