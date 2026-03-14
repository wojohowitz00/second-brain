# Architecture Patterns

**Domain:** Hybrid Open Brain / Second Brain personal OS
**Researched:** 2026-03-14
**Milestone context:** Subsequent — adding Proactive Layer to existing Obsidian + Claude Code system

---

## System Overview

The hybrid system has three established layers and one new layer being added. This document maps the full architecture including where the Proactive Layer fits.

```
┌─────────────────────────────────────────────────────────────────┐
│                    OBSIDIAN VAULT (iCloud sync)                 │
│  01_Projects/ 02_Areas/ 03_Research/ 04_Archive/  05_AI_Workspace/│
│  (Human PARA — AI reads only)                    (AI writes)   │
├─────────────────────────────────────────────────────────────────┤
│                    CLAUDE CODE INTERACTIVE LAYER               │
│  .claude/skills/  .claude/commands/  .claude/hooks/            │
│  _llm-context/    CLAUDE.md          auto memory               │
├─────────────────────────────────────────────────────────────────┤
│                    PYTHON AUTOMATED LAYER (MATURE)             │
│  Slack → Ollama classifier → Obsidian file routing             │
│  backend/_scripts/  (259 tests, do not modify)                │
└─────────────────────────────────────────────────────────────────┘
```

---

## Component Boundaries

| Component | Responsibility | Reads From | Writes To | Communicates With |
|-----------|---------------|------------|-----------|-------------------|
| **Obsidian Vault (01-04)** | Human knowledge store | User edits | User only | Dataview (query), Python backend (file in) |
| **05_AI_Workspace** | AI-generated content store | Claude Code skills | Claude Code skills | Obsidian Dataview (surface via queries) |
| **Python backend** | Automated Slack capture + classification | Slack API, Ollama | 01-04 PARA folders | Obsidian, Slack |
| **Claude Code skills** | Interactive AI capabilities (9 skills) | Vault (01-04 + 05), _llm-context | 05_AI_Workspace, daily/ notes | Hooks, Memory, Obsidian |
| **Claude Code commands** | Session entry points (7 commands) | Vault, skills | Triggers skill execution | Skills |
| **Claude Code hooks** | Automated lifecycle triggers | Hook event JSON | 05_AI_Workspace, Slack, stdout context | Claude session |
| **Claude Code memory** | Cross-session context persistence | ~/.claude/projects/.../memory/ | MEMORY.md + topic files | Every session start |
| **CLAUDE.md + rules/** | Session-persistent instructions | Static files | Claude context window | Every session |
| **_llm-context/** | Progressive context disclosure | Profile/style files | Claude context (on demand) | Skills load these on invocation |
| **Dataview dashboards** | Dynamic views across vault | YAML frontmatter across all notes | Read-only rendered views | Obsidian only |
| **Slack + macOS notifications** | Proactive alert delivery | Hook triggers | User-facing alerts | Hooks write, user receives |

---

## Data Flow

### Flow 1: Morning Ritual (Interactive Layer, existing)

```
User → /today command
  → today.md command loads
  → daily-digest skill invoked
  → reads tasks/, projects/, ideas/, people/ (01-04 PARA)
  → reads research/digests/ (05 once built)
  → writes daily/[date].md (interactive layer output)
  → optionally sends Slack DM
```

### Flow 2: Automated Slack Capture (Python Layer, existing, mature)

```
Slack #sb-inbox message
  → Python backend polls Slack API
  → Ollama classifies message
  → Routes to 01-04 PARA folder with YAML frontmatter
  → logs to _inbox_log/
```

### Flow 3: Hook-Triggered Proactive Alert (NEW - Proactive Layer)

```
Claude Code lifecycle event fires
  → Hook script reads event JSON from stdin
  → Script scans vault / evaluates condition
  → If threshold met: writes to 05_AI_Workspace/alerts/
  → Sends macOS notification (osascript) + Slack DM
  → Appends alert summary to daily/[date].md
  → Returns exit 0 to Claude (non-blocking)
```

### Flow 4: SessionStart Context Injection (NEW - Proactive Layer)

```
Claude Code session begins (startup or compact)
  → SessionStart hook fires
  → Hook script reads from ~/.claude/projects/.../memory/MEMORY.md
  → Hook script scans overdue tasks in vault
  → Outputs context string to stdout
  → Claude receives as pre-session context
  → Session proceeds with injected state
```

### Flow 5: AI Workspace Write (NEW - Proactive Layer)

```
Skill or hook generates AI content
  → Writes ONLY to 05_AI_Workspace/[subfolder]/
  → Follows naming convention: [date]-[type]-[slug].md
  → File has YAML frontmatter: type, generated_by, source_context, date
  → Obsidian Dataview queries 05_AI_Workspace to surface in dashboards
```

### Flow 6: Memory Update (NEW - Proactive Layer)

```
User corrects Claude or reveals preference
  → Claude decides this is worth remembering
  → Auto memory writes to ~/.claude/projects/.../memory/MEMORY.md
  → Or Claude writes to topic file (debugging.md, preferences.md, etc.)
  → Next session: first 200 lines of MEMORY.md injected at start
  → Topic files loaded on demand when relevant
```

### Flow 7: YAML-Dataview Query Loop (Obsidian Native)

```
Note with YAML frontmatter created by any source
  → Dataview indexes frontmatter automatically
  → Dashboard note contains dataview code block
  → Query: TABLE status, due_date FROM "01_Projects" WHERE type = "task"
  → Or: TABLE generated_by, date FROM "05_AI_Workspace" WHERE type = "digest"
  → Renders as live table in Obsidian, updates as files change
```

---

## Recommended Architecture

### 05_AI_Workspace Structure

```
05_AI_Workspace/
├── alerts/              # Time-sensitive proactive alerts
│   └── [date]-[type].md
├── digests/             # Daily/weekly AI-generated summaries
│   ├── daily/
│   │   └── [YYYY-MM-DD]-digest.md
│   └── weekly/
│       └── [YYYY-WW]-digest.md
├── research/            # AI-generated research outputs
│   └── [topic]/
│       └── [date]-[paper/topic].md
├── drafts/              # Writing assistance outputs
│   └── [project]/
└── dashboards/          # Dataview dashboard notes
    ├── task-dashboard.md
    ├── project-dashboard.md
    └── ai-activity.md
```

### YAML Frontmatter Convention for AI-Generated Files

All files in `05_AI_Workspace` must carry this frontmatter:

```yaml
---
type: [digest|alert|draft|research-summary]
generated_by: claude-code
skill: [skill-name]
source_context: [where data came from, e.g., "tasks/ scan"]
date: YYYY-MM-DD
status: [generated|reviewed|archived]
tags: [#ai-generated, #domain-tag]
---
```

This makes all AI content queryable by Dataview and distinguishable from human content.

### Hook Configuration Pattern

Hooks live in two locations depending on scope:

**Global (user-level, fires in any project):**
```
~/.claude/settings.json
hooks:
  SessionStart → inject vault summary into context
  Notification → macOS + Slack alert on idle
  Stop → optional: write session summary to 05_AI_Workspace
```

**Project-level (second-brain project only):**
```
second-brain/.claude/settings.json
hooks:
  PreToolUse (Write|Edit, matcher: "01_|02_|03_|04_") → block AI writes to PARA folders
  PostToolUse (Write) → log AI writes to 05_AI_Workspace to audit trail
  SessionStart (startup) → scan overdue tasks, inject into context
```

**Hook script location:**
```
second-brain/.claude/hooks/
├── protect-para-folders.sh    # PreToolUse: block writes to 01-04
├── inject-vault-summary.sh    # SessionStart: scan vault state
├── log-ai-writes.sh           # PostToolUse: audit trail
└── send-notification.sh       # Shared: osascript + Slack DM
```

### Memory File Organization

```
~/.claude/projects/[second-brain-path]/memory/
├── MEMORY.md              # Index, loaded first 200 lines every session
│                          # Contains: key preferences, recent patterns, current sprint
├── preferences.md         # Writing style, task management habits
├── patterns.md            # Recurring workflows Claude has learned
└── vault-conventions.md   # PARA structure, YAML field conventions
```

MEMORY.md concise index structure:
```markdown
# Memory Index

## Current Context
- [sprint/focus area, e.g., "adding proactive hooks"]
- [recent decisions]

## Key Preferences
- See preferences.md for full list
- Most important: [2-3 critical preferences inline]

## Vault Conventions
- See vault-conventions.md
- AI writes ONLY to 05_AI_Workspace/

## Recent Patterns
- [learned pattern 1]
- [learned pattern 2]
```

### Skill File Structure Pattern

Existing skills use a flat `skill.md` format (pre-frontmatter). New skills for the Proactive Layer should use current Claude Code frontmatter format:

```yaml
---
name: proactive-alert-check
description: Checks vault for overdue items and threshold conditions. Fires automatically on SessionStart or when invoked.
user-invocable: false
disable-model-invocation: false
allowed-tools: Read, Grep, Glob, Bash
hooks:
  PostToolUse:
    - matcher: "Write"
      hooks:
        - type: command
          command: "$CLAUDE_SKILL_DIR/../../hooks/log-ai-writes.sh"
---
```

Supporting files pattern for proactive skills:
```
skills/proactive/
├── alert-monitor/
│   ├── skill.md          # Main instructions + frontmatter
│   ├── thresholds.md     # Configurable alert thresholds
│   └── templates/
│       └── alert.md      # Alert file template
├── context-injector/
│   ├── skill.md
│   └── vault-scan.sh     # Shell script to scan vault state
```

### Dataview Dashboard Pattern

Dashboard notes in `05_AI_Workspace/dashboards/` use Dataview queries to surface content dynamically. No AI generation required — Obsidian renders these live.

Example task dashboard query:
```dataview
TABLE status, due_date, tags
FROM "01_Projects"
WHERE type = "task" AND status != "done"
SORT due_date ASC
```

Example AI activity dashboard:
```dataview
TABLE generated_by, skill, source_context
FROM "05_AI_Workspace"
WHERE date >= date(today) - dur(7 days)
SORT date DESC
```

The YAML frontmatter in each note is the contract between the data layer and the Dataview query layer. Changes to frontmatter field names require updating all corresponding queries.

---

## Patterns to Follow

### Pattern 1: Boundary Enforcement via PreToolUse Hook

**What:** Hook intercepts all Write/Edit tool calls and checks if file_path matches 01_-04_ prefix. Exits with code 2 and error message if AI tries to write to human PARA folders.

**When:** Always active in project settings.

**Implementation:**
```bash
#!/bin/bash
INPUT=$(cat)
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')

if echo "$FILE_PATH" | grep -qE "/(01_|02_|03_|04_)"; then
  echo "AI writes to human PARA folders (01-04) are prohibited. Write to 05_AI_Workspace/ instead." >&2
  exit 2
fi
exit 0
```

**Configuration:** `.claude/settings.json` → `PreToolUse` matcher `Write|Edit`.

### Pattern 2: Progressive Context Loading

**What:** Skills load context files (profile, style guide, vault conventions) only when that specific skill is invoked. Not at session start.

**When:** Any skill that needs domain context.

**How skills reference context:**
```markdown
## Dependencies
Load these files when invoked:
- `_llm-context/personal/profile.md` — personal context
- `_llm-context/writing/style-guide.md` — writing voice
```

**Why:** Loading all context upfront wastes tokens and hurts performance. One skill = one context load.

### Pattern 3: SessionStart as Lightweight State Injection

**What:** SessionStart hook runs a fast shell script that scans the vault for high-signal state (overdue task count, active project names, last digest date) and writes it to stdout as a brief context string.

**When:** Every session start (not compact — that uses PostCompact hook).

**Output format:**
```
=== Vault State (auto-injected) ===
Overdue tasks: 3
Active projects: Second Brain v2, CCBH Onboarding
Last AI digest: 2026-03-13
Focus today: proactive hooks milestone
================================
```

Claude receives this as pre-session context without any human prompt.

### Pattern 4: YAML as Contract Layer

**What:** Every file type has a canonical YAML frontmatter schema defined in templates. Dataview queries reference these exact field names. Skills use these same field names when writing files.

**When:** Whenever a skill creates a new file in 05_AI_Workspace.

**The chain:**
```
Template (backend/_templates/) → YAML schema
Skill writes file → uses template schema
Dataview queries → reference same field names
Dashboard renders → live view of correct data
```

Breaking a field name in the template breaks the Dataview query. This is the highest-risk coupling point in the system.

---

## Anti-Patterns to Avoid

### Anti-Pattern 1: AI Writing to Human PARA Folders

**What:** AI skill writes a generated file into 01_Projects/, 02_Areas/, etc.

**Why bad:** Contaminates human knowledge with AI-generated content. Breaks trust. User cannot easily audit what is human vs. AI-written.

**Instead:** All AI-generated content goes to 05_AI_Workspace/. PreToolUse hook enforces this.

### Anti-Pattern 2: Loading All Context at Session Start

**What:** CLAUDE.md imports all profile files, style guides, vault conventions upfront.

**Why bad:** Consumes context window before any task. Reduces adherence because instructions drown in irrelevant context.

**Instead:** Load context only in the skill that needs it. CLAUDE.md contains only project structure and critical rules (under 200 lines).

### Anti-Pattern 3: Blocking Hooks for Non-Critical Automation

**What:** Using PreToolUse or Stop hooks for logging, analytics, or nice-to-have behaviors that don't need to block execution.

**Why bad:** Blocking hooks add latency to every tool call. If the hook script fails, it can interfere with core workflows.

**Instead:** Use PostToolUse (non-blocking) for logging and audit. Use `async: true` for fire-and-forget operations. Reserve blocking hooks for true security/integrity requirements.

### Anti-Pattern 4: Hardcoded Paths in Hooks

**What:** Hook script references absolute paths like `/Users/richardyu/Library/Mobile Documents/...`.

**Why bad:** Breaks if vault moves. Not portable. Hard to maintain.

**Instead:** Use `$CLAUDE_PROJECT_DIR` for project-relative paths. Reference vault path from a config file or environment variable defined in SessionStart hook using `CLAUDE_ENV_FILE`.

### Anti-Pattern 5: Dataview Queries on Inline Fields Without YAML

**What:** Using Dataview inline fields (`[key:: value]`) scattered in note body instead of YAML frontmatter.

**Why bad:** Skills writing files must know where to put data. YAML frontmatter is a predictable top-of-file location. Inline fields are mixed into content and harder to write programmatically.

**Instead:** All queryable metadata in YAML frontmatter. Inline fields for ad-hoc human annotation only.

### Anti-Pattern 6: Memory Storing Volatile State

**What:** Writing today's task list or current project status to MEMORY.md.

**Why bad:** Memory is loaded fresh every session. Volatile data goes stale immediately and pollutes the 200-line budget.

**Instead:** Memory stores preferences, patterns, and conventions that change slowly. Current state comes from vault scan via SessionStart hook.

---

## Suggested Build Order

Dependencies flow upward — lower items must exist before higher items can be built.

```
Phase 1: Foundation
├── Create 05_AI_Workspace/ directory in Obsidian vault
├── Define YAML frontmatter schema for AI-generated files
├── Create file templates in backend/_templates/
└── Add basic Dataview dashboard in 05_AI_Workspace/dashboards/

Phase 2: Boundary Enforcement (before any AI writes)
├── PreToolUse hook: protect-para-folders.sh
├── PostToolUse hook: log-ai-writes.sh (audit trail)
└── Register hooks in .claude/settings.json

Phase 3: Memory & Cross-Session Context
├── Create memory directory structure
├── Seed MEMORY.md with vault conventions and key preferences
├── Create preferences.md and vault-conventions.md
└── Validate memory loads correctly on session start

Phase 4: SessionStart Context Injection
├── vault-scan.sh: queries overdue tasks, active projects, last digest date
├── SessionStart hook: startup matcher → runs vault-scan.sh
├── SessionStart hook: compact matcher → re-injects critical conventions
└── Test: verify context appears in Claude's session

Phase 5: Proactive Skills (reads vault, writes to 05_AI_Workspace)
├── Update daily-digest skill to write output to 05_AI_Workspace/digests/
├── Create alert-monitor skill with configurable thresholds
└── Create context-injector skill for on-demand vault summaries

Phase 6: Notification Layer
├── send-notification.sh: osascript + Slack DM
├── Wire Notification hook for idle prompts
└── Wire alert-monitor to notification script

Phase 7: Dashboard Completion
├── Refine Dataview queries based on actual field usage
├── Add ai-activity.md dashboard (surfaces all AI writes)
└── Wire new YAML frontmatter into existing task/project queries
```

**Critical dependency:** Phase 2 (boundary enforcement) must precede Phase 5 (proactive skills writing files). If AI skills write to vault before the PreToolUse hook is in place, they might accidentally write to human PARA folders.

**Safe to parallelize:** Phase 3 (memory) and Phase 4 (SessionStart hooks) are independent. Phase 1 (05_AI_Workspace structure) can be done anytime before Phase 5.

---

## Integration Points with Existing Architecture

### What Stays Unchanged

- Python backend (entire backend/_scripts/ — mature, 259 tests)
- Obsidian vault structure (01-04 PARA folders)
- Existing 9 skills (capture, surfacing, writing, research, meta)
- Existing 7 commands (today, weekly, new-task, pipeline, stuck, doable, learned)
- _llm-context/ progressive disclosure pattern

### What Gets Modified

| Existing Component | What Changes |
|-------------------|--------------|
| `daily-digest` skill | Add write path to `05_AI_Workspace/digests/daily/` alongside current `daily/[date].md` |
| `.claude/commands/today.md` | Add hook verification step: confirm protect-para hook is active |
| `backend/_templates/` | Add AI-generated file templates with required YAML schema |
| `CLAUDE.md` (project-level) | Add 05_AI_Workspace rules and boundary enforcement note |

### What Gets Added

| New Component | Purpose |
|---------------|---------|
| `05_AI_Workspace/` (vault) | AI content store |
| `.claude/hooks/` (project) | Hook scripts |
| `.claude/settings.json` (project) | Hook registrations |
| `~/.claude/projects/.../memory/` | Cross-session memory |
| `skills/proactive/` | New proactive skill category |

---

## Confidence Assessment

| Area | Confidence | Source |
|------|------------|--------|
| Claude Code hooks API (events, JSON schema, exit codes) | HIGH | Official docs at code.claude.com/docs/en/hooks |
| Claude Code memory (CLAUDE.md, auto memory, scope, 200-line limit) | HIGH | Official docs at code.claude.com/docs/en/memory |
| Claude Code skills (frontmatter schema, context vs. fork, allowed-tools) | HIGH | Official docs at code.claude.com/docs/en/skills |
| Obsidian Dataview (YAML indexing, query types) | HIGH | Official docs at blacksmithgu.github.io/obsidian-dataview/ |
| 05_AI_Workspace design (new, not yet built) | MEDIUM | Pattern extrapolated from constraints + Obsidian best practices |
| Hook script performance at scale | MEDIUM | Known behavior, not tested in this vault |
| Auto memory behavior with subagents | MEDIUM | Documented in official docs but not verified in practice |
| Obsidian Canvas interaction patterns | LOW | Not researched — Canvas not currently in skill architecture |

---

## Sources

- Claude Code Hooks reference: https://code.claude.com/docs/en/hooks (HIGH confidence — official docs, fetched 2026-03-14)
- Claude Code Hooks guide: https://code.claude.com/docs/en/hooks-guide (HIGH confidence — official docs, fetched 2026-03-14)
- Claude Code Memory reference: https://code.claude.com/docs/en/memory (HIGH confidence — official docs, fetched 2026-03-14)
- Claude Code Skills reference: https://code.claude.com/docs/en/skills (HIGH confidence — official docs, fetched 2026-03-14)
- Obsidian Dataview: https://blacksmithgu.github.io/obsidian-dataview/ (HIGH confidence — official plugin docs, fetched 2026-03-14)
- Existing project structure: second-brain/.claude/ (HIGH confidence — direct file system inspection)
- Existing skills: second-brain/.claude/skills/ (HIGH confidence — direct file system inspection)
- Claude Code hooks guide community: https://code.claude.com/docs/en/hooks-guide (HIGH confidence — official)
