# Second Brain

**Capture thoughts anywhere. Have them automatically organized.**

Second Brain is a macOS menu bar application that captures messages from Slack and automatically organizes them into your Obsidian vault using local AI classification.

![Status: v1.0.0](https://img.shields.io/badge/version-v1.0.0-blue)
![Tests: 259 passing](https://img.shields.io/badge/tests-259%20passing-green)
![Platform: macOS](https://img.shields.io/badge/platform-macOS-lightgrey)

---

## How It Works

```
┌─────────────────┐      ┌──────────────┐      ┌─────────────────┐
│  Slack Inbox    │──────│ Second Brain │──────│ Obsidian Vault  │
│  #sb-inbox      │      │  (menu bar)  │      │ ~/PARA/         │
└─────────────────┘      └──────────────┘      └─────────────────┘
                               │
                         ┌─────┴─────┐
                         │  Ollama   │
                         │ (local AI)│
                         └───────────┘
```

1. **Capture**: Post thoughts to your `#sb-inbox` Slack channel
2. **Classify**: Local LLM determines domain, PARA type, subject, and category
3. **File**: Markdown files created in the correct vault location
4. **Notify**: Menu bar shows status; macOS notification confirms filing

---

## Features

- **Local AI Classification** — Uses Ollama (no cloud API, no data leaves your machine)
- **PARA Organization** — Files organized by Domain → Projects/Areas/Resources/Archives → Subject
- **Menu Bar App** — Status icons, manual sync, recent activity
- **Auto-Polling** — Checks Slack every 2 minutes while running
- **First-Run Wizard** — Easy setup for Ollama, vault, and Slack credentials
- **Launch on Login** — Optional LaunchAgent for automatic startup

---

## Quick Start

### Prerequisites

- macOS (Apple Silicon or Intel)
- [Ollama](https://ollama.ai) installed
- Slack workspace with bot configured
- Obsidian vault with PARA folder structure

### Install

```bash
# Download and run installer
open pkg/SecondBrain-1.0.0.pkg
```

Or build from source:
```bash
./scripts/build_app.sh
./scripts/build_pkg.sh
```

### First Run

1. Launch **Second Brain** from Applications
2. Setup wizard guides you through:
   - Ollama installation check
   - Model download (llama3.2)
   - Vault path configuration
   - Slack credential validation
3. App starts monitoring your inbox

---

## Usage

### Capturing Thoughts

Post messages to your `#sb-inbox` Slack channel:

```
Just had a great idea for the RVM dashboard

Meeting notes from standup: discussed Q2 priorities

Need to research Kubernetes operators for the database migration
```

Second Brain classifies each message and files it automatically.

### Task Capture

Use special prefixes for task management:

```
todo: Create RVM dashboard domain:just-value project:rvm p1
kanban: Review PR for auth feature domain:personal project:apps p2
```

| Prefix | Effect |
|--------|--------|
| `todo:` | Creates task for Todo list |
| `kanban:` | Creates task for Kanban board |
| `domain:X` | Routes to specific domain folder |
| `project:X` | Tags with project name |
| `p1/p2/p3` | Sets priority (high/medium/low) |

### Status Commands

Reply to a message thread to change task status:

- `!done` — Mark complete
- `!progress` — Mark in progress
- `!blocked` — Mark blocked
- `!backlog` — Return to backlog

### Corrections

If classification was wrong, reply with:

```
fix: domain:personal para:projects subject:apps
```

---

## Menu Bar Controls

| Icon | Meaning |
|------|---------|
| 🧠 | Idle — ready for new messages |
| 🔄 | Syncing — processing messages |
| ⚠️ | Error — check Ollama or Slack connection |

**Menu options:**
- **Sync Now** — Trigger immediate sync
- **Recent Activity** — View last 5 filed notes
- **Health** — Check Ollama and vault status
- **Quit** — Exit application

---

## Configuration

### Environment Variables

Create `backend/_scripts/.env`:

```bash
SLACK_BOT_TOKEN=xoxb-your-token
SLACK_CHANNEL_ID=C0123456789
SLACK_USER_ID=U0123456789
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama3.2:latest
```

### Vault Structure

Your Obsidian vault should follow PARA organization:

```
~/PARA/
├── Personal/
│   ├── 1_Projects/
│   ├── 2_Areas/
│   ├── 3_Resources/
│   └── 4_Archives/
├── Work/
│   ├── 1_Projects/
│   └── ...
└── .obsidian/
```

---

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/build_app.sh` | Build .app bundle |
| `scripts/build_pkg.sh` | Build .pkg installer |
| `scripts/install_launchagent.sh` | Enable launch on login |
| `scripts/uninstall.sh` | Remove app and LaunchAgent |

---

## Documentation

- [User Guide](docs/USER-GUIDE.md) — Detailed usage instructions
- [Installation](docs/INSTALLATION.md) — Step-by-step setup
- [Troubleshooting](docs/TROUBLESHOOTING.md) — Common issues
- [Architecture](docs/ARCHITECTURE.md) — Technical details

---

## Development

### Setup

```bash
cd backend
uv sync
```

### Run Tests

```bash
cd backend
uv run pytest -v
```

### Run Locally

```bash
cd backend
uv run python _scripts/menu_bar_app.py
```

---

## Project Structure

```
second-brain/
├── backend/
│   ├── _scripts/        # Python modules
│   │   ├── menu_bar_app.py
│   │   ├── setup_wizard.py
│   │   ├── message_classifier.py
│   │   ├── ollama_client.py
│   │   ├── vault_scanner.py
│   │   └── ...
│   ├── tests/           # Test suite (259 tests)
│   └── pyproject.toml
├── scripts/             # Build scripts
├── resources/           # LaunchAgent plist
├── pkg/                 # Distribution package
├── dist/                # Built app bundle
└── .planning/           # Development docs
```

---

## Requirements

All 29 v1 requirements implemented:

- ✓ VAULT-01 to 05: Vault discovery and caching
- ✓ CLASS-01 to 06: Multi-level classification
- ✓ PROC-01 to 04: Message processing pipeline
- ✓ UI-01 to 05: Menu bar interface
- ✓ SETUP-01 to 06: First-run wizard
- ✓ DIST-01 to 03: Distribution packaging

---

## License

Private project.

---

## Version History

- **v1.0.0** (2026-01-31) — Initial release
  - Complete Slack-to-Obsidian pipeline
  - Local Ollama classification
  - macOS menu bar app
  - .pkg installer with LaunchAgent
