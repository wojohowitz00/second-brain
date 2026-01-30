---
category:
- '[[App Development]]'
- '[[Coding with AI]]'
tags:
- evergreen
- personal
- projects
created: '2026-01-28'
updated: '2026-01-28'
---
# Second Brain: Slack + Claude Code + Obsidian + Skills

A complete system for building a personal second brain using Claude Code, Obsidian, and Slack.

## Philosophy

**Your brain wasn't designed to be a storage system.** Every time you force it to remember something instead of think something new, you pay a hidden tax. This system closes open loops, routes information automatically, and surfaces what matters—while you focus on thinking.

### The Agentic Stack

| Layer | Responsibility | Who Handles It |
|-------|----------------|----------------|
| **Directive** | What you want | You |
| **Orchestration** | How to do it | Claude Code |
| **Execution** | Doing the work | Claude Code |

You become the **director**, not the orchestrator.

### Three Purposes

Everything serves one of three goals:
1. **Ideation** — Develop and connect ideas
2. **Research** — Gather and synthesize information
3. **Organization** — Route thoughts, surface what matters

## Quick Start

### 1. Copy to Your System

```bash
# Copy this template to your home directory
cp -r second-brain-template ~/SecondBrain

# Navigate to your new vault
cd ~/SecondBrain
```

### 2. Open in Obsidian

1. Open Obsidian
2. "Open folder as vault"
3. Select `~/SecondBrain`

### 3. Set Up Slack (Optional but Recommended)

1. Create a Slack app with scopes: `channels:history`, `chat:write`, `im:write`
2. Create private channel `#sb-inbox`
3. Export credentials:
   ```bash
   export SLACK_BOT_TOKEN="xoxb-..."
   export SLACK_CHANNEL_ID="C0123..."
   export SLACK_USER_ID="U0123..."
   ```

### 4. Run Brand & Voice Setup

```bash
cd ~/SecondBrain
claude "Help me create my brand system"
```

### 5. Start Using It

```bash
# Morning ritual
claude "/today"

# Quick task
claude "new task: Review quarterly report by Friday"

# What can Claude handle?
claude "/doable"
```

## Directory Structure

```
SecondBrain/
├── .claude/
│   ├── claude.md              # Global rules
│   ├── commands/              # Slash commands
│   └── skills/                # Capabilities
├── _llm-context/              # Context for Claude
├── _templates/                # File templates
├── _inbox_log/                # Audit trail
├── tasks/                     # One file per task
├── projects/                  # Ongoing work
├── people/                    # Relationship notes
├── ideas/                     # Explorations
├── admin/                     # One-off errands
├── research/                  # Papers and digests
├── daily/                     # Daily digests
├── weekly/                    # Weekly reviews
└── brands/                    # Brand profiles
```

## Core Commands

| Command | Purpose |
|---------|---------|
| `/today` | Morning ritual |
| `/new-task [desc]` | Quick task creation |
| `/doable` | What can Claude handle? |
| `/pipeline [domain]` | View tasks by domain |
| `/stuck` | What am I avoiding? |
| `/learned` | Document session learnings |

## Key Principles

1. **One reliable behavior**: Capture to Slack, everything else is automation
2. **Progressive disclosure**: Skills load context only when needed
3. **Trust through logging**: Every decision is tracked
4. **Safe defaults**: Low confidence = hold and ask
5. **Design for restart**: Miss a week? Brain dump and resume

## Documentation

See `GUIDE.md` for the complete guide including:
- Detailed setup instructions
- All skill configurations
- Workflow examples
- Principles reference

## License

MIT License - Use freely, modify as needed.
