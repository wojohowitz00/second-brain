# Phase 3: Core Daily Skills - Context

**Gathered:** 2026-03-14
**Status:** Ready for planning

<domain>
## Phase Boundary

Deliver the four skills that form the daily rhythm: morning briefing, end-of-day update, enhanced task creation, and Dataview dashboards. All four are invoked and read daily. Phase goal: the daily rhythm of starting work, capturing tasks, and closing out the day is fully automated and Dataview-queryable.

Creating posts, proactive pattern detection, and alert routing are separate phases.

</domain>

<decisions>
## Implementation Decisions

### Morning briefing structure
- Orient-first: summary header (X tasks due, Y overdue, Z follow-ups) before the detail list
- Each task entry shows: title + status + project (not full context block, not title-only)
- "Automation opportunities" section = tasks Claude could act on right now (e.g. "3 tasks marked waiting — want me to draft follow-ups?"), not passive observations
- Output: BOTH a vault note (05_AI_Workspace/daily-briefs/YYYY-MM-DD-brief.md) AND summary injected into session context at start

### End-of-day update
- Invocation: automatic at SessionEnd — fires whenever Claude Code session closes
- Data: auto-detect facts (task status changes, session activity) + ask one optional reflection question
- Session learnings captured to MEMORY.md: both decisions/rationale (continuity) and patterns/preferences (personalization)
- Vault write: appends a "## Day Summary" section to the existing daily-brief note for that day (not a separate file)

### Task creation (/new-task)
- Interaction: natural language — user describes in plain English, Claude extracts fields
- Required minimum: title only — everything else optional
- After creation: confirm + offer to add notes ("Want to add any notes or context?")
- Quick capture variant: /new-task quick — zero-friction, title only, status defaults to backlog, no prompts

### Dataview dashboards
- Task dashboard: sorted by priority then due date within each status group
- Project dashboard: "at risk" = has overdue tasks OR no activity in 7+ days (both signals)
- Filter: show everything (all statuses, all projects) — no default filter
- Usage pattern: reference when needed (not daily home base) — can be detailed rather than optimized for glanceability

### Claude's Discretion
- Exact Dataview query syntax and column layout
- Morning brief formatting details (emoji usage, section separators)
- How "one optional reflection question" is phrased at EOD
- Timeout behavior for the auto SessionEnd hook (must be fast)
- How /new-task parses ambiguous natural language (e.g. "do X by end of week")

</decisions>

<specifics>
## Specific Ideas

- Morning brief should feel like a situation report, not a to-do list — orient first, then act
- EOD "Day Summary" appended to the morning brief keeps one note per day as the complete record of that day
- Quick capture (/new-task quick) is intentionally minimal — the point is zero friction, details added later

</specifics>

<deferred>
## Deferred Ideas

- None — discussion stayed within phase scope

</deferred>

---

*Phase: 03-core-daily-skills*
*Context gathered: 2026-03-14*
