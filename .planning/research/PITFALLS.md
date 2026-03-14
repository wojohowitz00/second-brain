# Domain Pitfalls: Hybrid Open Brain / Second Brain with Claude Code + Obsidian

**Domain:** AI-powered personal knowledge management OS (Obsidian + Claude Code)
**Researched:** 2026-03-14
**Overall confidence:** HIGH (official Claude Code docs) / MEDIUM (Obsidian community, verified forum)

---

## Critical Pitfalls

Mistakes that cause rewrites, data corruption, or permanent vault damage.

---

### Pitfall 1: AI Writing Into Human PARA Folders (Vault Pollution)

**What goes wrong:** Claude Code writes generated summaries, AI-drafted notes, or "insight" content directly into 01_Projects, 02_Areas, 03_Research, or 04_Archive. Over time, the vault fills with AI-generated content that's indistinguishable from human-written notes. Quality degrades silently — human-authored notes get buried, trust in vault content erodes, and retrieval becomes unreliable.

**Why it happens:** Skills that write to "the most relevant folder" follow the same PARA logic a human would use. Without a hard boundary, AI naturally puts AI content where human content lives.

**Consequences:** Loss of vault integrity. Irreversible if AI-generated notes accumulate without tagging — you can't recover which notes were human-authored. The "second brain" stops reflecting actual thinking and becomes an AI slop repository.

**Warning signs:**
- Notes in 01–04 folders with no `created:` date matching a real work session
- Notes that are smoother / more generic than your usual writing style
- Dataview queries counting more notes than you remember creating

**Prevention:**
- Hard rule enforced at the skill level: AI writes *only* to `05_AI_Workspace/`. Zero exceptions.
- All AI-generated notes must include `ai_generated: true` in YAML frontmatter and an `ai_generated_by:` field
- Session hooks that write to daily notes must append to a designated AI section (e.g., `## AI Updates`) rather than free-form insertion
- Treat vault purity as a constraint documented in CLAUDE.md — not just a guideline

**Phase:** Address in Phase 1 (AI workspace setup) before any skill writes to the vault. Do not build write-capable skills without this boundary in place first.

---

### Pitfall 2: Context Window Bloat Killing Skill Performance

**What goes wrong:** Skills load too much context — entire vault indexes, full note contents, multi-file YAML dumps — and Claude's reasoning quality degrades as the context fills. The "lost in the middle" problem causes earlier instructions to be effectively ignored. Skills that work fine on small vaults silently degrade as the vault grows.

**Why it happens:** It feels safer to give Claude more context. Loading `_llm-context/` files plus a full task list plus recent notes plus people notes plus project statuses seems comprehensive — but 50,000 tokens of mixed context is worse than 8,000 tokens of targeted context.

**Consequences:** Skills become slower, produce generic output, miss specific instructions embedded in the middle of context, and occasionally hallucinate details from unrelated earlier context (context pollution). Anthropic's docs confirm: "LLM performance degrades as context fills. Claude may start forgetting earlier instructions or making more mistakes."

**Warning signs:**
- Skills that used to give specific, tailored output now produce generic advice
- Claude asks about things already in CLAUDE.md or a skill file
- A skill invocation consumes noticeably more tokens over time without a scope change
- Claude "mixes files from different modules" or "applies outdated conventions from a previous exchange"

**Prevention:**
- Follow the existing progressive context loading architecture (`_llm-context/`) strictly — skills load only their relevant context file
- Never load entire vault content. Use filename patterns, Dataview query results (summaries not full notes), or file metadata only
- Skills should specify their context scope explicitly in their SKILL.md preamble
- Use subagents for investigation tasks that require reading many files — they report back summaries without polluting the main context
- Run `/clear` between unrelated skill invocations in long sessions
- Set a personal rule: if a skill's context loading exceeds ~10 files, it needs to be redesigned

**Phase:** Design context boundaries in Phase 1 (skills architecture). Audit context usage when adding each new skill.

---

### Pitfall 3: iCloud Sync Race Conditions on External Writes

**What goes wrong:** Claude Code writes a file to the Obsidian vault (located at `iCloud~md~obsidian/Documents/Home/`) while iCloud is simultaneously syncing. iCloud Drive's sync daemon does not use NSFileCoordinator for external writes, meaning a write from a Python script or Claude Code tool can collide with an in-progress sync. The result is silent data loss — one version overwrites the other with no conflict notification.

**Why it happens:** iCloud Drive is designed for app-initiated writes with coordination APIs. External processes writing directly to the filesystem bypass the coordination layer. Obsidian itself is aware of this (it uses the Obsidian Sync alternative partly for this reason), but the vault location on iCloud is the most common setup.

**Consequences:** Notes silently lose content. If a skill writes a daily briefing at the same time mobile Obsidian is syncing the same note from an iPhone edit, one version disappears. With no conflict resolution, the loss is invisible until noticed manually.

**Warning signs:**
- Notes that were edited on mobile and also touched by a skill have missing sections
- iCloud shows persistent "uploading" spinner for vault files after a skill runs
- Notes in `05_AI_Workspace/` are shorter than expected after a sync cycle

**Prevention:**
- All skill file writes must be append-only or write-to-new-file. Never overwrite an existing note in place.
- For append operations, use atomic writes: write to a temp file, then move (rename) into position — this is a single filesystem operation that's safer with iCloud
- Add a brief stabilization check before writing: verify the target file is not currently being modified (check mtime stability)
- Avoid writing to the same note from multiple sources simultaneously (e.g., a session-start hook and a background monitoring process should not target the same daily note)
- Keep the `05_AI_Workspace/` folder as the only AI write target — reduces surface area for conflicts with human-edited notes

**Phase:** Address in Phase 2 (file write infrastructure) before any automated/scheduled writes are introduced.

---

### Pitfall 4: YAML Frontmatter Schema Lock-In

**What goes wrong:** Early in development, you define a YAML frontmatter schema for people, projects, tasks, or habits. You build Dataview queries on top of it. Six weeks later, you realize `status` should be `project_status` to avoid collision with task status, or `contact_type` needs a new enum value. Renaming a property breaks every Dataview query that references it — silently returning empty results rather than errors.

**Why it happens:** YAML frontmatter has no schema enforcement. Obsidian Properties and Dataview both accept whatever you put in. Iteration feels free until you have 50 notes and 15 queries depending on a property name.

**Consequences:** Dataview queries return empty tables with no error. Dashboards show zero results. Debugging requires reading query code and note frontmatter manually — there's no type error, just missing data. Migration requires touching every note with the old property name.

**Warning signs:**
- Dataview queries that used to show results now show empty tables
- Adding a new note in a category doesn't appear in the expected dashboard
- Property names in existing notes don't match the current skill's expected schema

**Prevention:**
- Define a canonical YAML schema document before writing any Dataview queries (a schema file in `_llm-context/` that all skills reference)
- Use Obsidian's native Properties panel — it enforces consistent property types visually and catches typos at entry time
- Adopt conservative naming: prefer explicit namespaced properties (`person_type`, `project_phase`) over ambiguous generic ones (`type`, `status`)
- When schema must change: update the schema doc, then use a migration script to update all affected notes before updating any queries. Never update queries first.
- Keep query count low — fewer queries means fewer things to break when schema evolves

**Phase:** Define schema in Phase 1 (data layer design) before building any Dataview queries or skills that write frontmatter.

---

## Moderate Pitfalls

Mistakes that cause delays, degraded experience, or accumulating technical debt.

---

### Pitfall 5: Claude Code Hook Reliability Over-Reliance

**What goes wrong:** Session-start and session-end hooks are designed to auto-surface stale tasks and update dashboards. When hooks fail silently — due to timeout, JSON parsing issues from shell profile output, or a non-zero exit code — Claude continues working without the hook running. There's no user notification for non-critical hook failures. The proactive system stops working with no indication.

**Why it happens:** Hooks with non-zero exit codes (other than exit code 2) produce non-blocking errors visible only in verbose mode (`Ctrl+O`). HTTP hooks that receive a non-2xx response also fail silently and non-blockingly. Shell profiles that print text on startup corrupt JSON parsing.

**Consequences:** Morning briefings stop running. End-of-day dashboard updates don't happen. The proactive layer becomes unreliable without the user knowing. Trust in the system degrades.

**Warning signs:**
- Dashboards have stale data that should have been updated by session-end hook
- Morning briefing output is missing from the daily note
- Running a hook manually works, but automated triggering doesn't

**Prevention:**
- All session hooks must write a completion timestamp to a log file as their last action — this provides a lightweight audit trail independent of Claude's output
- Keep hook commands simple and dependency-light (pure bash or Python with no external API calls)
- Test hooks in verbose mode (`Ctrl+O`) during development to see error output
- Ensure shell profiles do not print text on startup (use `[[ -z "$PS1" ]] && return` guards in `.zshrc` / `.bashrc`)
- Never use `async: true` for hooks that must complete before Claude responds (async hooks cannot block behavior and failures are invisible)
- Design the system to be graceful when hooks skip: dashboards should show last-updated timestamps so you can see when they last ran

**Phase:** Address in Phase 3 (hooks implementation). Test hook reliability explicitly before treating hooks as the proactive trigger mechanism.

---

### Pitfall 6: Dataview Query Performance and Rendering Issues

**What goes wrong:** Dataview queries without explicit `FROM` scope constraints scan the entire vault. With a vault of several hundred notes, complex queries (especially those combining multiple WHERE clauses, sorting, and grouping) cause Obsidian to freeze briefly on note open and to show "jumping" content as queries render asynchronously. On mobile (iOS), Dataview query results sometimes show "no results" when they work on macOS — a known cross-platform inconsistency.

**Why it happens:** Dataview's query engine was not designed for speed. It has received no significant updates in a significant period. The async rendering model causes visual instability. The iOS/macOS inconsistency is a documented issue in Dataview's GitHub.

**Consequences:** Dashboard notes feel slow and unstable. Mobile experience degrades. Complex nested queries become unmaintainable — the DQL (Dataview Query Language) syntax lacks type errors or helpful debugging.

**Warning signs:**
- Notes with multiple Dataview blocks take more than 1-2 seconds to fully render
- Content "jumps" visually as queries load sequentially
- A query that returns results on macOS returns nothing on iOS

**Prevention:**
- Always specify `FROM` with a folder path or tag in every Dataview query — never scan the whole vault
- Limit dashboard notes to 3-5 Dataview blocks maximum per note
- Use simple queries for frequently-opened dashboards; reserve complex queries for infrequently-visited analysis notes
- Test all queries on iOS if mobile usage is expected
- Monitor Obsidian Bases (the native core plugin successor to Dataview) — it may become the preferred query layer. Design YAML schemas that are compatible with both Dataview and Bases to enable future migration.
- Do not use Dataview inline queries (backtick syntax) in notes that will be frequently edited — they conflict with editor rendering

**Phase:** Address in Phase 2 (dashboard design). Apply FROM-scoping as a code review rule on every Dataview query before merge.

---

### Pitfall 7: AI Memory Coherence and Staleness

**What goes wrong:** Claude Code memory files accumulate entries about your preferences, projects, and context over multiple sessions. Older entries become stale (a project listed as "in progress" finishes, a preference changes) but remain in memory. Conflicting entries appear (two memories with different values for the same preference). Claude reconciles these by averaging them or picking one arbitrarily, producing subtly wrong behavior.

**Why it happens:** Memory systems are easy to write to and hard to prune. The path of least resistance is to add new entries; removing or updating old ones requires deliberate review. LLMs "struggle to reconcile conflicts between internal knowledge and externally retrieved information" (per 2025 memory systems research).

**Consequences:** Claude surfaces outdated task priorities, references projects that are complete, or applies preferences you've changed. The personal OS feels "off" — not wrong enough to debug, but not reliably accurate. Trust in proactive suggestions erodes.

**Warning signs:**
- Claude references a project or person you haven't thought about in weeks
- A proactive suggestion contradicts your current actual priority
- Memory files have entries with dates more than 4-6 weeks old that haven't been reviewed

**Prevention:**
- Memory files must include `last_verified:` timestamps on each entry
- Add a monthly memory audit as a recurring task — the weekly review skill should surface memory entries older than 30 days for review
- Use structured sections in memory files (active, archived) rather than an ever-growing flat list
- Prefer specificity over breadth: memory should capture durable preferences and patterns, not transient project state (transient state belongs in vault notes, not memory)
- Design skills to explicitly check memory staleness before acting on it: "This preference was last verified 6 weeks ago — is it still accurate?"

**Phase:** Address in Phase 2 (memory system design). Audit memory coherence at every weekly review.

---

### Pitfall 8: Obsidian Plugin Conflicts and Compatibility Breakage

**What goes wrong:** One plugin update breaks another plugin's functionality. Known interactions: Smart Connections cannot read Dataview-generated content (queries that pull tasks connected to specific people). Smart Connections 3.x introduced cross-platform inconsistencies where query results work on macOS but fail on iOS. Obsidian core updates can break community plugins that use internal APIs.

**Why it happens:** Obsidian plugins use both public APIs and internal undocumented APIs. Plugin developers don't coordinate compatibility. The ecosystem has 800+ community plugins with no central testing.

**Consequences:** A Dataview dashboard that Smart Connections was summarizing for AI context stops returning results. A Templater template that populates YAML frontmatter breaks silently after a plugin update. Workflows depending on inter-plugin functionality fail unpredictably.

**Warning signs:**
- A skill that reads Obsidian content via Smart Connections returns empty or partial results
- YAML frontmatter created by Templater has unexpected formatting after a plugin update
- Mobile and desktop show different results for the same note or query

**Prevention:**
- Pin plugin versions for the 4-5 core plugins this system depends on (Dataview, Smart Connections, Templater, Tasks, Local REST API). Update deliberately, not automatically.
- Do not design skills that depend on inter-plugin data pipelines (e.g., "Smart Connections reads a Dataview result"). Treat plugins as independent tools.
- Add `.smart-env/` to iCloud sync ignore patterns to prevent Smart Connections index conflicts
- Test mobile compatibility for any Dataview query used in a frequently-accessed note
- Design fallback behavior for skill steps that depend on plugin outputs — if the Local REST API is unavailable, the skill should degrade gracefully rather than crash

**Phase:** Address in Phase 1 (plugin configuration audit). Document pinned plugin versions in the project.

---

### Pitfall 9: CLAUDE.md Over-specification and Rule Dilution

**What goes wrong:** CLAUDE.md grows with every session as new rules, preferences, and context are added. When CLAUDE.md exceeds a certain length, Claude begins ignoring rules buried in the middle — the "lost in the middle" problem applied to configuration. Instructions that were followed reliably when the file was short stop being followed consistently when the file is long.

**Why it happens:** Every time Claude does something wrong, the instinct is to add a rule to CLAUDE.md. This is additive-only by default. Rules that Claude already follows correctly by default also get written down "for safety." The file bloats.

**Consequences:** Critical rules (like "never write to PARA folders 01-04") stop being reliably applied. The system becomes non-deterministic — Claude follows rules some sessions but not others. Debugging becomes difficult because it's unclear whether a rule exists or is being ignored.

**Warning signs:**
- CLAUDE.md exceeds 200 lines
- Claude violates a rule that's explicitly written in CLAUDE.md
- Multiple entries that say similar things with slightly different wording

**Prevention:**
- Keep CLAUDE.md under 100 lines. Ruthlessly prune.
- Convert behavioral rules to hooks (hooks don't negotiate; CLAUDE.md does)
- Move domain knowledge to skills — CLAUDE.md is for session-level configuration, not encyclopedic context
- Periodically audit: for each line in CLAUDE.md, ask "would removing this cause Claude to make a mistake?" If no, delete it
- Add emphasis markers (`IMPORTANT:`, `CRITICAL:`) sparingly — if everything is critical, nothing is

**Phase:** Ongoing. Audit CLAUDE.md before adding any new rule.

---

## Minor Pitfalls

Issues that cause annoyance but are fixable without architectural changes.

---

### Pitfall 10: Alert Fatigue from Over-engineered Proactive Layer

**What goes wrong:** The proactive layer (morning briefings, end-of-day updates, Slack alerts, macOS notifications) surfaces too many items. The user starts ignoring notifications. Briefings that are too long get skimmed or skipped. The system produces more output than it saves in attention.

**Why it happens:** Building each alert in isolation, each one seems valuable. Collectively, they add up to more than a person can meaningfully act on. Alert fatigue is documented across incident management, productivity tools, and AI assistant research — "73% had outages linked to ignored or suppressed alerts."

**Consequences:** The user builds a habit of dismissing AI output. Genuinely important alerts get lost in the noise. The proactive system trains the user to ignore it.

**Warning signs:**
- Morning briefing is routinely not read past the first section
- Slack notifications from the system are regularly dismissed unread
- The user mentions feeling overwhelmed by the system's output

**Prevention:**
- Establish a hard limit: no more than 5 items per briefing, 3 priority items surfaced per session
- Use signal strength tiers: only surface items the system has high confidence are actionable
- "Actionable or silent" rule: if the system can't suggest a specific action for an alert, don't surface it
- Design the morning briefing to be completable in under 3 minutes. If it takes longer, it will be skipped.
- Let the proactive layer evolve gradually — start with the briefing only, add features based on demonstrated value

**Phase:** Phase 3 (proactive layer). Constrain scope aggressively. Add one alert type at a time, measure usage, then decide whether to add the next.

---

### Pitfall 11: Skill Scope Creep and Context Entanglement

**What goes wrong:** Skills start focused (morning briefing = today's tasks + calendar + one insight) and expand over time (morning briefing += last week's incomplete items + CRM follow-ups + habit trends + project milestones + research queue). Each addition feels incremental. The skill becomes slow, its output becomes unfocused, and its context requirements balloon.

**Why it happens:** It's easier to add to an existing skill than to create a new one. The morning briefing becomes the catch-all skill.

**Consequences:** Briefings become long and unfocused. The skill's context requirements grow, hitting Pitfall 2 (context bloat). Maintenance becomes difficult — changing one output section risks breaking another.

**Prevention:**
- Maintain the single-responsibility principle for skills: one skill, one purpose
- Skills should have a stated context budget (e.g., "morning briefing loads at most 5 context files")
- When a skill's output exceeds one page, split it into two skills
- Use skill chaining deliberately rather than building one massive skill

**Phase:** Ongoing. Review skill scope at each new feature addition.

---

### Pitfall 12: External Write to Vault During Obsidian Indexing

**What goes wrong:** A skill writes a new note to `05_AI_Workspace/` while Obsidian is re-indexing the vault (which happens on startup, after sync, and periodically). Obsidian may not pick up the new file immediately, or may pick it up mid-write, resulting in a partially-indexed note. Dataview queries that should include the new note miss it until the next indexing cycle.

**Why it happens:** Obsidian's file watcher relies on filesystem events. Rapid writes (e.g., a skill writing multiple files in sequence) can overwhelm the watcher or miss events.

**Consequences:** New AI-generated insights or briefings don't appear in Dataview dashboards until Obsidian is restarted or the vault is manually re-indexed.

**Prevention:**
- Write one file at a time; add a short pause (1-2 seconds) between sequential writes when a skill writes multiple files
- Prefer appending to existing notes over creating new notes when possible — existing notes are already indexed
- For skills that create new notes and then query them, design the query step to run after a short delay or on the next invocation, not immediately after the write

**Phase:** Phase 2 (file write implementation detail). Low severity, but worth knowing before seeing mysterious Dataview misses.

---

## Phase-Specific Warnings

| Phase Topic | Likely Pitfall | Mitigation |
|-------------|---------------|------------|
| AI workspace folder setup (Phase 1) | Forgetting to establish hard write boundary before building any skills | Define and document the boundary in CLAUDE.md and skill templates before any vault write capability exists |
| YAML schema design (Phase 1) | Designing schema iteratively without a canonical document, leading to drift | Write schema doc first, use Properties panel to enforce types |
| Plugin configuration (Phase 1) | Not pinning plugin versions; a Dataview update breaks all queries | Pin Dataview, Smart Connections, Templater, Tasks, Local REST API before building on them |
| Claude Code memory system (Phase 2) | Memory growing without pruning mechanism, leading to staleness | Design memory structure with timestamps and a pruning/audit cadence |
| Dashboard + Dataview (Phase 2) | Queries without FROM scope, slow rendering, mobile failures | FROM clause on every query; mobile test before shipping |
| File write infrastructure (Phase 2) | iCloud race conditions on overwrite | Append-only or atomic write patterns; never overwrite-in-place |
| Session hooks (Phase 3) | Silent failures, no audit trail | Hook completion logging; test in verbose mode |
| Proactive layer (Phase 3) | Alert fatigue from too many simultaneous alerts | One alert type at a time; enforce briefing length limit |
| CLAUDE.md (ongoing) | Over-specification causing rule dilution | Keep under 100 lines; convert rules to hooks; prune regularly |

---

## Sources

- [Claude Code Best Practices — Official Docs](https://code.claude.com/docs/en/best-practices) — HIGH confidence
- [Claude Code Hooks Reference — Official Docs](https://code.claude.com/docs/en/hooks) — HIGH confidence
- [Dataview vs Datacore vs Obsidian Bases — Obsidian Rocks](https://obsidian.rocks/dataview-vs-datacore-vs-obsidian-bases/) — MEDIUM confidence
- [Dataview Performance Issues — Obsidian Forum](https://forum.obsidian.md/t/dataview-very-slow-performance/52592) — MEDIUM confidence
- [Design your vault for AI orientation — Obsidian Forum](https://forum.obsidian.md/t/design-your-vault-for-ai-orientation-not-just-human-navigation/112010) — MEDIUM confidence
- [iCloud Drive iOS Sync Deep Dive — Carlo Zottmann](https://zottmann.org/2025/09/08/ios-icloud-drive-synchronization-deep.html) — MEDIUM confidence
- [iCloud Sync Issues — Obsidian Forum](https://forum.obsidian.md/t/understanding-icloud-sync-issues/78186) — MEDIUM confidence
- [Smart Connections unable to read Dataview content — Obsidian Forum](https://forum.obsidian.md/t/obsidian-smart-connections-unable-to-read-dataview-generated-content/99290) — MEDIUM confidence
- [AI Fatigue Research — BCG / Fortune, March 2026](https://fortune.com/2026/03/10/ai-brain-fry-workplace-productivity-bcg-study/) — MEDIUM confidence
- [State of Incident Management 2025 — Runframe](https://runframe.io/blog/state-of-incident-management-2025) — MEDIUM confidence
- [Claude Code context window management — Understanding context window, Damian Galarza](https://www.damiangalarza.com/posts/2025-12-08-understanding-claude-code-context-window/) — MEDIUM confidence
- [10 Claude Code Hooks from 108 hours autonomous operation — DEV Community](https://dev.to/yurukusa/10-claude-code-hooks-i-collected-from-108-hours-of-autonomous-operation-now-open-source-5633) — LOW confidence (single practitioner account, no official verification)
