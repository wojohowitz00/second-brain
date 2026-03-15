# /weekly — Weekly Review

Generate a comprehensive weekly summary. Run Sunday afternoon.

## Process

### 1. Gather Data

**Completed this week:**
- Tasks marked #done with completion in past 7 days
- Items from _inbox_log/ processed this week

**Still open:**
- Tasks overdue
- Tasks pushed/rescheduled during the week
- Projects with no activity in 7+ days

**Volume metrics:**
- Count of items added to each category
- Count of items completed
- Net change (growing backlog or shrinking?)

**Research:**
- Papers saved and summarized this week

### 2. Identify Patterns

Look for:
- Tasks that keep getting pushed (avoidance signals)
- Tags with high volume (what's consuming attention)
- People not followed up with
- Ideas stuck in "in-progress" too long
- Recurring themes in captures

### 3. Generate Review

Write to `weekly/[YYYY-WW].md`

## Output Format

```markdown
# Week Review: [YYYY-WW]
*[Date range: Monday - Sunday]*

## Completed
[List completed items]
- [task]

## This Week's Numbers
| Category | Added | Completed | Net |
|----------|-------|-----------|-----|
| Tasks    | X     | Y         | +/- |
| Ideas    | X     | Y         | +/- |
| People   | X     | Y         | +/- |

## Still Open
Items that didn't get done:
- [ ] [task] — [brief context]

## Patterns Noticed
- [Pattern 1]
- [Pattern 2]

## Suggested Focus Next Week
1. **[Priority 1]** — [why this matters now]
2. **[Priority 2]** — [why this matters now]
3. **[Priority 3]** — [why this matters now]

## Maintenance Suggestions
- [X] overdue items to address or delete
- [Y] stale ideas to activate or archive
- [Z] people follow-ups overdue

---
*Review generated [timestamp]*
```

## Insights Detection

As part of the weekly review, Claude performs vault-wide pattern analysis:
- Dormant projects (14+ days inactive while still marked active)
- Neglected domains (no activity vs other active domains in past 14 days)
- Overcommitment (10+ active tasks)
- Goal drift (tasks referencing inactive or missing projects)

Results are saved to `05_AI_Workspace/insights/YYYY-MM-DD-insights.md` and summarized in the weekly review under `## Vault Insights`. The full report is linked via `[[YYYY-MM-DD-insights]]` in the Patterns Noticed section.

## Prompt

End with:
"Want to walk through any stuck items? Or should I help clear some of the overdue backlog?"
