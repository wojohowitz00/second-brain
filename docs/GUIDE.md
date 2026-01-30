---
category:
- '[[App Development]]'
- '[[Learning Science]]'
tags:
- evergreen
- personal
- projects
created: '2026-01-28'
updated: '2026-01-28'
---
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

For the first time in history, we have systems that actively work against the information we give them while we sleep—classifying, routing, summarizing, surfacing, nudging without us remembering to do any of it.

### The Agentic Stack

| Layer | Responsibility | Who Handles It |
|-------|----------------|----------------|
| **Directive** | What you want | You |
| **Orchestration** | How to do it | Claude Code |
| **Execution** | Doing the work | Claude Code |

**You become the director, not the orchestrator.**

- An **orchestrator** is in the pit, waving arms, telling every musician when to play
- A **director** says "I want this scene to feel tense" and the team figures out how

### Three Purposes

Everything serves one of three goals:

1. **Ideation** — Develop and connect ideas
2. **Research** — Gather and synthesize information
3. **Organization** — Route thoughts, surface what matters

---

## Quick Start

### 1. Set Up Your Vault

```bash
cp -r second-brain-template ~/SecondBrain
cd ~/SecondBrain
```

### 2. Open in Obsidian

Open Obsidian → "Open folder as vault" → Select `~/SecondBrain`

### 3. Create Your Brand (First Step)

```bash
claude "Help me create my brand system"
```

### 4. Start Using It

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
- `business/profile.md` — Work context (index to products, audience)
- `writing/style-guide.md` — Voice and tone

**Key insight**: Too much irrelevant context hurts performance. Load only what's needed.

### Tasks as Files

Every task is a single markdown file in `tasks/`:
- Notes embedded IN the task
- Full-text search across all context
- Claude finds things even with wrong keywords

### Auto-Tagging

Claude applies tags from taxonomy:
- **Domain**: #sales, #content, #product, #admin, #research, #people
- **Context**: #quick, #deep, #collab
- **Status**: #active, #waiting, #blocked, #someday, #done

### Inbox Log (Trust Through Logging)

Every processed thought is logged in `_inbox_log/[date].md`. When something feels off, you can trace what happened.

---

## Daily Workflows

### Morning Ritual
```bash
cd ~/SecondBrain && claude "/today"
```

### Capture
**Slack**: Post to `#sb-inbox` (one thought per message)
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

### Recovery
```bash
/clear
```
Start fresh. Context files mean no re-explaining.

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
- Creates personalized style guide
- Run first when setting up
- Trigger: "help me create my brand"

**Skill Creator** (`_meta/skill-creator/`)
- Build new skills for the system
- Trigger: "create a new skill for [X]"

### Capture Skills

**Inbox Processor** (`capture/inbox-processor/`)
- Classifies and routes thoughts
- Auto-tags based on content
- Logs to audit trail
- Trigger: "process inbox" or part of /today

### Surfacing Skills

**Daily Digest** (`surfacing/daily-digest/`)
- Morning summary with priorities
- Identifies automation opportunities
- Trigger: part of /today or "daily digest"

**Weekly Review** (`surfacing/weekly-review/`)
- Patterns and progress analysis
- Suggested focus for next week
- Trigger: /weekly or "review my week"

### Writing Skills

**Writing Buddy** (`writing/writing-buddy/`)
- Research on demand
- Critique against your style guide
- Never rewrites — only critiques
- Triggers: "critique", "is this true?", "fix typos"

### Research Skills

**Research Engine** (`research/research-engine/`)
- Daily searches of academic sources
- Paper summarization
- Configure topics in `research/topics.md`

### Integration Skills

**MCP Client** (`mcp-client/`)
- Connect external services (Gmail, Calendar, Slack, Asana)
- Read-only by default for safety
- Configure in `mcp-config.json`

---

## Customization

### Adding Context

When you find yourself explaining something repeatedly:
```bash
claude "/learned"
```
This captures new context to the appropriate file.

### Creating Skills

```bash
claude "create a new skill for [capability]"
```

Skill Creator walks you through:
1. What should it do?
2. When should it trigger?
3. What inputs/outputs?

### Adding MCP Servers

1. Copy `mcp-config.example.json` to `mcp-config.json`
2. Add server configuration
3. Test: `claude "list tools in [server]"`
4. Document gotchas in `claude.md`

### Scheduling (Optional)

Once manual flow is trusted, add cron:
```cron
0 7 * * * cd ~/SecondBrain && claude "/today"
0 16 * * 0 cd ~/SecondBrain && claude "/weekly"
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

### Automation vs Augmentation

For every task, ask:
- **Automate**: Claude does it without me
- **Augment**: Claude helps me do it
- **Human only**: I want to do this myself

### The Director Mindset

You describe what you want. Claude figures out the steps, writes code, runs it, tests it, fixes errors. You focus on knowing what needs to be done.

---

## File Locations Quick Reference

| Content | Location |
|---------|----------|
| Global rules | `.claude/claude.md` |
| Slash commands | `.claude/commands/` |
| Skills | `.claude/skills/` |
| Context for Claude | `_llm-context/` |
| Templates | `_templates/` |
| Tasks | `tasks/` |
| Daily digests | `daily/` |
| Weekly reviews | `weekly/` |
| Audit trail | `_inbox_log/` |
| Research | `research/` |
| Brand profiles | `brands/` |

---

## Getting Help

- Run any skill with questions: `claude "how does [skill] work?"`
- Check skill.md files for detailed documentation
- Use `/learned` to improve the system based on usage

The system gets smarter as you use it. Small learnings compound.
