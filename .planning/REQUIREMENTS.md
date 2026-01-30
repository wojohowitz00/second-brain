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

- [ ] **VAULT-01**: App scans Obsidian vault to discover domain folders (Personal, CCBH, Just Value)
- [ ] **VAULT-02**: App scans PARA subfolders within each domain (Projects/Areas/Resources/Archives)
- [ ] **VAULT-03**: App scans subject subfolders within each PARA section
- [ ] **VAULT-04**: App caches vault structure with configurable TTL (default 6 hours)
- [ ] **VAULT-05**: User can manually trigger vault rescan from menu bar

### Classification

- [ ] **CLASS-01**: App classifies message domain (Personal, CCBH, Just Value)
- [ ] **CLASS-02**: App classifies PARA type (Projects, Areas, Resources, Archives)
- [ ] **CLASS-03**: App classifies subject within the PARA folder
- [ ] **CLASS-04**: App assigns category tag to each note
- [ ] **CLASS-05**: Classification runs locally via Ollama (no cloud API)
- [ ] **CLASS-06**: Classification uses vault vocabulary from scanner

### Processing

- [ ] **PROC-01**: App processes Slack messages on startup (backlog since last run)
- [ ] **PROC-02**: App polls Slack every 2 minutes while running
- [ ] **PROC-03**: App creates .md files with domain/para/subject/category frontmatter
- [ ] **PROC-04**: App places files in correct vault folder path

### User Interface

- [ ] **UI-01**: App displays menu bar icon showing sync status (idle/syncing/error)
- [ ] **UI-02**: User can trigger manual sync from menu bar
- [ ] **UI-03**: User can view recent activity from menu bar
- [ ] **UI-04**: User can quit app from menu bar
- [ ] **UI-05**: App shows notification when new notes are filed

### Setup

- [ ] **SETUP-01**: First-run wizard checks if Ollama is installed
- [ ] **SETUP-02**: First-run wizard guides Ollama download if missing
- [ ] **SETUP-03**: First-run wizard checks if required model is available
- [ ] **SETUP-04**: First-run wizard triggers model download with progress indicator
- [ ] **SETUP-05**: First-run wizard allows user to configure vault path
- [ ] **SETUP-06**: First-run wizard validates Slack credentials

### Distribution

- [ ] **DIST-01**: App is distributed as .pkg installer
- [ ] **DIST-02**: Installer places app in /Applications
- [ ] **DIST-03**: App can be launched on login (optional LaunchAgent)

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
| VAULT-01 | — | Pending |
| VAULT-02 | — | Pending |
| VAULT-03 | — | Pending |
| VAULT-04 | — | Pending |
| VAULT-05 | — | Pending |
| CLASS-01 | — | Pending |
| CLASS-02 | — | Pending |
| CLASS-03 | — | Pending |
| CLASS-04 | — | Pending |
| CLASS-05 | — | Pending |
| CLASS-06 | — | Pending |
| PROC-01 | — | Pending |
| PROC-02 | — | Pending |
| PROC-03 | — | Pending |
| PROC-04 | — | Pending |
| UI-01 | — | Pending |
| UI-02 | — | Pending |
| UI-03 | — | Pending |
| UI-04 | — | Pending |
| UI-05 | — | Pending |
| SETUP-01 | — | Pending |
| SETUP-02 | — | Pending |
| SETUP-03 | — | Pending |
| SETUP-04 | — | Pending |
| SETUP-05 | — | Pending |
| SETUP-06 | — | Pending |
| DIST-01 | — | Pending |
| DIST-02 | — | Pending |
| DIST-03 | — | Pending |

---

*Requirements defined: 2026-01-30*
