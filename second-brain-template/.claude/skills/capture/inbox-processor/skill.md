# Inbox Processor

## Description
Process raw thoughts from Slack inbox channel (or manual input), classify them, route to appropriate Obsidian folder, log the audit trail, and reply with confirmation. Use when user says "process inbox" or as part of /today command.

## Triggers
- "process inbox"
- "process my thoughts"
- "check sb-inbox"
- "what's in my inbox"
- Part of /today morning ritual

## Dependencies
- Slack API credentials (if using Slack): SLACK_BOT_TOKEN, SLACK_CHANNEL_ID, SLACK_USER_ID
- Obsidian vault at ~/SecondBrain/
- Classification prompt in `classifier-prompt.md`

## Workflow

### 1. Fetch New Messages

**If Slack configured:**
- Query Slack API for messages in #sb-inbox since last processed timestamp
- Store last_ts in `.last_processed_ts` in this skill folder
- Filter out: bot messages, system messages, "fix:" replies

**If manual input:**
- User provides thoughts directly in conversation
- Process each line/thought separately

### 2. Classify Each Message

For each message, use the classification prompt in `classifier-prompt.md`.

**Classification categories:**
| Category | Criteria |
|----------|----------|
| `tasks` | Has a specific deadline or time-bound action |
| `projects` | Multi-step work, ongoing effort |
| `people` | About a specific person, relationship, follow-up |
| `ideas` | Speculative, creative, exploratory |
| `admin` | One-off task, errand, logistics |

**Confidence threshold:** 0.6
- ≥ 0.6: File automatically
- < 0.6: Log as "NEEDS REVIEW", ask for clarification

### 3. Auto-Tag

Apply tags from the taxonomy in claude.md:

**Domain tags** (infer from content):
- #sales, #content, #product, #admin, #research, #people

**Context tags** (infer from scope):
- #quick — appears completable in <15 min
- #deep — requires focus time
- #collab — involves other people

**Status:**
- Default to #active for new items

### 4. Write to Obsidian

Use templates from `_templates/` for frontmatter structure.

**File location by type:**
- tasks → `tasks/[filename].md`
- projects → `projects/[filename].md`
- people → `people/[filename].md`
- ideas → `ideas/[filename].md`
- admin → `admin/[filename].md`

**Filename:** kebab-case derived from content
- Example: "Follow up with Marcus about deal" → `follow-up-with-marcus-about-deal.md`

### 5. Log to Audit Trail

Append to `_inbox_log/[YYYY-MM-DD].md`:

```markdown
| Time | Original | Destination | Filed As | Confidence | Tags |
|------|----------|-------------|----------|------------|------|
| 09:15 | Follow up with Marcus... | people | marcus-deal-followup.md | 0.92 | #sales #collab |
```

Create the log file with headers if it doesn't exist.

### 6. Confirm Filing

**Success (confidence ≥ 0.6):**
```
✓ Filed to *[destination]* as `[filename]`
Tags: [tags]
Confidence: [X]%
```

If using Slack, reply in thread and add:
```
_Reply `fix: tasks|projects|people|ideas|admin` if wrong_
```

**Low confidence (< 0.6):**
```
⚠️ Not sure where this goes (confidence: [X]%)
Please clarify with a prefix:
• `task:` — has a deadline
• `project:` — ongoing work
• `person:` — about someone specific
• `idea:` — to explore later
• `admin:` — one-off errand
```

### 7. Handle Fix Commands

If user replies with "fix: [destination]":
1. Move the file to correct folder
2. Update frontmatter type
3. Update inbox log with correction
4. Confirm: "Moved to [destination]"

## Error Handling

- **Slack API fails:** Log error, retry once, then notify user
- **File write fails:** Log to inbox_log with ERROR status, alert user
- **Classification fails:** Default to "ideas" with low confidence flag
- **Duplicate filename:** Append timestamp to make unique

## Output

- New files in appropriate folders
- Updated `_inbox_log/[date].md`
- Confirmation messages
- Slack thread replies (if configured)
