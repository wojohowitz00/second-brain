# Second Brain User Guide

Complete guide to using the Second Brain macOS application.

---

## Table of Contents

1. [Overview](#overview)
2. [Getting Started](#getting-started)
3. [Capturing Thoughts](#capturing-thoughts)
4. [Task Management](#task-management)
5. [Menu Bar Interface](#menu-bar-interface)
6. [Corrections and Fixes](#corrections-and-fixes)
7. [Understanding Classification](#understanding-classification)
8. [Daily Workflow](#daily-workflow)
9. [Tips and Best Practices](#tips-and-best-practices)

---

## Overview

Second Brain captures your thoughts from Slack and automatically organizes them into your Obsidian vault. The key insight: **capture should be effortless, organization should be automatic**.

### How It Works

1. You post a thought to Slack (one thought per message)
2. Second Brain polls Slack every 2 minutes
3. Local AI (Ollama) classifies the thought
4. A markdown file is created in the correct vault location
5. You get a notification confirming the filing

### What Gets Created

For each message, Second Brain creates a `.md` file with:

```yaml
---
domain: Personal
para: Projects
subject: second-brain-app
category: development
source: slack
created: 2026-01-31T10:30:00
confidence: 0.85
---

Your original thought goes here as the note content.
```

---

## Getting Started

### First Launch

When you first launch Second Brain, the setup wizard guides you through:

#### Step 1: Welcome
Brief introduction to the app.

#### Step 2: Ollama Check
- Checks if Ollama is installed
- If not installed, provides download link: https://ollama.ai
- Waits for you to install before continuing

#### Step 3: Model Download
- Checks if `llama3.2:latest` model is available
- If not, downloads it (this may take a few minutes)
- Shows download progress

#### Step 4: Vault Configuration
- Shows default vault path (`~/PARA`)
- Allows you to browse and select a different path
- Validates the path has `.obsidian/` folder (confirms it's an Obsidian vault)
- Scans and displays discovered domains

#### Step 5: Slack Credentials
- Prompts for Slack Bot Token (starts with `xoxb-`)
- Prompts for Channel ID (starts with `C`)
- Validates by making a test API call
- Shows connected workspace name

#### Step 6: Complete
- Summary of configuration
- Starts the menu bar app

### After Setup

The app runs in your menu bar. You'll see a brain icon (🧠) indicating it's ready.

---

## Capturing Thoughts

### Basic Capture

Post any thought to your `#sb-inbox` Slack channel:

```
Just realized we should add caching to the API endpoints
```

Second Brain will:
1. Classify it (likely: domain=Work, para=Projects, subject=api-optimization, category=architecture)
2. Create a file like `2026-01-31-api-caching-idea.md`
3. Place it in `~/PARA/Work/1_Projects/api-optimization/`
4. Reply to your message with the filing location

### Multiple Thoughts

Post each thought as a separate message:

```
Message 1: Need to call Mom about birthday plans

Message 2: Research shows 10% improvement with caching

Message 3: Meeting with Sarah moved to Thursday
```

**Don't combine multiple thoughts** — each message becomes one file.

### Rich Captures

Include context for better classification:

```
For the RVM project: the dashboard needs a date picker component. 
Should look at react-datepicker or build custom.
```

The AI uses context clues ("RVM project", "dashboard", "react") to classify accurately.

---

## Task Management

### Creating Tasks

Use prefixes to create structured tasks:

#### Todo Tasks
```
todo: Write unit tests for the classifier
```

#### Kanban Tasks
```
kanban: Review PR #42 for the auth feature
```

### Task Metadata

Add structured information with indicators:

| Indicator | Example | Effect |
|-----------|---------|--------|
| `domain:` | `domain:personal` | Routes to Personal folder |
| `project:` | `project:second-brain` | Tags with project name |
| `p1` | | High priority (urgent) |
| `p2` | | Medium priority (default) |
| `p3` | | Low priority (someday) |

#### Full Example
```
todo: Implement user authentication domain:work project:webapp p1
```

Creates a high-priority task in Work domain, tagged with webapp project.

### Changing Task Status

Reply to the original Slack message with status commands:

| Command | New Status | Use When |
|---------|------------|----------|
| `!done` | Complete | Task is finished |
| `!progress` | In Progress | Actively working on it |
| `!blocked` | Blocked | Waiting on something external |
| `!backlog` | Backlog | Returning to queue |

#### Example
Original message:
```
todo: Write API documentation p2
```

Later, reply in thread:
```
!progress
```

The task's status field updates from `backlog` to `in_progress`.

### Viewing Tasks

Tasks appear in your Obsidian vault's dashboard views:

- **Kanban Board** — Tasks grouped by status columns
- **Todo List** — All open tasks sorted by priority

---

## Menu Bar Interface

### Status Icons

| Icon | Status | Meaning |
|------|--------|---------|
| 🧠 | Idle | Ready, no active processing |
| 🔄 | Syncing | Currently fetching/processing messages |
| ⚠️ | Error | Problem with Ollama or Slack |

### Menu Options

Click the menu bar icon to see:

#### Sync Now
Triggers an immediate sync instead of waiting for the 2-minute poll cycle. Use when you just posted something and want it processed immediately.

#### Recent Activity
Shows the last 5 notes that were filed:

```
✓ api-caching-idea.md → Projects/api-optimization
✓ meeting-notes-standup.md → Areas/meetings
✓ birthday-reminder.md → Personal/family
```

Click any item to open it in Obsidian.

#### Health
Shows system status:

```
Ollama: ✓ Running (llama3.2:latest)
Vault: ✓ Connected (3 domains found)
Slack: ✓ Connected (workspace: MyTeam)
```

#### Notifications
Toggle macOS notifications on/off. When enabled, you'll see a notification each time a note is filed.

#### Quit
Exits the application completely. Use `uninstall.sh` if you want to also remove the LaunchAgent.

---

## Corrections and Fixes

### When Classification Is Wrong

If Second Brain mis-classifies something, reply to the Slack message with a fix command:

```
fix: domain:personal para:projects subject:home-renovation
```

### Fix Command Format

```
fix: [field:value] [field:value] ...
```

Available fields:
- `domain:` — Domain folder (Personal, Work, etc.)
- `para:` — PARA type (projects, areas, resources, archives)
- `subject:` — Subject folder name
- `category:` — Category tag

### Examples

Move to different domain:
```
fix: domain:work
```

Change PARA type and subject:
```
fix: para:areas subject:health-fitness
```

Full reclassification:
```
fix: domain:personal para:resources subject:recipes category:cooking
```

### What Happens

1. Second Brain reads your fix command
2. Moves the file to the new location
3. Updates the frontmatter
4. Replies confirming the change

---

## Understanding Classification

### The Four Levels

Second Brain classifies each thought at four levels:

#### 1. Domain
Your high-level life areas. Examples:
- Personal
- Work
- Side Projects

Domains come from your vault's top-level folders.

#### 2. PARA Type
The organizational category within a domain:
- **Projects** — Active work with deadlines
- **Areas** — Ongoing responsibilities
- **Resources** — Reference material
- **Archives** — Completed/inactive items

#### 3. Subject
Specific topic folders within each PARA section:
- `Projects/webapp-v2/`
- `Areas/health-fitness/`
- `Resources/recipes/`

#### 4. Category
A tag for cross-cutting themes:
- `development`
- `meetings`
- `ideas`
- `research`

### How Classification Works

1. **Vault Vocabulary** — Scanner reads your actual folder structure
2. **LLM Prompt** — Your message + vocabulary sent to Ollama
3. **JSON Response** — AI returns structured classification
4. **Validation** — Invalid responses normalized to safe defaults
5. **File Creation** — Note created with classification in frontmatter

### Confidence Scores

Each classification includes a confidence score (0.0-1.0):

- **0.8+** — High confidence, likely correct
- **0.5-0.8** — Medium confidence, might need review
- **< 0.5** — Low confidence, manual check recommended

Low-confidence items still get filed, but you may want to review them.

---

## Daily Workflow

### Morning Routine

1. **Launch Second Brain** (or verify it's running)
2. **Brain dump** to `#sb-inbox` — everything on your mind
3. **Wait 2 minutes** (or click Sync Now)
4. **Check Recent Activity** — verify filings look correct
5. **Open Obsidian** — review today's dashboard

### Throughout the Day

- Quick capture: Post to Slack whenever a thought strikes
- Task capture: Use `todo:` or `kanban:` prefixes
- No need to organize — that's automatic

### End of Day

1. Check **Recent Activity** for anything misfiled
2. Use **fix:** commands for any corrections
3. Review completed tasks: `!done` in Slack threads

### Weekly Review

1. Open your Obsidian dashboard
2. Review Kanban board — anything stuck?
3. Archive completed projects
4. Empty or move blocked items

---

## Tips and Best Practices

### Writing Good Captures

**Include context:**
```
❌ Bad: "Database thing"
✅ Good: "For the RVM project: need to add connection pooling to PostgreSQL"
```

**One thought per message:**
```
❌ Bad: "Call Mom. Also need groceries. And fix the bug in auth."
✅ Good: Three separate messages
```

**Be specific:**
```
❌ Bad: "Meeting notes"
✅ Good: "Meeting notes from Q2 planning with Sarah - budget approved"
```

### Handling Low Confidence

If you notice repeated misclassifications:
1. Check your vault structure — is it consistent?
2. Use more context in messages
3. Create subject folders for recurring topics
4. Use explicit `domain:` indicators

### Optimizing Performance

- **Cold start**: First classification after Ollama starts takes ~30s
- **Warm**: Subsequent classifications take ~5s
- **Keep Ollama running** for faster response

### Vault Structure Tips

Keep your vault structure consistent:
```
✅ Good:
~/PARA/Personal/1_Projects/
~/PARA/Work/1_Projects/

❌ Bad:
~/PARA/Personal/Projects/
~/PARA/Work/1_Projects/
```

Second Brain learns from your actual folder names, so consistency helps.

### When Things Go Wrong

1. **Check menu bar icon** — is it showing error (⚠️)?
2. **Click Health** — which service is down?
3. **Restart Ollama** if classification fails
4. **Check Slack** if messages aren't being fetched
5. **See Troubleshooting guide** for detailed fixes

---

## Keyboard Shortcuts

There are no global keyboard shortcuts (menu bar apps typically don't have them).

To quickly access:
1. **Click menu bar icon** — one click to open menu
2. **Cmd+Tab** to Obsidian for your filed notes

---

## Privacy & Security

- **All AI processing is local** — Ollama runs on your machine
- **No data sent to cloud** — except Slack API for fetching messages
- **Credentials stored locally** — in `backend/_scripts/.env`
- **Files stored in your vault** — full control over your data

---

## Getting Help

- **README.md** — Quick start and overview
- **INSTALLATION.md** — Step-by-step setup
- **TROUBLESHOOTING.md** — Common issues and solutions
- **ARCHITECTURE.md** — Technical deep dive

For issues:
1. Check menu bar Health status
2. Review `backend/_scripts/.state/` for logs
3. Run tests: `cd backend && uv run pytest`

---

*Last updated: 2026-01-31 | Version: v1.0.0*
