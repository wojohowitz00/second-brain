---
status: testing
phase: 04-proactive-layer
source: [04-01-SUMMARY.md, 04-02-SUMMARY.md, 04-03-SUMMARY.md]
started: 2026-03-15T05:10:00Z
updated: 2026-03-15T05:10:00Z
---

## Current Test

number: 1
name: Insights Detection via /weekly
expected: |
  Running /weekly produces a dated insights report at 05_AI_Workspace/insights/YYYY-MM-DD-insights.md containing at least one of: goal drift, neglected areas, overcommitment, or dormant projects — with specific [[wikilink]] note references
awaiting: user response

## Tests

### 1. Insights Detection via /weekly
expected: Running /weekly produces a dated insights report at 05_AI_Workspace/insights/YYYY-MM-DD-insights.md with at least one detection (goal drift, neglected areas, overcommitment, dormant projects) with [[wikilink]] note references
result: [pending]

### 2. Insights Hard Cap (5-10 items)
expected: The insights report contains no more than 5-10 items total, prioritized: overcommitment > goal drift > dormant projects > neglected areas
result: [pending]

### 3. Alert Routing via /today (Overdue Items)
expected: Running /today with an overdue task (due_date in the past) triggers: (1) Slack message in configured channel with :rotating_light: format, (2) macOS system notification, (3) entry in daily brief
result: [pending]

### 4. Alert Routing via /today (Due-Today Items)
expected: Running /today with a due-today task triggers: (1) macOS system notification, (2) entry in daily brief — NO Slack message
result: [pending]

### 5. Alert Routing via /today (Stale Follow-ups)
expected: Running /today with a stale follow-up (7+ days no activity) triggers: (1) entry in daily brief only — NO Slack, NO macOS notification
result: [pending]

### 6. 5-Item Alert Cap
expected: Morning briefing surfaces no more than 5 alert items total; overflow count is annotated (e.g., "and N more") rather than silently dropped
result: [pending]

### 7. Canvas Visual Weekly Review via /weekly
expected: Running /weekly produces 05_AI_Workspace/canvas/weekly-review.canvas as valid JSON Canvas v1.0 with three swimlanes (Active-green, Waiting-yellow, Blocked-red) containing project cards showing only blocked/overdue tasks
result: [pending]

### 8. Canvas Opens in Obsidian
expected: The weekly-review.canvas file opens correctly in Obsidian's Canvas view, rendering the swimlane layout visually
result: [pending]

### 9. Weekly Review Pipeline Coherence
expected: /weekly workflow executes steps in order: data gathering → completed items → open items → metrics → patterns → insights (5a) → canvas (5b) → review generation → prompt
result: [pending]

## Summary

total: 9
passed: 0
issues: 0
pending: 9
skipped: 0

## Gaps

[none yet]
