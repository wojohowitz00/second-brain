# /pipeline [domain]

Generate a filtered view of tasks by domain.

## Default (no argument)
Show sales pipeline: all items tagged #sales, grouped by status

## With Argument
- `/pipeline content` → all #content items
- `/pipeline product` → all #product items
- `/pipeline admin` → all #admin items
- `/pipeline research` → all #research items

## Process

1. Search `tasks/` folder for items matching the domain tag
2. Group by status (#active, #waiting, #blocked, #someday)
3. Sort each group by due_date (earliest first)
4. Generate markdown report

## Output Format

```markdown
# [Domain] Pipeline — [Date]

## Active
- [ ] [task] (due [date])
- [ ] [task] (due [date])

## Waiting
- [ ] [task] — waiting on [context from notes]

## Blocked
- [ ] [task] — blocked by [reason from notes]

## Someday
- [ ] [task]
- [ ] [task]

---
Total: [X] items | Active: [Y] | Blocked: [Z]
```

## Notes

Generate on-the-fly from vault search. Don't require pre-built views.

If a task has notes explaining why it's waiting or blocked, include that context.
