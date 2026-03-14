# Feature Landscape: Hybrid Open Brain / Second Brain OS

**Domain:** AI-powered personal knowledge management with proactive monitoring, structured data, and persistent memory
**Researched:** 2026-03-14
**Milestone context:** Subsequent — adding proactive AI, structured data, dashboards, and persistent memory to an existing Obsidian + Claude Code system
**Overall confidence:** HIGH (core features), MEDIUM (specific implementation patterns)

---

## Table Stakes

Features users expect. Missing = system feels incomplete.

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| **Persistent AI memory across sessions** | Without this, Claude starts blank every time; defeats the "knows me deeply" promise | Med | Claude Code memory system (not vault-based); session context, preferences, decisions |
| **Morning briefing generation** | Consolidates scattered inputs into one daily orientation; standard in ChatGPT Pulse, Dume.ai, BriefingAM, Granola | Med | Pulls calendar, tasks, open items, follow-ups; outputs to Obsidian daily note |
| **Structured contact records with rich metadata** | People tracking without schema (name, company, title, email) is unusable; expected from any CRM | Low | YAML frontmatter fields; phone, email, title, company, tags |
| **Meeting → person linkage** | Standard in every PKM CRM (Obsibrain, Tana, Notion): link attendees to meeting notes via [[NAME]] | Low | Obsidian wikilinks handle this natively |
| **Dataview-powered dashboards** | Users of Obsidian expect queryable views over YAML; Dataview is the de facto standard | Med | Tables of tasks by status, people by last-contact, projects by priority |
| **Inbox processing / triage automation** | Capture without processing creates hoarding; triage is the table-stakes automation in every PKM | Med | Existing skill; needs to surface stale inbox items proactively |
| **Weekly review generation** | Standard in PARA, GTD, and every productivity system; Claude Code can automate synthesis | Med | Existing skill; needs enrichment with people and project metadata |
| **YAML frontmatter schema for people, projects, tasks** | Without consistent schema, Dataview queries fail; schema is the foundation for every other feature | Low | Define once in skill context; enforce via Templater templates |
| **Task creation with rich metadata** | Tasks without due date, project link, priority are not actionable; table stakes in any task manager | Low | Dataview-compatible fields: due, priority, project, status, tags |
| **AI workspace separation (05_AI_Workspace)** | Without a dedicated write zone, AI outputs pollute the human vault; separation is architectural must-have | Low | Folder boundary; Claude never writes to 01-04 |

**Complexity note:** "Low" here means low implementation effort given the existing stack (Obsidian + Claude Code + Dataview). All Low items are YAML schemas, Templater templates, or skill additions — not new infrastructure.

---

## Differentiators

Features that set this hybrid system apart. Not expected by most PKM users, but uniquely valuable given the Open Brain / Second Brain architecture.

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| **Proactive pattern detection across vault** | Surfaces "you haven't followed up with X in 30 days" or "this project has no open tasks" — AI as active monitor, not passive retrieval | High | Requires scheduled or hook-triggered scan; cross-references people, tasks, projects; outputs to briefing |
| **Session hooks (start/end automation)** | Eliminates manual invocation — system automatically surfaces stale tasks on start, updates dashboards on end; rare in PKM tools | Med | Claude Code SessionStart hook; end-of-day skill chained to session close |
| **360-degree people hub (aggregated relationship context)** | Automatically aggregates all meetings, tasks, and mentions for a person across the vault via Dataview; no manual linking required | Med | Dataview query on each person note pulling all notes with [[PersonName]] |
| **Insights skill (weekly pattern analysis)** | Goes beyond summarization — detects drift, overcommitment, neglected areas; more like a thinking partner than a reporter | High | Claude reads vault-wide context, compares against stated goals; outputs flagged observations |
| **Canvas-based visual weekly review** | Spatial layout showing projects, people, tasks in relationship — not just a list | Med | Obsidian Canvas; Claude generates via file write to 05_AI_Workspace |
| **Open Brain / Second Brain write boundary** | AI writes to 05_AI_Workspace; human vault (01-04) is read-only for Claude; unique architectural decision that prevents AI "pollution" of human thinking | Low | Enforced via CLAUDE.md vault context; no other system formalizes this boundary |
| **Skills as institutional memory** | Each skill encodes repeatable process (like Anthropic's internal pattern); skills compound — each session generates new permanent capabilities | Med | Existing skill system; differentiator is treating skills as first-class knowledge artifacts |
| **Context-aware briefing from vault history** | Morning briefing references *your* notes, decisions, and patterns — not generic news. "Based on what you wrote last week about X..." | High | Depends on persistent memory + vault semantic search; more differentiated than calendar/email-only briefings |
| **Structured data in Markdown (not a database)** | Everything queryable via Dataview stays in local `.md` files; portable, no vendor lock-in, survives tool switching | Low | Architectural choice already made; worth naming explicitly as a differentiator vs. Notion/Supabase |
| **Alert routing (Slack + macOS + Obsidian)** | Proactive alerts delivered where user already is; not buried in a dashboard they have to open | Med | Existing Slack integration; extend with macOS notifications and daily note injection |

---

## Anti-Features

Features to explicitly NOT build. Common mistakes in the PKM / AI agent domain.

| Anti-Feature | Why Avoid | What to Do Instead |
|--------------|-----------|-------------------|
| **Automatic AI writes to human vault folders (01-04)** | Destroys trust in your own notes; you stop knowing what you wrote vs. what AI generated; impossible to undo at scale | Hard boundary: AI writes only to `05_AI_Workspace`; reads everywhere |
| **External database (Supabase, SQLite, Postgres)** | Breaks data locality promise; adds infrastructure dependency; vault becomes partial source of truth | YAML frontmatter + Dataview; everything in `.md` files |
| **React dashboards / web apps** | Splits attention between Obsidian and a browser tab; defeats the "all in Obsidian" UX goal | Obsidian Canvas + Dataview notes; dashboards live in the vault |
| **Auto-tagging / auto-categorizing without human review** | Creates the "Collector's Fallacy" at scale — AI files thousands of notes you never review; gives false sense of organization | Triage skill flags items for human decision; AI suggests, human confirms |
| **Full vault context loading into every prompt** | Destroys performance and coherence; LLMs perform worse with irrelevant context; expensive | Progressive context loading (`_llm-context/`); skill-specific context only |
| **Morning briefing that only covers external sources (news, email)** | Misses the core value proposition — personal context. Generic briefings are a commodity (ChatGPT Pulse does this) | Briefing must primarily reference vault content: open tasks, follow-ups, recent notes, stated goals |
| **Perfect taxonomy upfront** | "Folder Anxiety" — spending hours designing hierarchy before using it; leads to abandonment (documented anti-pattern across Notion, Obsidian communities) | Start with PARA (already in place); add schema fields when a real use case demands them |
| **AI that replaces thinking (pure consumption mode)** | PKM value comes from engagement and synthesis; outsourcing cognition produces "generic, lifeless output"; noted explicitly in community research | AI as thinking partner with human review loop; all AI-generated content tagged `<ai-generated>` for inspection |
| **Polling loops / aggressive monitoring** | Background processes that constantly scan vault degrade system performance; macOS battery impact | Hook-triggered (SessionStart) or scheduled (cron) at reasonable intervals (daily, not per-minute) |
| **Multi-user / team features** | Scope creep; personal system with personal data and personal memory doesn't generalize to teams without rearchitecting | Personal only; explicitly out of scope in PROJECT.md |
| **Mobile app development** | Obsidian mobile handles vault access; building a separate mobile app is significant effort with marginal gain | Use Obsidian mobile + Obsidian Sync (or iCloud); no custom mobile development |

---

## Feature Dependencies

Dependencies map shows which features must be built before others.

```
YAML frontmatter schema (people, projects, tasks)
  └── Dataview-powered dashboards
      └── 360-degree people hub
      └── Dashboard skill (generate/refresh)
  └── Structured contact records
      └── People/CRM skill
          └── Follow-up monitoring (proactive alerts)

Persistent AI memory (Claude Code memory system)
  └── Context-aware morning briefing
  └── Pattern detection / Insights skill
  └── Session continuity ("pick up where you left off")

AI workspace folder (05_AI_Workspace)
  └── All AI write operations (briefings, dashboards, insights)
  └── Open Brain / Second Brain boundary enforcement

Session hooks (SessionStart / SessionEnd)
  └── Inbox surface on start
  └── Dashboard refresh on end
  └── End-of-day update skill

Morning briefing skill
  ← depends on: YAML schema, persistent memory, AI workspace folder
  ← optionally enhanced by: proactive pattern detection

Proactive pattern detection (Insights skill)
  ← depends on: YAML schema, persistent memory, structured contact records
  ← produces: alerts, briefing injections, Canvas visual review

Alert system (Slack + macOS + Obsidian)
  ← depends on: Existing Slack integration (v1.0), AI workspace folder
  ← triggered by: Insights skill, session hooks, morning briefing
```

**Critical path:** YAML schema → Dataview dashboards → AI workspace folder → persistent memory → morning briefing → proactive monitoring

---

## MVP Recommendation

For this milestone (subsequent), the existing system already has capture, classification, and 9 skills. The MVP here means "minimum set to feel like a proactive OS rather than a reactive tool."

**Prioritize first (unlocks everything else):**
1. YAML frontmatter schema for people, projects, tasks — foundation for all queries
2. AI workspace folder (05_AI_Workspace) with boundary rules in CLAUDE.md — enables AI write operations
3. Persistent AI memory (Claude Code memory system) — enables session continuity

**Prioritize second (core daily value):**
4. Morning briefing skill — most visible daily value; references vault + calendar + open tasks
5. Session hooks (SessionStart: surface stale tasks; SessionEnd: update dashboards) — removes manual invocation
6. Structured contact records + 360-degree people hub (Dataview query on person notes)

**Prioritize third (differentiating proactive layer):**
7. Insights/pattern detection skill — flags drift, neglected follow-ups, overcommitment
8. Alert routing (Slack + macOS notifications) — delivers proactive outputs where user already is
9. Canvas-based visual weekly review — spatial orientation, not just lists

**Defer to post-MVP:**
- Enhanced task metadata richness (add fields incrementally as real use cases emerge; avoid schema over-engineering upfront)
- Daily news briefing integration (external sources are table stakes for generic briefing tools, not differentiated here)
- Multi-agent separation (specialized agents per domain: people, projects, research — useful but complex; start with single agent with domain-specific skills)

---

## Sources

- [Obsidian AI Second Brain Complete Guide 2026 — NxCode](https://www.nxcode.io/resources/news/obsidian-ai-second-brain-complete-guide-2026) — HIGH confidence (verified features match known Obsidian/Claude Code capabilities)
- [Obsidian × Claude Code Workflow Guide — Axton Liu](https://www.axtonliu.ai/newsletters/ai-2/posts/obsidian-claude-code-workflows) — HIGH confidence (concrete workflow patterns, hook implementations)
- [How to Build Your AI Second Brain Using Obsidian + Claude Code — Noah Vnct](https://noahvnct.substack.com/p/how-to-build-your-ai-second-brain) — HIGH confidence (skill system, reading vs. writing patterns)
- [Obsibrain Meetings and CRM Docs](https://www.obsibrain.com/docs/features/meetings-and-crm) — HIGH confidence (concrete CRM field schema for Obsidian)
- [Building Your AI Second Brain — Ron Forbes](https://www.ronforbes.com/blog/building-your-ai-second-brain) — MEDIUM confidence (anti-patterns and table stakes categorization; single blog source)
- [Morning Briefing — Dume.ai Docs](https://docs.dume.ai/system-workflows/morning-briefing) — HIGH confidence (official product docs; concrete data source and output structure)
- [Obsidian Dataview Plugin — GitHub](https://github.com/blacksmithgu/obsidian-dataview) — HIGH confidence (official repo; Dataview capabilities)
- [Obsidian Bases Plugin — kevsrobots.com](https://www.kevsrobots.com/learn/obsidian/08_dataview_and_bases.html) — MEDIUM confidence (secondary source for Bases v1.9.0 release)
- [Second Brain Features — thesecondbrain.io](https://www.thesecondbrain.io/company/features) — MEDIUM confidence (competitor product; useful for what the market expects)
- [AI PKM Proactive Insights — Sensay Medium](https://asksensay.medium.com/implementing-a-wisdom-engine-for-personal-knowledge-management-3c76b8d8f760) — LOW confidence (single Medium post; useful for proactive surfacing pattern description)
- [Tana vs Obsidian comparison — TaskFoundry](https://www.taskfoundry.com/2025/07/which-knowledge-hub-wins-notion-obsidian-tana.html) — MEDIUM confidence (structured data comparison; multiple tools analyzed)
