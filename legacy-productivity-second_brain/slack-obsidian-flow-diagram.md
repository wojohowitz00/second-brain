---
category:
- '[[Coding with AI]]'
- '[[App Development]]'
- '[[Writing]]'
tags:
- personal
- projects
created: '2026-01-28'
updated: '2026-01-28'
---
# Slack → Obsidian Data Flow

## Architecture Overview

```
┌─────────────┐     ┌──────────────┐     ┌────────────────┐     ┌─────────────┐
│   Slack     │────▶│ process_inbox │────▶│ Claude API     │────▶│  Obsidian   │
│  #sb-inbox  │     │     .py       │     │ Classification │     │   Vault     │
└─────────────┘     └──────────────┘     └────────────────┘     └─────────────┘
                           │                      │                      │
                           │                      │                      │
                           ▼                      ▼                      ▼
                    ┌──────────────┐      ┌──────────────┐      ┌──────────────┐
                    │ State Files  │      │ Validation   │      │ Wikilinks    │
                    │ (tracking)   │      │ & Fallback   │      │ & Stubs      │
                    └──────────────┘      └──────────────┘      └──────────────┘
```

## Step-by-Step Flow

### 1. Message Reception
- **File**: `slack_client.py`
- **Function**: `fetch_messages(oldest=last_ts)`
- Fetches new messages from #sb-inbox since last run
- Stores last processed timestamp in `.last_processed_ts`

### 2. Idempotency Check
- **File**: `state.py`
- **Function**: `is_message_processed(ts)`
- Checks `processed_messages.json` (30-day TTL)
- Prevents duplicate processing if script runs multiple times

### 3. Classification (THE KEY STEP)
- **File**: `process_inbox.py`
- **Function**: `classify_thought(text)` → **NOW FIXED!**
- Calls Claude API with classification prompt
- Returns JSON:
```json
{
  "destination": "people|projects|ideas|admin",
  "confidence": 0.0-1.0,
  "filename": "kebab-case-name",
  "extracted": {
    "name": "...",
    "next_action": "...",
    ...
  },
  "linked_entities": [
    {"name": "Person Name", "type": "person"}
  ]
}
```

### 4. Validation
- **File**: `schema.py`
- **Function**: `validate_classification(raw_result)`
- Validates structure, sanitizes filename
- Falls back to "ideas" with 0.3 confidence if invalid
- Clamps confidence to 0.0-1.0 range

### 5. Confidence Gate
- **Threshold**: 0.6
- **If >= 0.6**: Proceed to file creation
- **If < 0.6**: Log only, ask user to repost with prefix

### 6. Wikilink Processing
- **File**: `wikilinks.py`
- **Function**: `process_linked_entities(linked_entities)`
- Searches vault for existing people/projects
- Creates stub files for new entities
- Returns wikilink map for text insertion

### 7. File Writing
- **File**: `process_inbox.py`
- **Function**: `write_to_obsidian(classification, text, timestamp)`
- Builds YAML frontmatter based on destination type
- Inserts wikilinks into body and original capture
- Writes to `~/SecondBrain/{destination}/{filename}.md`
- Handles duplicates by appending timestamp

### 8. Logging & Tracking
- **Inbox Log**: `_inbox_log/YYYY-MM-DD.md`
  - Daily audit trail with confidence scores
  - Flags items with confidence < 0.6 as "NEEDS REVIEW"
- **Daily Note**: `daily/YYYY-MM-DD.md`
  - Appends capture entry with wikilink
- **Message Mapping**: `message_mapping.json`
  - Maps Slack timestamp → Obsidian filepath
  - Used by `fix:` commands to relocate files

### 9. Slack Reply
- **Success (conf >= 0.6)**:
```
✓ Filed to *projects* as `my-project.md`
Confidence: 95%
_Reply `fix: people|projects|ideas|admin` if wrong_
```

- **Low Confidence (conf < 0.6)**:
```
⚠️ Not sure where this goes (confidence: 50%)
Please repost with a prefix like:
• `person: ...`
• `project: ...`
```

### 10. Error Handling
- **Dead Letter Queue**: `_inbox_log/FAILED-YYYY-MM-DD.md`
  - Logs failures with full error traces
  - Alerts via Slack DM if 3+ failures in one day
- **Health Monitoring**: `health_check.py`
  - Tracks last successful run
  - Sends alerts if system hasn't run in 60+ minutes

---

## File Structure Created

```
~/SecondBrain/
├── people/
│   └── john-doe.md          ← Person notes
├── projects/
│   └── my-project.md        ← Project with next_action
├── ideas/
│   └── interesting-idea.md  ← Insights and possibilities
├── admin/
│   └── todo-task.md         ← One-off tasks
├── daily/
│   └── 2026-01-14.md        ← Daily note with capture log
└── _inbox_log/
    ├── 2026-01-14.md        ← Audit trail
    └── FAILED-2026-01-14.md ← Error log
```

### Example File Output

**projects/customer-acquisition.md**:
```yaml
---
type: project
name: Customer Acquisition Strategy
status: active
next_action: draft new customer acquisition approach
tags: []
created: 2026-01-13
---

Part of broader [[business-strategy]] initiative.

## Original Capture

> project: [[customer-acquisition-strategy]]. draft new prompt for customer acquisition
```

---

## What I Fixed

1. **Replaced placeholder** in `classify_thought()` with actual Claude API call
2. **Added anthropic package** to `requirements.txt`
3. **Implemented JSON parsing** that handles Claude's markdown-wrapped responses
4. **Added fallback logic** if API key is missing

---

## Next Steps to Complete Setup

### 1. Set ANTHROPIC_API_KEY

Add to `~/SecondBrain/_scripts/.env`:
```bash
echo "ANTHROPIC_API_KEY=sk-ant-..." >> ~/SecondBrain/_scripts/.env
```

Or set globally:
```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

### 2. Install Dependencies

```bash
cd ~/SecondBrain/_scripts
pip3 install --break-system-packages -r requirements.txt
```

### 3. Test the System

```bash
cd ~/SecondBrain/_scripts
python3 process_inbox.py
```

Watch for:
- ✓ Messages classified with **high confidence** (>= 0.6)
- ✓ Files appearing in `~/SecondBrain/{destination}/`
- ✓ Daily note updated in `daily/YYYY-MM-DD.md`
- ✓ Slack replies with "✓ Filed to..." message

### 4. Monitor Logs

```bash
# Today's processing log
cat ~/SecondBrain/_inbox_log/$(date +%Y-%m-%d).md

# Check for failures
cat ~/SecondBrain/_inbox_log/FAILED-$(date +%Y-%m-%d).md
```

---

## Why Your Recent Messages Worked

The Jan 13 messages that **did** get filed all started with `"project:"`:
```
project: birmingham background history...
project: customer acquisition strategy...
```

This suggests either:
1. You have ANTHROPIC_API_KEY set somewhere that made the real API call work
2. There's a separate Claude Code integration that handled those
3. The prefix triggered a manual classification path I haven't found

**To verify**: Check if `ANTHROPIC_API_KEY` exists:
```bash
env | grep ANTHROPIC
```
