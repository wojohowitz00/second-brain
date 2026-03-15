# Phase 4: Proactive Layer - Context

**Gathered:** 2026-03-15
**Status:** Ready for planning

<domain>
## Phase Boundary

Build the observation and notification layer on top of the existing system. Three capabilities: (1) an insights skill that detects vault-wide patterns, (2) an alert routing system that delivers urgent items across channels, and (3) a Canvas visual weekly review board. Does NOT add new capture, task management, or recurring scheduling — those are separate phases.

</domain>

<decisions>
## Implementation Decisions

### Insights detection
- Skill runs as part of `/weekly` — not on session start, not a standalone command
- Staleness threshold: 14 days of no activity = neglected/dormant
- Goal drift triggers on EITHER: (a) domain with no activity in 14+ days while other domains have activity, OR (b) active tasks that don't map to any active project
- Overcommitment flag: 10+ active tasks triggers a warning

### Alert routing behavior
- Urgent item criteria: overdue tasks, stale follow-ups (people/waiting tasks with no activity in 7+ days), tasks due today
- Severity-based routing:
  - Overdue → all three channels (Slack + macOS notification + Obsidian daily note)
  - Due today → macOS notification + Obsidian daily note only
  - Stale follow-ups → Obsidian daily note only
- Cap: 5 items max per morning briefing
- Priority when capped: overdue first → due-today → stale
- Slack destination: dedicated channel (#second-brain or #alerts — confirm channel name during implementation)

### Canvas layout
- Organizing principle: swimlanes by status (active / waiting / blocked), project cards inside each lane
- Card content: project card + only blocked/overdue tasks surfaced — problem-focused, not full task list
- Update cadence: generated fresh on each `/weekly` run (Claude overwrites the canvas file)
- No "Wins" section — board is active/blocked work only

### Insight report format
- Insights: observation + recommendation (e.g., "Project X dormant 18 days — consider archiving or adding a next task")
- All insights link to specific notes using [[note-name]] Obsidian format
- Structure: grouped by insight type — sections for Goal Drift / Neglected Areas / Overcommitment / Dormant Projects
- Length: hard cap of 5–10 items — only the most important patterns surface

### Claude's Discretion
- Exact Canvas JSON structure and card positioning (spatial layout details)
- How to detect "no activity" (file mtime vs frontmatter last-modified)
- Slack API call implementation details
- macOS notification mechanism (terminal-notifier, osascript, etc.)

</decisions>

<specifics>
## Specific Ideas

- Canvas note lives in `05_AI_Workspace/canvas/` — already gated; validate Canvas JSON write capability before building (known risk flagged in STATE.md)
- Insights report saved to `05_AI_Workspace/insights/` with dated filename
- Alert routing is part of morning briefing logic, not a separate invocation

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 04-proactive-layer*
*Context gathered: 2026-03-15*
