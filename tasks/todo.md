# Second Brain System - Implementation Plan

## Overview

Building a robust Second Brain system that captures thoughts from Slack, classifies them with Claude, and stores them in Obsidian with full graph/linking capabilities.

---

## Phase 1: Critical Reliability Fixes

High-impact, low-complexity fixes to make the system reliable.

### 1.1 Message-to-File Mapping
- [ ] Create `.message_mapping.json` to track `{message_ts: filepath}`
- [ ] Update `process_inbox.py` to write mapping on every successful file write
- [ ] Update `fix_handler.py` to use mapping instead of log parsing

### 1.2 Idempotency Check
- [ ] Add `.processed_messages.json` to track processed message IDs
- [ ] Check before processing to skip duplicates
- [ ] Clean up old entries (>30 days) to prevent unbounded growth

### 1.3 Error Handling + Dead Letter Queue
- [ ] Wrap classification in try/except
- [ ] Create `_inbox_log/FAILED-{date}.md` for failed items
- [ ] Add retry logic with exponential backoff (using tenacity)
- [ ] Send alert to Slack DM on repeated failures

### 1.4 JSON Schema Validation
- [ ] Define schema for classification response
- [ ] Validate Claude's response before using
- [ ] Fallback to "ideas" category if invalid

### 1.5 Basic Health Check Script
- [ ] Create `health_check.py`
- [ ] Verify last successful run < 1 hour ago
- [ ] Check for stuck/failed items
- [ ] Send alert if unhealthy

### 1.6 Network Retry Logic
- [ ] Add tenacity library dependency
- [ ] Wrap all `requests` calls with retry decorator
- [ ] Handle Slack rate limits (429)

---

## Phase 2: Obsidian Integration

Leverage Obsidian's unique capabilities for knowledge graphs.

### 2.1 Wikilink Generation
- [ ] Update classification prompt to extract `linked_entities`
- [ ] Transform mentions to `[[wikilinks]]` in captured text
- [ ] Create stub files for new people/projects mentioned

### 2.2 Dataview Dashboard
- [ ] Create `dashboard.md` with Dataview queries
- [ ] Active projects, stale items, orphan notes
- [ ] Replace Python digest with live Obsidian view

### 2.3 Daily Notes Integration
- [ ] Use Obsidian daily note format for logs
- [ ] Append captures to daily note instead of separate log

### 2.4 Aliases for People
- [ ] Add `aliases` field to person template
- [ ] Update classification to check existing aliases

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

## Review

_To be filled after implementation_
