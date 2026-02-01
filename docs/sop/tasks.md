# Task handling (SOP)

When to treat a note as a task and which status/board values to use.

## When to set type: task

- The user explicitly uses the `todo:` or `kanban:` prefix in the message, or
- The message is clearly an actionable item (next step, to-do, assignment) and category is `task`.

## Allowed status values

- `backlog` — Not started (default for new tasks).
- `in_progress` — Actively being worked on.
- `blocked` — Waiting on something.
- `done` — Completed.

## Board (domain)

- Tasks are assigned to a board by domain (e.g. Personal, Just-Value, CCBH). Use the same domain as the note’s domain for consistency.

## Correction (fix:)

- Replies with `fix: domain:X para:Y subject:Z` move the note to the correct folder. The agent does not re-classify; it applies the user’s override.
