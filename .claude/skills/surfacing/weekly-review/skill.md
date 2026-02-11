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
- Folder structure with tasks/, projects/, ideas/, people/, admin/
- `_inbox_log/` files for the past 7 days (pipe-delimited format)
- Items with date-based frontmatter

## Workflow

### 1. Determine Date Range

Calculate week number (ISO format: YYYY-WW), start date (Monday), end date (Sunday/today).

### 2. Gather Completed Items

Search all folders for items marked #done or status: done with completion/modification date in past 7 days.

### 3. Gather Open Items

- Tasks not yet done
- Tasks overdue or pushed multiple times
- Projects with no changes in 7+ days

### 4. Calculate Metrics

From `_inbox_log/` files for the week:

| Category | Added | Completed | Net Change |
|----------|-------|-----------|------------|
| Tasks    | X     | Y         | +/- Z      |
| Projects | X     | Y         | +/- Z      |
| People   | X     | Y         | +/- Z      |
| Ideas    | X     | Y         | +/- Z      |
| Admin    | X     | Y         | +/- Z      |

### 5. Identify Patterns

- Which tags appeared most frequently?
- Tasks pushed more than once (avoidance signals)
- People follow-ups overdue
- Common topics in ideas

### 6. Generate Review

Write to `weekly/[YYYY-WW].md` with completed items, metrics, stuck items, patterns, and 3 suggested priorities for next week.

### 7. Prompt

End with:
"Want to walk through any stuck items? Or should I help clear some overdue backlog?"

## Output Constraints

- Completed section: Show all (celebrate wins!)
- Patterns: 2-4 insights, not exhaustive
- Focus suggestions: Exactly 3, with reasoning
- Total length: Under 400 words

## Error Handling

- If no inbox_log files exist: Note "No capture data available for metrics"
- If week is incomplete: Note "Partial week review (X days)"
- Missing folders: Skip sections, note in output
