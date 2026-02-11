# Task handling (SOP)

When to treat a note as a task and which status/board values to use.

## When to set type: task

- The user explicitly uses the `todo:` or `kanban:` prefix in the message, or
- The message is clearly an actionable item (next step, to-do, assignment) and category is `task`.

## Allowed status values

- `backlog` — Not started (default for new tasks).
- `active` — Currently working on.
- `in_progress` — Actively being worked on (alias for active).
- `waiting` — Blocked on external input.
- `blocked` — Waiting on a dependency.
- `someday` — No urgency, future consideration.
- `done` — Completed.

## Domain Tags

- `#sales` — Pipeline and deals
- `#content` — Writing, videos, posts
- `#product` — Course/platform work
- `#admin` — Operations, logistics
- `#research` — Learning and synthesis
- `#people` — Relationship management

## Context Tags

- `#quick` — Completable in <15 minutes
- `#deep` — Requires focus time
- `#collab` — Involves coordinating with others

## Board (domain)

- Tasks are assigned to a board by domain (e.g. Personal, Just-Value, CCBH). Use the same domain as the note's domain for consistency.

## Correction (fix:)

- Replies with `fix: domain:X para:Y subject:Z` move the note to the correct folder. The agent does not re-classify; it applies the user's override.
