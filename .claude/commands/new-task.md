# /new-task [description]

Create a task from natural language. Two modes: standard (rich metadata extraction) and quick (zero-friction capture).

---

## Mode Detection

- `/new-task quick [title]` → Quick mode (no inference, no prompts)
- `/new-task [description]` → Standard mode (NL parsing, full metadata)

---

## Standard Mode: `/new-task [description]`

### Step 1 — Parse and extract fields

Read the description and extract the following fields. Only include a field if there is a clear signal. Omit fields with no evidence — do not write empty values.

**title** (Required)
- Clean, concise task title in sentence case
- Strip filler: "I need to", "ASAP", "by Friday", "urgent"
- Example: "I need to ASAP fix the login bug" → "Fix the login bug"

**due_date** (Optional — omit if no date mentioned)
- BARE ISO format: `YYYY-MM-DD` — NEVER quote this value. Quoted dates break Dataview.
- Inference rules:
  - "today" / "EOD" / "end of day" → today's date
  - "tomorrow" → tomorrow's date
  - "by Friday" / "this Friday" → the coming Friday
  - "end of week" → coming Sunday
  - "next week" / "next Monday" → next Monday
  - "end of month" → last day of current month
  - No date mentioned → omit field entirely (do not write `due_date: null`)

**status** (Default: `backlog`)
- Enum: `backlog | active | waiting | blocked | done | someday`
- Default is `backlog`. Do not use `active` unless explicitly requested.

**priority** (Optional — default `medium` if any task signals exist)
- Enum: `high | medium | low`
- "urgent", "critical", "ASAP", "important", "high priority" → `high`
- "someday", "eventually", "when I have time", "low priority" → `low`
- Default → `medium`

**project** (Optional — omit if no project mentioned)
- Format: `"[[ProjectName]]"` (quoted wikilink — required for valid YAML + Dataview)
- If the description names a known project (check `projects/` folder), use wikilink format
- If no project signal → omit field entirely

**domain** (Optional — omit if no clear signal)
- Enum: `sales | content | product | admin | research | people`
- Inference:
  - "email", "call", "schedule", "invoice", "book", "admin" → `admin`
  - "write", "post", "article", "video", "newsletter", "content" → `content`
  - "research", "read", "learn", "study", "explore", "investigate" → `research`
  - "sales", "client", "deal", "pipeline", "prospect", "proposal" → `sales`
  - "build", "code", "ship", "feature", "bug", "deploy", "fix" → `product`
  - Person names, "follow up with", "check in with", "reach out to", "thank you to" → `people`
  - No clear signal → omit field entirely

**context** (Optional — omit if no clear signal)
- Enum: `quick | deep | collab`
- "quick", "5 min", "2 min", "takes a second", "short", "call" → `quick`
- "review", "analyze", "write", "think through", "deep dive", "draft", "plan" → `deep`
- "with [person]", "schedule meeting", "discuss", "pair", "collaborate" → `collab`
- No clear signal → omit field entirely

**tags** (Optional)
- Include domain tag (e.g., `#admin`) if domain was inferred
- Include context tag (e.g., `#quick`) if context was inferred
- Add any explicit tags from the description
- If no tags apply → omit field

**created** (Required)
- Today's date in BARE ISO format: `YYYY-MM-DD` — NEVER quote this value.

### Step 2 — Create the file

- **Location:** `tasks/` directory
- **Filename:** kebab-case, strip filler words, no special characters, concise
  - "Send thank you note to Claire by Friday" → `send-thank-you-note-to-claire.md`
  - "ASAP fix the login bug" → `fix-the-login-bug.md`
- **Frontmatter:** Include only fields with values. Omit fields with no signal.

```yaml
---
type: task
title: [extracted title]
due_date: YYYY-MM-DD
status: backlog
priority: medium
project: "[[ProjectName]]"
domain: admin
context: deep
tags: [#admin, #deep]
created: YYYY-MM-DD
---
```

CRITICAL: `due_date` and `created` must be bare ISO dates. NEVER quote them (`"2026-03-14"` breaks Dataview — it becomes text, not a date).

### Step 3 — Confirm creation

Show what was created:

```
Created: tasks/[filename].md
  Title:    [title]
  Due:      [YYYY-MM-DD or "none"]
  Priority: [high | medium | low]
  Status:   backlog
  Domain:   [domain or "—"]
  Context:  [context or "—"]
```

### Step 4 — Offer notes (ONE prompt only)

Ask: "Want to add any notes or context?"

- If yes → append the user's notes as body text below the frontmatter
- If no → done
- Do NOT prompt again. One offer, one response, done.

---

## Quick Mode: `/new-task quick [title]`

Zero-friction capture. No inference, no prompts.

1. Take the title exactly as given
2. Create file in `tasks/` with minimal frontmatter:

```yaml
---
type: task
title: [title as given]
status: backlog
created: YYYY-MM-DD
---
```

3. Confirm with one line: `Created: tasks/[filename].md — backlog`
4. No prompts. No offers. Done.

---

## Examples

`/new-task Send thank you note to Claire by Friday`
→ title: "Send thank you note to Claire", due_date: [next Friday bare ISO], priority: medium, domain: people, context: quick, tags: [#people, #quick]

`/new-task Review Q3 sales numbers`
→ title: "Review Q3 sales numbers", priority: medium, domain: sales, context: deep, tags: [#sales, #deep]

`/new-task ASAP fix the login bug`
→ title: "Fix the login bug", priority: high, domain: product, tags: [#product]

`/new-task Research newsletter platforms by end of month`
→ title: "Research newsletter platforms", due_date: [last day of month bare ISO], priority: medium, domain: research, context: deep, tags: [#research, #deep]

`/new-task quick Buy groceries`
→ title: "Buy groceries", status: backlog, created: today. One-line confirm. Done.

---

## Field Quick Reference

| Field | Type | Default | Notes |
|-------|------|---------|-------|
| type | literal | task | Always "task" |
| title | text | required | Sentence case, strip filler |
| due_date | bare ISO date | omit | NEVER quote — breaks Dataview |
| status | enum | backlog | Not active |
| priority | enum | medium | high/medium/low |
| project | wikilink | omit | Quoted: `"[[Name]]"` |
| domain | enum | omit | sales/content/product/admin/research/people |
| context | enum | omit | quick/deep/collab |
| tags | array | omit | Domain + context tags if inferred |
| created | bare ISO date | today | NEVER quote — breaks Dataview |

---

## Canonical Schema

Field definitions and Dataview compatibility rules: `.planning/phases/01-foundation/yaml-frontmatter-schema.md`
