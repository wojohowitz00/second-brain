---
phase: 04-proactive-layer
plan: 02
subsystem: skills
tags: [slack, osascript, notifications, alerts, morning-briefing, daily-digest]

# Dependency graph
requires:
  - phase: 03-core-daily-skills
    provides: morning briefing skill (daily-digest) that this extends with alert routing
provides:
  - Severity-based alert routing in daily-digest skill (Step 2.5)
  - Three-channel delivery: Slack for overdue, macOS notification for overdue+due-today, daily brief for all
  - 5-item cap with overdue-first priority ordering
  - Updated /today command documentation with routing table
affects: [04-03-insights-engine, 04-04-weekly-canvas]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Severity tiering: overdue > due-today > stale, each tier reduces channel reach"
    - "Single consolidated macOS notification (not per-item) to prevent notification fatigue"
    - "Overflow annotation appended to daily brief when cap exceeded"
    - "skill.md step numbering: 2.5 inserted between 2 and 3 to preserve flow"

key-files:
  created: []
  modified:
    - .claude/skills/surfacing/daily-digest/skill.md
    - .claude/commands/today.md

key-decisions:
  - "Alert routing lives ONLY in skill Step 2.5 — session-start.sh remains context-injection only (no external delivery)"
  - "5-item cap applied before any delivery — overflow count noted in daily brief rather than suppressed silently"
  - "Stale follow-up threshold is 7 days (file mtime check via stat on macOS)"
  - "macOS notification is single consolidated count, not per-item, to reduce fatigue"
  - "Delivery failures log warning and continue — alert channel failures never block the briefing"

patterns-established:
  - "Alert routing pattern: collect all urgent items, sort by severity, cap at 5, then route each tier to appropriate channels"
  - "Anti-patterns section in skill.md is the canonical guard against misuse of session-start.sh"

# Metrics
duration: 1min
completed: 2026-03-15
---

# Phase 4 Plan 2: Severity-Based Alert Routing Summary

**Three-channel alert routing added to morning briefing: overdue items get Slack + macOS notification + daily brief; due-today get macOS + daily brief; stale follow-ups get daily brief only, capped at 5 items with overdue-first priority.**

## Performance

- **Duration:** ~1 min
- **Started:** 2026-03-15T04:40:34Z
- **Completed:** 2026-03-15T04:41:55Z
- **Tasks:** 2
- **Files modified:** 2

## Accomplishments

- Added Step 2.5 "Alert Routing (External Delivery)" to daily-digest skill with full routing logic
- Defined urgent item criteria (overdue, due-today, stale follow-ups) and 5-item cap with overflow annotation
- Routing table specifies exactly which channels each severity tier reaches (Slack only for overdue, consolidated macOS notification for overdue+due-today, daily brief for all)
- Updated Anti-Patterns section with 4 new guards against double-firing and cap violations
- Updated /today command with new step 5 and dedicated Alert Routing section with routing table

## Task Commits

Each task was committed atomically:

1. **Task 1: Add alert routing to daily-digest skill** - `9edf5f4` (feat)
2. **Task 2: Update /today command documentation** - `7a030b0` (docs)

**Plan metadata:** (forthcoming docs commit)

## Files Created/Modified

- `.claude/skills/surfacing/daily-digest/skill.md` - Added Step 2.5 with alert routing logic, routing table, Slack/osascript delivery specs, error handling, and 4 new anti-patterns
- `.claude/commands/today.md` - Added step 5 to "What It Does" and new "Alert Routing" section with routing table and behavior notes

## Decisions Made

- Alert routing lives exclusively in skill Step 2.5 — session-start.sh is context-injection only and must never be modified for external delivery
- 5-item cap applied before any delivery; overflow count appended to daily brief rather than silently dropped
- Stale follow-up detection uses file mtime (7-day threshold) via `stat -f "%Sm" -t "%s"` on macOS
- Single consolidated macOS notification with total count (not per-item) to minimize notification fatigue
- Delivery failures log warning to session output but never block the briefing

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required beyond the existing `SLACK_CHANNEL_ID` in `backend/_scripts/.env` (set up in prior phases).

## Next Phase Readiness

- Alert routing is complete and guarded against double-firing
- Daily-digest skill is now the single source of truth for all external delivery from the morning briefing
- Ready for Phase 4 Plan 3 (Insights Engine) or Plan 4 (Weekly Canvas)

---
*Phase: 04-proactive-layer*
*Completed: 2026-03-15*
