# macOS Menu Bar App Architecture with Local LLM Backend

**Research Date:** 2026-01-30
**Context:** Adding menu bar presence and Ollama integration to existing Python backend

---

## Component Overview

### 1. Menu Bar App (macOS Native Layer)

**Technology:** `rumps` (Ridiculously Uncomplicated macOS Python Statusbar)

**Purpose:** Provide user-facing interface and application lifecycle management

**Responsibilities:**
- Display status icon in menu bar (shows sync state: idle, syncing, error)
- Present dropdown menu with actions (Sync Now, View Logs, Preferences, Quit)
- Launch on login (LaunchAgent configuration)
- Coordinate backend processing lifecycle
- Display notifications for user-facing events

**Key Characteristics:**
- Lightweight UI thread (minimal CPU/memory footprint)
- No direct LLM or Slack communication (delegates to backend)
- Manages background worker lifecycle
- Persists across sleep/wake cycles

**Communication:**
- Spawns backend worker process
- Reads status from shared state file (`~/.second-brain/status.json`)
- Uses IPC (file-based or simple socket) for manual trigger commands

---

### 2. Backend Worker (Processing Engine)

**Technology:** Python asyncio-based event loop

**Purpose:** Orchestrate message processing, classification, and Obsidian writing

**Responsibilities:**
- Poll Slack API for new messages (every 2 minutes when active)
- Queue messages for classification
- Coordinate with Ollama for classification
- Write classified thoughts to Obsidian vault
- Handle correction flow ("fix:" commands)
- Update shared state for menu bar status display

**Key Characteristics:**
- Single-threaded event loop (async I/O for Slack, Ollama)
- Spawned by menu bar app on launch
- Runs continuously in background
- Graceful shutdown on SIGTERM

**Communication:**
- Reads configuration from `~/.second-brain/config.json`
- Writes status to `~/.second-brain/status.json` (last sync, error state)
- Accepts manual trigger via file-based command queue

---

### 3. Ollama Client (LLM Integration Layer)

**Technology:** `ollama-python` client library

**Purpose:** Interface with local Ollama service for classification

**Responsibilities:**
- Check Ollama service availability
- Load configured model (e.g., llama3.2:3b)
- Send classification prompts with structured output
- Parse JSON responses
- Handle model loading delays and errors

**Key Characteristics:**
- Synchronous HTTP calls to `localhost:11434/api/generate`
- Structured JSON output via prompt engineering
- Fallback to lower confidence on parsing failures
- Model-agnostic (configurable model name)

**Communication:**
- HTTP REST API to Ollama service
- No authentication (localhost-only)
- Timeout handling (30s for classification)

---

### 4. Vault Scanner (Dynamic Discovery Layer)

**Technology:** Python filesystem walker with caching

**Purpose:** Build dynamic vocabulary of domain/PARA/subject structure

**Responsibilities:**
- Scan Obsidian vault folder structure
- Extract domain names (Personal, CCBH, Just Value)
- Extract PARA folders (Projects, Areas, Resources, Archives)
- Extract subject subfolders within each PARA section
- Cache results with TTL (refresh every 6 hours or on manual trigger)

**Key Characteristics:**
- Runs on startup and periodically
- Builds classification context for LLM prompts
- Adapts to vault changes without code updates
- Stores map in `~/.second-brain/vault_map.json`

**Communication:**
- Reads from filesystem (`~/Library/Mobile Documents/iCloud~md~obsidian/Documents/Home`)
- Writes to cache file for backend worker consumption

---

### 5. Slack Integration Layer (Existing)

**Technology:** `requests` with retry logic

**Purpose:** Fetch messages and send replies

**Responsibilities:**
- Poll `conversations.history` API
- Fetch thread replies for "fix:" detection
- Send confirmation messages
- Send DM alerts on failures

**Key Characteristics:**
- Exponential backoff retry (3 attempts)
- Rate limit handling (429 responses)
- State-based message tracking (idempotency)

**Communication:**
- HTTPS to Slack API (`slack.com/api/*`)
- OAuth token authentication
- JSON payload/response

---

### 6. State Management Layer (Existing)

**Technology:** File-based JSON with atomic writes

**Purpose:** Track processed messages, file mappings, run history

**Responsibilities:**
- Record processed message timestamps
- Map Slack message TS to vault file paths
- Track last successful run for health checks
- Dead letter queue for failed messages

**Key Characteristics:**
- File locking (fcntl) for concurrent access
- TTL-based cleanup (30-day retention)
- Append-only logs for audit trail

**Communication:**
- Filesystem writes to `~/.second-brain/.state/`
- Shared state files read by menu bar app for status display

---

### 7. First-Run Wizard (Setup Component)

**Technology:** `tkinter` dialog or CLI prompts with validation

**Purpose:** Guide initial setup for non-technical users

**Responsibilities:**
- Check Ollama installation (`which ollama`)
- Guide model download (`ollama pull llama3.2:3b`)
- Validate vault path exists
- Create configuration file
- Test Slack credentials
- Offer to install as Login Item

**Key Characteristics:**
- Runs only on first launch (or when config missing)
- Blocking UI (prevents main app launch until complete)
- Validation at each step
- Graceful exit on cancel

**Communication:**
- Spawns subprocess for `ollama pull`
- Writes to `~/.second-brain/config.json`
- Tests Slack API with provided token

---

## Data Flow

### Startup Sequence

```
1. Menu Bar App Launch
   ↓
2. Check ~/.second-brain/config.json
   ├─ Missing → Run First-Run Wizard → Create config → Continue
   └─ Exists → Validate config → Continue
   ↓
3. Spawn Backend Worker Process
   ↓
4. Backend Worker Initialization
   ├─ Load configuration
   ├─ Run Vault Scanner (build domain/PARA/subject map)
   ├─ Check Ollama availability (HTTP GET /api/tags)
   ├─ Load state (last processed timestamp)
   └─ Start event loop
   ↓
5. Menu Bar App Updates Status
   └─ Read ~/.second-brain/status.json
   └─ Display "Idle" or "Error: Ollama not running"
```

---

### Message Processing Flow

```
1. Slack Poll (every 2 minutes)
   ↓
2. Fetch new messages since last timestamp
   ↓
3. Filter: Skip "fix:" commands, bot messages, already processed
   ↓
4. For each message:
   ├─ Build classification prompt with vault map context
   ├─ Send to Ollama (/api/generate with JSON schema)
   ├─ Parse JSON response
   ├─ Validate classification schema
   │  └─ On error: Fallback to "ideas" with low confidence
   ├─ Write to Obsidian vault
   │  ├─ Determine path: domain/PARA/subject/filename.md
   │  ├─ Generate frontmatter (YAML)
   │  ├─ Insert wikilinks
   │  └─ Write file
   ├─ Update state (mark processed, map TS → file path)
   ├─ Log to inbox log
   ├─ Append to daily note
   └─ Send Slack confirmation reply
   ↓
5. Update status.json (last sync time, message count)
   ↓
6. Menu bar app reads status.json → updates icon tooltip
```

---

### Manual Trigger Flow (User clicks "Sync Now")

```
1. Menu bar app writes command to ~/.second-brain/commands/trigger_sync
   ↓
2. Backend worker detects command file (event loop checks every 1s)
   ↓
3. Backend runs immediate Slack poll (skip 2-minute timer)
   ↓
4. Process messages as normal
   ↓
5. Update status.json with "Manual sync completed"
   ↓
6. Menu bar app displays notification
   ↓
7. Delete command file
```

---

### Correction Flow ("fix:" command)

```
1. Slack Poll detects "fix:" message in thread
   ↓
2. Extract parent message TS and new destination
   ↓
3. Lookup file path from message mapping (state.message_mapping[parent_ts])
   ↓
4. Determine new path: domain/PARA/subject/filename.md
   ↓
5. Move file to new location
   ↓
6. Update frontmatter (domain, para, subject fields)
   ↓
7. Update state mapping (point parent_ts to new file path)
   ↓
8. Send Slack confirmation
```

---

### Health Check Flow (runs every 5 minutes)

```
1. Backend worker checks last successful Slack poll
   ├─ If > 10 minutes ago → Mark as unhealthy
   └─ Update status.json with error state
   ↓
2. Check Ollama availability
   ├─ HTTP GET /api/tags
   ├─ If timeout or error → Mark as unhealthy
   └─ Update status.json
   ↓
3. Menu bar app reads status.json
   └─ Display warning icon if unhealthy
   └─ Show "Error: Ollama not responding" in menu
```

---

## Component Boundaries

### What Talks to What

**Menu Bar App:**
- Reads: `~/.second-brain/status.json`, `~/.second-brain/config.json`
- Writes: `~/.second-brain/commands/trigger_sync`
- Spawns: Backend Worker process

**Backend Worker:**
- Reads: `~/.second-brain/config.json`, `~/.second-brain/.state/*`, `~/.second-brain/commands/*`
- Writes: `~/.second-brain/status.json`, `~/.second-brain/.state/*`, Obsidian vault files
- Calls: Slack API, Ollama API

**Vault Scanner:**
- Reads: Obsidian vault filesystem
- Writes: `~/.second-brain/vault_map.json`

**Ollama Client:**
- Calls: `localhost:11434/api/generate`, `localhost:11434/api/tags`

**Slack Client:**
- Calls: `slack.com/api/conversations.history`, `slack.com/api/chat.postMessage`

**State Manager:**
- Reads/Writes: `~/.second-brain/.state/processed_messages.json`, `message_mapping.json`, `run_history.json`

**First-Run Wizard:**
- Reads: System (checks for `ollama` binary, vault path)
- Writes: `~/.second-brain/config.json`
- Spawns: `ollama pull llama3.2:3b`

---

### Isolation Principles

1. **Menu bar app never does I/O** (Slack, Ollama, Obsidian) — only UI and lifecycle management
2. **Backend worker never does GUI** — only console logs and status file writes
3. **Ollama client is abstraction** — backend never calls Ollama HTTP API directly
4. **State files are single source of truth** — no in-memory state shared across components
5. **Vault scanner is independent** — can be tested/run standalone

---

## Build Order (Dependencies)

### Phase 1: Foundation (No new dependencies)
**Goal:** Validate existing backend works with current architecture

1. **Extract Slack client** — Already done (`slack_client.py`)
2. **Extract state management** — Already done (`state.py`)
3. **Extract validation** — Already done (`schema.py`)
4. **Extract wikilinks** — Already done (`wikilinks.py`)

**Deliverable:** Modular backend scripts that can be imported as library

---

### Phase 2: Vault Scanner (New component, no external deps)
**Goal:** Enable dynamic domain/PARA/subject discovery

1. **Implement vault walker** — Scan folders, build hierarchy map
2. **Implement caching** — Write/read `vault_map.json` with TTL
3. **Add refresh trigger** — Detect vault changes or manual refresh
4. **Test with real vault** — Ensure accurate extraction

**Deliverable:** `vault_scanner.py` module that returns domain/PARA/subject tree

**Dependencies:** Phase 1 (uses filesystem, no external deps)

---

### Phase 3: Ollama Integration (Replaces Claude API)
**Goal:** Local LLM classification without API calls

1. **Install ollama-python** — `uv add ollama`
2. **Create Ollama client** — Wrapper around `ollama.generate()` with JSON schema
3. **Build classification prompt** — Include vault map context from Phase 2
4. **Test classification quality** — Compare vs Claude API on sample messages
5. **Add fallback handling** — Low confidence on parse failures

**Deliverable:** `ollama_client.py` module that replaces `classify_thought()` placeholder

**Dependencies:** Phase 2 (needs vault map for prompt context)

---

### Phase 4: Backend Worker Refactor (Event loop)
**Goal:** Move from cron to persistent background process

1. **Create async event loop** — Replace cron-triggered scripts
2. **Add periodic polling** — 2-minute interval for Slack checks
3. **Add health monitoring** — Ollama/Slack availability checks every 5 minutes
4. **Add command queue** — File-based IPC for manual triggers
5. **Add graceful shutdown** — SIGTERM handler for clean exit

**Deliverable:** `worker.py` that runs as background daemon

**Dependencies:** Phase 3 (needs Ollama client)

---

### Phase 5: Menu Bar App (macOS UI)
**Goal:** User-facing application with status display

1. **Install rumps** — `uv add rumps`
2. **Create basic menu bar app** — Icon, menu items
3. **Add status display** — Read `status.json`, update icon/tooltip
4. **Add manual trigger** — "Sync Now" writes to command queue
5. **Add preferences** — Open config file in editor
6. **Add log viewer** — Open `~/SecondBrain/_inbox_log/` in Finder

**Deliverable:** `menu_bar.py` that spawns worker and shows status

**Dependencies:** Phase 4 (needs worker process)

---

### Phase 6: First-Run Wizard (Setup UX)
**Goal:** Guide initial configuration for non-technical users

1. **Create wizard dialog** — CLI prompts with validation
2. **Add Ollama check** — Detect installation, offer download link
3. **Add model download** — Run `ollama pull llama3.2:3b` with progress
4. **Add vault path input** — Browse for Obsidian vault
5. **Add Slack credential input** — Token, channel ID, user ID
6. **Add config generation** — Write `config.json`

**Deliverable:** `setup_wizard.py` that runs on first launch

**Dependencies:** Phase 5 (integrated into menu bar app launch sequence)

---

### Phase 7: Packaging & Distribution (.pkg installer)
**Goal:** Single-click installation for non-technical users

1. **Choose packager** — PyInstaller vs py2app (recommend PyInstaller for simplicity)
2. **Create spec file** — Bundle menu_bar.py as standalone app
3. **Include dependencies** — Embed Python runtime, rumps, ollama-python
4. **Create .pkg installer** — macOS Installer with LaunchAgent setup
5. **Test on clean Mac** — Verify installation without dev tools

**Deliverable:** `SecondBrain-Installer.pkg` for distribution

**Dependencies:** Phase 6 (all components functional)

---

## Suggested Build Order Summary

| Phase | Component | External Deps | Build Time | Risk |
|-------|-----------|---------------|------------|------|
| 1 | Foundation | None (existing) | 0 days | Low |
| 2 | Vault Scanner | None | 1-2 days | Low |
| 3 | Ollama Integration | `ollama-python` | 2-3 days | Medium (model quality) |
| 4 | Backend Worker | None | 2-3 days | Medium (async refactor) |
| 5 | Menu Bar App | `rumps` | 1-2 days | Low |
| 6 | First-Run Wizard | None | 1-2 days | Low |
| 7 | Packaging | `pyinstaller` | 2-3 days | High (platform quirks) |

**Total estimated build time:** 9-15 days (assuming serial development)

**Critical path:** Phase 1 → 2 → 3 → 4 → 5 → 6 → 7

**Parallelizable:** Phase 5 (Menu Bar App) can start after Phase 4 wireframe, Phase 6 (Wizard) can develop in parallel with Phase 5

---

## Key Architectural Decisions

### 1. Event-Driven vs Polling for Slack
**Decision:** Polling (existing pattern)
**Rationale:**
- Slack webhooks require public endpoint (not suitable for local-only app)
- Polling every 2 minutes sufficient for use case (not real-time critical)
- Existing cron-based polling works, just move to event loop
- Simpler error handling (retry logic already implemented)

**Alternative considered:** Slack Events API with ngrok tunnel — rejected due to complexity and dependency on external service

---

### 2. Menu Bar Framework: rumps vs pyobjc
**Decision:** rumps
**Rationale:**
- Pythonic API (no Objective-C bridging)
- Well-maintained, active community
- Minimal boilerplate for statusbar apps
- Works with PyInstaller for packaging

**Alternative considered:** pyobjc (lower-level, more control) — rejected due to steep learning curve

---

### 3. Process Model: Single vs Multi-Process
**Decision:** Multi-process (menu bar spawns worker)
**Rationale:**
- Isolates UI from I/O failures (worker crash doesn't kill menu bar)
- Easier to restart worker without re-launching app
- Menu bar stays responsive during Ollama delays
- Standard pattern for macOS statusbar apps

**Alternative considered:** Single-process with threads — rejected due to GIL limitations and complexity

---

### 4. IPC Mechanism: File-Based vs Sockets
**Decision:** File-based command queue
**Rationale:**
- Simple to implement (write command file, worker polls)
- No socket port conflicts
- Persistent across worker restarts
- Easy to debug (inspect command files)

**Alternative considered:** Unix domain sockets — rejected due to added complexity for minimal benefit

---

### 5. Ollama Model: Llama 3.2 (3B) vs Mistral (7B)
**Decision:** Llama 3.2 (3B) for initial implementation
**Rationale:**
- Fits in MacBook Air M1 8GB RAM
- Faster inference (< 5s for classification)
- Good instruction-following for structured output
- Smaller download size (1.9GB)

**Alternative considered:** Mistral 7B (better quality) — defer until testing confirms 3B insufficient

---

### 6. Packaging: PyInstaller vs py2app
**Decision:** PyInstaller
**Rationale:**
- Simpler workflow (single-file bundle)
- Better documentation for CLI apps → GUI transition
- Active community, macOS support well-tested
- Easier to debug (less abstraction)

**Alternative considered:** py2app (more macOS-native) — may revisit in Phase 7 if PyInstaller has issues

---

## Risk Mitigation

### Risk: Ollama classification quality < Claude API
**Mitigation:**
- Implement A/B testing (classify with both, compare confidence)
- Add manual review queue for low-confidence (<0.6) classifications
- Allow fallback to Claude API via config flag
- Test on 100-message corpus before full switch

---

### Risk: Menu bar app killed by macOS (memory pressure)
**Mitigation:**
- Keep menu bar process minimal (< 50MB resident)
- Delegate all I/O to worker process
- Worker can be killed/restarted without UI loss
- Store state on disk (no critical in-memory data)

---

### Risk: Vault scanner performance on large vaults (10k+ files)
**Mitigation:**
- Cache results with 6-hour TTL
- Scan only folder structure (ignore file contents)
- Run scanner in background thread
- Limit depth to 5 levels (domain → PARA → subject → category → subcategory)

---

### Risk: Ollama service not running when app starts
**Mitigation:**
- First-run wizard checks Ollama installation
- Health check detects Ollama down, updates status
- Menu bar app shows clear error message
- Worker retries Ollama connection with backoff

---

### Risk: .pkg installation fails on user machines
**Mitigation:**
- Test on clean macOS 10.15, 11, 12, 13 VMs
- Sign .pkg with Apple Developer ID (avoid Gatekeeper blocks)
- Include uninstaller script
- Provide manual installation instructions as fallback

---

## Open Questions

1. **Model selection:** Should we bundle model in .pkg or download on first run?
   *Recommendation:* Download on first run (model files are 1.9GB+, too large for installer)

2. **Vault path:** Hardcode iCloud path or allow custom?
   *Recommendation:* Allow custom in first-run wizard (supports non-iCloud vaults)

3. **LaunchAgent vs Login Item:** Which autostart mechanism?
   *Recommendation:* LaunchAgent (survives restarts, doesn't require user login)

4. **Logging verbosity:** Console logs or GUI log viewer?
   *Recommendation:* Both (console for debugging, GUI for user-friendly access)

5. **Update mechanism:** Auto-update or manual download?
   *Recommendation:* Defer to post-MVP (manual download from GitHub releases initially)

---

## Conclusion

The architecture cleanly separates concerns:
- **Menu bar app** = UI and lifecycle
- **Backend worker** = I/O and orchestration
- **Ollama client** = LLM abstraction
- **Vault scanner** = dynamic discovery
- **State manager** = persistence

This enables independent testing, phased rollout, and clear debugging paths. The build order minimizes risk by validating Ollama integration (Phase 3) before investing in UI (Phase 5) and packaging (Phase 7).

**Next steps:**
1. Validate Phase 1 (existing backend) works as library imports
2. Implement Phase 2 (vault scanner) to enable vault-aware prompts
3. Test Ollama classification quality in Phase 3 before committing to full migration

---

*Architecture research completed: 2026-01-30*
