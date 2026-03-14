---
phase: 03-core-daily-skills
plan: 03
subsystem: ui
tags: [claude-commands, task-creation, dataview, natural-language-parsing, yaml]

# Dependency graph
requires:
  - phase: 01-foundation
    provides: canonical YAML frontmatter schema with task fields and Dataview typing rules
provides:
  - Enhanced /new-task command with NL parsing for rich metadata (priority, domain, context, project)
  - Quick capture mode (/new-task quick) for zero-friction task creation
  - Dataview-compatible task frontmatter ensuring dashboard queries work correctly
affects:
  - 03-04-dataview-dashboard (tasks created by this command feed the dashboard queries)
  - any future skill that creates tasks

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Command instruction file pattern: prose rules + inference tables + field quick reference + canonical schema link"
    - "Omit-on-no-signal pattern: fields only written when evidence exists, no empty values"
    - "Mode detection pattern: keyword prefix (quick) selects simplified workflow"

key-files:
  created: []
  modified:
    - .claude/commands/new-task.md

key-decisions:
  - "Default status is backlog, not active — tasks start unscheduled until user deliberately promotes them"
  - "Omit fields with no signal rather than writing empty/null values — cleaner frontmatter, no Dataview noise"
  - "Post-creation notes offer is exactly one prompt — no loop, preserves command velocity"
  - "Quick mode takes title as-is with zero inference — optimized for speed over richness"

patterns-established:
  - "Command files include a Field Quick Reference table summarizing all fields, defaults, and notes"
  - "Command files link to canonical schema file to avoid duplicating field definitions"
  - "Inference rules documented as keyword → enum value tables for deterministic behavior"

# Metrics
duration: 51s
completed: 2026-03-14
---

# Phase 3 Plan 03: Enhanced /new-task Command Summary

**Rewrote /new-task with full Dataview-compatible metadata extraction (priority, domain, context, project, due date inference) and a zero-friction /new-task quick capture variant**

## Performance

- **Duration:** 51 seconds
- **Started:** 2026-03-14T23:07:53Z
- **Completed:** 2026-03-14T23:08:44Z
- **Tasks:** 1
- **Files modified:** 1

## Accomplishments

- Replaced minimal 4-field command with full 10-field NL parsing command (type, title, due_date, status, priority, project, domain, context, tags, created)
- Added natural language inference rules for due dates (7 patterns), priority (3 tiers), domain (6 categories), and context (3 types)
- Added /new-task quick mode for zero-friction capture with no prompts, no inference, one-line confirm
- Enforced bare ISO date rule explicitly with "NEVER quote" callout to protect Dataview compatibility
- Default status changed from `active` to `backlog` to match canonical schema intent

## Task Commits

Each task was committed atomically:

1. **Task 1: Rewrite /new-task command with rich metadata and quick capture** - `ad7ddba` (feat)

**Plan metadata:** (follows)

## Files Created/Modified

- `.claude/commands/new-task.md` - Full rewrite: standard mode (NL parsing → rich frontmatter), quick mode (title + backlog + created), field quick reference table, inference rule tables, examples, canonical schema link

## Decisions Made

- Default status `backlog` (not `active`) — tasks start in backlog until user schedules them; this matches the canonical schema intent and the Dataview dashboard design in plan 03-04
- Omit fields with no signal — cleaner frontmatter, avoids Dataview null-matching edge cases
- One post-creation notes offer, not a loop — preserves command velocity; additional context can always be added manually
- Quick mode takes title verbatim — no inference, no prompts, optimized for speed

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- /new-task command now produces Dataview-compatible frontmatter for all task fields used in the 03-04 dashboard (priority, domain, context, status, due_date)
- Quick mode provides zero-friction capture path alongside rich standard mode
- No blockers for 03-04 (Dataview dashboard plan)

---
*Phase: 03-core-daily-skills*
*Completed: 2026-03-14*
