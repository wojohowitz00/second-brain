# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-03-14)

**Core value:** Claude Code knows me deeply across sessions and proactively surfaces what matters
**Current focus:** Phase 4 — Proactive Layer (COMPLETE)

## Current Position

Phase: 4 of 4 (Proactive Layer) — Complete
Plan: 3 of 3 in current phase
Status: All phases complete — v2.0 Hybrid Brain OS milestone reached
Last activity: 2026-03-15 — Completed 04-03-PLAN.md: Canvas visual weekly review skill

Progress: [██████████] 100% (12/12 total plans)

## Performance Metrics

**Velocity:**
- Total plans completed: 9
- Average duration: ~1.5 minutes
- Total execution time: ~13.5 minutes

**By Phase:**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| 01-foundation | 3/3 | ~6.5 min | ~2.2 min |
| 02-memory-and-session-context | 2/2 | ~2.2 min | ~1.1 min |
| 03-core-daily-skills | 4/4 | ~4.3 min | ~1.1 min |
| 04-proactive-layer | 3/3 | ~4.6 min | ~1.5 min |

**Recent Trend:**
- Last 5 plans: 03-04 (60s), 04-01 (80s), 04-02 (81s), 04-03 (~90s)
- Trend: fast execution, consistently under 90 sec

*Updated after each plan completion*

## Accumulated Context

### Decisions

Decisions are logged in PROJECT.md Key Decisions table.
Recent decisions affecting current work:

- Foundation: AI writes ONLY to `05_AI_Workspace/` — enforced by PreToolUse hook before any skill has write capability
- Foundation: YAML frontmatter schema defined before any Dataview queries are built (prevents schema lock-in)
- Foundation: Claude Code memory (not vault files) stores cross-session preferences and patterns
- 01-01: CLAUDE.md files serve dual purpose — write policy docs AND iCloud directory sync anchors (empty dirs don't sync)
- 01-01: canvas/ subfolder gated behind Phase 4 research; documented in canvas/CLAUDE.md to prevent premature use
- 01-02: Hook registered in settings.json (committed), not settings.local.json (machine-local) — ensures hook ships with the project
- 01-02: Bash blocking in the hook is best-effort; Write/Edit are the primary enforcement points
- 01-03: Date fields must be bare ISO format (no quotes) — quoted dates become TEXT in Dataview, breaking date queries
- 01-03: Schema is additive — no existing template fields removed or renamed; new fields are optional
- 02-01: MEMORY.md kept under 200 lines (45 lines) — Claude Code auto-load limit
- 02-01: Post-compaction re-injection requires no additional code; CLAUDE.md + MEMORY.md both reloaded automatically after compaction
- 02-01: MEMORY.md stores learned facts; CLAUDE.md stores rules — complementary, not overlapping
- 02-02: Session hooks registered in global ~/.claude/settings.json (not project-level), consistent with bd prime pattern
- 02-02: SessionStart plain-text output (not JSON) — injected directly into Claude context, clearest for model comprehension
- 02-02: Silent exit 0 when no items to report — avoids context noise when tasks are healthy
- 03-02: Hook handles mechanical writes (timestamp only); EOD skill handles interactive reflection — clean separation of concerns
- 03-02: Day Summary idempotent via grep check — multiple sessions same day produce at most one Day Summary header
- 03-02: projects-health.md refresh added proactively to session-end.sh (Plan 03-04 creates the file)
- 03-03: Default task status is `backlog` (not `active`) — tasks start unscheduled until user deliberately promotes them
- 03-03: Omit fields with no signal — no empty values in frontmatter, cleaner notes and avoids Dataview null-matching edge cases
- 03-03: Post-creation notes offer is exactly one prompt — no loop, preserves command velocity
- 03-03: Quick mode takes title verbatim — no inference, no prompts, optimized for speed over richness
- 03-04: FROM "" + WHERE type filter is the correct Dataview pattern for vault-external files (tasks/projects in project root)
- 03-04: SORT before GROUP BY ensures intra-group ordering in Dataview queries
- 03-04: file.mtime stale detection avoids complex cross-file JOINs for project staleness
- 03-01: Skill files are instruction documents for Claude — no test harness needed; correctness is verified by reading the spec
- 03-01: Morning brief uses static markdown tables (not Dataview) — brief is a snapshot at invocation time, not a live view
- 03-01: Idempotent daily output: overwrite same-day file; daily-briefs are one-file-per-day
- 03-01: Automation opportunities = actionable offers Claude can execute right now, not passive observations
- 04-01: Insights run only as part of /weekly — not standalone, not on session start
- 04-01: Goal drift skips tasks with empty/missing project field silently — absence of linkage is not drift
- 04-01: Insights hard cap 5-10 items, prioritized: overcommitment > goal drift > dormant projects > neglected areas
- 04-01: Claude reads files directly (bash stat/grep) for insights — not Dataview queries
- 04-02: Alert routing lives ONLY in skill Step 2.5 — session-start.sh remains context-injection only (no external delivery)
- 04-02: 5-item cap applied before any delivery; overflow count appended to daily brief rather than silently dropped
- 04-02: Stale follow-up detection uses file mtime (7-day threshold) via stat on macOS
- 04-02: Single consolidated macOS notification (not per-item) to minimize notification fatigue
- 04-03: Canvas is problem-focused — shows only blocked/overdue tasks per project, not full workload
- 04-03: Deterministic node IDs (lane-{status}, proj-{filename}) make canvas diffable week over week in git
- 04-03: No Wins/Completed lane — board shows active/blocked work only; review doc handles completed items
- 04-03: Canvas step placed as 5b — after insights (5a) and before Generate Review (6)

### Pending Todos

None yet.

### Blockers/Concerns

- Phase 3 (Dataview iOS): Dashboard notes used on mobile must be tested on iOS before Phase 3 ships — known macOS/iOS query inconsistencies exist.
- 01-03 (Human verify): ✓ Dataview dashboard rendering verified in Obsidian (2026-03-14).
- 04-03 (Canvas validation): Skill document defines JSON Canvas v1.0 format; first real /weekly run will validate Obsidian renders it correctly. Low risk — spec is well-defined.

## Session Continuity

Last session: 2026-03-15
Stopped at: Completed 04-03-PLAN.md — Canvas visual weekly review skill. All 12 plans complete.
Resume file: None
