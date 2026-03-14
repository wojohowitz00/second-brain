# Hybrid Brain OS

## What This Is

A personal operating system that evolves the existing Second Brain (Slack→Ollama→Obsidian menu bar app) into a hybrid Open Brain / Second Brain system. It combines automated capture, interactive AI partnership, and proactive monitoring — all native to Obsidian and Claude Code. Built for one person across four life domains: personal productivity, professional work, people/CRM, and research.

## Core Value

Claude Code knows me deeply across sessions and proactively surfaces what matters — not just filing things away, but telling me what I should focus on, who I should follow up with, and what patterns I'm not seeing.

## Requirements

### Validated

- ✓ Slack message capture and auto-classification — existing (v1.0, Second Brain)
- ✓ PARA-based vault organization — existing
- ✓ Local LLM classification via Ollama — existing
- ✓ macOS menu bar app with status/sync — existing
- ✓ 7 Claude Code commands (/today, /weekly, /new-task, etc.) — existing
- ✓ 9 Claude Code skills (inbox processor, daily digest, weekly review, etc.) — existing
- ✓ Progressive context loading system (_llm-context/) — existing

### Active

- [ ] AI Workspace folder in Obsidian vault (05_AI_Workspace) with strict separation rules
- [ ] Persistent AI memory across sessions via Claude Code memory system
- [ ] Morning briefing skill — comprehensive daily briefing across all domains
- [ ] End-of-day update skill — sync tasks, update dashboards, capture learnings
- [ ] People/CRM skill — relationship tracking with follow-up management
- [ ] Dashboard skill — generate/refresh Dataview-powered Obsidian dashboard notes
- [ ] Insights skill — proactive pattern detection across vault content
- [ ] Alert system — Slack + macOS notifications + Obsidian daily note
- [ ] Structured data via YAML frontmatter + Dataview queries (people, projects, habits)
- [ ] Session hooks — auto-surface stale tasks on start, auto-update dashboards on end
- [ ] Canvas templates for visual weekly reviews and project maps
- [ ] Enhanced task creation with Dataview-compatible rich metadata

### Out of Scope

- External database (Supabase, SQLite) — Using Obsidian-native YAML + Dataview instead
- React dashboards / web apps — Obsidian notes + Canvas only
- MCP server development — Using existing file system access and Slack integration
- Mobile app — Obsidian mobile handles vault access
- Multi-user / team features — Personal system only
- Modifying the Python backend — v1.0 is mature and stable

## Context

- **Existing system**: Second Brain v1.0 at `apps/second-brain/` — macOS menu bar app, Python backend, 259 tests, 9 phases complete
- **Obsidian vault**: `/Users/richardyu/Library/Mobile Documents/iCloud~md~obsidian/Documents/Home/`
- **Vault structure**: PARA (01_Projects, 02_Areas_of_Interest, 03_Research, 04_Archive) with consistent YAML frontmatter
- **Installed Obsidian plugins**: Dataview, Smart Connections, Templater, Tasks, Local REST API, MCP Tools, Auto Note Mover, Git
- **notes-to-self/** system: Recently initialized in vault for Claude Code interaction (currently empty)
- **Inspiration**: Anthropic's internal use of Claude Code — skills encoding institutional knowledge, plugin stacking, Dashmaker, productivity updates, morning briefings

## Constraints

- **Data locality**: All data stays local (Obsidian files, Ollama, Claude Code memory) — no cloud database
- **Vault purity**: AI never writes to human PARA folders (01-04). AI workspace (05) is the only AI-writable area
- **Backward compatibility**: Existing Slack capture pipeline must continue working unchanged
- **Obsidian-native**: Dashboards and views must work within Obsidian (Dataview, Canvas, Properties) — no external web apps
- **Progressive context**: Skills must load only relevant context, never dump entire vault into context window

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Obsidian-native data layer (YAML + Dataview) over Supabase | Keep everything local, no external service dependency, vault is portable | — Pending |
| AI workspace folder over Claude Code-only storage | Dashboards and insights visible in Obsidian, queryable by Dataview, human-reviewable | — Pending |
| Evolve existing project over building from scratch | Preserve 259 tests, 9 completed phases, mature Slack pipeline, existing skills | — Pending |
| Hooks for automation over manual triggers | Session-start/end hooks enable proactive behavior without user remembering to invoke | — Pending |
| Claude Code memory over vault-based AI memory | Session context and preferences don't belong in the knowledge vault | — Pending |

---
*Last updated: 2026-03-14 after initialization*
