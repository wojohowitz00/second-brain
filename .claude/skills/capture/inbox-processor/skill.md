# Inbox Processor

## Description
Process raw thoughts from Slack inbox channel (or manual input), classify them, route to appropriate folder, log the audit trail, and reply with confirmation. Use when user says "process inbox" or as part of /today command.

Note: Automated Slack capture uses the Python backend pipeline. This skill is for manual/interactive classification.

## Triggers
- "process inbox"
- "process my thoughts"
- "check sb-inbox"
- "what's in my inbox"
- Part of /today morning ritual

## Dependencies
- Obsidian vault structure with tasks/, projects/, people/, ideas/, admin/ folders
- Classification prompt in `classifier-prompt.md`
- Optional: Slack API credentials for pulling from #sb-inbox

## Workflow

### 1. Fetch New Messages

**If Slack configured:**
- Query Slack API for messages in #sb-inbox since last processed timestamp
- Filter out: bot messages, system messages, "fix:" replies

**If manual input:**
- User provides thoughts directly in conversation
- Process each line/thought separately

### 2. Classify Each Message

Use the classification prompt in `classifier-prompt.md`.

**Classification categories:**
| Category | Criteria |
|----------|----------|
| `tasks` | Has a specific deadline or time-bound action |
| `projects` | Multi-step work, ongoing effort |
| `people` | About a specific person, relationship, follow-up |
| `ideas` | Speculative, creative, exploratory |
| `admin` | One-off task, errand, logistics |

**Confidence threshold:** 0.6
- >= 0.6: File automatically
- < 0.6: Log as "NEEDS REVIEW", ask for clarification

### 3. Auto-Tag

Apply tags from the taxonomy in claude.md:
- **Domain tags**: #sales, #content, #product, #admin, #research, #people
- **Context tags**: #quick (<15 min), #deep (focus time), #collab (involves others)
- **Status**: Default to #active for new items

### 4. Write to Vault

Use templates from `backend/_templates/` for frontmatter structure.

**File location by type:**
- tasks → `tasks/[filename].md`
- projects → `projects/[filename].md`
- people → `people/[filename].md`
- ideas → `ideas/[filename].md`
- admin → `admin/[filename].md`

**Filename:** kebab-case derived from content

### 5. Log to Audit Trail

Append to `_inbox_log/[YYYY-MM-DD].md`:

```markdown
| Time | Original | Destination | Filed As | Confidence | Tags |
|------|----------|-------------|----------|------------|------|
| 09:15 | Follow up with Marcus... | people | marcus-deal-followup.md | 0.92 | #sales #collab |
```

### 6. Confirm Filing

**Success (confidence >= 0.6):**
```
Filed to [destination] as [filename]
Tags: [tags] | Confidence: [X]%
```

**Low confidence (< 0.6):**
```
Not sure where this goes (confidence: [X]%)
Please clarify: task: | project: | person: | idea: | admin:
```

## Error Handling

- **Classification fails:** Default to "ideas" with low confidence flag
- **Duplicate filename:** Append timestamp to make unique
- **File write fails:** Log to inbox_log with ERROR status, alert user
