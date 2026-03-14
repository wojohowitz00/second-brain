---
phase: 03-core-daily-skills
plan: 04
subsystem: ui
tags: [dataview, obsidian, dashboards, tasks, projects]

# Dependency graph
requires:
  - phase: 01-foundation
    provides: YAML frontmatter schema with type/status/priority/health fields
  - phase: 02-memory-and-session-context
    provides: session-end.sh hook that updates refreshed_by frontmatter
provides:
  - Live task dashboard grouped by status with priority/due-date sorting
  - Live project health dashboard with stale detection
  - Both dashboards use FROM "" pattern for vault-external file handling
affects: [03-core-daily-skills, 04-canvas-weekly-review, session-end-hook]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "FROM \"\" with WHERE type filter — handles notes outside vault folder structure"
    - "SORT before GROUP BY — ensures intra-group sort order in Dataview"
    - "file.mtime stale detection — no-activity threshold without JOIN queries"

key-files:
  created:
    - "05_AI_Workspace/dashboards/projects-health.md"
  modified:
    - "05_AI_Workspace/dashboards/tasks-by-status.md"

key-decisions:
  - "FROM \"\" scans all vault notes — required because tasks/projects live outside vault folder"
  - "SORT placed before GROUP BY — Dataview evaluates sort within groups this way"
  - "health ASC sort in Active Projects — alphabetical (green < red < yellow) is acceptable for now"
  - "file.mtime stale detection — avoids complex cross-file JOINs, uses implicit Dataview field"

patterns-established:
  - "Dashboard pattern: type=dashboard frontmatter, three query sections, refreshed_by field"
  - "Query pattern: FROM \"\" + WHERE type filter for all vault-external content"

# Metrics
duration: 1min
completed: 2026-03-15
---

# Phase 3 Plan 4: Dataview Dashboards Summary

**Live Dataview task dashboard (Overdue/Due This Week/All by Status) and project health dashboard (Active/Stale/All) using FROM "" pattern for vault-external files**

## Performance

- **Duration:** ~1 min
- **Started:** 2026-03-14T23:08:01Z
- **Completed:** 2026-03-14T23:08:56Z
- **Tasks:** 2
- **Files modified:** 2 (vault files outside git)

## Accomplishments
- Replaced Phase 1 stub `tasks-by-status.md` with three-section live Dataview dashboard
- Created new `projects-health.md` with active projects, stale detection, and all-projects views
- Both dashboards use `FROM ""` with `WHERE type =` filter — the correct pattern for content outside vault folder structure

## Task Commits

Each task was committed atomically:

1. **Task 1: Replace tasks-by-status dashboard** - `ce1b91e` (feat)
2. **Task 2: Create projects-health dashboard** - `4acb56a` (feat)

**Plan metadata:** (included in final commit below)

## Files Created/Modified
- `05_AI_Workspace/dashboards/tasks-by-status.md` (vault) - Three Dataview sections: Overdue, Due This Week, All Tasks by Status grouped by status
- `05_AI_Workspace/dashboards/projects-health.md` (vault) - Three Dataview sections: Active Projects, Stale Projects (7+ days), All Projects

## Decisions Made
- Used `FROM ""` with `WHERE type = "task"/"project"` — tasks and projects live in project root outside Obsidian vault, so `FROM "tasks"` returns zero results
- Placed `SORT priority DESC, due_date ASC` before `GROUP BY status` — Dataview evaluates sort within each group
- Used `health ASC` sort for Active Projects — alphabetical ordering (green first) is acceptable; avoids complexity
- Used `file.mtime` for stale detection — implicit Dataview field, no cross-file JOIN needed

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered
- Shell verification commands with spaces in path failed in bash (iCloud path contains spaces). Verified using Read tool directly instead. Files confirmed correct.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness
- Both dashboards ready for use in Obsidian
- `refreshed_by` field in place for `session-end.sh` to update via sed
- Phase 3 plans 01-03 (today-skill, writing-buddy, research-engine) can proceed independently
- Known concern: iOS Dataview rendering should be tested before Phase 3 ships (logged in STATE.md)

---
*Phase: 03-core-daily-skills*
*Completed: 2026-03-15*
