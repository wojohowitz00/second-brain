# Requirements: Hybrid Brain OS

**Defined:** 2026-03-14
**Core Value:** Claude Code knows me deeply across sessions and proactively surfaces what matters

## v2 Requirements

Requirements for the hybrid evolution. Each maps to roadmap phases.

### Foundation

- [x] **FOUND-01**: AI Workspace folder (05_AI_Workspace) created in Obsidian vault with dashboards/, insights/, canvas/, daily-briefs/ subfolders and CLAUDE.md write rules
- [x] **FOUND-02**: PreToolUse hook that blocks Claude from writing to human PARA folders (01-04), exits with code 2 and explanation on violation
- [x] **FOUND-03**: Canonical YAML frontmatter schema document for people, projects, and tasks with Dataview-compatible field names
- [ ] **FOUND-04**: Claude Code persistent memory system initialized with user profile, vault conventions, preferences, and reference pointers

### Daily Workflow

- [ ] **DAILY-01**: Morning briefing skill that generates comprehensive daily briefing (overdue tasks, due today, follow-ups, calendar, automation opportunities) and outputs to 05_AI_Workspace/daily-briefs/
- [ ] **DAILY-02**: End-of-day update skill that syncs tasks, refreshes dashboards, captures session learnings to Claude Code memory
- [ ] **DAILY-03**: Session hooks — SessionStart surfaces stale tasks and upcoming deadlines, SessionEnd triggers dashboard refresh
- [ ] **DAILY-04**: Enhanced /new-task command with Dataview-compatible rich metadata (due, priority, project, domain, context tags)

### Proactive Layer

- [ ] **PROACT-01**: Insights skill that performs weekly vault-wide analysis detecting drift from goals, neglected areas, overcommitment, dormant projects
- [ ] **PROACT-02**: Alert routing system that delivers urgent items via Slack channel post + macOS notification + Obsidian daily note append
- [ ] **PROACT-03**: Dataview dashboard notes in 05_AI_Workspace/dashboards/ for productivity overview (tasks by status/priority) and project status (active projects with health indicators)
- [ ] **PROACT-04**: Canvas visual weekly review board in 05_AI_Workspace/canvas/ showing projects, tasks, and domains in spatial layout

## v3 Requirements

Deferred to future milestone. Tracked but not in current roadmap.

### People/CRM

- **CRM-01**: Structured contact records with rich YAML frontmatter (name, company, relationship, last_contact, follow_up_date, interaction_count)
- **CRM-02**: 360-degree people hub with Dataview queries aggregating meetings, tasks, and mentions per person
- **CRM-03**: Follow-up monitoring with proactive alerts when contacts go cold (30+ days) or follow-ups are overdue
- **CRM-04**: CRM dashboard note with Dataview tables showing overdue follow-ups, contact health, interaction history

## Out of Scope

| Feature | Reason |
|---------|--------|
| External database (Supabase, SQLite) | Using Obsidian-native YAML + Dataview; data locality constraint |
| React dashboards / web apps | Obsidian notes + Canvas only; single-app UX goal |
| MCP server development | Using existing file system access and Slack integration |
| Mobile app | Obsidian mobile handles vault access |
| Multi-user / team features | Personal system only |
| Modifying Python backend | v1.0 is mature and stable (259 tests) |
| Auto-tagging without human review | Creates collector's fallacy; AI suggests, human confirms |
| Full vault context loading | Destroys performance; keep progressive loading discipline |
| Perfect taxonomy upfront | Start with PARA; add schema fields when real use cases demand |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| FOUND-01 | Phase 1 | Complete |
| FOUND-02 | Phase 1 | Complete |
| FOUND-03 | Phase 1 | Complete |
| FOUND-04 | Phase 2 | Pending |
| DAILY-01 | Phase 3 | Pending |
| DAILY-02 | Phase 3 | Pending |
| DAILY-03 | Phase 2 | Pending |
| DAILY-04 | Phase 3 | Pending |
| PROACT-01 | Phase 4 | Pending |
| PROACT-02 | Phase 4 | Pending |
| PROACT-03 | Phase 3 | Pending |
| PROACT-04 | Phase 4 | Pending |

**Coverage:**
- v2 requirements: 12 total
- Mapped to phases: 12
- Unmapped: 0 ✓

---
*Requirements defined: 2026-03-14*
*Last updated: 2026-03-14 after initial definition*
