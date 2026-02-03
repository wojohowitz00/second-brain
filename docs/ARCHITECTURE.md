# Second Brain Architecture

Technical documentation for developers and advanced users.

---

## Table of Contents

1. [System Overview](#system-overview)
2. [Component Architecture](#component-architecture)
3. [Data Flow](#data-flow)
4. [Module Reference](#module-reference)
5. [State Management](#state-management)
6. [Classification Pipeline](#classification-pipeline)
7. [File System Layout](#file-system-layout)
8. [Configuration](#configuration)
9. [Testing Strategy](#testing-strategy)
10. [Build System](#build-system)

---

## System Overview

Second Brain is a macOS menu bar application that integrates three systems:

```
┌─────────────────────────────────────────────────────────────┐
│                      Second Brain                           │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────────┐   │
│  │ Menu Bar UI │  │  Processing  │  │  Classification  │   │
│  │   (rumps)   │──│   Pipeline   │──│    (Ollama)      │   │
│  └─────────────┘  └──────────────┘  └──────────────────┘   │
│         │                │                    │             │
│         ▼                ▼                    ▼             │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────────┐   │
│  │    State    │  │ File Writer  │  │  Vault Scanner   │   │
│  │ Management  │  │              │  │                  │   │
│  └─────────────┘  └──────────────┘  └──────────────────┘   │
└─────────────────────────────────────────────────────────────┘
         │                │                    │
         ▼                ▼                    ▼
    ┌─────────┐     ┌──────────┐        ┌──────────┐
    │  Slack  │     │ Obsidian │        │  Ollama  │
    │   API   │     │  Vault   │        │  Server  │
    └─────────┘     └──────────┘        └──────────┘
```

### Key Design Decisions

1. **Local-first**: All AI processing via Ollama (no cloud APIs)
2. **PARA organization**: Files organized by Domain/PARA/Subject/Category
3. **Polling model**: 2-minute intervals (vs webhooks requiring public endpoint)
4. **Single-shot classification**: One LLM call for all 4 levels (vs cascading calls)
5. **Menu bar app**: Persistent background process with minimal UI

---

## Component Architecture

### Layer Separation

```
┌────────────────────────────────────────────────────────────┐
│                    Presentation Layer                       │
│  menu_bar_app.py, notifications.py, setup_wizard.py        │
├────────────────────────────────────────────────────────────┤
│                    Business Logic Layer                     │
│  process_inbox.py, message_classifier.py, file_writer.py   │
├────────────────────────────────────────────────────────────┤
│                    Integration Layer                        │
│  slack_client.py, ollama_client.py, vault_scanner.py       │
├────────────────────────────────────────────────────────────┤
│                    Infrastructure Layer                     │
│  state.py, schema.py, wikilinks.py                         │
└────────────────────────────────────────────────────────────┘
```

### Dependency Graph

```
menu_bar_app
    ├── process_inbox
    │       ├── slack_client
    │       ├── message_classifier
    │       │       ├── ollama_client
    │       │       └── vault_scanner
    │       ├── file_writer
    │       └── state
    ├── vault_scanner
    ├── notifications
    └── state

setup_wizard
    ├── ollama_client
    ├── vault_scanner
    └── slack_client
```

---

## Data Flow

### Message Processing Flow

```
1. Slack API
   │
   ▼
2. slack_client.fetch_messages()
   │ Returns: List[dict] of messages
   ▼
3. process_inbox.process_message()
   │ For each message:
   ▼
4. message_classifier.classify()
   │ Returns: ClassificationResult(domain, para, subject, category, confidence)
   ▼
5. file_writer.create_note_file()
   │ Returns: Path to created file
   ▼
6. notifications.notify_note_filed()
   │
   ▼
7. slack_client.post_reply()
```

### YouTube Ingestion Flow (optional)

```
1. User provides YouTube URL (CLI or menu bar)
   │
   ▼
2. youtube_ingest.fetch_youtube_metadata()
   │ yt-dlp
   ▼
3. Transcript generation
   │ captions via yt-dlp or local Whisper
   ▼
4. Optional summarization (Ollama)
   │ summary + outline + actions
   ▼
5. file_writer.create_youtube_note_file()
   │ Writes to <Domain>/3_Resources/VideoNotes/
```

### Classification Flow

```
1. Input: message text
   │
   ▼
2. vault_scanner.get_vocabulary()
   │ Returns: {domains: [...], subjects: {...}}
   │
   ▼
3. Build prompt with vocabulary
   │
   ▼
4. ollama_client.chat()
   │ Returns: LLM response text
   │
   ▼
5. Parse JSON response
   │ Fallback: regex extraction
   │
   ▼
6. Validate against vocabulary
   │ Invalid values → defaults
   │
   ▼
7. Return ClassificationResult
```

---

## Module Reference

### menu_bar_app.py (348 lines)

**Purpose**: macOS menu bar UI using rumps framework.

**Key Classes**:
- `MenuBarCore`: Business logic (testable without UI)
- `MenuBarApp`: rumps.App wrapper

**Key Methods**:
```python
class MenuBarCore:
    def set_status(status: str) -> None
    def get_recent_activity() -> List[dict]
    def sync() -> None
    def get_health() -> dict
    def open_note(path: str) -> None
```

### setup_wizard.py (400 lines)

**Purpose**: First-run setup flow.

**Key Classes**:
- `SetupStep`: Enum of wizard steps
- `SetupWizard`: Step-by-step wizard logic

**Key Methods**:
```python
class SetupWizard:
    def is_ollama_installed() -> bool
    def is_model_available(model: str) -> bool
    def download_model(model: str, callback: Callable) -> bool
    def validate_vault_path(path: str) -> bool
    def validate_slack_credentials(token: str) -> dict
    def run() -> bool
```

### message_classifier.py (330 lines)

**Purpose**: Multi-level classification using Ollama.

**Key Classes**:
- `ClassificationResult`: dataclass with domain, para, subject, category, confidence
- `MessageClassifier`: Main classifier

**Key Methods**:
```python
class MessageClassifier:
    def classify(message: str) -> ClassificationResult
    def _build_prompt(message: str, vocabulary: dict) -> str
    def _parse_response(response: str) -> dict
    def _validate_classification(result: dict, vocabulary: dict) -> dict
```

### ollama_client.py (281 lines)

**Purpose**: Interface to local Ollama server.

**Key Classes**:
- `OllamaError`, `OllamaServerNotRunning`, `OllamaModelNotFound`, `OllamaTimeout`
- `OllamaClient`

**Key Methods**:
```python
class OllamaClient:
    def is_healthy() -> bool
    def is_model_available(model: str) -> bool
    def chat(prompt: str, model: str = None) -> str
    def list_models() -> List[str]
```

### vault_scanner.py (332 lines)

**Purpose**: Discover PARA folder structure.

**Key Classes**:
- `VaultScanner`

**Key Methods**:
```python
class VaultScanner:
    def scan() -> dict
    def get_domains() -> List[str]
    def get_para_types(domain: str) -> List[str]
    def get_subjects(domain: str, para_type: str) -> List[str]
    def get_vocabulary() -> dict
    def invalidate_cache() -> None
```

### file_writer.py (199 lines)

**Purpose**: Create markdown files with frontmatter.

**Key Functions**:
```python
def sanitize_filename(text: str) -> str
def build_frontmatter(classification: ClassificationResult, source: str) -> str
def create_note_file(
    message: str, 
    classification: ClassificationResult, 
    vault_path: Path
) -> Path
```

### process_inbox.py (276 lines)

**Purpose**: Main processing loop.

**Key Functions**:
```python
def process_message(message: dict) -> Optional[Path]
def process_all() -> List[Path]
def main_loop() -> None  # 2-minute polling
def get_classifier() -> MessageClassifier  # Singleton
```

### slack_client.py (238 lines)

**Purpose**: Slack API wrapper.

**Key Classes**:
- `SlackAPIError`, `SlackRateLimitError`
- `SlackClient`

**Key Methods**:
```python
class SlackClient:
    def fetch_messages(oldest: float = None) -> List[dict]
    def fetch_thread_replies(thread_ts: str) -> List[dict]
    def post_reply(thread_ts: str, text: str) -> None
    def post_message(text: str) -> None
```

### state.py (287 lines)

**Purpose**: Persistent state management.

**Key Functions**:
```python
def is_message_processed(message_id: str) -> bool
def mark_message_processed(message_id: str) -> None
def get_file_for_message(message_id: str) -> Optional[Path]
def set_file_for_message(message_id: str, path: Path) -> None
def cleanup_old_entries(ttl_days: int = 30) -> None
```

### notifications.py (164 lines)

**Purpose**: macOS native notifications via osascript.

**Key Functions**:
```python
def notify_note_filed(title: str, path: str) -> None
def notifications_enabled() -> bool
def set_notifications_enabled(enabled: bool) -> None
```

---

## State Management

### State Files

```
backend/_scripts/.state/
├── .last_processed_ts        # Timestamp of last processed message
├── vault_cache.json          # Cached vault structure (6-hour TTL)
├── recent_activity.json      # Last 5 filed notes
├── setup_state.json          # Wizard completion state
└── notifications_config.json # Notification preferences
```

### Processed Messages State

Messages are tracked by timestamp:
```python
# .last_processed_ts contains Unix timestamp
1706745600.123456
```

Only messages newer than this timestamp are processed.

### Vault Cache

```json
{
  "timestamp": 1706745600,
  "ttl_hours": 6,
  "domains": ["Personal", "Work"],
  "structure": {
    "Personal": {
      "1_Projects": ["app-dev", "home-reno"],
      "2_Areas": ["health", "finance"],
      "3_Resources": ["recipes", "books"],
      "4_Archives": []
    }
  }
}
```

---

## Classification Pipeline

### Mirrored storage (attachments)

When a Slack message has file attachments, the app downloads them into the same vault folder as the note (1:1 mirrored). Allowed types: pdf, images (png, jpg, gif, webp), audio (mp3, m4a, wav), video (mp4, mov), text (txt, md, csv). Max size 50MB per file. The note body gets an "## Attachments" section with markdown links to the downloaded files. Implemented in [slack_client](backend/_scripts/slack_client.py) (`get_message_files`, `download_file`), [file_writer](backend/_scripts/file_writer.py) (`safe_attachment_filename`, `append_attachments_section`), and [process_inbox](backend/_scripts/process_inbox.py) (`_process_attachments`).

### Mode: single vs pipeline

- **single** (default): One LLM call classifies domain, PARA type, subject, and category.
- **pipeline**: Three steps in sequence — (1) domain only, (2) PARA only given domain, (3) subject + category given domain and PARA. Each step can use a different model (e.g. smaller models for domain/PARA).

Set `CLASSIFICATION_MODE=pipeline` to enable. Optional per-step models: `OLLAMA_MODEL_DOMAIN`, `OLLAMA_MODEL_PARA`, `OLLAMA_MODEL_FULL` (default: `OLLAMA_MODEL` for all).

### Prompt Structure

```
You are a classification system. Classify the following message into:
1. Domain: One of [Personal, Work, Side_Projects]
2. PARA Type: One of [Projects, Areas, Resources, Archives]
3. Subject: Specific topic folder
4. Category: Content tag

Available subjects by domain/PARA:
- Personal/Projects: app-dev, home-renovation
- Personal/Areas: health, finance
...

Message: "{user's message}"

Respond with JSON only:
{"domain": "...", "para": "...", "subject": "...", "category": "...", "confidence": 0.0-1.0}
```

### Response Parsing

1. **JSON extraction**: Try `json.loads(response)`
2. **Regex fallback**: Extract key-value pairs if JSON fails
3. **Validation**: Check values against vocabulary
4. **Normalization**: Invalid values → defaults

### Default Values

```python
DEFAULT_DOMAIN = "Personal"
DEFAULT_PARA = "Resources"
DEFAULT_SUBJECT = "general"
DEFAULT_CATEGORY = "uncategorized"
```

---

## File System Layout

### Project Structure

```
second-brain/
├── backend/
│   ├── _scripts/           # Python modules
│   │   ├── menu_bar_app.py
│   │   ├── setup_wizard.py
│   │   ├── message_classifier.py
│   │   ├── ollama_client.py
│   │   ├── vault_scanner.py
│   │   ├── file_writer.py
│   │   ├── process_inbox.py
│   │   ├── slack_client.py
│   │   ├── state.py
│   │   ├── notifications.py
│   │   ├── schema.py
│   │   ├── wikilinks.py
│   │   ├── fix_handler.py
│   │   ├── status_handler.py
│   │   ├── task_parser.py
│   │   └── domain_classifier.py
│   ├── tests/              # Test suite
│   ├── pyproject.toml      # Dependencies
│   └── uv.lock
├── scripts/                # Build scripts
│   ├── build_app.sh
│   ├── build_pkg.sh
│   ├── install_launchagent.sh
│   └── uninstall.sh
├── resources/              # Runtime resources
│   └── com.secondbrain.app.plist
├── dist/                   # Built app
│   └── Second Brain.app/
├── pkg/                    # Installer
│   └── SecondBrain-1.0.0.pkg
├── SecondBrain.spec        # PyInstaller spec
└── setup.py                # py2app config (unused)
```

### App Bundle Structure

```
Second Brain.app/
└── Contents/
    ├── Frameworks/         # Python + native libs
    ├── Info.plist          # Bundle metadata
    ├── MacOS/
    │   └── Second Brain    # Executable
    ├── Resources/          # Python modules
    └── _CodeSignature/
```

---

## Configuration

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `SLACK_BOT_TOKEN` | Yes | - | Slack bot token (xoxb-...) |
| `SLACK_CHANNEL_ID` | Yes | - | Inbox channel ID (C...) |
| `SLACK_USER_ID` | No | - | Your user ID (U...) |
| `OLLAMA_HOST` | No | `http://localhost:11434` | Ollama server URL |
| `OLLAMA_MODEL` | No | `llama3.2:latest` | Model for classification |
| `VAULT_PATH` | No | iCloud Obsidian Home | Obsidian vault path |
| `YOUTUBE_INGEST_ENABLED` | No | - | Enable YouTube dependency checks in health/menu bar |
| `CHECK_YOUTUBE_DEPS` | No | - | Alias to enable YouTube dependency checks |
| `YOUTUBE_TRANSCRIPT_MODE` | No | - | Expected transcript mode (whisper) for health checks |
| `OLLAMA_MODEL_SUMMARY` | No | - | Override model used for YouTube summarization |

### Info.plist Keys

```xml
<key>LSUIElement</key>
<true/>                     <!-- Hide from dock -->

<key>CFBundleIdentifier</key>
<string>com.secondbrain.app</string>
```

### LaunchAgent

```xml
<key>RunAtLoad</key>
<true/>                     <!-- Start on login -->

<key>KeepAlive</key>
<false/>                    <!-- Don't auto-restart -->
```

---

## Testing Strategy

### Test Pyramid

```
         ┌─────────────────┐
         │  Integration    │  17 tests
         │    Tests        │  (test_integration.py)
         └────────┬────────┘
                  │
    ┌─────────────┴─────────────┐
    │      Unit Tests           │  242 tests
    │  (test_*.py per module)   │
    └───────────────────────────┘
```

### Test Files

| File | Tests | Coverage |
|------|-------|----------|
| test_schema.py | Schema validation |
| test_state.py | State persistence |
| test_slack_client.py | Slack API |
| test_ollama_client.py | Ollama client |
| test_vault_scanner.py | Vault discovery |
| test_message_classifier.py | Classification |
| test_file_writer.py | File creation |
| test_process_inbox.py | Processing pipeline |
| test_menu_bar_app.py | UI core logic |
| test_notifications.py | macOS notifications |
| test_setup_wizard.py | Setup wizard |
| test_integration.py | Cross-module |

### Running Tests

```bash
# All tests
cd backend && uv run pytest -v

# Single module
uv run pytest tests/test_message_classifier.py -v

# With coverage
uv run pytest --cov=_scripts --cov-report=html
```

---

## Build System

### PyInstaller Build

```bash
./scripts/build_app.sh
```

Uses `SecondBrain.spec`:
- Entry point: `backend/_scripts/menu_bar_app.py`
- Hidden imports: All local modules listed explicitly
- Excludes: test, pytest
- Bundle type: macOS .app with `LSUIElement=True`

### Package Build

```bash
./scripts/build_pkg.sh
```

Uses `pkgbuild`:
- Root: `dist/` directory
- Install location: `/Applications`
- Identifier: `com.secondbrain.app`

### Dependencies

Managed with `uv` and `pyproject.toml`:
```toml
dependencies = [
    "rumps>=0.4.0",
    "ollama>=0.4.0",
    "requests>=2.31.0",
    "httpx>=0.27.0",
    "pyobjc-core>=10.0",
    "pyobjc-framework-Cocoa>=10.0",
    "pyinstaller>=6.0.0",
]
```

---

*Last updated: 2026-01-31 | Version: v1.0.0*
