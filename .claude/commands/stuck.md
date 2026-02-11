# /stuck — What Am I Avoiding?

Surface items that haven't moved and may need attention or deletion.

## Find

1. **Severely Overdue**: Tasks overdue by more than 7 days
2. **Repeatedly Pushed**: Tasks rescheduled 3+ times (check modification history or inbox_log)
3. **Dormant Projects**: Projects with no activity in 14+ days
4. **Stale Ideas**: Ideas marked "in-progress" for 30+ days

## Process

1. Search all folders for matching criteria
2. Sort by age (oldest first)
3. Generate report with context
4. Offer actionable options

## Output Format

```markdown
# Stuck Items — [Date]

## Severely Overdue (>7 days)
- [ ] [task] — due [date], [X] days overdue
  > [First line of notes if present]

## Repeatedly Pushed
- [ ] [task] — rescheduled [X] times
  > Last due date: [date]

## Dormant Projects
- [ ] [project] — last touched [date]
  > Next action was: [next_action field]

## Stale Ideas
- [ ] [idea] — in-progress since [date]
  > [oneliner field]

---
Summary: [X] stuck items identified
```

## Prompt

After output, ask:

"These items might be stuck for a reason. Want to:
1. Talk through why something's blocked?
2. Delete/archive items that aren't happening?
3. Break something into smaller pieces?
4. Just reschedule with realistic dates?"
