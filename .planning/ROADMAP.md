# Roadmap: Second Brain

## Overview

Transform existing Slack-to-Obsidian backend into a standalone macOS app with local LLM classification. The journey moves from validating table stakes, through adding dynamic vault discovery and Ollama-based classification, to building menu bar presence and packaging for distribution. Critical validation checkpoint at Phase 3 (Ollama connection) before investing in UI/packaging.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [x] **Phase 1: Foundation Validation** - Verify existing backend still works ✓
- [ ] **Phase 2: Vault Scanner** - Dynamic domain/PARA/subject discovery
- [ ] **Phase 3: Ollama Connection** - Local LLM integration and health checks
- [ ] **Phase 4: Basic Classification** - Single-level domain classification proof
- [ ] **Phase 5: Multi-Level Classification** - Complete PARA/subject/category pipeline
- [ ] **Phase 6: Processing Integration** - Wire classification to message processor
- [ ] **Phase 7: Menu Bar Interface** - macOS UI layer with status display
- [ ] **Phase 8: First-Run Wizard** - Setup UX for Ollama and vault
- [ ] **Phase 9: Packaging** - .pkg installer for distribution

## Phase Details

### Phase 1: Foundation Validation
**Goal**: Existing backend capabilities are verified working
**Depends on**: Nothing (first phase)
**Requirements**: None (validates existing implementation)
**Success Criteria** (what must be TRUE):
  1. Backend can fetch messages from Slack channel
  2. Backend can create .md files with frontmatter in test vault
  3. Backend can process fix: corrections
  4. State tracking correctly prevents duplicate processing
**Plans**: 2 plans

Plans:
- [x] 01-01-PLAN.md - Unit tests for schema validation and state management ✓
- [x] 01-02-PLAN.md - Integration tests for Slack, file creation, and fix handling ✓

### Phase 2: Vault Scanner
**Goal**: App dynamically discovers vault structure for classification vocabulary
**Depends on**: Phase 1
**Requirements**: VAULT-01, VAULT-02, VAULT-03, VAULT-04, VAULT-05
**Success Criteria** (what must be TRUE):
  1. Scanner discovers all three domain folders (Personal, CCBH, Just Value)
  2. Scanner discovers PARA subfolders within each domain
  3. Scanner discovers subject folders within each PARA section
  4. Scanner caches structure with 6-hour TTL and exposes as vocabulary
  5. User can manually trigger rescan (prep for future menu bar integration)
**Plans**: 2 plans

Plans:
- [ ] 02-01-PLAN.md - Core vault scanner with three-level traversal (TDD)
- [ ] 02-02-PLAN.md - Cache layer with TTL and vocabulary extraction (TDD)

### Phase 3: Ollama Connection
**Goal**: App can communicate with local Ollama instance
**Depends on**: Phase 2
**Requirements**: CLASS-05
**Success Criteria** (what must be TRUE):
  1. App detects if Ollama is running
  2. App can load specified model (Llama 3.2 3B)
  3. App can send prompt and receive response
  4. App handles Ollama errors gracefully (not running, model missing, timeout)
**Plans**: TBD

Plans:
- [ ] 03-01: [TBD during planning]

**VALIDATION CHECKPOINT:** Do not proceed to UI/packaging until Ollama classification quality is verified.

### Phase 4: Basic Classification
**Goal**: App classifies messages into domains using Ollama
**Depends on**: Phase 3
**Requirements**: CLASS-01
**Success Criteria** (what must be TRUE):
  1. Given a message, app returns valid domain (Personal, CCBH, Just Value)
  2. Classification uses vault vocabulary from scanner
  3. Invalid/unexpected responses are caught and logged
  4. Classification completes within 30 seconds (cold start) or 5 seconds (warm)
**Plans**: TBD

Plans:
- [ ] 04-01: [TBD during planning]

### Phase 5: Multi-Level Classification
**Goal**: App completes full classification pipeline (domain → PARA → subject → category)
**Depends on**: Phase 4
**Requirements**: CLASS-02, CLASS-03, CLASS-04, CLASS-06
**Success Criteria** (what must be TRUE):
  1. App classifies PARA type (Projects/Areas/Resources/Archives)
  2. App classifies subject within PARA folder
  3. App assigns category tag to message
  4. Classification uses vault vocabulary from scanner for all levels
  5. Full pipeline produces valid domain/para/subject/category tuple
**Plans**: TBD

Plans:
- [ ] 05-01: [TBD during planning]

### Phase 6: Processing Integration
**Goal**: Classified messages become .md files in correct vault locations
**Depends on**: Phase 5
**Requirements**: PROC-01, PROC-02, PROC-03, PROC-04
**Success Criteria** (what must be TRUE):
  1. App processes backlog on startup
  2. App polls Slack every 2 minutes while running
  3. Created .md files have domain/para/subject/category in frontmatter
  4. Files are placed in correct vault folder path (domain/PARA/subject/)
  5. End-to-end: Slack message → classified → filed in vault within one poll cycle
**Plans**: TBD

Plans:
- [ ] 06-01: [TBD during planning]

### Phase 7: Menu Bar Interface
**Goal**: User has macOS menu bar presence showing status and controls
**Depends on**: Phase 6
**Requirements**: UI-01, UI-02, UI-03, UI-04, UI-05
**Success Criteria** (what must be TRUE):
  1. Menu bar icon appears showing sync status (idle/syncing/error)
  2. User can trigger manual sync from menu bar
  3. User can view recent activity (last 5 filed notes)
  4. User can quit app from menu bar
  5. System notification appears when new notes are filed
**Plans**: TBD

Plans:
- [ ] 07-01: [TBD during planning]

### Phase 8: First-Run Wizard
**Goal**: New users can complete setup without CLI knowledge
**Depends on**: Phase 7
**Requirements**: SETUP-01, SETUP-02, SETUP-03, SETUP-04, SETUP-05, SETUP-06
**Success Criteria** (what must be TRUE):
  1. On first launch, wizard checks if Ollama is installed
  2. If missing, wizard guides download with clickable link
  3. Wizard checks if required model is available
  4. If missing, wizard triggers model download with progress indicator
  5. Wizard allows user to configure vault path (with default)
  6. Wizard validates Slack credentials before completion
**Plans**: TBD

Plans:
- [ ] 08-01: [TBD during planning]

### Phase 9: Packaging
**Goal**: App is distributed as .pkg installer for non-technical users
**Depends on**: Phase 8
**Requirements**: DIST-01, DIST-02, DIST-03
**Success Criteria** (what must be TRUE):
  1. .pkg installer builds from Python codebase
  2. Installer places app in /Applications
  3. User can optionally enable launch on login
  4. Installed app runs without Python environment visible to user
**Plans**: TBD

Plans:
- [ ] 09-01: [TBD during planning]

## Progress

**Execution Order:**
Phases execute in numeric order: 1 → 2 → 3 → 4 → 5 → 6 → 7 → 8 → 9

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Foundation Validation | 2/2 | Complete ✓ | 2026-01-31 |
| 2. Vault Scanner | 0/2 | Planned | - |
| 3. Ollama Connection | 0/TBD | Not started | - |
| 4. Basic Classification | 0/TBD | Not started | - |
| 5. Multi-Level Classification | 0/TBD | Not started | - |
| 6. Processing Integration | 0/TBD | Not started | - |
| 7. Menu Bar Interface | 0/TBD | Not started | - |
| 8. First-Run Wizard | 0/TBD | Not started | - |
| 9. Packaging | 0/TBD | Not started | - |
