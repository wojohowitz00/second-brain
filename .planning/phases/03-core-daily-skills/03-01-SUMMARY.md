---
phase: 03-core-daily-skills
plan: 01
subsystem: skills
tags: [morning-briefing, daily-brief, daily-digest, vault-write, dataview, tasks, people, projects]

# Dependency graph
requires:
  - phase: 01-foundation
    provides: 05_AI_Workspace write policy, YAML frontmatter schema (bare ISO dates, type field)
  - phase: 02-memory-and-session-context
    provides: session hooks infrastructure (SessionEnd will append Day Summary to daily-brief)
provides:
  - Morning briefing skill spec (daily-digest/skill.md) with orient-first structure
  - Updated /today command pointing to morning briefing skill
  - Vault output path 05_AI_Workspace/daily-briefs/YYYY-MM-DD-daily-brief.md
  - Static markdown brief with At a Glance counts, task tables, follow-ups, active projects, automation opportunities
affects:
  - 03-02 (EOD update): appends Day Summary to the same daily-brief note this plan creates
  - 03-03 (task creation): /new-task skill feeds tasks that morning briefing reads
  - 03-04 (Dataview dashboards): daily-brief frontmatter (type: daily-brief) queryable by dashboards

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Skill files are instruction documents for Claude, not executable code"
    - "Morning brief is idempotent: overwrite if file exists for today (one file per day)"
    - "Static markdown tables in vault notes — no Dataview queries in skill output"
    - "Orient-first: At a Glance summary counts before any detail lists"

key-files:
  created: []
  modified:
    - .claude/skills/surfacing/daily-digest/skill.md
    - .claude/commands/today.md

key-decisions:
  - "Skill.md is an instruction file not code — Claude reads it to know how to behave when /today is invoked"
  - "daily/ folder deprecated — output goes to 05_AI_Workspace/daily-briefs/ per vault write policy"
  - "Slack DM step removed from /today — deferred to a later phase"
  - "Inbox processing removed from /today — that is a separate skill"
  - "Static markdown tables (not Dataview queries) for brief content — brief is a snapshot, not a live view"

patterns-established:
  - "Orient-first pattern: summary counts header before detail sections"
  - "Section omission pattern: skip entire section when no data, no empty placeholders"
  - "Automation opportunities = actionable offers Claude can execute right now, not passive observations"
  - "Idempotent daily output: overwrite same-day file rather than appending or failing"

# Metrics
duration: 1m 16s
completed: 2026-03-14
---

# Phase 3 Plan 01: Morning Briefing Skill Summary

**Morning briefing skill rewritten with orient-first structure (At a Glance counts), static markdown tables for tasks/people/projects, vault output to 05_AI_Workspace/daily-briefs/, and focused /today command**

## Performance

- **Duration:** 1m 16s
- **Started:** 2026-03-14T23:07:32Z
- **Completed:** 2026-03-14T23:08:48Z
- **Tasks:** 2
- **Files modified:** 2

## Accomplishments

- Rewrote daily-digest skill as a morning briefing spec: reads tasks, people, projects; writes dated vault note; injects conversational session summary
- Updated /today command to be clean and focused: just invoke the morning briefing skill (Slack DM and inbox processing removed)
- Established orient-first pattern: At a Glance summary header appears before any detail lists

## Task Commits

Each task was committed atomically:

1. **Task 1: Rewrite daily-digest skill.md as morning briefing** - `e106f09` (feat)
2. **Task 2: Update /today command to invoke morning briefing skill** - `0b66f20` (feat)

**Plan metadata:** (docs commit follows)

## Files Created/Modified

- `.claude/skills/surfacing/daily-digest/skill.md` - Rewritten as morning briefing skill: data sources (tasks/people/projects), vault output path, note structure with all 7 sections, session summary instructions, anti-patterns
- `.claude/commands/today.md` - Simplified to 22-line command file pointing to morning briefing skill; Slack DM and inbox steps removed

## Decisions Made

- Skill files are instruction documents for Claude, not executable code — this means no test harness needed
- `daily/` folder is deprecated; all output routes to `05_AI_Workspace/daily-briefs/` per vault write policy from Phase 1
- Slack DM step explicitly deferred to a later phase (documented in anti-patterns section)
- Static markdown tables chosen over Dataview queries for the brief — a brief is a snapshot captured at time of invocation, not a live view
- Idempotent daily output: if today's file exists, overwrite it rather than appending or erroring

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Morning briefing skill is ready to invoke via `/today`
- Vault output path `05_AI_Workspace/daily-briefs/YYYY-MM-DD-daily-brief.md` is set and documented
- Plan 03-02 (EOD update) can build directly on this: it appends `## Day Summary` to the file this skill creates
- The `<!-- Day Summary will be appended by session-end hook -->` comment in the note template provides the insertion anchor for Plan 03-02

---
*Phase: 03-core-daily-skills*
*Completed: 2026-03-14*
