# Project Research Summary

**Project:** Hybrid Brain OS — Proactive AI Monitoring Layer on Existing Second Brain
**Domain:** AI-powered personal knowledge management OS (Obsidian + Claude Code)
**Researched:** 2026-03-14
**Confidence:** HIGH

## Executive Summary

This project adds a proactive AI layer to an existing Obsidian-based Second Brain system. The foundation (Python capture backend, Ollama classification, Slack integration, 9 Claude Code skills, 259 tests) is mature and stays unchanged. The new milestone extends the system in three directions: persistent cross-session memory, structured data with YAML frontmatter and Dataview dashboards, and a proactive notification layer (morning briefings, session hooks, pattern detection). Research across all four dimensions points to the same architectural principle: the AI writes only to a dedicated `05_AI_Workspace/` folder and reads everywhere else. This boundary is not optional — it is the load-bearing constraint that keeps the human-authored vault trustworthy.

The recommended approach is additive and dependency-ordered. The YAML frontmatter schema must be defined before any Dataview queries are built. The `05_AI_Workspace/` folder and its write-boundary enforcement (via a `PreToolUse` hook) must exist before any AI skills are given write capability. Memory and session hooks come next, enabling cross-session continuity. Only then do proactive skills (morning briefing, pattern detection, alert routing) get built on top of this stable base. This ordering is not just a preference — it prevents the system's most severe pitfall, vault pollution, from ever occurring.

The primary risks are vault integrity loss from premature AI writes, YAML schema lock-in from iterating without a canonical document, and iCloud sync race conditions on file writes. All three are addressed by the phase ordering recommended below. Secondary risks — context window bloat, hook reliability, alert fatigue, and CLAUDE.md over-specification — are real but recoverable if caught early. The research confidence is HIGH across all four dimensions because the core stack (Claude Code, Dataview, Obsidian hooks) is verified against official documentation.

---

## Key Findings

### Recommended Stack

The Claude Code layer (CLAUDE.md hierarchy, skills, hooks, auto memory) combined with Obsidian's Dataview plugin and YAML frontmatter covers all requirements without any external services or databases. Claude Code ≥ 2.1.59 is required for auto memory. Dataview 0.5.70 is in maintenance mode but stable and sufficient — Obsidian Bases is Catalyst-only and not yet production-ready. Skills should live in `~/.claude/skills/` (personal scope) since they encode personal workflow knowledge. Hooks in `.claude/settings.json` provide deterministic automation that CLAUDE.md instructions cannot guarantee.

**Core technologies:**
- **CLAUDE.md + `.claude/rules/`**: Session-persistent instructions — keep under 100 lines total; use `@imports` and scoped rules to avoid bloat
- **Claude Code Skills** (`~/.claude/skills/`): On-demand workflow execution with `disable-model-invocation: true` for side-effect workflows; context loaded only at invocation
- **Claude Code Hooks** (SessionStart, PreToolUse, PostToolUse, Stop): Deterministic lifecycle automation; `startup` matcher for new-session-only triggers; `PreToolUse` for vault boundary enforcement
- **Claude Code Auto Memory** (`~/.claude/projects/.../memory/MEMORY.md`): Cross-session preference and pattern persistence; 200-line limit on MEMORY.md index; topic files for details
- **Dataview plugin** (0.5.70): Live YAML-backed table and task queries; always specify `FROM` clause; avoid inline fields in favor of YAML frontmatter
- **YAML frontmatter (Obsidian Properties)**: Single source of truth for all structured data; lowercase field names; canonical schema document required before building queries
- **macOS osascript + Slack webhook**: Alert delivery; existing Slack integration in Python backend is reusable

**Do not use:** Obsidian Bases (early access), Datacore (beta), external databases, React dashboards, MCP server for vault access (Claude Code reads filesystem directly), inline Dataview fields.

### Expected Features

The existing system handles capture, classification, and 9 interactive skills. This milestone needs to feel like a proactive OS, not a reactive tool. The critical path for the MVP is: YAML schema → AI workspace folder → persistent memory → morning briefing → session hooks → people/CRM → proactive pattern detection.

**Must have (table stakes):**
- Persistent AI memory across sessions — without this, the "knows me deeply" promise fails
- Morning briefing generation — daily orientation pulling vault tasks, follow-ups, open items
- Structured contact records with YAML schema — CRM is unusable without consistent fields
- Dataview-powered dashboards — queryable views over people, projects, tasks
- YAML frontmatter schema for people, projects, tasks — foundation for every query
- AI workspace separation (`05_AI_Workspace/`) — architectural must-have before any AI writes
- Session hooks (SessionStart / SessionEnd) — eliminates manual invocation of briefings and updates

**Should have (differentiators):**
- Proactive pattern detection — surfaces "you haven't followed up with X in 30 days"
- 360-degree people hub — aggregated relationship context from all vault mentions
- Alert routing (Slack + macOS + Obsidian daily note) — delivers outputs where user already is
- Canvas-based visual weekly review — spatial layout of projects, people, tasks
- Skills as institutional memory — each skill encodes a repeatable personal process

**Defer to post-MVP:**
- Enhanced task metadata richness — add fields only when real use cases demand them
- Daily news briefing integration — generic external briefings are a commodity; personal context is the differentiator
- Multi-agent separation by domain — useful but complex; start with single agent + domain-specific skills

### Architecture Approach

The system has three existing layers (Obsidian vault as human knowledge store, Claude Code interactive layer, Python automated capture backend) and adds a fourth Proactive Layer. All components communicate through the file system — there is no API between layers, which is a deliberate data-locality constraint. The `05_AI_Workspace/` folder is the single AI write target, queryable by Dataview just like human PARA folders. YAML frontmatter is the contract layer between data producers (skills, hooks, humans) and data consumers (Dataview queries, dashboards). Changing a YAML field name without migrating all dependent queries is the highest-risk coupling point in the system.

**Major components:**
1. **`05_AI_Workspace/` (vault)** — AI content store with subfolders: `alerts/`, `digests/`, `dashboards/`, `research/`, `drafts/`; all files carry `generated_by`, `skill`, `date`, `status` frontmatter for Dataview auditability
2. **Claude Code hooks** — `PreToolUse` blocks AI writes to folders 01–04 (boundary enforcement); `SessionStart (startup)` injects vault state (overdue tasks, active projects, last digest date); `Stop` triggers optional dashboard refresh; `Notification` passes macOS alerts
3. **Claude Code memory** (`~/.claude/projects/.../memory/`) — MEMORY.md index (200-line limit) plus topic files (`preferences.md`, `patterns.md`, `vault-conventions.md`); stores durable preferences not transient task state
4. **Proactive skills** — `morning-briefing`, `alert-monitor`, `insights`, `eod-update`; each scoped to its own context files; single responsibility; context budget of ~5-10 files per skill
5. **Dataview dashboards** (`05_AI_Workspace/dashboards/`) — live YAML queries; every query has explicit `FROM` clause; 3-5 blocks per dashboard note maximum
6. **Python backend (unchanged)** — Slack capture → Ollama classification → PARA routing; 259 tests; do not modify

### Critical Pitfalls

1. **Vault pollution from AI writes to human PARA folders (01–04)** — Enforce `PreToolUse` hook that blocks writes to folders matching `01_|02_|03_|04_` before building any write-capable skills. All AI content goes to `05_AI_Workspace/` with `ai_generated: true` in frontmatter. This is irreversible if ignored at scale.

2. **YAML schema lock-in** — Write a canonical schema document before building any Dataview queries or skills that write frontmatter. Renaming a YAML field silently empties all dependent Dataview queries. Use namespaced property names (`person_type`, not `type`) to avoid collisions. Migration order: update schema doc → migrate notes → update queries (never queries first).

3. **iCloud sync race conditions** — Never overwrite existing vault notes in place. All skill writes must be append-only or write-to-new-file using atomic rename. Do not write to the same note from multiple simultaneous sources (e.g., session hook and background monitor both targeting the same daily note).

4. **Context window bloat** — Skills must load only their specific context files (`_llm-context/` pattern already in place). Never load full note contents or vault-wide dumps. If a skill reads more than ~10 files, redesign it. Use subagents for investigation tasks that report back summaries.

5. **Hook silent failures** — Hooks that fail non-critically do so silently (no user notification). All hooks must write a completion timestamp as their last action. Test hooks in verbose mode (`Ctrl+O`). Shell profiles that print on startup corrupt hook JSON parsing — add `[[ -z "$PS1" ]] && return` guards.

---

## Implications for Roadmap

Based on research, the phase ordering is driven by three hard dependencies: (1) the write boundary must exist before any AI write capability; (2) YAML schema must be defined before Dataview queries; (3) memory and hooks must be operational before proactive skills are valuable.

### Phase 1: Foundation — AI Workspace, Schema, and Write Boundary

**Rationale:** This phase must come first because every subsequent phase either writes to `05_AI_Workspace/` or queries YAML frontmatter. Building skills before the boundary hook is in place risks vault pollution that is difficult to reverse. Schema drift becomes exponentially more expensive to fix as notes accumulate.

**Delivers:** `05_AI_Workspace/` folder structure; canonical YAML frontmatter schema document; `PreToolUse` boundary enforcement hook; basic Dataview dashboard in `05_AI_Workspace/dashboards/`; pinned plugin versions documented.

**Addresses:** AI workspace separation, YAML schema for people/projects/tasks, Dataview dashboards (skeleton).

**Avoids:** Vault pollution (Pitfall 1), YAML schema lock-in (Pitfall 4), plugin compatibility breakage (Pitfall 8).

**Research flag:** Standard patterns — no additional research needed. Official docs cover all components.

### Phase 2: Memory and Session Context

**Rationale:** Persistent memory is the prerequisite for context-aware briefings. Session hooks require memory to inject meaningful state. This phase is independent of Phase 1's data layer (can run in parallel with Phase 1's schema work) but must precede any proactive skill that references past sessions.

**Delivers:** Memory directory structure with MEMORY.md + topic files; seed memory with vault conventions and key preferences; SessionStart hook (startup matcher) that injects vault state summary (overdue task count, active projects, last digest date); PostCompact hook re-injects critical conventions.

**Addresses:** Persistent AI memory across sessions, session hooks for stale task surfacing.

**Avoids:** Memory staleness (Pitfall 7) by designing timestamps and audit cadence from the start; context bloat (Pitfall 2) by keeping memory at durable preferences only.

**Research flag:** Standard patterns — Claude Code memory API is well-documented. Hook JSON format verified from official docs.

### Phase 3: Core Daily Skills (Briefing, People, EOD)

**Rationale:** With the workspace, schema, and memory in place, the high-value daily workflow skills can be built safely. Morning briefing is the most visible daily output. People/CRM delivers the 360-degree relationship context. EOD update closes the daily loop. All three write to `05_AI_Workspace/` and are now protected by Phase 1 boundary enforcement.

**Delivers:** Morning briefing skill (`~/.claude/skills/morning-briefing/`) writing to `05_AI_Workspace/digests/daily/`; structured contact records with YAML schema and Templater template; 360-degree people hub (Dataview query per person note); EOD update skill; SessionEnd hook triggering dashboard refresh.

**Addresses:** Morning briefing generation, structured contact records, meeting-to-person linkage, inbox triage enrichment, weekly review enrichment.

**Avoids:** Context bloat (each skill loads only its own context); skill scope creep (Pitfall 11) by keeping each skill single-responsibility from the start.

**Research flag:** Standard patterns for morning briefing and CRM fields (Obsibrain schema is well-documented). Deeper consideration needed for people hub Dataview query design — test on iOS before finalizing.

### Phase 4: Proactive Layer (Pattern Detection, Alerts, Canvas)

**Rationale:** This phase requires all prior phases to be operational. Pattern detection queries need the YAML schema (Phase 1), must write findings to `05_AI_Workspace/` (Phase 1 boundary), and needs session memory to compare current vs. past state (Phase 2). Alert routing extends the existing Slack integration. Canvas visual review is additive.

**Delivers:** Insights/pattern detection skill with configurable thresholds; alert routing (macOS osascript + Slack DM + daily note injection); Canvas-based visual weekly review template in `05_AI_Workspace/`; alert-monitor with "actionable or silent" rule enforced.

**Addresses:** Proactive pattern detection, alert routing, Canvas visual weekly review, follow-up monitoring.

**Avoids:** Alert fatigue (Pitfall 10) — launch with morning briefing only, add alert types one at a time based on demonstrated value; enforce 5-item max per briefing.

**Research flag:** Needs `/gsd:research-phase` for the Canvas generation pattern — Canvas interaction from skills is LOW confidence in current research. All other components in this phase use well-documented patterns.

### Phase Ordering Rationale

- Phase 1 before Phase 3 because `PreToolUse` boundary enforcement must exist before any skill writes to vault
- Phase 1 before Phase 4 because pattern detection writes to `05_AI_Workspace/` and queries YAML frontmatter
- Phase 2 parallel with Phase 1 data layer because memory structure is independent of YAML schema, but must precede Phase 3 skills
- Phase 4 last because it depends on all three prior phases and is the most complex; alert fatigue risk increases if alerts are built before the daily briefing habit is established
- Plugin version pinning happens in Phase 1 before anything is built on top of it

### Research Flags

Needs `/gsd:research-phase` during planning:
- **Phase 4 (Canvas generation):** Research is LOW confidence on Obsidian Canvas interaction patterns from Claude Code skills. Validate whether skills can write `.canvas` JSON files reliably and how Obsidian picks them up.

Standard patterns (skip research-phase):
- **Phase 1 (Foundation):** Claude Code hooks API and Dataview queries are fully documented and verified.
- **Phase 2 (Memory/Hooks):** Claude Code memory and SessionStart hook patterns are from official docs.
- **Phase 3 (Daily skills):** Morning briefing and CRM patterns are well-established in the Obsidian + Claude Code community. People hub via Dataview is a standard pattern.

---

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | Claude Code hooks, skills, memory API all verified from official docs (March 2026). Dataview verified from official plugin docs. One exception: Obsidian Bases status is MEDIUM — confirmed Catalyst-only but GA timeline unclear. |
| Features | HIGH (core), MEDIUM (implementation) | Table stakes and differentiators verified against official product docs, community guides, and competitor analysis. Specific implementation patterns (people hub query design, alert threshold tuning) are MEDIUM — patterns exist but need iteration. |
| Architecture | HIGH (Claude Code layer), MEDIUM (new components) | All existing layer integration points verified from direct file system inspection. New components (05_AI_Workspace design, hook scripts) are MEDIUM — extrapolated from constraints and best practices, not yet tested in this vault. |
| Pitfalls | HIGH (critical), MEDIUM (moderate) | Critical pitfalls (vault pollution, YAML lock-in, iCloud race conditions) are well-documented across official and community sources. Moderate pitfalls (hook reliability, memory staleness) are MEDIUM — known issues with confirmed mitigations. |

**Overall confidence:** HIGH

### Gaps to Address

- **Canvas skill integration:** Research explicitly flagged LOW confidence on Obsidian Canvas file write patterns from Claude Code skills. Address in Phase 4 research before building the visual weekly review.
- **Hook script performance at vault scale:** Known behavior but not tested in this vault. Monitor performance when `vault-scan.sh` runs on a vault of hundreds of notes. Set a scan time budget (under 2 seconds) before shipping SessionStart hook.
- **Auto memory behavior with subagents:** Documented in official docs but not verified in practice. Validate that memory writes from subagent context flows propagate correctly to MEMORY.md.
- **iOS Dataview query compatibility:** Several pitfalls note macOS/iOS query inconsistencies. Any dashboard note used on mobile must be tested on iOS explicitly before Phase 3 ships.

---

## Sources

### Primary (HIGH confidence — official documentation, verified 2026-03-14)
- Claude Code best practices: https://code.claude.com/docs/en/best-practices
- Claude Code hooks reference: https://code.claude.com/docs/en/hooks
- Claude Code hooks guide: https://code.claude.com/docs/en/hooks-guide
- Claude Code memory: https://code.claude.com/docs/en/memory
- Claude Code skills: https://code.claude.com/docs/en/skills
- Dataview official docs: https://blacksmithgu.github.io/obsidian-dataview/
- Obsidian changelog: https://obsidian.md/changelog/
- Obsibrain CRM field schema: https://www.obsibrain.com/docs/features/meetings-and-crm

### Secondary (MEDIUM confidence — community consensus, cross-referenced)
- Obsidian × Claude Code workflow guide (Axton Liu): https://www.axtonliu.ai/newsletters/ai-2/posts/obsidian-claude-code-workflows
- Obsidian AI Second Brain guide 2026 (NxCode): https://www.nxcode.io/resources/news/obsidian-ai-second-brain-complete-guide-2026
- Building your AI Second Brain (Noah Vnct): https://noahvnct.substack.com/p/how-to-build-your-ai-second-brain
- Dataview vs Datacore vs Bases comparison: https://obsidian.rocks/dataview-vs-datacore-vs-obsidian-bases/
- iCloud Drive sync deep dive (Carlo Zottmann): https://zottmann.org/2025/09/08/ios-icloud-drive-synchronization-deep.html
- Dataview performance issues: https://forum.obsidian.md/t/dataview-very-slow-performance/52592
- Hooks, Rules, Skills overview: https://jessezam.medium.com/hooks-rules-and-skills-feedback-loops-in-claude-code-d47e5f58364d
- Auto memory (MEMORY.md): https://medium.com/@joe.njenga/anthropic-just-added-auto-memory-to-claude-code-memory-md-i-tested-it-0ab8422754d2

### Tertiary (LOW confidence — single source or inference)
- Obsidian Canvas skill interaction patterns — not researched; Canvas architectural fit inferred from Canvas JSON format documentation only
- 10 Claude Code hooks from autonomous operation (DEV Community): https://dev.to/yurukusa/10-claude-code-hooks-i-collected-from-108-hours-of-autonomous-operation-now-open-source-5633 — useful practitioner patterns, not officially verified

---
*Research completed: 2026-03-14*
*Ready for roadmap: yes*
