# Weekly Review

## Description
Generate a comprehensive weekly summary of what happened, what's stuck, patterns noticed, and suggested focus for next week. Designed to run Sunday afternoon.

## Triggers
- Part of /weekly command
- "weekly review"
- "review my week"
- "what happened this week"
- "sunday review"

## Dependencies
- Obsidian vault with established folder structure
- `_inbox_log/` files for the past 7 days
- Items with date-based frontmatter

## Workflow

### 1. Determine Date Range

Calculate:
- Week number (ISO format: YYYY-WW)
- Start date (Monday)
- End date (Sunday/today)

### 2. Gather Completed Items

Search all folders for items marked #done or status: done with completion/modification date in past 7 days:
- Tasks completed
- Projects completed or milestones hit
- Ideas explored/developed
- Admin items handled

### 3. Gather Open Items

**Still active:**
- Tasks not yet done
- Projects in progress

**Problematic:**
- Tasks overdue
- Tasks pushed/rescheduled multiple times this week
- Projects with no commits/changes in 7+ days

### 4. Calculate Metrics

From `_inbox_log/` files for the week:

| Category | Added | Completed | Net Change |
|----------|-------|-----------|------------|
| Tasks    | X     | Y         | +/- Z      |
| Projects | X     | Y         | +/- Z      |
| People   | X     | Y         | +/- Z      |
| Ideas    | X     | Y         | +/- Z      |
| Admin    | X     | Y         | +/- Z      |

**Health indicators:**
- Growing backlog? (more added than completed)
- Shrinking backlog? (good progress)
- Stable? (sustainable pace)

### 5. Identify Patterns

Analyze the week for:

**Attention patterns:**
- Which tags appeared most frequently?
- What consumed the most captures?

**Avoidance patterns:**
- Tasks pushed more than once
- Items overdue more than 7 days
- Projects with no activity

**People patterns:**
- Who came up frequently?
- Any overdue follow-ups?

**Theme patterns:**
- Common topics in ideas
- Recurring challenges

### 6. Generate Suggested Focus

Based on patterns, identify 3 priorities for next week:
- Address avoidance items
- Continue momentum on active projects
- Handle relationship follow-ups

### 7. Generate Review

Write to `weekly/[YYYY-WW].md`:

```markdown
# Week Review: [YYYY-WW]
*[Monday date] — [Sunday date]*

## ✅ Completed This Week
Celebrate these wins:
- [x] [task/project]
- [x] [task/project]
- [x] [task/project]

## 📊 Weekly Numbers

| Category | Added | Completed | Net |
|----------|-------|-----------|-----|
| Tasks    | X     | Y         | +Z  |
| Projects | X     | Y         | -Z  |
| People   | X     | Y         | +Z  |
| Ideas    | X     | Y         | +Z  |
| Admin    | X     | Y         | -Z  |

**Health:** [Growing backlog / Shrinking backlog / Stable pace]

## 🚧 Still Open

### Overdue
- [ ] [task] — due [date], [X] days overdue

### Pushed Multiple Times
- [ ] [task] — rescheduled [X] times this week

### Dormant Projects
- [ ] [project] — no activity since [date]

## 🔍 Patterns Noticed

1. **[Pattern]**: [Observation and implication]
   - Example: "Most captures were #content related — content creation dominating attention"

2. **[Pattern]**: [Observation]
   - Example: "Three tasks involving [person] got pushed — possible relationship friction"

3. **[Pattern]**: [Observation]
   - Example: "Research backlog growing faster than consumption"

## 🎯 Suggested Focus Next Week

Based on this week's patterns:

1. **[Priority 1]**
   Why: [Reasoning based on patterns]
   
2. **[Priority 2]**
   Why: [Reasoning]
   
3. **[Priority 3]**
   Why: [Reasoning]

## 🧹 Maintenance Actions

Consider:
- [ ] [X] overdue items to address or delete
- [ ] [Y] stale ideas to activate or archive
- [ ] [Z] people follow-ups past due

---
*Review generated [timestamp]*
```

### 8. Deliver

**Obsidian:**
- Save to `weekly/[YYYY-WW].md`

**Slack (if configured):**
- Send full review to DM

### 9. Prompt

End with:

"That's your week in review. Want to:
1. Walk through any stuck items?
2. Help clear some overdue backlog?
3. Plan next week's focus in more detail?
4. Archive/delete items that aren't happening?"

## Output Constraints

- Completed section: Show all (celebrate wins!)
- Stuck items: Group by type (overdue, pushed, dormant)
- Patterns: 2-4 insights, not exhaustive
- Focus suggestions: Exactly 3, with reasoning
- Total length: Under 400 words for readable summary

## Error Handling

- If no inbox_log files exist: Note "No capture data available for metrics"
- If week is incomplete: Note "Partial week review (X days)"
- Missing folders: Skip sections, note in output
