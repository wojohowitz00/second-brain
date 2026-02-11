# Second Brain: Complete Guide

## Table of Contents

1. [Philosophy & Architecture](#philosophy--architecture)
2. [Quick Start](#quick-start)
3. [Core Concepts](#core-concepts)
4. [Daily Workflows](#daily-workflows)
5. [Commands Reference](#commands-reference)
6. [Skills Reference](#skills-reference)
7. [Customization](#customization)
8. [Principles Reference](#principles-reference)

---

## Philosophy & Architecture

### Why This Exists

**Your brain wasn't designed to be a storage system.** Every time you force it to remember something instead of think something new, you pay a hidden tax:

- Relationships that cool because you forgot what mattered to someone
- Projects that fail the same way you predicted 3 weeks ago but didn't write down
- The constant background hum of open loops you can't close

### The Two-Layer System

This second brain has two complementary layers:

| Layer | What | How |
|-------|------|-----|
| **Python Backend** | Automated Slack capture + local AI classification | macOS menu bar app, Ollama, PARA vault |
| **Claude Code Interactive** | Morning rituals, task creation, writing, research | Commands, skills, context files |

### The Agentic Stack

| Layer | Responsibility | Who Handles It |
|-------|----------------|----------------|
| **Directive** | What you want | You |
| **Orchestration** | How to do it | Claude Code |
| **Execution** | Doing the work | Claude Code |

**You become the director, not the orchestrator.**

### Three Purposes

Everything serves one of three goals:

1. **Ideation** — Develop and connect ideas
2. **Research** — Gather and synthesize information
3. **Organization** — Route thoughts, surface what matters

---

## Quick Start

### 1. Set Up Your Vault

The Python backend handles automated capture. For Claude Code interactive features:

```bash
cd ~/PARA/01_Projects/Personal/apps/second-brain
```

### 2. Create Your Brand (First Step)

```bash
claude "Help me create my brand system"
```

### 3. Start Using It

```bash
claude "/today"                    # Morning ritual
claude "new task: Review report"   # Quick capture
claude "/doable"                   # What can Claude handle?
```

---

## Core Concepts

### Progressive Disclosure

Skills load context in layers:
1. **Level 1**: Description (always visible) — decides IF relevant
2. **Level 2**: Full skill.md (on invocation) — HOW to execute
3. **Level 3**: Supporting files (as needed) — DETAILS

### Context Files

Small files organized by topic in `_llm-context/`:
- `personal/profile.md` — Personal background
- `business/profile.md` — Work context
- `writing/style-guide.md` — Voice and tone

**Key insight**: Too much irrelevant context hurts performance. Load only what's needed.

### Tasks as Files

Every task is a single markdown file in `tasks/`:
- Notes embedded IN the task
- Full-text search across all context
- Claude finds things even with wrong keywords

### Auto-Tagging

Claude applies tags from taxonomy (see `docs/sop/tasks.md`):
- **Domain**: #sales, #content, #product, #admin, #research, #people
- **Context**: #quick, #deep, #collab
- **Status**: #active, #waiting, #blocked, #someday, #done

### Inbox Log (Trust Through Logging)

Every processed thought is logged in `_inbox_log/[date].md`.

---

## Daily Workflows

### Morning Ritual
```bash
cd ~/PARA/01_Projects/Personal/apps/second-brain && claude "/today"
```

### Capture
**Slack**: Post to `#sb-inbox` (automated by Python backend)
**Direct**: `claude "new task: [description]"`

### Working Session
Keep Claude open while writing:
- "Is there evidence for [claim]?"
- "Critique this section"
- "Fix typos"

### End of Day
```bash
claude "/learned"
```

### Weekly Review (Sunday)
```bash
claude "/weekly"
```

---

## Commands Reference

| Command | Purpose |
|---------|---------|
| `/today` | Morning ritual — process inbox, generate digest |
| `/new-task [desc]` | Quick task creation with auto-tagging |
| `/doable` | What can Claude handle for me? |
| `/pipeline [domain]` | View tasks filtered by domain |
| `/stuck` | Surface items that haven't moved |
| `/learned` | End-of-session documentation |
| `/weekly` | Weekly review and planning |

---

## Skills Reference

### Meta Skills

**Brand & Voice Generator** (`_meta/brand-voice/`)
- Creates personalized style guide. Run first when setting up.

**Skill Creator** (`_meta/skill-creator/`)
- Build new skills for the system.

### Capture Skills

**Inbox Processor** (`capture/inbox-processor/`)
- Interactive classification and routing (complements automated Python backend).

### Surfacing Skills

**Daily Digest** (`surfacing/daily-digest/`)
- Morning summary with priorities and automation opportunities.

**Weekly Review** (`surfacing/weekly-review/`)
- Patterns, progress analysis, and suggested focus.

### Writing Skills

**Writing Buddy** (`writing/writing-buddy/`)
- Research, critique, and polish. Never rewrites — only critiques.

### Research Skills

**Research Engine** (`research/research-engine/`)
- Daily searches, paper summarization, topic tracking.

### Integration Skills

**MCP Client** (`mcp-client/`)
- Connect external services. Read-only by default for safety.

---

## Customization

### Adding Context

When you find yourself explaining something repeatedly:
```bash
claude "/learned"
```

### Creating Skills

```bash
claude "create a new skill for [capability]"
```

### Scheduling (Optional)

Once manual flow is trusted, add cron:
```cron
0 7 * * * cd ~/PARA/01_Projects/Personal/apps/second-brain && claude "/today"
0 16 * * 0 cd ~/PARA/01_Projects/Personal/apps/second-brain && claude "/weekly"
```

---

## Principles Reference

### The 12 Engineering Principles

1. **One reliable behavior**: Capture to inbox. Everything else is automation.
2. **Separate memory/compute/interface**: Obsidian (memory), Claude (compute), Slack+Obsidian UI (interface).
3. **Prompts as APIs**: Fixed input/output format, no surprises.
4. **Trust mechanisms**: Inbox log, confidence scores, fix button.
5. **Safe defaults**: Low confidence = hold and ask.
6. **Small outputs**: Daily digest under 200 words.
7. **Next action as unit**: "Email Sarah to confirm deadline" not "work on website".
8. **Routing over organizing**: 4-5 stable buckets, AI decides.
9. **Minimal categories**: More = more decisions = death.
10. **Design for restart**: Miss a week? Brain dump and resume.
11. **Core loop first**: Capture → process → surface. Add modules later.
12. **Maintainability over cleverness**: Fewer tools, clear logs, easy fixes.

---

## File Locations Quick Reference

| Content | Location |
|---------|----------|
| Global rules | `.claude/claude.md` |
| Slash commands | `.claude/commands/` |
| Skills | `.claude/skills/` |
| Context for Claude | `_llm-context/` |
| Templates | `backend/_templates/` |
| Tasks | `tasks/` |
| Daily digests | `daily/` |
| Weekly reviews | `weekly/` |
| Audit trail | `_inbox_log/` |
| Research | `research/` |
| Brand profiles | `brands/` |
| Python backend | `backend/_scripts/` |
| SOP docs | `docs/sop/` |
