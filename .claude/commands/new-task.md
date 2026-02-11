# /new-task [description]

Quick task creation from natural language.

## Process

1. Parse the description
2. Extract:
   - Task title
   - Due date (if mentioned, otherwise null)
   - Inferred tags from content
3. Create file in `tasks/` with proper frontmatter
4. Auto-tag based on taxonomy in claude.md
5. If due today, add to current daily file
6. Confirm: "Created: [filename] — due [date], tagged [tags]"

## Examples

`/new-task Send thank you note to Claire by Friday`
→ Creates `send-thank-you-note-to-claire.md`, due_date: Friday, tags: #people #quick

`/new-task Review Q3 sales numbers`
→ Creates `review-q3-sales-numbers.md`, due_date: null, tags: #sales #deep

`/new-task Call dentist to reschedule tomorrow`
→ Creates `call-dentist-to-reschedule.md`, due_date: tomorrow, tags: #admin #quick

## Filename Convention

- Use kebab-case
- Keep concise but descriptive
- No special characters

## Frontmatter Template

```yaml
---
type: task
title: [extracted title]
due_date: [YYYY-MM-DD or null]
status: active
tags: [inferred tags]
created: [today's date]
---
```
