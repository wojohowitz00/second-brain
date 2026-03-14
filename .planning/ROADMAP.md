# Roadmap: Hybrid Brain OS

## Overview

This milestone evolves the existing Second Brain into a proactive AI operating system. Starting from a stable v1.0 foundation (Python backend, Obsidian vault, 9 Claude Code skills), four phases add the architectural layer that makes the system self-aware: a protected AI workspace, cross-session memory, daily workflow skills, and a proactive pattern-detection layer. Each phase builds directly on the previous — the write boundary must exist before skills write, memory must exist before skills are context-aware, daily skills must run before proactive detection has signal to analyze.

## Milestones

- 🚧 **v2.0 Hybrid Brain OS** — Phases 1-4 (in progress)

## Phases

- [ ] **Phase 1: Foundation** — AI workspace folder, write boundary enforcement, and canonical YAML schema
- [ ] **Phase 2: Memory and Session Context** — Persistent cross-session memory and session lifecycle hooks
- [ ] **Phase 3: Core Daily Skills** — Morning briefing, end-of-day update, enhanced task creation, and dashboards
- [ ] **Phase 4: Proactive Layer** — Insights detection, alert routing, and visual canvas review

## Phase Details

### Phase 1: Foundation

**Goal:** The vault has a protected AI writing area and a canonical data schema, making every subsequent AI write safe and queryable.

**Depends on:** Nothing (first phase)

**Requirements:** FOUND-01, FOUND-02, FOUND-03

**Success Criteria** (what must be TRUE):
1. An `05_AI_Workspace/` folder exists in the Obsidian vault with `dashboards/`, `insights/`, `canvas/`, and `daily-briefs/` subfolders, each containing a `CLAUDE.md` write policy
2. Any attempt by Claude to write a file into folders `01_`, `02_`, `03_`, or `04_` is blocked automatically before the write occurs, with an explanation of the violation
3. A canonical YAML frontmatter schema document exists defining field names, types, and example values for people, project, and task notes — and it is referenced from the vault CLAUDE.md
4. A skeleton Dataview dashboard note exists in `05_AI_Workspace/dashboards/` that successfully renders at least one live query (tasks by status)

**Plans:** TBD

Plans:
- [ ] 01-01: Create AI workspace folder structure and write policy
- [ ] 01-02: Implement PreToolUse hook for vault write boundary enforcement
- [ ] 01-03: Define and publish canonical YAML frontmatter schema

---

### Phase 2: Memory and Session Context

**Goal:** Claude knows who I am at the start of every session and automatically surfaces stale work without being asked.

**Depends on:** Phase 1

**Requirements:** FOUND-04, DAILY-03

**Success Criteria** (what must be TRUE):
1. Claude Code memory is initialized with vault conventions, user preferences, and reference pointers — and this context is available at the start of a fresh session without manual re-loading
2. When a new Claude Code session starts, stale tasks (overdue or untouched for 7+ days) and upcoming deadlines are surfaced automatically in the session context
3. When a Claude Code session ends, dashboard notes in `05_AI_Workspace/dashboards/` are refreshed automatically without the user invoking a command
4. After a context compaction event, critical vault conventions are re-injected so Claude does not lose working knowledge of the system

**Plans:** TBD

Plans:
- [ ] 02-01: Initialize Claude Code memory structure with vault profile and preferences
- [ ] 02-02: Implement SessionStart and SessionEnd hooks

---

### Phase 3: Core Daily Skills

**Goal:** The daily rhythm of starting work, capturing tasks, and closing out the day is fully automated and Dataview-queryable.

**Depends on:** Phase 2

**Requirements:** DAILY-01, DAILY-02, DAILY-04, PROACT-03

**Success Criteria** (what must be TRUE):
1. Invoking the morning briefing skill (or having it triggered by session start) produces a dated briefing note in `05_AI_Workspace/daily-briefs/` covering overdue tasks, items due today, follow-ups needing attention, and automation opportunities
2. Invoking the end-of-day update skill syncs task statuses, refreshes dashboards, and appends a session learnings entry to Claude Code memory
3. Creating a task via `/new-task` produces a note with Dataview-compatible frontmatter fields (due, priority, project, domain, context tags) that appears correctly in the productivity dashboard Dataview queries
4. Two live Dataview dashboard notes exist in `05_AI_Workspace/dashboards/` — one showing tasks by status and priority, one showing active projects with health indicators — and both render correctly in Obsidian

**Plans:** TBD

Plans:
- [ ] 03-01: Build morning briefing skill writing to `05_AI_Workspace/daily-briefs/`
- [ ] 03-02: Build end-of-day update skill with memory capture
- [ ] 03-03: Enhance `/new-task` with Dataview-compatible rich metadata
- [ ] 03-04: Build productivity and project status dashboard notes with Dataview queries

---

### Phase 4: Proactive Layer

**Goal:** The system proactively surfaces patterns, alerts, and visual overviews — the user receives insight without asking.

**Depends on:** Phase 3

**Requirements:** PROACT-01, PROACT-02, PROACT-04

**Success Criteria** (what must be TRUE):
1. Running the insights skill performs a vault-wide analysis and produces a report in `05_AI_Workspace/insights/` that identifies at least one of: goal drift, neglected areas, overcommitment, or dormant projects — with specific note references
2. An urgent item (overdue task, stale follow-up) triggers a notification delivered via all three channels: a Slack channel post, a macOS system notification, and an append to the Obsidian daily note
3. A Canvas visual weekly review board exists in `05_AI_Workspace/canvas/` showing active projects, open tasks, and domains in a spatial layout — and it opens correctly in Obsidian's Canvas view
4. Alert volume is bounded — no more than 5 alert items surface in a single morning briefing, preventing alert fatigue from the start

**Plans:** TBD

Plans:
- [ ] 04-01: Build insights skill with vault-wide pattern detection
- [ ] 04-02: Implement alert routing to Slack, macOS notifications, and Obsidian daily note
- [ ] 04-03: Build Canvas visual weekly review template and generation skill

---

## Progress

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Foundation | 0/3 | Not started | - |
| 2. Memory and Session Context | 0/2 | Not started | - |
| 3. Core Daily Skills | 0/4 | Not started | - |
| 4. Proactive Layer | 0/3 | Not started | - |

---

*Roadmap created: 2026-03-14*
*Milestone: v2.0 Hybrid Brain OS*
*Coverage: 12/12 v2 requirements mapped*
