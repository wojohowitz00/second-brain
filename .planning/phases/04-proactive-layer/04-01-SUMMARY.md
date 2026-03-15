---
phase: 04-proactive-layer
plan: 01
subsystem: insights
tags: [insights, pattern-detection, weekly-review, dormant-projects, goal-drift]

# Dependency graph
requires:
  - phase: 03-core-daily-skills
    provides: weekly-review skill and /weekly command to integrate with
provides:
  - Vault-wide insights detection skill with four pattern rules
  - Updated /weekly workflow with insights step between Identify Patterns and Generate Review
  - Dated insights reports written to 05_AI_Workspace/insights/
affects:
  - 04-proactive-layer (subsequent plans build on insights skill)
  - /weekly command (now includes insights detection step)

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Insight cap pattern: hard 5-10 item limit with priority-ordered truncation"
    - "Detection tag pattern: PROACT-01 applied to all four rules for traceability"
    - "Wikilink output pattern: all insight references use [[note-name]] format"
    - "Skip-silently pattern: tasks without project field skip goal drift check"

key-files:
  created:
    - .claude/skills/surfacing/insights/skill.md
  modified:
    - .claude/skills/surfacing/weekly-review/skill.md
    - .claude/commands/weekly.md

key-decisions:
  - "Insights run only as part of /weekly — not standalone, not on session start (per CONTEXT.md)"
  - "14-day staleness threshold for both dormant projects and neglected areas"
  - "Overcommitment threshold: 10+ active tasks"
  - "Goal drift: skip tasks with empty/missing project field silently — absence of linkage is not drift"
  - "Hard cap 5-10 items, prioritized: overcommitment > goal drift > dormant > neglected"
  - "Do NOT use Dataview queries — Claude reads files directly via bash stat/grep"

patterns-established:
  - "Insights output to 05_AI_Workspace/insights/YYYY-MM-DD-insights.md with bare ISO dates"
  - "Weekly review references insights report via [[YYYY-MM-DD-insights]] wikilink"
  - "Skill integration via explicit step reference (step 5a) in workflow document"

# Metrics
duration: 1min 20sec
completed: 2026-03-15
---

# Phase 4 Plan 01: Vault-Wide Insights Detection Summary

**Skill-based vault pattern detector with four rules (dormant projects, neglected areas, overcommitment, goal drift) integrated as step 5a in the /weekly workflow**

## Performance

- **Duration:** 1 min 20 sec
- **Started:** 2026-03-15T04:39:55Z
- **Completed:** 2026-03-15T04:41:15Z
- **Tasks:** 2
- **Files modified:** 3

## Accomplishments

- Created insights detection skill with all four PROACT-01 detection rules, 14-day thresholds, and 5-10 item cap
- Integrated insights step (5a) into weekly-review skill between Identify Patterns and Generate Review
- Updated /weekly command with Insights Detection section documenting behavior and output path

## Task Commits

1. **Task 1: Create insights detection skill** - `3785455` (feat)
2. **Task 2: Integrate insights into weekly review workflow** - `81b3087` (feat)

**Plan metadata:** (docs commit below)

## Files Created/Modified

- `.claude/skills/surfacing/insights/skill.md` — New insights detection skill (165 lines), four detection rules with macOS-specific stat commands, error handling, anti-patterns
- `.claude/skills/surfacing/weekly-review/skill.md` — Added step 5a and insights skill dependency
- `.claude/commands/weekly.md` — Added Insights Detection section with output path and behavior description

## Decisions Made

- Insights run only as part of /weekly, never standalone — per CONTEXT.md to prevent noise on session start
- Tasks with empty/missing `project` field skip goal drift silently — absence of linkage is not drift
- Hard cap of 5-10 items with priority order: overcommitment > goal drift > dormant projects > neglected areas
- Claude reads files directly (bash stat/grep) rather than using Dataview — this is a Claude analysis skill, not a vault query

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Insights detection skill ready for use in /weekly invocations
- 05_AI_Workspace/insights/ directory will be created on first run (Claude writes files there)
- Phase 4 Plan 02 (alert routing) and Plan 03 (Canvas weekly review) can now proceed
- Canvas plan still flagged LOW confidence on Canvas JSON write patterns — validate before executing

---
*Phase: 04-proactive-layer*
*Completed: 2026-03-15*
