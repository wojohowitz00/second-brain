# Second Brain System - Implementation Plan

## Overview

Building a robust Second Brain system that captures thoughts from Slack, classifies them with Claude, and stores them in Obsidian with full graph/linking capabilities.

---

## Phase 1: Critical Reliability Fixes ✅ COMPLETE

High-impact, low-complexity fixes to make the system reliable.

### 1.1 Message-to-File Mapping ✅
- [x] Create `.message_mapping.json` to track `{message_ts: filepath}`
- [x] Update `process_inbox.py` to write mapping on every successful file write
- [x] Update `fix_handler.py` to use mapping instead of log parsing

### 1.2 Idempotency Check ✅
- [x] Add `.processed_messages.json` to track processed message IDs
- [x] Check before processing to skip duplicates
- [x] Clean up old entries (>30 days) to prevent unbounded growth

### 1.3 Error Handling + Dead Letter Queue ✅
- [x] Wrap classification in try/except
- [x] Create `_inbox_log/FAILED-{date}.md` for failed items
- [x] Add retry logic with exponential backoff
- [x] Send alert to Slack DM on repeated failures

### 1.4 JSON Schema Validation ✅
- [x] Define schema for classification response
- [x] Validate Claude's response before using
- [x] Fallback to "ideas" category if invalid

### 1.5 Basic Health Check Script ✅
- [x] Create `health_check.py`
- [x] Verify last successful run < 1 hour ago
- [x] Check for stuck/failed items
- [x] Send alert if unhealthy

### 1.6 Network Retry Logic ✅
- [x] Create shared `slack_client.py` module
- [x] Wrap all `requests` calls with retry logic
- [x] Handle Slack rate limits (429)

---

## Phase 2: Obsidian Integration ✅ COMPLETE

Leverage Obsidian's unique capabilities for knowledge graphs.

### 2.1 Wikilink Generation ✅
- [x] Update classification prompt to extract `linked_entities`
- [x] Transform mentions to `[[wikilinks]]` in captured text
- [x] Create stub files for new people/projects mentioned

### 2.2 Dataview Dashboard ✅
- [x] Create `dashboard.md` with Dataview queries
- [x] Active projects, stale items, orphan notes
- [x] Replace Python digest with live Obsidian view

### 2.3 Daily Notes Integration ✅
- [x] Use Obsidian daily note format for logs
- [x] Append captures to daily note instead of separate log

### 2.4 Aliases for People ✅
- [x] Add `aliases` field to person template
- [x] Update classification to check existing aliases

---

## Architecture Decisions

### Why NOT webhooks
- Adds infrastructure complexity (ngrok, always-on)
- 2-minute polling is sufficient for personal use

### Why NOT SQLite
- Obsidian can't read SQLite
- JSON files are human-readable and debuggable

### Why JSON for state
- Atomic reads/writes
- Structured data
- Easy debugging

---

## Review - Phase 1 Complete

**Date:** 2026-01-09

### Files Created/Modified

| File | Purpose |
|------|---------|
| `_scripts/slack_client.py` | Shared Slack API client with retry logic |
| `_scripts/state.py` | State management (mapping, idempotency, health) |
| `_scripts/schema.py` | Classification validation and sanitization |
| `_scripts/health_check.py` | Health monitoring script |
| `_scripts/process_inbox.py` | Updated with all reliability features |
| `_scripts/fix_handler.py` | Updated to use message mapping |
| `_scripts/daily_digest.py` | Updated to use shared client |
| `_scripts/weekly_review.py` | Updated to use shared client |

### Architecture Summary

```
_scripts/
├── slack_client.py    # Retry-wrapped Slack API
├── state.py           # JSON state files in .state/
├── schema.py          # Validation + sanitization
├── health_check.py    # Monitoring (run via cron)
├── process_inbox.py   # Main processing (uses all above)
├── fix_handler.py     # Handle fix: commands
├── daily_digest.py    # Morning digest
└── weekly_review.py   # Weekly summary

.state/
├── message_mapping.json     # ts -> filepath
├── processed_messages.json  # idempotency
└── last_run.json           # health status
```

### What's Robust Now

1. **No message loss** - Idempotency check prevents duplicates
2. **Fix commands work** - Direct ts -> filepath mapping
3. **Errors don't crash** - Dead letter queue captures failures
4. **Network resilience** - Automatic retry with backoff
5. **Bad data handled** - Schema validation with fallbacks
6. **Monitoring** - Health check + alerts on failure

### Next Steps

~~Phase 2: Obsidian Integration~~ ✅ COMPLETE

---

## Review - Phase 2 Complete

**Date:** 2026-01-09

### Files Created/Modified

| File | Purpose |
|------|---------|
| `_scripts/wikilinks.py` | NEW: Entity linking and stub file creation |
| `_scripts/schema.py` | Updated: Added linked_entities validation |
| `_scripts/process_inbox.py` | Updated: Wikilink insertion, daily notes, aliases |
| `~/SecondBrain/dashboard.md` | NEW: Dataview dashboard in vault |

### Key Features Added

1. **Wikilinks** - Entities mentioned in captures are auto-linked with `[[]]`
2. **Stub Files** - New people/projects get auto-created stub files with `#stub` tag
3. **Dataview Dashboard** - Live queries for active projects, stale items, orphans
4. **Daily Notes** - Captures appended to `daily/YYYY-MM-DD.md` with wikilinks
5. **Alias Matching** - People can have nicknames that resolve to main file

### Architecture Summary

```
_scripts/
├── wikilinks.py       # NEW: Entity linking + stubs
├── schema.py          # linked_entities validation
├── process_inbox.py   # Wikilinks + daily notes
└── ...

~/SecondBrain/
├── dashboard.md       # Dataview queries
├── daily/             # Daily notes with captures
├── people/            # Person files with aliases
└── projects/          # Project files
```

### What's Connected Now

1. **Knowledge Graph** - Captured entities create links between notes
2. **No Orphans** - Dashboard surfaces unlinked notes
3. **Daily Context** - Each day's captures visible in one place
4. **Name Flexibility** - "John" matches "John Smith" via aliases

### Implementation Complete

Both Phase 1 (reliability) and Phase 2 (Obsidian integration) are now complete.
The system is production-ready for personal use.
