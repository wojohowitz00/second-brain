# Phase 3: Core Daily Skills - Research

**Researched:** 2026-03-15
**Domain:** Claude Code skills, bash scripting, Obsidian Dataview, natural-language task parsing
**Confidence:** HIGH

---

## Summary

Phase 3 delivers four daily-rhythm deliverables: a morning briefing skill, an end-of-day update integrated into SessionEnd, an enhanced `/new-task` command, and two live Dataview dashboards. All four are Claude Code–native: no new dependencies are required beyond what Phases 1–2 already established. The standard approach is bash scripts + Claude Code skills (.md files in `.claude/skills/` and `.claude/commands/`), writing Dataview-native markdown to `05_AI_Workspace/`.

The key architectural question for this phase is where computation happens. Morning briefing computation (scanning tasks, people, projects) runs as Claude reads files directly — not in a hook script. SessionEnd EOD update *does* use the existing hook (already registered) and must stay fast (<5s timeout). Dataview dashboards contain live query code blocks that execute in Obsidian — Claude only writes the static wrapper and query text, not pre-computed results.

The existing tasks-by-status dashboard created in Phase 1 needs to be replaced/extended with the full dashboard spec from this phase. The daily-briefs folder (`05_AI_Workspace/daily-briefs/`) already exists per the AI workspace CLAUDE.md and can be written to immediately. The Dataview `GROUP BY` + `SORT` behavior has important execution-order semantics that affect the dashboard queries.

**Primary recommendation:** Implement morning briefing and EOD update as Claude Code skills (`.md` instruction files) that read task/people/project files directly. Implement dashboards as vault notes with embedded Dataview query blocks. Enhance `/new-task` with richer field extraction but keep the existing file-creation pattern.

---

## Standard Stack

This phase is pure Claude Code + Dataview — no new libraries.

### Core

| Tool | Version | Purpose | Why Standard |
|------|---------|---------|--------------|
| Claude Code skills (.md) | Current | Morning briefing, EOD update instruction files | Established pattern in this project; progressive disclosure |
| Claude Code commands (.md) | Current | Enhanced `/new-task` command | Already exists as `new-task.md`; needs enrichment |
| Obsidian Dataview | Installed in vault | Live task/project dashboards | Dataview queries execute live in Obsidian; no rebuild needed |
| bash (session-end.sh) | System | EOD hook extension | Already registered in `~/.claude/settings.json`; just extend it |
| MEMORY.md | Auto-loaded | Session learning capture | Already seeded in Phase 2; EOD update writes here |

### Supporting

| Tool | Purpose | When to Use |
|------|---------|-------------|
| `awk` / `grep` / `sed` | Frontmatter field extraction in hooks | Session-end script needs to scan task status changes |
| `date` (macOS BSD) | Date arithmetic in bash | Morning brief date headers; EOD timestamp |
| `wc -l` | MEMORY.md line count guard | Before writing learnings to ensure <200 line limit |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|-----------|-----------|---------|
| Skill .md files for morning briefing | Python script | .md files are the established skill pattern; Python adds complexity without benefit here |
| Dataview live queries in dashboards | Pre-computed markdown tables | Pre-computed tables go stale; Dataview renders live in Obsidian — always fresh |
| Extending session-end.sh for EOD | Separate EOD hook | session-end.sh already registered; cleaner to extend it than add another hook entry |

**No new installs required.** This phase extends existing infrastructure only.

---

## Architecture Patterns

### Recommended File Structure

```
.claude/
├── commands/
│   └── new-task.md              # MODIFY: add priority, project, domain, context fields
├── skills/
│   └── surfacing/
│       ├── daily-digest/
│       │   └── skill.md         # REPLACE: rewrite to implement new morning brief spec
│       └── eod-update/
│           └── skill.md         # CREATE: end-of-day update skill
└── hooks/
    └── session-end.sh           # MODIFY: add EOD data capture logic

05_AI_Workspace/
├── daily-briefs/                # EXISTS: write YYYY-MM-DD-daily-brief.md here
└── dashboards/
    ├── tasks-by-status.md       # REPLACE: current Phase 1 stub — write full dashboard
    └── projects-health.md       # CREATE: new project health dashboard
```

### Pattern 1: Morning Briefing Skill

**What:** A Claude Code skill invoked by `/today` or explicitly. Claude reads task/people/project files, generates a structured brief, and writes it to `05_AI_Workspace/daily-briefs/YYYY-MM-DD-daily-brief.md`. The brief is also injected into session context (Claude has already read the files, so it summarizes inline).

**Structure (locked by CONTEXT.md decisions):**
```
## Summary Header      ← X tasks due, Y overdue, Z follow-ups (orient first)
## Tasks               ← title | status | project (one line each)
## Automation Opportunities ← active offers: "3 tasks marked waiting — want me to draft follow-ups?"
```

**Output target:** `05_AI_Workspace/daily-briefs/YYYY-MM-DD-daily-brief.md`

**Filename convention (from AI workspace CLAUDE.md):** `YYYY-MM-DD-daily-brief.md`

**Daily brief frontmatter:**
```yaml
---
type: daily-brief
date: 2026-03-15
generated_by: claude
---
```

**Skill invocation triggers to keep:**
- `/today`
- "morning briefing"
- "what's on today"
- "daily brief"

**Data sources Claude reads directly:**
- `tasks/*.md` — due_date, status, project fields
- `people/*.md` — follow_up_date field (from YAML schema)
- `projects/*.md` — status, health, next_action fields

**Note:** `people/` and `projects/` directories currently have only README.md (no real files). The skill must handle empty directories gracefully (skip section, no error).

### Pattern 2: End-of-Day Update (SessionEnd Extension)

**What:** SessionEnd hook already runs `session-end.sh`. The EOD update extends it to: (1) detect task status changes made during the session, (2) ask one reflection question via stdout injection (not possible in hooks — hooks are pre-session, not interactive). **Critical finding:** hooks cannot be interactive. The reflection question must come from a skill, not a hook.

**Architecture split:**
- `session-end.sh` (hook): writes "## Day Summary" section to the day's daily-brief note, appends dashboard refresh timestamp
- EOD skill (skill.md): interactive component — asks reflection question, captures session learnings to MEMORY.md

**Day Summary section appended to daily-brief note:**
```markdown
## Day Summary

*Session closed: YYYY-MM-DD HH:MM*

### Tasks Updated
[auto-detected from task file modification times]

### Session Learnings
[written by EOD skill, not hook]
```

**SessionEnd hook constraint (confirmed from Phase 2 research):** 5000ms timeout configured in settings.json. The hook must complete within this. Writing a single "Day Summary" header to the daily-brief file takes <100ms.

**MEMORY.md line guard:** Before appending session learnings to MEMORY.md, check `wc -l ~/.claude/projects/.../memory/MEMORY.md` and warn if approaching 200 lines.

### Pattern 3: Enhanced /new-task Command

**Current state:** `new-task.md` creates tasks with `type`, `title`, `due_date`, `status`, `tags`, `created` — missing `priority`, `project`, `domain`, `context`.

**Required additions per YAML schema:**
- `priority: medium` (default medium if not specified)
- `project: "[[ProjectName]]"` (wikilink format — quoted in YAML)
- `domain: admin` (infer from content keywords)
- `context: deep` (infer: quick for <15 min tasks, deep otherwise)

**Natural language parsing approach (Claude's discretion):**
- Due date inference: "by Friday" → next Friday's date; "end of week" → coming Sunday; "tomorrow" → tomorrow; "EOD" → today; month references → nearest occurrence
- Priority signals: "urgent", "critical", "ASAP", "important" → high; "someday", "eventually", "when I have time" → low; default → medium
- Domain signals: "email", "call", "admin" → admin; "write", "post", "content" → content; "research", "read", "learn" → research; "sales", "client", "deal" → sales; "build", "code", "ship" → product; person names → people
- Context signals: "quick", "5 min", "2 min" → quick; "review", "analyze", "write", "think" → deep; "with", "schedule", "meet" → collab

**Quick capture variant (/new-task quick):**
```yaml
---
type: task
title: [title only]
status: backlog
created: YYYY-MM-DD
---
```
No prompts. No inference. Just title + status + created. Filename from title (kebab-case).

**Post-creation offer (locked decision):** Always offer "Want to add any notes or context?" after standard creation. Skip for `/new-task quick`.

**Status default:** CONTEXT.md specifies quick capture defaults to `backlog`. For standard `/new-task`, default should also be `backlog` (consistent; user can change if active).

**Frontmatter template (enhanced):**
```yaml
---
type: task
title: [extracted title]
due_date: YYYY-MM-DD          # bare ISO, no quotes — or omit if not mentioned
status: backlog
priority: medium              # inferred or default
project: "[[ProjectName]]"    # or omit if not mentioned
domain: admin                 # inferred from content keywords
context: deep                 # inferred or omit
tags: []
created: YYYY-MM-DD
---
```

### Pattern 4: Dataview Dashboard Queries

**Verified Dataview syntax (from official docs):**

```
WHERE due_date < date(today) AND status != "done"
WHERE file.mtime < date(today) - dur(7 days)    # for "no activity in 7+ days"
SORT priority DESC, due_date ASC                 # multi-field sort
GROUP BY status
```

**Execution order matters:** Commands process in written order. Put `WHERE` before `GROUP BY` before `SORT`. `LIMIT` before `SORT` limits before sorting — so always `SORT` before `LIMIT`.

**Task dashboard — sorted by priority then due date within status groups:**

```dataview
TABLE without id
  file.link AS Task,
  status AS Status,
  priority AS Priority,
  due_date AS Due,
  project AS Project,
  domain AS Domain
FROM "tasks"
WHERE type = "task"
SORT priority DESC, due_date ASC
GROUP BY status
```

Note on `GROUP BY` + `SORT`: Dataview processes `SORT` before `GROUP BY` — tasks within each group will be sorted by priority then due_date.

**Project dashboard — at-risk detection:**

"At risk" = has overdue tasks OR no activity in 7+ days (both signals, per CONTEXT.md).

```dataview
TABLE without id
  file.link AS Project,
  status AS Status,
  health AS Health,
  next_action AS "Next Action",
  deadline AS Deadline
FROM "projects"
WHERE type = "project" AND status = "active"
SORT health ASC, deadline ASC
```

**At-risk indicator:** Dataview cannot easily JOIN across files (tasks referencing a project). The health field in project frontmatter (`green | yellow | red`) is the right signal. Claude sets `health: red` on projects with overdue tasks when updating projects. The `file.mtime < date(today) - dur(7 days)` check works for "no activity" since project file modification time tracks last update.

**Supplementary at-risk query (stale projects — no activity in 7+ days):**

```dataview
TABLE without id
  file.link AS Project,
  health AS Health,
  file.mtime AS "Last Updated"
FROM "projects"
WHERE type = "project" AND status = "active"
  AND file.mtime < date(today) - dur(7 days)
SORT file.mtime ASC
```

**Dashboard file targets (from AI workspace CLAUDE.md):**
- Tasks: `05_AI_Workspace/dashboards/tasks-by-status.md` (replace Phase 1 stub)
- Projects: `05_AI_Workspace/dashboards/projects-health.md` (create new)

**Dashboard frontmatter:**
```yaml
---
type: dashboard
created: YYYY-MM-DD
refreshed_by: YYYY-MM-DD
---
```

**`FROM "tasks"` path issue (identified in Phase 2 research):** Dataview `FROM "tasks"` queries a vault-relative path. Tasks live in the project root (`/Users/richardyu/.../second-brain/tasks/`), NOT in the vault. The existing `tasks-by-status.md` already uses `FROM "tasks"` — this returns zero results until vault has a `tasks/` folder, OR tasks are symlinked, OR the Dataview query is changed to use `FROM ""` with a WHERE filter. **This is a pre-existing issue from Phase 1 that must be addressed.**

**Resolution options:**
1. Create a symlink from vault `tasks/` → project `tasks/` (file system level)
2. Use `FROM ""` with `WHERE type = "task"` (scans all vault notes, slower)
3. Move tasks into vault (breaks current architecture)

**Recommendation:** Option 1 (symlink) is cleanest. Option 2 works without filesystem changes. The planner should make a decision on this — it's a blocker for Dataview dashboards working correctly.

### Anti-Patterns to Avoid

- **Interactive prompts in hooks:** `session-end.sh` cannot ask questions. Reflection question must come from an EOD skill that Claude invokes, not from the hook.
- **Pre-computing Dataview table content:** Write the query syntax, not a static markdown table. Dataview renders live.
- **Hardcoding dates in dashboard notes:** The `refreshed_by` field is fine; don't hardcode task counts or summaries (they go stale).
- **Writing to vault PARA folders (01–04):** Write guard hook will block this. All writes go to `05_AI_Workspace/`.
- **Quoted dates in task frontmatter:** `due_date: "2026-03-15"` is TEXT in Dataview, breaking date comparisons. `due_date: 2026-03-15` (bare) is typed as date.
- **Overwriting MEMORY.md completely:** EOD update should append/update specific sections, not overwrite the file — preserves existing preferences and patterns learned.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Task scanning for morning brief | Custom indexer or caching layer | Claude reads task files directly each invocation | Skills run on-demand; files are small; no index needed |
| Date parsing from natural language | Regex date parser | Claude's built-in NLU | Claude handles "next Friday", "end of week", "EOD" natively |
| Dashboard rendering | Python script to generate HTML/markdown tables | Dataview live queries | Dataview re-evaluates automatically when vault opens |
| Session learnings persistence | Custom database | MEMORY.md append | Already established in Phase 2; consistent with architecture |
| Project health computation | Automated health scoring script | Claude sets health field when updating projects | Schema has `health: green|yellow|red`; human/Claude judgment beats automation for small data |

**Key insight:** All four deliverables in this phase are instruction/configuration problems, not code problems. The work is writing clear skill specifications and correct Dataview queries.

---

## Common Pitfalls

### Pitfall 1: `FROM "tasks"` Returns Zero Results

**What goes wrong:** Dataview dashboard appears to work (no syntax errors) but shows no tasks because tasks live in the project directory, not the Obsidian vault.

**Why it happens:** Dataview's `FROM "folder"` queries vault-relative paths. The tasks folder is at `second-brain/tasks/`, which is not inside the Obsidian vault (`~/Library/Mobile Documents/.../Home/`).

**How to avoid:** Decide before creating dashboards whether to symlink or use `FROM ""`. A symlink at vault root pointing to the project tasks/ folder allows `FROM "tasks"` to work. Without it, use `FROM ""` with `WHERE type = "task"` as a fallback (slower but functional).

**Warning signs:** Dashboard renders, all columns empty, no "query error" shown.

### Pitfall 2: EOD Hook Tries to Be Interactive

**What goes wrong:** session-end.sh outputs a reflection question expecting user response. Hooks run non-interactively — output goes to stdout (injected as context) but there's no conversation turn to receive a reply.

**Why it happens:** Confusing hook stdout injection (context prepended to session) with interactive conversation.

**How to avoid:** Keep session-end.sh purely data-writing (append Day Summary section to daily-brief). Reflection question lives in the EOD skill that Claude invokes interactively before session close.

**Warning signs:** reflection question appears in context at session start of the NEXT session (because it was appended to context at the end of the previous one).

### Pitfall 3: MEMORY.md Overflow from Session Learnings

**What goes wrong:** Each EOD session appends learnings to MEMORY.md; after 10-15 sessions it exceeds 200 lines and content stops auto-loading.

**Why it happens:** Unbounded append without line count management.

**How to avoid:** Before appending, check `wc -l` on MEMORY.md. If >170 lines, consolidate/prune before adding. The EOD skill should include this check as a step. Target: keep MEMORY.md under 150 lines (headroom for growth).

**Warning signs:** MEMORY.md exceeds 200 lines; Claude seems to have forgotten preferences it previously knew.

### Pitfall 4: Daily Brief Accumulates Stale "Automation Opportunities"

**What goes wrong:** Automation opportunities section lists stale opportunities (e.g., "3 waiting tasks — draft follow-ups?") that were already actioned days ago.

**Why it happens:** Brief is generated fresh each day but tasks may still be in "waiting" status even after follow-ups were drafted.

**How to avoid:** Automation opportunities should only list tasks where the suggested action hasn't been explicitly done. The skill should note: "flag only tasks whose status hasn't changed since the last brief." In practice, keep automation opportunities based on current live status — accept that some suggestions repeat.

**Warning signs:** User stops reading the automation opportunities section because it's always the same stale list.

### Pitfall 5: `/new-task` Prompt Loop Friction

**What goes wrong:** Standard `/new-task` asks confirmation + "want to add notes?" — two prompts per task. If user is in rapid capture mode this becomes annoying.

**Why it happens:** CONTEXT.md locked the post-creation offer, but it should be a single offer, not a loop.

**How to avoid:** Post-creation offer is ONE message. User says yes or no. Done. Don't prompt again. The quick variant (`/new-task quick`) skips even this. Avoid multi-turn confirmation dialogs.

**Warning signs:** User starts using quick variant for everything because standard is too chatty.

### Pitfall 6: Dataview `SORT` + `GROUP BY` Ordering Confusion

**What goes wrong:** Tasks within status groups appear in random order rather than priority → due date order.

**Why it happens:** Execution order: if `GROUP BY` comes before `SORT` in the query, sorting applies to groups not rows within groups. Dataview processes commands in written order.

**How to avoid:** Write `SORT` before `GROUP BY` in the query. Dataview will sort rows first, then group them — maintaining sort order within groups.

**Warning signs:** Dashboard shows tasks in each group but ordering within groups looks wrong.

---

## Code Examples

Verified patterns from official Dataview docs and existing codebase:

### Task Dashboard Query (verified syntax)

```dataview
TABLE without id
  file.link AS Task,
  status AS Status,
  priority AS Priority,
  due_date AS Due,
  project AS Project
FROM "tasks"
WHERE type = "task"
SORT priority DESC, due_date ASC
GROUP BY status
```

Source: Official Dataview docs (fetched 2026-03-15) — `SORT` before `GROUP BY` for intra-group ordering.

### Project Health Dashboard Query (verified syntax)

```dataview
TABLE without id
  file.link AS Project,
  health AS Health,
  next_action AS "Next Action",
  deadline AS Deadline,
  file.mtime AS "Last Updated"
FROM "projects"
WHERE type = "project" AND status = "active"
SORT health ASC, deadline ASC
```

### Stale Project Detection (verified syntax)

```dataview
TABLE without id
  file.link AS Project,
  file.mtime AS "Last Modified"
FROM "projects"
WHERE type = "project"
  AND status = "active"
  AND file.mtime < date(today) - dur(7 days)
SORT file.mtime ASC
```

Source: `file.mtime` is a verified implicit field (Dataview docs, 2026-03-15).

### Morning Brief Note Skeleton

```markdown
---
type: daily-brief
date: 2026-03-15
generated_by: claude
---

# Daily Brief — 2026-03-15

## At a Glance
X tasks due today · Y overdue · Z follow-ups

## Tasks
| Task | Status | Project |
|------|--------|---------|
| ... | ... | ... |

## Automation Opportunities
- 3 tasks marked `waiting` — want me to draft follow-ups?

---
<!-- Day Summary appended by session-end.sh -->
```

### Day Summary Section (appended by session-end.sh)

```bash
# In session-end.sh, append to today's daily-brief:
BRIEF="$VAULT/05_AI_Workspace/daily-briefs/$(date +%Y-%m-%d)-daily-brief.md"
if [[ -f "$BRIEF" ]]; then
  cat >> "$BRIEF" << EOF

## Day Summary
*Session closed: $(date +%Y-%m-%d %H:%M)*
EOF
fi
```

### Enhanced /new-task Frontmatter Template

```yaml
---
type: task
title: [natural language title]
due_date: YYYY-MM-DD           # bare ISO — no quotes
status: backlog
priority: medium               # high | medium | low (inferred or default)
project: "[[ProjectName]]"     # wikilink in quotes, or omit
domain: admin                  # inferred from keywords
context: deep                  # quick | deep | collab (inferred)
tags: []
created: YYYY-MM-DD
---
```

### MEMORY.md Session Learnings Append Pattern

```bash
# Check line count before appending
MEMORY="$HOME/.claude/projects/-Users-richardyu-PARA-01-Projects-Personal-apps-second-brain/memory/MEMORY.md"
lines=$(wc -l < "$MEMORY")
if [[ $lines -gt 170 ]]; then
  echo "WARNING: MEMORY.md at $lines lines — consolidate before adding more"
fi
```

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|-----------------|--------------|--------|
| `/today` command (existing) | Morning briefing skill with structured brief format + vault note output | Phase 3 | Brief now persists in vault; orients before listing |
| Manual EOD capture | SessionEnd hook + EOD skill | Phase 3 | Auto-detected task changes; structured Day Summary appended |
| Basic `/new-task` (title only) | Enhanced `/new-task` with rich YAML fields | Phase 3 | Tasks appear correctly in Dataview dashboards |
| Stub `tasks-by-status.md` (Phase 1) | Full dashboard with GROUP BY status + projects health | Phase 3 | Live queryable dashboards in Obsidian |

**Deprecated/outdated:**
- Existing `daily-digest/skill.md`: writes to `daily/[YYYY-MM-DD].md` (project root, not vault). Phase 3 replaces this with vault writes to `05_AI_Workspace/daily-briefs/`. The old skill.md should be replaced, not extended.
- Existing `/today` command: The `today.md` command writes to `daily/` and sends Slack DM. Phase 3 replaces the morning briefing portion; Slack DM is deferred to a later phase.

---

## Open Questions

1. **`FROM "tasks"` vault path resolution**
   - What we know: Tasks live in project root (`second-brain/tasks/`), NOT in the Obsidian vault. Dataview `FROM "tasks"` queries vault-relative paths. Current stub dashboard uses `FROM "tasks"` which returns zero results.
   - What's unclear: Should tasks be symlinked into the vault? Or should the query use `FROM ""` with `WHERE type = "task"`? This is a blocker for dashboard functionality.
   - Recommendation: The planner should create a task for this decision. Symlink is cleanest (one-time setup, `FROM "tasks"` works as written). `FROM ""` works without filesystem changes but scans everything. **Default recommendation: use `FROM ""` with `WHERE type = "task"` — zero setup, works immediately, slight performance hit is acceptable for small vaults.**

2. **Whether EOD skill or hook captures reflection**
   - What we know: Hooks are non-interactive. The locked decision says "ask one optional reflection question" at EOD. This must be in a skill, not a hook.
   - What's unclear: Is there an automatic trigger to invoke the EOD skill, or does the user invoke it manually? The locked decision says "invocation: automatic at SessionEnd."
   - Recommendation: Split cleanly — session-end.sh handles the mechanical write (Day Summary timestamp) automatically. The EOD *skill* (interactive reflection question + MEMORY.md update) is invoked manually by user before closing, or Claude prompts for it during the session. The automatic part is the timestamp; the interactive part requires manual invocation.

3. **What replaces vs. what extends existing skills**
   - What we know: `daily-digest/skill.md` writes to `daily/` (wrong path). `today.md` command duplicates much of what the morning brief skill will do.
   - What's unclear: Should Phase 3 replace these files, or create parallel new ones?
   - Recommendation: Replace `daily-digest/skill.md` with the new morning briefing spec (same skill folder, new content). The `today.md` command can be updated to point to the new skill. Don't create duplicates.

---

## Sources

### Primary (HIGH confidence)

- Obsidian Dataview official docs (fetched 2026-03-15):
  - `https://blacksmithgu.github.io/obsidian-dataview/queries/data-commands/` — WHERE, SORT, GROUP BY, FLATTEN syntax; execution order
  - `https://blacksmithgu.github.io/obsidian-dataview/reference/functions/` — date(), dur(), default(), striptime(), file.mtime
  - `https://blacksmithgu.github.io/obsidian-dataview/annotation/metadata-pages/` — file.mtime, file.mday, file.ctime implicit fields
- Phase 2 RESEARCH.md — SessionEnd timeout (5000ms configured), hook stdout behavior, MEMORY.md 200-line limit
- Phase 2 implementation artifacts (02-01-SUMMARY.md, 02-02-SUMMARY.md) — confirmed what Phase 2 actually built
- `~/.claude/settings.json` — inspected directly; confirmed SessionEnd registered with 5000ms timeout
- `.claude/hooks/session-end.sh` — inspected directly; current implementation (timestamp-only)
- `.claude/hooks/session-start.sh` — inspected directly; task scanning pattern for reuse
- `05_AI_Workspace/CLAUDE.md` — inspected; daily-brief filename convention, write rules, subfolder purposes
- `05_AI_Workspace/dashboards/tasks-by-status.md` — inspected; current Phase 1 stub to be replaced
- `.planning/phases/01-foundation/yaml-frontmatter-schema.md` — inspected; full field definitions
- `.claude/commands/new-task.md` — inspected; current state to be enhanced
- `.claude/skills/surfacing/daily-digest/skill.md` — inspected; existing skill to be replaced

### Secondary (MEDIUM confidence)

- `.claude/skills/_meta/skill-creator/skill.md` — skill structure conventions (from codebase)
- `.claude/commands/today.md` — existing command to be updated

### Tertiary (LOW confidence)

- Dataview `GROUP BY` + `SORT` intra-group ordering behavior — documented in official docs but "commands process in written order" is the stated behavior; actual rendering order in Obsidian should be verified visually when dashboards are first opened

---

## Metadata

**Confidence breakdown:**
- Dataview query syntax (WHERE, SORT, GROUP BY): HIGH — official docs fetched directly
- Dataview `file.mtime` implicit field: HIGH — official docs
- Dataview `FROM "tasks"` path issue: HIGH — filesystem verified (tasks not in vault)
- SessionEnd hook constraints: HIGH — Phase 2 research + settings.json inspection
- Skill .md file structure: HIGH — existing skills inspected
- MEMORY.md line limit: HIGH — Phase 2 verified (200-line limit)
- Natural language parsing approach for /new-task: MEDIUM — Claude's NLU capability is well-established; specific edge case handling is discretionary
- EOD interactive vs. automatic split: MEDIUM — derived from hook architecture constraints

**Research date:** 2026-03-15
**Valid until:** 2026-04-15 (Dataview API is stable; Claude Code hooks API stable; MEMORY.md limit unlikely to change)
