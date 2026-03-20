# Codebase Structure

**Analysis Date:** 2026-01-30

## Directory Layout

```
second-brain/
├── .planning/                    # GSD orchestration artifacts
│   └── codebase/                 # Codebase analysis documents
│
├── backend/                      # Python backend (Slack + Obsidian integration)
│   ├── _scripts/                 # Core processing scripts
│   │   ├── __pycache__/          # Python compiled cache
│   │   ├── .state/               # Runtime state files (generated)
│   │   ├── process_inbox.py      # Main: Fetch → Classify → Write
│   │   ├── fix_handler.py        # Correction handler for "fix:" commands
│   │   ├── health_check.py       # System health monitoring
│   │   ├── daily_digest.py       # Morning summary generation
│   │   ├── weekly_review.py      # Weekly digest generation
│   │   ├── slack_client.py       # Slack API wrapper with retry logic
│   │   ├── state.py              # State management with atomic JSON ops
│   │   ├── schema.py             # Classification validation
│   │   ├── wikilinks.py          # Entity extraction and linking
│   │   ├── configure.py          # Setup helper script
│   │   ├── .env.example          # Environment variable template
│   │   ├── requirements.txt      # Legacy requirements (see pyproject.toml)
│   │   ├── README.md             # Scripts documentation
│   │   ├── SKILL.md              # Skill definitions for Claude Code
│   │   └── SKILL.md              # Claude Code skill reference
│   │
│   ├── _templates/               # Markdown templates for Obsidian
│   │   ├── project.md            # Project template
│   │   ├── idea.md               # Idea template
│   │   └── person.md             # Person template
│   │
│   ├── tasks/                    # Task tracking
│   │   └── todo.md               # Task list
│   │
│   ├── .venv/                    # Virtual environment (generated)
│   ├── .beads/                   # Issue tracking database
│   ├── .gitattributes            # Git attributes
│   ├── pyproject.toml            # Project metadata and dependencies
│   ├── uv.lock                   # Dependency lock file
│   ├── setup.sh                  # Initialization script
│   ├── README.md                 # Backend documentation
│   ├── AGENTS.md                 # Claude Code agent definitions
│   ├── dashboard.md              # Obsidian dashboard template
│   └── UV_USAGE.md               # uv package manager notes
│
├── ios/                          # iOS application (SwiftUI)
│   ├── SecondBrain/              # Main app sources
│   │   ├── SecondBrainApp.swift  # App entry point
│   │   ├── ContentView.swift     # Root view
│   │   └── Assets.xcassets/      # Images/colors
│   │
│   ├── SecondBrainTests/         # Unit tests
│   │   └── SecondBrainTests.swift
│   │
│   ├── SecondBrainUITests/       # UI tests
│   │   ├── SecondBrainUITests.swift
│   │   └── SecondBrainUITestsLaunchTests.swift
│   │
│   └── SecondBrain.xcodeproj/    # Xcode project configuration
│
├── docs/                         # Documentation
│   ├── README.md                 # System overview and philosophy
│   └── GUIDE.md                  # Complete setup and usage guide
│
├── .git/                         # Git repository
├── .gitignore                    # Git ignore rules
├── .planning/                    # GSD planning artifacts
├── README.md                     # Root project README
└── [other files]                 # Stray markdown files from workflow
```

## Directory Purposes

**backend/_scripts/:**
- Purpose: Core processing automation - the heart of the system
- Contains: Python modules for Slack integration, classification, state management, validation
- Key files:
  - `process_inbox.py` - Main processing orchestrator
  - `slack_client.py` - All Slack API interactions
  - `state.py` - Persistent state with file locking
  - `schema.py` - Classification validation
  - `wikilinks.py` - Entity linking

**backend/_templates/:**
- Purpose: Markdown templates used during Obsidian file creation
- Contains: Template files with YAML frontmatter and placeholder content
- Key files:
  - `project.md` - Template for project captures
  - `person.md` - Template for people notes
  - `idea.md` - Template for ideas

**backend/tasks/:**
- Purpose: Task and issue tracking for Second Brain backend
- Contains: Task definitions in markdown format
- Key files: `todo.md`

**ios/SecondBrain/:**
- Purpose: iOS app source code (SwiftUI based)
- Contains: Swift source files, asset catalogs
- Key files:
  - `SecondBrainApp.swift` - App lifecycle and scene
  - `ContentView.swift` - Root UI component

**ios/SecondBrainTests/:**
- Purpose: Unit tests for iOS app
- Contains: XCTest-based tests
- Key files: `SecondBrainTests.swift`

**ios/SecondBrainUITests/:**
- Purpose: UI/integration tests for iOS app
- Contains: XCTest UI tests with launch tests
- Key files: `SecondBrainUITests.swift`, `SecondBrainUITestsLaunchTests.swift`

**docs/:**
- Purpose: System-level documentation (not app-specific)
- Contains: Architecture, philosophy, setup guides
- Key files:
  - `README.md` - System overview with philosophy and layer descriptions
  - `GUIDE.md` - Complete setup, commands, and workflow guide

**backend/.state/:**
- Purpose: Runtime state directory (generated, not committed)
- Contains: JSON files for state management
- Key files:
  - `processed_messages.json` - Timestamp tracking for idempotency
  - `message_mapping.json` - Maps Slack TS to Obsidian file paths
  - `run_history.json` - Health check and run status logs

## Key File Locations

**Entry Points:**

- `backend/_scripts/process_inbox.py` - Main polling loop, triggered every 2 min via cron
- `backend/_scripts/fix_handler.py` - Correction handler, triggered every 5 min via cron
- `backend/_scripts/health_check.py` - Health monitor, triggered hourly via cron
- `backend/_scripts/daily_digest.py` - Manual/scheduled digest generation
- `backend/_scripts/weekly_review.py` - Manual/scheduled review generation
- `ios/SecondBrain/SecondBrainApp.swift` - iOS app entry point

**Configuration:**

- `backend/_scripts/.env` - Environment variables (not committed, created from `.env.example`)
- `backend/pyproject.toml` - Project metadata, dependencies, build config
- `backend/uv.lock` - Locked dependency versions
- `ios/SecondBrain.xcodeproj/project.pbxproj` - Xcode configuration

**Core Logic:**

- `backend/_scripts/process_inbox.py` - Classification pipeline and Obsidian writing
- `backend/_scripts/slack_client.py` - HTTP client with retry/backoff
- `backend/_scripts/state.py` - Idempotency and state persistence
- `backend/_scripts/schema.py` - Validation and fallback logic
- `backend/_scripts/wikilinks.py` - Entity extraction and linking

**Testing:**

- `ios/SecondBrainTests/SecondBrainTests.swift` - Unit tests
- `ios/SecondBrainUITests/SecondBrainUITests.swift` - UI tests

## Naming Conventions

**Files:**

- `*_*.py` (snake_case) - Python modules: `process_inbox.py`, `slack_client.py`
- `*.swift` (PascalCase for files, describe component) - Swift files: `SecondBrainApp.swift`, `ContentView.swift`
- `.env` (dotfile prefix) - Environment configuration files: `.env`, `.env.example`
- `*.md` (markdown) - Documentation: `README.md`, `GUIDE.md`

**Directories:**

- `_scripts/` (underscore prefix) - Internal automation scripts
- `_templates/` (underscore prefix) - Template resources
- `.state/` (dot prefix for hidden) - Runtime state (generated)
- `.venv/` (dot prefix) - Virtual environment (generated)
- `.beads/` (dot prefix) - Issue tracking data (generated)
- PascalCase - iOS module names: `SecondBrain/`, `SecondBrainTests/`, `SecondBrainUITests/`

## Where to Add New Code

**New Feature (Backend - Python):**

1. **Logic-only feature** (e.g., new digest type):
   - Primary code: `backend/_scripts/{feature_name}.py`
   - Import from existing modules (`slack_client`, `state`) as needed
   - Test: Create `backend/_scripts/{feature_name}_test.py` if complex logic
   - Entry point: Add cron line to `backend/README.md` (Automation section)

2. **Integration with processing pipeline** (e.g., new classification destination):
   - Modify: `backend/_scripts/process_inbox.py` (write_to_obsidian function)
   - Modify: `backend/_scripts/schema.py` (add to VALID_DESTINATIONS)
   - Modify: `backend/_scripts/state.py` (if new state needed)
   - Template: Add to `backend/_templates/{new_dest}.md`

3. **Error handling improvement**:
   - Modify: `backend/_scripts/slack_client.py` (for Slack errors)
   - Modify: `backend/_scripts/process_inbox.py` (for pipeline errors)
   - Test with dead letter queue simulation

**New Feature (iOS - Swift):**

1. **New view/screen**:
   - Primary code: `ios/SecondBrain/{FeatureName}View.swift`
   - Update: `ios/SecondBrain/SecondBrainApp.swift` (add route if needed)
   - Test: `ios/SecondBrainTests/` or `ios/SecondBrainUITests/`

2. **Shared model/service**:
   - Primary code: `ios/SecondBrain/{ModelName}.swift`
   - Test: `ios/SecondBrainTests/{ModelName}Tests.swift`

**New Utility Module:**

- Shared helpers (Python): `backend/_scripts/utilities.py` or feature-specific module
- Shared helpers (iOS): `ios/SecondBrain/Utilities/` directory
- Import patterns: Use relative imports within package

## Special Directories

**backend/.state/:**
- Purpose: Runtime state persistence
- Generated: Yes (created by state.py on first run)
- Committed: No (added to .gitignore)
- Manual edits: Not recommended (can cause idempotency issues)

**backend/.venv/:**
- Purpose: Python virtual environment
- Generated: Yes (created by `uv sync`)
- Committed: No (added to .gitignore)
- Manual edits: Not needed

**backend/.beads/:**
- Purpose: Issue tracking database (Beads tool)
- Generated: Yes (created by `bd` commands)
- Committed: Yes (contains task definitions)
- Manual edits: Use `bd` commands, not direct file edits

**ios/SecondBrain.xcodeproj/:**
- Purpose: Xcode project configuration
- Generated: No (checked in)
- Committed: Yes
- Manual edits: Use Xcode UI or manual plist editing (carefully)

**ios/SecondBrain/Assets.xcassets/:**
- Purpose: Image and color assets for iOS app
- Generated: No (checked in)
- Committed: Yes
- Manual edits: Use Xcode Asset Catalog editor

## File Organization Patterns

**Import Organization (Python):**

```python
# 1. Standard library
import os
import json
from pathlib import Path
from datetime import datetime

# 2. Third-party
import requests
import yaml

# 3. Local modules
from slack_client import fetch_messages, reply_to_message
from state import is_message_processed, mark_message_processed
from schema import validate_classification
from wikilinks import process_linked_entities
```

**Module Structure (Python):**

```python
#!/usr/bin/env python3
"""
Module docstring.
Purpose and responsibilities.
"""

# Imports
# Constants
# Exception classes (if any)
# Main functions
# Helper functions
# __main__ entry point
```

**Obsidian Vault Structure (Generated):**

When a message is processed, files are created in:

```
~/SecondBrain/
├── people/          # Personality/relationship notes
├── projects/        # Multi-step work items
├── ideas/           # Insights and explorations
├── admin/           # One-off tasks and errands
├── daily/           # Daily notes with wikilinks
└── _inbox_log/      # Processing audit trail
```

File naming:
- `kebab-case.md` - Obsidian convention
- Example: `sarah-chen.md`, `q2-roadmap.md`, `ai-safety-thoughts.md`

---

*Structure analysis: 2026-01-30*
