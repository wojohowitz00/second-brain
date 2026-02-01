# Release v1.0.0: Second Brain

**Release Date:** 2026-01-31
**Tag:** v1.0.0

---

## Overview

Second Brain is a macOS menu bar application that automatically captures thoughts from Slack and organizes them into your Obsidian vault using local LLM classification.

**Core Value:** Capture thoughts anywhere, have them automatically organized.

---

## Features

### Intelligent Classification
- Multi-level classification: Domain → PARA → Subject → Category
- Local LLM via Ollama (no cloud API required)
- Uses your vault's actual folder structure as vocabulary

### Seamless Integration
- Captures messages from Slack channel
- Creates properly formatted .md files with frontmatter
- Places files in correct vault location automatically

### macOS Native Experience
- Menu bar app with status icons (idle/syncing/error)
- Manual sync trigger
- Recent activity view
- System notifications for new notes

### Easy Setup
- First-run wizard guides through Ollama installation
- Model download with progress indicator
- Vault path configuration
- Slack credential validation

### Distribution
- .pkg installer for easy installation
- Optional launch-on-login via LaunchAgent
- No Python knowledge required for end users

---

## Installation

### Prerequisites
- macOS (Apple Silicon or Intel)
- Ollama installed (`brew install ollama`)
- Slack workspace with bot configured

### Install
```bash
# Double-click the installer
open pkg/SecondBrain-1.0.0.pkg

# Or use command line
sudo installer -pkg pkg/SecondBrain-1.0.0.pkg -target /
```

### Enable Login Startup (Optional)
```bash
./scripts/install_launchagent.sh
```

---

## Technical Details

| Metric | Value |
|--------|-------|
| Python LOC | 4,452 |
| Test count | 259 |
| Requirements | 29/29 |
| Phases | 9 |
| App size | 33 MB |
| Installer size | 36 MB |

### Key Dependencies
- rumps (macOS menu bar)
- ollama (local LLM)
- httpx/requests (API clients)
- PyInstaller (packaging)

---

## Requirements Completed

- **VAULT-01 to 05**: Vault discovery and caching
- **CLASS-01 to 06**: Classification pipeline
- **PROC-01 to 04**: Message processing
- **UI-01 to 05**: Menu bar interface
- **SETUP-01 to 06**: First-run wizard
- **DIST-01 to 03**: Distribution packaging

---

## Known Limitations

- Single Slack channel support (v2 planned)
- No Apple code signing (Gatekeeper may prompt)
- Requires Ollama running for classification

---

## What's Next (v2 Roadmap)

- [ ] Learning from corrections
- [ ] Batch reclassification
- [ ] Multiple Slack channels
- [ ] iOS capture app
- [ ] Apple Developer ID signing

---

## Credits

Built with GSD (Get Stuff Done) methodology.
Planning docs in `.planning/` directory.

---

*Released: 2026-01-31*
