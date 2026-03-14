# Morning Briefing Skill

## Description

Generate a structured daily brief that orients the user with summary counts before listing details. Write a dated note to the vault and inject a conversational summary into session context.

This skill is the daily situation report: orient first, then act.

## Triggers

- `/today`
- "morning briefing"
- "what's on today"
- "daily brief"

## Data Sources

Read directly from the project root (not the vault):

- `tasks/*.md` — extract `due_date`, `status`, `project`, `title` from frontmatter (skip README.md)
- `people/*.md` — extract `follow_up_date`, `name` from frontmatter (skip README.md)
- `projects/*.md` — extract `status`, `health`, `next_action`, `name` from frontmatter (skip README.md)

**Graceful empty handling:** If a directory has only README.md or no files, skip that section entirely. Do not error or show "All clear!" placeholders.

## Workflow

### 1. Read Data

Scan the three directories. For each `.md` file (skip README.md):
- Parse YAML frontmatter
- Skip tasks with `status: done`
- Collect overdue tasks: `due_date` < today AND `status` != done
- Collect due today: `due_date` = today AND `status` != done
- Collect upcoming: `due_date` within next 7 days (excluding today) AND `status` != done
- Collect follow-ups: `follow_up_date` <= today + 7 days
- Collect active projects: `status: active`

### 2. Write Vault Note

Write to: `05_AI_Workspace/daily-briefs/YYYY-MM-DD-daily-brief.md`

Use today's date in the filename. If the file exists, overwrite it (daily briefs are idempotent — one file per day).

**Frontmatter:**
```yaml
---
type: daily-brief
date: YYYY-MM-DD
generated_by: claude
---
```

Note: `date` must be bare ISO format — no quotes. Quoted dates break Dataview date queries.

**Note structure:**

```markdown
# Daily Brief — YYYY-MM-DD

## At a Glance
X tasks due today · Y overdue · Z follow-ups needing attention

## Overdue Tasks
| Task | Status | Project | Due |
|------|--------|---------|-----|
| ... | ... | ... | ... |

(sorted oldest first; omit entire section if no overdue tasks)

## Due Today
| Task | Status | Project |
|------|--------|---------|
| ... | ... | ... |

(omit entire section if nothing due today)

## Upcoming (Next 7 Days)
| Task | Status | Project | Due |
|------|--------|---------|-----|
| ... | ... | ... | ... |

(omit entire section if no upcoming tasks)

## Follow-ups
| Person | Follow-up Date |
|--------|----------------|
| ... | ... |

(people where follow_up_date <= today + 7 days; omit section if none)

## Active Projects
| Project | Health | Next Action |
|---------|--------|-------------|
| ... | ... | ... |

(projects where status = active; omit section if none)

## Automation Opportunities
- [Actionable offers based on current task/people state]

Examples of good automation opportunities:
- "3 tasks marked `waiting` — want me to draft follow-ups?"
- "2 tasks have no due date — want me to help prioritize?"
- "Task 'X' is 5 days overdue — want me to reschedule it?"

Only list opportunities where Claude could act RIGHT NOW in this session.
Omit this section entirely if no actionable opportunities exist.

---
<!-- Day Summary will be appended by session-end hook -->
```

### 3. Inject Session Summary

After writing the vault note, provide a conversational summary inline:

1. Lead with the "At a Glance" counts
2. List the top 3–5 most urgent items (overdue first, then due today)
3. State automation opportunities as offers ("Want me to...")
4. End with: "Want me to start on any of these, or dive into something else?"

Keep this session summary scannable — it should orient, not overwhelm.

## Output Constraints

- Overdue section: ALL items, sorted oldest first
- Due today: ALL items
- Upcoming: items within next 7 days only
- Follow-ups: people where `follow_up_date` is within 7 days of today
- Active projects: projects with `status: active` only
- Session summary: top 3–5 most urgent items

## Anti-Patterns

- Do NOT write to `daily/` (that folder is deprecated)
- Do NOT send a Slack DM (deferred to a later phase)
- Do NOT use pre-computed Dataview queries in the vault note (write static markdown tables)
- Do NOT include tasks with `status: done`
- Do NOT quote dates in frontmatter (`date: "2026-03-14"` is wrong; `date: 2026-03-14` is correct)

## Error Handling

- Missing or malformed frontmatter: skip that file, continue
- Directory doesn't exist: skip that section entirely
- Directory contains only README.md: skip that section entirely
- File for today already exists: overwrite it
