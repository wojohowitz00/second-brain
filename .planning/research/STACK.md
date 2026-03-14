# Technology Stack: Hybrid Brain OS

**Project:** Hybrid Brain OS — proactive AI monitoring layer on existing Second Brain
**Research type:** Stack dimension only (subsequent milestone)
**Researched:** 2026-03-14
**Overall confidence:** HIGH (primary sources: official Claude Code docs, official Obsidian changelog, Dataview official docs)

---

## Scope Note

This document covers the stack for the *new* milestone additions only. The existing Python backend (Slack capture, Ollama classification, macOS menu bar app, 259 tests) is **out of scope** — it is mature and unchanged.

---

## Recommended Stack

### Claude Code Layer

| Technology | Version / Location | Purpose | Why |
|---|---|---|---|
| **CLAUDE.md** (user-level) | `~/.claude/CLAUDE.md` | Persistent personal context across all projects | Loaded every session; ideal for vault paths, personal preferences, domain context that applies everywhere. Scoped to you only — not committed. |
| **CLAUDE.md** (project-level) | `second-brain/CLAUDE.md` | Project-specific context for this system | Vault structure, PARA conventions, file path patterns, established workflow rules. Can import sub-files with `@` syntax. |
| **Skills** | `~/.claude/skills/<name>/SKILL.md` (personal) or `.claude/skills/<name>/SKILL.md` (project) | On-demand workflow execution (`/morning`, `/weekly`, `/people`, etc.) | Load only when invoked — don't bloat every session. Frontmatter controls auto-invocation vs. explicit `/slash-command` invocation. Use `disable-model-invocation: true` for side-effect workflows you want to control manually. |
| **Hooks** | `~/.claude/settings.json` (global) or `.claude/settings.json` (project) | Deterministic automation at session lifecycle points | Unlike CLAUDE.md instructions (advisory), hooks are guaranteed. Use `SessionStart` for stale-task surfacing, `Stop` / `SessionEnd` for dashboard updates, `Notification` for macOS alerts. |
| **Auto Memory** | `~/.claude/projects/<project>/memory/MEMORY.md` | Claude-maintained learnings across sessions | Requires Claude Code ≥ v2.1.59. Claude writes what it discovers — preferred vault paths, user patterns, corrections made. 200-line limit on `MEMORY.md`; detailed notes go into topic files (`debugging.md`, `patterns.md`) in the same directory. |
| **`.claude/rules/`** | `.claude/rules/*.md` with optional `paths:` frontmatter | Scoped rules loaded only for specific file types or directories | Better than giant CLAUDE.md. Rules without `paths` load at launch; rules with `paths` load lazily when Claude touches matching files. |

**Confidence:** HIGH — all Claude Code details verified against official docs at code.claude.com (March 2026).

---

### Obsidian Data Layer

| Technology | Version | Purpose | Why |
|---|---|---|---|
| **Dataview** plugin | 0.5.70 (April 2024, maintenance mode) | Structured queries across vault notes via YAML frontmatter | The battle-tested standard. ~3 million downloads. Embeds as `dataview` codeblocks in notes. Supports LIST, TABLE, TASK, CALENDAR query types with DQL (Dataview Query Language) and DataviewJS for complex logic. |
| **YAML Frontmatter** (Obsidian Properties) | Core feature (Obsidian ≥ 1.4) | Structured metadata on every note | Native to Obsidian. Dataview reads all YAML fields automatically. The canonical way to attach structured data (status, type, dates, people) to notes. |
| **Obsidian Bases** | Core plugin, Obsidian ≥ 1.9.0 (currently Catalyst early access; 1.12.5 is latest) | GUI-driven database views over note properties | DO NOT USE YET for this milestone. Still in extended early access (Catalyst-only as of March 2026). Limited to table views. Cannot aggregate tasks. Dataview covers all needed use cases today. Monitor for GA release. |
| **Obsidian Canvas** | Core feature, Obsidian ≥ 1.1 | Visual dashboards — weekly review maps, project relationship maps | JSON-based open format. Drag-and-drop nodes that can be notes, text cards, or web embeds. Suitable for static visual layouts; not queryable by Dataview. Best used as fixed-layout visual templates, not dynamic dashboards. |
| **Templater** plugin | Active (verify version in plugin settings) | Note templates with dynamic content (dates, prompts, computed fields) | More powerful than Obsidian's built-in Templates. Supports JavaScript templating via `tp.*` functions. Required for creating structured notes with correct YAML frontmatter on creation. |

**Confidence:** HIGH for Dataview and YAML (official docs verified). MEDIUM for Bases (changelog verified: 1.9.0 introduced Bases, 1.12.5 current; GA status unclear — described as "extended early access" throughout 2025-2026). HIGH for Canvas (core feature, stable).

---

### Notification / Alerting Layer

| Technology | Purpose | Why |
|---|---|---|
| **macOS `osascript`** | Native macOS notifications from hooks | No dependencies. Works directly in Claude Code `Notification` hooks. Pattern: `osascript -e 'display notification "..." with title "Claude Code"'` |
| **Slack (existing `#sb-inbox`)** | Async alerts for things requiring attention | Already integrated in v1.0 Python backend. Skills can write to Slack via existing backend API or directly via `curl` to Slack webhook. Reuse existing infrastructure, no new service. |
| **Obsidian daily note** | In-vault alert log (stale tasks, follow-ups, AI insights) | Keeps alerts in the knowledge system. Skills write to the current daily note in `05_AI_Workspace/daily/`. Visible in Obsidian mobile too. |

**Confidence:** HIGH for osascript (hook docs verified). HIGH for Slack (existing system). MEDIUM for daily note write pattern (common community pattern, not officially documented).

---

### File System / Storage

| Approach | Purpose | Why |
|---|---|---|
| **`05_AI_Workspace/` folder in vault** | All AI-generated content (dashboards, insights, briefings, daily notes, memory scratchpads) | Maintains vault purity constraint. Human PARA folders (01-04) are never AI-written. Dataview can query this folder the same as any other. |
| **Claude Code memory files** (`~/.claude/projects/...`) | Claude's own session learnings, preferences, corrections | Kept outside vault intentionally. Session context and personal AI preferences are not knowledge artifacts. |
| **YAML frontmatter in vault notes** | All structured data: task status, person metadata, project state, habit tracking | No external database. Everything lives in markdown files. Portable, versionable via Obsidian Git plugin. Queryable by Dataview. |

**Confidence:** HIGH — consistent with project constraints in PROJECT.md and community best practice.

---

## Skill File Format (Prescriptive)

Skills for this project follow this exact format:

```markdown
---
name: morning-briefing
description: Generate morning briefing with priorities, stale tasks, and focus recommendations. Use when starting the day.
disable-model-invocation: true
allowed-tools: Read, Grep, Glob, Bash(osascript *)
---

# Morning Briefing

[Instructions for Claude...]

$ARGUMENTS
```

**Key frontmatter decisions:**

| Field | When to Use | Rationale |
|---|---|---|
| `disable-model-invocation: true` | Any skill with side effects (writes to vault, sends Slack, sends notifications) | You control timing of morning briefings, EOD updates, Slack alerts — Claude should not auto-trigger these |
| `allowed-tools: Read, Grep, Glob` | Read-only skills (digest generation, pattern detection) | Scope Claude's tool access to what the skill actually needs |
| `context: fork` | Research-heavy skills that read many vault files | Keeps investigation in a subagent, preserves main session context |
| `user-invocable: false` | Background reference skills (vault conventions, PARA rules) | Claude loads automatically when relevant; not a meaningful slash command |

**Personal skills location:** `~/.claude/skills/` — shared across all projects, not committed to this repo.
**Project skills location:** `.claude/skills/` — if skills are specific to this project.

For this system, use **personal skills** (`~/.claude/skills/`) since skills encode personal workflow knowledge that applies across all your Claude sessions, not just when in the `second-brain/` directory.

---

## Hook Configuration Format (Prescriptive)

Hooks live in `~/.claude/settings.json` (global, personal) or `.claude/settings.json` (project).

**Pattern for session-start task surfacing:**

```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "startup",
        "hooks": [
          {
            "type": "command",
            "command": "echo 'Scan ~/.claude/projects/*/memory/MEMORY.md and the vault at ~/Library/Mobile\\ Documents/iCloud~md~obsidian/Documents/Home/ for stale tasks (due date passed, status=in-progress for >7 days). Surface the top 3 most urgent items at session start.'"
          }
        ]
      }
    ]
  }
}
```

**Pattern for macOS notification on idle:**

```json
{
  "hooks": {
    "Notification": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "osascript -e 'display notification \"Claude Code needs your attention\" with title \"Second Brain\"'"
          }
        ]
      }
    ]
  }
}
```

**Pattern for session-end dashboard update:**

```json
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "prompt",
            "prompt": "Check if any dashboard notes in 05_AI_Workspace need updating based on the work done this session. If so, update them. Otherwise respond with {\"ok\": true}."
          }
        ]
      }
    ]
  }
}
```

**Available hook events (verified from official docs):**

| Event | Use For |
|---|---|
| `SessionStart` (matcher: `startup`) | Surface stale tasks on new session |
| `SessionStart` (matcher: `compact`) | Re-inject vault context after compaction |
| `Stop` | Dashboard refresh after session |
| `SessionEnd` | Cleanup, final sync |
| `Notification` | macOS alert pass-through |
| `PostToolUse` (matcher: `Write\|Edit`) | Trigger Dataview refresh notification |
| `PreToolUse` (matcher: `Write\|Edit`) | Block writes to PARA folders (01-04) — vault purity enforcement |

**Confidence:** HIGH — all hook events and JSON format verified from official hooks guide at code.claude.com.

---

## Dataview Query Patterns (Prescriptive)

### Standard query codeblock syntax

````markdown
```dataview
TABLE status, due, priority
FROM "01_Projects"
WHERE status != "done"
SORT priority DESC, due ASC
LIMIT 20
```
````

### Query type selection guide

| Use | Query Type | Notes |
|---|---|---|
| Dashboard tables (projects, people, habits) | `TABLE` | Multiple columns, custom headers with `AS "label"` |
| Simple lists (recent captures, active areas) | `LIST` | Single value per row; use `WITHOUT ID` to suppress file link |
| Task tracking across vault | `TASK` | Aggregates checkboxes from all matched notes; unique to Dataview, not available in Bases |
| Date-based habit/event views | `CALENDAR` | Requires a date field in frontmatter |

### YAML frontmatter conventions for Dataview queries

All notes that should be queryable must have consistent YAML frontmatter. Recommend standardizing on:

```yaml
---
type: project | area | resource | person | daily | capture
status: active | in-progress | waiting | done | archived
priority: 1 | 2 | 3
due: 2026-03-20
tags: [work, personal]
domain: professional | personal | people | research
created: 2026-03-14
---
```

**Critical:** Dataview treats YAML field names as case-sensitive. `Status` and `status` are different fields. Standardize on lowercase.

### DataviewJS (for complex dashboard logic)

````markdown
```dataviewjs
const pages = dv.pages('"01_Projects"')
  .where(p => p.status === "active")
  .sort(p => p.priority, 'asc');
dv.table(["Project", "Status", "Due"],
  pages.map(p => [p.file.link, p.status, p.due]));
```
````

Use DataviewJS when: computed columns are needed, you need conditional logic, or you need to aggregate across multiple sources in one table.

**Dataview version note:** 0.5.70 (April 2024) is the current release. Project is in maintenance mode — new maintainer (@holroy) since March 2024. Functional and stable; do not expect new features. Bases is the eventual successor but is not production-ready.

**Confidence:** HIGH for DQL syntax (official docs). MEDIUM for version status (GitHub releases verified, maintenance mode inferred from release cadence).

---

## What NOT to Use (Anti-Stack)

| Technology | Why Not |
|---|---|
| **Obsidian Bases** (now) | Still Catalyst-only early access as of March 2026. Cannot aggregate tasks. Only table views. Dataview covers all current needs. Revisit for GA release. |
| **Datacore** | Beta. Requires React knowledge for advanced queries. Overkill for personal system. Dataview is sufficient. |
| **Supabase / SQLite** | Explicitly out of scope. Breaks data locality constraint. Vault YAML is the database. |
| **MCP server (obsidian-local-rest-api for Claude Code)** | Adds external service dependency (plugin must be running). For this system, Claude Code reads vault files directly via filesystem — simpler, no service dependency. MCP is useful for Claude Desktop integration but unnecessary here. |
| **React dashboards / web apps** | Out of scope. Obsidian Canvas + Dataview notes are the dashboard layer. |
| **Inline Dataview fields (`[key:: value]`)** | Avoid in favor of YAML frontmatter. Frontmatter is native Obsidian Properties; inline fields are a Dataview-specific pattern that doesn't integrate with Obsidian's Properties panel or Bases. |
| **Global `CLAUDE.md` > 200 lines** | Performance degrades. Claude ignores rules buried in long files. Use `@imports` and `.claude/rules/` to modularize. |
| **Skills for rules Claude should always follow** | Use CLAUDE.md or `.claude/rules/` for always-on rules. Skills are for on-demand workflows, not baseline behavior. |
| **`SessionStart` hook for every session** (without `startup` matcher) | Triggers on `resume`, `compact`, and `clear` too — creates excessive noise. Use matcher `startup` for new-session-only surfacing. |

---

## CLAUDE.md Architecture (Prescriptive)

Given the personal system scope, use this hierarchy:

```
~/.claude/CLAUDE.md                      # Global personal rules (50-100 lines max)
~/.claude/rules/vault.md                 # Vault paths and PARA conventions
~/.claude/rules/ai-workspace.md          # 05_AI_Workspace folder rules and write constraints
~/.claude/skills/morning-briefing/       # /morning skill
~/.claude/skills/eod-update/             # /eod skill
~/.claude/skills/weekly-review/          # /weekly skill (extend existing)
~/.claude/skills/people-crm/             # /people skill
~/.claude/skills/dashboard/              # /dashboard skill
~/.claude/skills/insights/               # /insights skill
~/.claude/projects/<project>/memory/     # Auto-memory (Claude-managed, do not edit structure)
```

**Keep `~/.claude/CLAUDE.md` focused on:**
- Vault absolute path
- The rule: AI never writes to 01-04 PARA folders
- Preferred notification patterns (Slack channel name, notification style)
- Personal writing voice (for /writing skills)

**Put vault conventions in `~/.claude/rules/vault.md`** with `paths:` frontmatter scoped to markdown files, so it loads lazily when Claude works with `.md` files.

---

## Version Summary

| Component | Version | Status | Source |
|---|---|---|---|
| Claude Code | ≥ 2.1.59 (for auto-memory) | Active | Official docs |
| Obsidian | 1.12.5 (March 2026, Catalyst) | Active | Official changelog |
| Dataview plugin | 0.5.70 (April 2024) | Maintenance | GitHub releases |
| Obsidian Bases | Ships with Obsidian ≥ 1.9.0 | Early access (Catalyst) | Official changelog |
| Obsidian Canvas | Ships with Obsidian ≥ 1.1 | Stable | Core feature |
| Templater plugin | Active (check plugin settings) | Active | Community plugin |
| YAML Frontmatter (Properties) | Ships with Obsidian ≥ 1.4 | Stable | Core feature |

---

## Sources

**HIGH confidence (official documentation, verified March 2026):**
- Claude Code best practices: https://code.claude.com/docs/en/best-practices
- Claude Code hooks guide: https://code.claude.com/docs/en/hooks-guide
- Claude Code memory / CLAUDE.md: https://code.claude.com/docs/en/memory
- Claude Code skills: https://code.claude.com/docs/en/skills
- Dataview official docs: https://blacksmithgu.github.io/obsidian-dataview/
- Dataview query types: https://blacksmithgu.github.io/obsidian-dataview/queries/query-types/
- Obsidian changelog: https://obsidian.md/changelog/

**MEDIUM confidence (community sources, cross-referenced):**
- Dataview vs Datacore vs Obsidian Bases comparison: https://obsidian.rocks/dataview-vs-datacore-vs-obsidian-bases/
- Obsidian Bases introduction (1.9.0): https://5typos.net/2025/05/23/obsidian-1-9-0-desktop-introduces-bases
- Dataview GitHub releases (version/maintenance status): https://github.com/blacksmithgu/obsidian-dataview/releases
- Hooks, Rules, Skills overview: https://jessezam.medium.com/hooks-rules-and-skills-feedback-loops-in-claude-code-d47e5f58364d
- Auto-memory MEMORY.md: https://medium.com/@joe.njenga/anthropic-just-added-auto-memory-to-claude-code-memory-md-i-tested-it-0ab8422754d2
