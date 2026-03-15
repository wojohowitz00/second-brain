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

### 2.5. Alert Routing (External Delivery)

After writing the daily brief vault note, deliver urgent items through external channels based on severity.

**Urgent item criteria:**
- Overdue: tasks with `due_date` < today AND `status` != done
- Due today: tasks with `due_date` = today AND `status` != done
- Stale follow-ups: people notes with `follow_up_date` <= today AND file mtime older than 7 days (use `stat -f "%Sm" -t "%s"` on macOS, compare against 7-day threshold)

**5-item cap with priority ordering:**
1. Collect all urgent items (overdue + due-today + stale follow-ups)
2. Sort: overdue first (oldest `due_date` first), then due-today, then stale follow-ups
3. Take first 5 items only
4. If more than 5 exist, append an overflow note to the daily brief: `> N additional urgent items not shown — cap of 5 reached.`

**Severity-based routing:**

| Severity | Slack | macOS Notification | Daily Brief |
|----------|-------|--------------------|-------------|
| Overdue | YES | YES | YES (already in note) |
| Due today | NO | YES | YES (already in note) |
| Stale follow-up | NO | NO | YES (already in note) |

**Slack delivery (overdue items only):**

```bash
source /Users/richardyu/PARA/01_Projects/Personal/apps/second-brain/backend/_scripts/.env
python3 -c "
import sys
sys.path.insert(0, '/Users/richardyu/PARA/01_Projects/Personal/apps/second-brain/backend/_scripts')
from slack_client import post_message
import os
post_message(channel=os.environ['SLACK_CHANNEL_ID'], text='FORMATTED_ALERT_TEXT')
"
```

Format the Slack message as:
```
:rotating_light: Second Brain Alert — N overdue items
- Task Name (due YYYY-MM-DD, N days overdue)
- Task Name (due YYYY-MM-DD, N days overdue)
```

**macOS notification (overdue + due-today items):**

```bash
osascript -e "display notification \"N items need attention\" with title \"Second Brain\" subtitle \"Morning Alert\""
```

Use a single consolidated notification (not one per item). Count = overdue + due-today items combined (capped at 5 total across all tiers).

**Error handling:**
- Slack post fails (network, auth): log warning in session output, continue. Do NOT block the briefing.
- `osascript` fails: log warning in session output, continue.
- No urgent items: skip alert routing entirely — no empty Slack posts, no empty notifications.

**CRITICAL:** `session-start.sh` is context-injection ONLY. It must NOT be modified to do external delivery. All Slack/osascript delivery happens in THIS skill step only. This prevents double-firing.

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
- Do NOT use pre-computed Dataview queries in the vault note (write static markdown tables)
- Do NOT include tasks with `status: done`
- Do NOT quote dates in frontmatter (`date: "2026-03-14"` is wrong; `date: 2026-03-14` is correct)
- Do NOT add alert routing to `session-start.sh` — that script is context-injection only; all external delivery (Slack, osascript) happens in Step 2.5 of this skill only
- Do NOT send more than 5 alert items regardless of how many urgent items exist — apply the cap before any external delivery
- Do NOT send Slack messages for due-today or stale follow-up items — Slack is for overdue items only
- Do NOT fire empty notifications — skip alert routing entirely when no urgent items exist

## Error Handling

- Missing or malformed frontmatter: skip that file, continue
- Directory doesn't exist: skip that section entirely
- Directory contains only README.md: skip that section entirely
- File for today already exists: overwrite it
