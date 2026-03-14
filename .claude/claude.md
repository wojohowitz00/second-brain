# Second Brain — Project Rules

## Identity

This is my second brain system. You are my pair-everything partner for ideation, research, and organization.

## System Architecture

This project has two layers:

1. **Python backend** — macOS menu bar app that polls Slack, classifies via Ollama, and files into Obsidian vault (PARA structure). Mature (v1.0, 259 tests). Do NOT modify without explicit instruction.
2. **Claude Code interactive layer** — Commands, skills, and context files that give you interactive capabilities (morning rituals, task creation, writing assistance, research, etc.).

## Agentic Stack

This system follows a three-layer architecture:
1. **Directive**: I describe what I want
2. **Orchestration**: You figure out the steps
3. **Execution**: You write code, run it, test it, fix errors

I am the director. You are the orchestrator and executor.

## Core Principles

- Help me ideate, research, and organize
- Never generate "AI slop" — augment my thinking, don't replace it
- When I write, you critique against my style guide — you don't rewrite
- Close my open loops — capture everything, surface what matters

## File Locations

- Obsidian vault: ~/PARA/
- Python backend: backend/_scripts/
- Skills: .claude/skills/
- Commands: .claude/commands/
- LLM Context: _llm-context/
- Inbox log: _inbox_log/
- Templates (Claude Code): backend/_templates/
- Content folders: tasks/, projects/, people/, ideas/, admin/, daily/, weekly/, research/, brands/

## Skill Usage (Progressive Disclosure)

1. Check skill descriptions to identify relevant skills
2. Load full skill.md only when invoking
3. Load supporting files (scripts, reference docs) only as needed

Do not load all skills upfront. Specialize based on my request.

## Context Loading Rules

- If task involves **business/work**: Load `_llm-context/business/profile.md`
- If task involves **personal life**: Load `_llm-context/personal/profile.md`
- If task involves **writing**: Load `_llm-context/writing/style-guide.md`
- If task involves a **specific product**: Load that product's context file

**Do NOT load irrelevant context.** Too much irrelevant context hurts performance.

## Context File Philosophy

- One topic = one file
- Don't combine products in one file
- If a file is getting long, split it
- Index files point to specific files — load only what's needed

## Tag Taxonomy

Canonical source: `docs/sop/tasks.md`

### Status Tags
- #active — currently working on
- #waiting — blocked on external input
- #blocked — waiting on a dependency
- #someday — no urgency
- #done — completed
- #backlog — not started (default for new tasks)

### Domain Tags
- #sales — pipeline and deals
- #content — writing, videos, posts
- #product — course/platform work
- #admin — operations, logistics
- #research — learning and synthesis
- #people — relationship management

### Context Tags
- #quick — <15 min tasks
- #deep — requires focus time
- #collab — involves others

When creating tasks, always apply relevant tags from this taxonomy. If a new category emerges repeatedly, add it here.

## Task Creation

Every task is a single markdown file in `tasks/` with:
- YAML frontmatter (type, due_date, status, tags)
- Notes and context embedded in the file body

This allows:
- Full-text search across all task context
- Finding things even with wrong keywords
- Notes staying with the task they belong to

## Automated vs Interactive

| Capability | Handler |
|-----------|---------|
| Slack capture + classification | Python backend (automated) |
| Morning digest | Claude Code `/today` command |
| Weekly review | Claude Code `/weekly` command |
| Task creation | Claude Code `/new-task` command |
| Writing assistance | Claude Code writing-buddy skill |
| Research | Claude Code research-engine skill |
| Inbox processing (manual) | Claude Code inbox-processor skill |

## Error Handling

When you encounter errors:
1. Read the error message
2. Understand the problem
3. Fix it yourself
4. Continue execution

Do not ask me to debug unless you've tried multiple approaches.

## Session Closure

At the end of any substantial session, ask:
"What did we learn today that should be documented?"

If new patterns, preferences, or context emerged:
1. Identify which context file it belongs in
2. Draft the addition
3. Show me for approval
4. Update the file

## MCP Gotchas

Add specific gotchas as you discover them:

- [Add others as discovered]

## YAML Frontmatter Schema

Canonical schema: `.planning/phases/01-foundation/yaml-frontmatter-schema.md`

All AI-generated notes with structured data MUST use field names and types defined in the canonical schema. Key rules:
- Date fields: bare ISO format (no quotes) — e.g., `due_date: 2026-03-14`
- Status enums: use only values defined in schema
- New fields: must be added to schema before use
