# Requirements

**Project:** Second Brain
**Version:** v1.0
**Last Updated:** 2026-01-30

---

## Validated (Existing)

These capabilities exist in the current codebase:

- ✓ **SLACK-01**: Fetch messages from Slack channel with retry/rate limiting — existing
- ✓ **SLACK-02**: Track processed messages for idempotency — existing
- ✓ **SLACK-03**: Reply to messages with filing confirmation — existing
- ✓ **SLACK-04**: Handle `fix:` thread replies for corrections — existing
- ✓ **WRITE-01**: Create .md files with YAML frontmatter — existing
- ✓ **WRITE-02**: Sanitize filenames and handle duplicates — existing
- ✓ **WRITE-03**: Extract and link entities as wikilinks — existing
- ✓ **HEALTH-01**: Monitor system health and alert on failures — existing
- ✓ **DIGEST-01**: Generate daily digest summaries — existing
- ✓ **DIGEST-02**: Generate weekly review summaries — existing

---

## v1 Requirements

### Vault Discovery

- [x] **VAULT-01**: App scans Obsidian vault to discover domain folders (Personal, CCBH, Just Value) ✓
- [x] **VAULT-02**: App scans PARA subfolders within each domain (Projects/Areas/Resources/Archives) ✓
- [x] **VAULT-03**: App scans subject subfolders within each PARA section ✓
- [x] **VAULT-04**: App caches vault structure with configurable TTL (default 6 hours) ✓
- [x] **VAULT-05**: User can manually trigger vault rescan from menu bar ✓

### Classification

- [x] **CLASS-01**: App classifies message domain (Personal, CCBH, Just Value) ✓
- [x] **CLASS-02**: App classifies PARA type (Projects, Areas, Resources, Archives) ✓
- [x] **CLASS-03**: App classifies subject within the PARA folder ✓
- [x] **CLASS-04**: App assigns category tag to each note ✓
- [x] **CLASS-05**: Classification runs locally via Ollama (no cloud API) ✓
- [x] **CLASS-06**: Classification uses vault vocabulary from scanner ✓

### Processing

- [x] **PROC-01**: App processes Slack messages on startup (backlog since last run) ✓
- [x] **PROC-02**: App polls Slack every 2 minutes while running ✓
- [x] **PROC-03**: App creates .md files with domain/para/subject/category frontmatter ✓
- [x] **PROC-04**: App places files in correct vault folder path ✓

### User Interface

- [x] **UI-01**: App displays menu bar icon showing sync status (idle/syncing/error) ✓
- [x] **UI-02**: User can trigger manual sync from menu bar ✓
- [x] **UI-03**: User can view recent activity from menu bar ✓
- [x] **UI-04**: User can quit app from menu bar ✓
- [x] **UI-05**: App shows notification when new notes are filed ✓

### Setup

- [x] **SETUP-01**: First-run wizard checks if Ollama is installed ✓
- [x] **SETUP-02**: First-run wizard guides Ollama download if missing ✓
- [x] **SETUP-03**: First-run wizard checks if required model is available ✓
- [x] **SETUP-04**: First-run wizard triggers model download with progress indicator ✓
- [x] **SETUP-05**: First-run wizard allows user to configure vault path ✓
- [x] **SETUP-06**: First-run wizard validates Slack credentials ✓

### Distribution

- [x] **DIST-01**: App is distributed as .pkg installer ✓
- [x] **DIST-02**: Installer places app in /Applications ✓
- [x] **DIST-03**: App can be launched on login (optional LaunchAgent) ✓

---

## v2 Requirements (Deferred)

- [ ] **V2-01**: Learning from corrections to improve future classification
- [ ] **V2-02**: Batch reclassification when vault structure changes
- [ ] **V2-03**: Multiple Slack channel support
- [ ] **V2-04**: iOS native capture app (bypass Slack)
- [ ] **V2-05**: Apple Developer ID signing and notarization for public distribution

---

## Out of Scope

| Exclusion | Reason |
|-----------|--------|
| Real-time sync | Event-driven with 2-min polling is sufficient |
| Multi-user support | Personal tool, single vault |
| Cloud sync of state | Obsidian handles vault sync via iCloud |
| Custom LLM training | Off-the-shelf Ollama models sufficient |
| App Store distribution | Sandboxing conflicts with vault access |
| Slack webhooks | Requires public endpoint; polling simpler |

---

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| VAULT-01 | Phase 2 | Complete |
| VAULT-02 | Phase 2 | Complete |
| VAULT-03 | Phase 2 | Complete |
| VAULT-04 | Phase 2 | Complete |
| VAULT-05 | Phase 2 | Complete |
| CLASS-01 | Phase 4 | Complete |
| CLASS-02 | Phase 5 | Complete |
| CLASS-03 | Phase 5 | Complete |
| CLASS-04 | Phase 5 | Complete |
| CLASS-05 | Phase 3 | Complete |
| CLASS-06 | Phase 5 | Complete |
| PROC-01 | Phase 6 | Complete |
| PROC-02 | Phase 6 | Complete |
| PROC-03 | Phase 6 | Complete |
| PROC-04 | Phase 6 | Complete |
| UI-01 | Phase 7 | Complete |
| UI-02 | Phase 7 | Complete |
| UI-03 | Phase 7 | Complete |
| UI-04 | Phase 7 | Complete |
| UI-05 | Phase 7 | Complete |
| SETUP-01 | Phase 8 | Complete |
| SETUP-02 | Phase 8 | Complete |
| SETUP-03 | Phase 8 | Complete |
| SETUP-04 | Phase 8 | Complete |
| SETUP-05 | Phase 8 | Complete |
| SETUP-06 | Phase 8 | Complete |
| DIST-01 | Phase 9 | Complete |
| DIST-02 | Phase 9 | Complete |
| DIST-03 | Phase 9 | Complete |

---

*Requirements defined: 2026-01-30*
