---
phase: 02-memory-and-session-context
plan: 02
subsystem: infra
tags: [bash, hooks, session-start, session-end, claude-code, tasks, dashboard]

# Dependency graph
requires:
  - phase: 01-foundation
    provides: tasks/ directory structure, YAML frontmatter schema, 05_AI_Workspace/ write policy
provides:
  - SessionStart hook that surfaces overdue/upcoming/stale tasks as plain-text context
  - SessionEnd hook that refreshes tasks-by-status dashboard timestamp
  - Both hooks registered in global ~/.claude/settings.json
affects: [03-dataview-queries, 04-canvas]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Claude Code hooks use bash scripts in .claude/hooks/ with absolute paths registered in global settings.json"
    - "SessionStart hook uses awk frontmatter extraction + macOS date -j arithmetic; silent exit 0 when no items"
    - "SessionEnd hook uses sed -i '' for in-place frontmatter field update"

key-files:
  created:
    - .claude/hooks/session-start.sh
    - .claude/hooks/session-end.sh
  modified:
    - ~/.claude/settings.json

key-decisions:
  - "Hooks registered in global ~/.claude/settings.json (not project settings.json) following existing bd prime/gsd-check-update pattern"
  - "SessionStart output is plain-text (not JSON) — injected directly into Claude context without parsing overhead"
  - "Silent exit when no items to report — no noise when tasks are healthy"
  - "SessionEnd uses sed -i '' (macOS in-place) targeting only refreshed_by field — minimal footprint"
  - "SessionEnd given 5000ms timeout — well above actual runtime (~5ms)"

patterns-established:
  - "Hook scripts: always exit 0, handle missing files gracefully, use absolute paths"
  - "Task scanning: awk extracts between first two --- delimiters; skip README.md; skip done status"

# Metrics
duration: 1m 14s
completed: 2026-03-14
---

# Phase 2 Plan 02: Session Lifecycle Hooks Summary

**SessionStart/SessionEnd bash hooks that auto-surface overdue/stale tasks at session open and refresh the tasks-by-status dashboard timestamp at session close, registered in global settings.json**

## Performance

- **Duration:** 1m 14s
- **Started:** 2026-03-14T08:27:26Z
- **Completed:** 2026-03-14T08:28:40Z
- **Tasks:** 2
- **Files modified:** 3

## Accomplishments

- SessionStart hook scans tasks/*.md frontmatter, buckets into overdue/upcoming/stale, outputs capped plain-text summary to Claude context
- SessionEnd hook refreshes `refreshed_by` field in tasks-by-status.md dashboard with today's date
- Both hooks registered in global ~/.claude/settings.json alongside existing bd prime and gsd-check-update hooks

## Task Commits

Each task was committed atomically:

1. **Task 1: Create SessionStart hook script** - `7d5e0f6` (feat)
2. **Task 2: Create SessionEnd hook and register both hooks** - `ff0a3b2` (feat)

**Plan metadata:** (docs commit follows)

## Files Created/Modified

- `.claude/hooks/session-start.sh` - Scans tasks/ for overdue/upcoming/stale items, outputs plain-text to stdout, always exits 0
- `.claude/hooks/session-end.sh` - Updates refreshed_by date in tasks-by-status dashboard, always exits 0
- `~/.claude/settings.json` - Added session-start.sh to SessionStart array; added SessionEnd array with session-end.sh (5s timeout)

## Decisions Made

- Hooks go in global `~/.claude/settings.json` (not project-level), consistent with existing bd prime pattern — global hooks fire in every project context
- Plain-text output over JSON: SessionStart output is injected directly into Claude context, plain-text is clearest for model comprehension
- Silent when healthy: script outputs nothing and exits 0 if no overdue/upcoming/stale tasks — avoids noise pollution in context
- macOS date -j primary with GNU date -d fallback — supports both macOS and Linux environments

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required. Settings.json was updated automatically; hooks will fire on next Claude Code session start/end.

## Next Phase Readiness

- Session lifecycle hooks are live — task status will appear in context from next session onward
- Phase 3 (Dataview queries) can proceed: the refreshed_by field updated by session-end.sh is already defined in the schema from 01-03
- No blockers introduced

---
*Phase: 02-memory-and-session-context*
*Completed: 2026-03-14*
