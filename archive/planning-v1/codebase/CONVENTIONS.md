# Coding Conventions

**Analysis Date:** 2026-01-30

## Language & Environment

**Primary Language:** Python 3.9+

**Package Manager:** uv (modern Python package manager)

**Entry Point Style:** All scripts use `if __name__ == "__main__":` guard pattern for CLI execution.

## Naming Patterns

**Files:**
- `snake_case.py` for all Python modules
- Descriptive names: `slack_client.py`, `process_inbox.py`, `state.py`
- Scripts in `backend/_scripts/` directory

**Functions:**
- `snake_case` for all function names
- Verb-first naming for actions: `fetch_messages()`, `validate_classification()`, `process_linked_entities()`
- Single-letter names (e.g., `f`, `k`, `v`) used in loops and comprehensions
- Example from `state.py`: `_atomic_json_read()`, `mark_message_processed()`, `cleanup_old_processed_messages()`

**Variables:**
- `snake_case` for variables and parameters
- All lowercase for constants stored in uppercase: `MAX_RETRIES`, `PROCESSED_MESSAGE_TTL_DAYS`, `VAULT_PATH`
- Descriptive names over abbreviations: `processed_messages` not `pm`
- Prefixes used for clarity: `fm` for frontmatter, `ts` for timestamp

**Type Hints:**
- Type hints used throughout: `Optional[Path]`, `dict`, `list`, `tuple`
- Return types documented: `-> dict`, `-> bool`, `-> tuple[bool, str]`
- Imports from `typing` module for advanced types

**Classes:**
- Custom exception classes inherit from `Exception`
- Example: `class ValidationError(Exception)` in `schema.py`
- Example: `class SlackAPIError(Exception)` in `slack_client.py`

## Code Style

**Formatting:**
- PEP 8 compliant (120 character line width observed in practice)
- 4-space indentation
- Consistent blank lines between functions and sections

**Imports:**
- Standard library imports first
- Third-party imports second (requests, yaml, pyyaml)
- Local module imports last
- Example from `process_inbox.py`:
  ```python
  import os
  import json
  from datetime import datetime
  from pathlib import Path

  from slack_client import fetch_messages, reply_to_message, send_dm
  from state import set_file_for_message, is_message_processed
  from schema import validate_classification, create_fallback_classification, ValidationError
  ```

**Linting/Formatting:**
- No automated linter configuration found (eslintrc, prettier, black config)
- Manual formatting follows PEP 8

## Error Handling

**Pattern: Custom Exception Hierarchy**
- `SlackAPIError`: Base exception for Slack API failures
- `SlackRateLimitError(SlackAPIError)`: Specialized rate limit handling
- `ValidationError(Exception)`: Schema validation failures
- Located in: `slack_client.py`, `schema.py`

**Pattern: Fallback Defaults**
- Validation functions return sanitized defaults rather than failing
- Example from `schema.py`: If `confidence` is missing, default to 0.5; if invalid, clamp to [0,1]
- Example from `schema.py`: Invalid filenames sanitized to kebab-case
- `create_fallback_classification()` in `schema.py` provides low-confidence catchall for invalid inputs

**Pattern: Try-Except with Context**
- Broad exception catching in main loops to prevent script crashes
- Error details logged via `log_to_dead_letter()` in `state.py`
- Example from `process_inbox.py`:
  ```python
  try:
      raw_classification = classify_thought(text)
      classification = validate_classification(raw_classification)
  except ValidationError as e:
      print(f"Validation error for message {ts}: {e}")
      classification = create_fallback_classification(text, error=str(e))
  ```

**Pattern: Graceful Degradation**
- Network failures trigger exponential backoff retry in `_request_with_retry()` in `slack_client.py`
- Max 3 retries with backoff from 1s to 30s
- Low-confidence classifications trigger review workflow instead of failure
- Missing state files default to empty dict in `_atomic_json_read()` in `state.py`

**Pattern: Atomic File Operations**
- State files written to temp file, then renamed (atomic POSIX rename)
- File locking with `fcntl` for concurrent access
- Example from `state.py`: `_atomic_json_write()` writes to `.tmp` before rename

## Logging & Observability

**Logging:**
- `print()` statements used for CLI output (no logging framework detected)
- Error messages include context: message timestamps, operation type, error details
- Example from `slack_client.py`: `print(f"Slack API error: {error}")`
- Structured output in main scripts: counters, status messages
- Example from `process_inbox.py`: `print(f"Processed {processed_count} messages, {failed_count} failures")`

**Dead Letter Queue:**
- Failed messages logged to `_inbox_log/FAILED-{date}.md` in Obsidian vault
- Function: `log_to_dead_letter()` in `state.py`
- Captures: timestamp, original text, error traceback, error type
- Used for manual recovery and debugging

**Health Checks:**
- System state tracked in JSON files: `message_mapping.json`, `processed_messages.json`, `last_run.json`
- Location: `backend/_scripts/.state/`
- Health check script: `health_check.py` verifies run freshness and failure count

## Comments & Docstrings

**Module-Level:**
- Every Python file starts with docstring describing purpose and responsibilities
- Example from `state.py`:
  ```python
  """
  State management for Second Brain processing.

  Handles:
  - Message-to-file mapping (which Slack message created which file)
  - Processed message tracking (idempotency)
  - Last successful run tracking (health checks)
  """
  ```

**Function-Level:**
- Google-style docstrings with Args, Returns sections
- Example from `state.py`:
  ```python
  def is_system_healthy(max_age_minutes: int = 60) -> tuple[bool, str]:
      """
      Check if the system is healthy.

      Args:
          max_age_minutes: Maximum age of last successful run

      Returns:
          Tuple of (is_healthy, message)
      """
  ```

**Inline Comments:**
- Used sparingly for non-obvious logic
- Reason-based: explain *why*, not *what*
- Example from `wikilinks.py`: `# Sort by length (longest first) to handle overlapping names`
- Example from `schema.py`: `# Clamp to valid range rather than reject`

**Section Headers:**
- `# --- Section Name ---` format for logical grouping within files
- Example from `state.py`: `# --- Message-to-File Mapping ---`, `# --- Dead Letter Queue ---`

## Data Structures

**Dictionaries:**
- Used extensively for JSON serialization and schema validation
- Keys always strings, values typed
- Frontmatter format: YAML-style dicts with typed values
- Example classification dict structure:
  ```python
  {
      "destination": "people",  # Required: enum string
      "confidence": 0.85,       # Required: 0.0-1.0
      "filename": "john-smith",  # Required: kebab-case string
      "extracted": {...},       # Required: dict with type-specific fields
      "linked_entities": [...]   # Required: list of {name, type} dicts
  }
  ```

**Type Conversions:**
- Timestamps: strings in ISO format (stored) <-> float for calculations
- File paths: `Path` objects from `pathlib` (never strings)
- YAML frontmatter: parsed with `yaml.safe_load()`, written manually (no yaml.dump)

## Module Organization

**Horizontal Layers (separation of concerns):**

1. **API Layer:** `slack_client.py`
   - All external API calls isolated here
   - Retry logic centralized
   - Token/credential management
   - Custom exception classes

2. **Data Layer:** `state.py`
   - Persistence logic (file read/write)
   - Atomic operations and locking
   - State tracking and health checks

3. **Domain Layer:** `schema.py`, `wikilinks.py`
   - Business rules (classification validation, entity linking)
   - Domain-specific transformations

4. **Orchestration Layer:** `process_inbox.py`, `fix_handler.py`, `daily_digest.py`, `health_check.py`
   - Main business logic
   - Coordinates between layers
   - Error handling and dead-letter queues

**Exports & Public API:**
- All modules export functions (no classes except exceptions)
- No `__all__` declarations found
- Modules imported with `from module import function` pattern

## Constants & Configuration

**Constants Location:**
- File-path constants at module level: `VAULT_PATH = Path.home() / "SecondBrain"`
- Magic numbers extracted: `MAX_RETRIES = 3`, `INITIAL_BACKOFF = 1.0`, `PROCESSED_MESSAGE_TTL_DAYS = 30`
- Validation enums: `VALID_DESTINATIONS = {"people", "projects", "ideas", "admin"}`
- Located near top of file after imports

**Environment Variables:**
- Read via `os.environ.get()` at function level
- Variables: `SLACK_BOT_TOKEN`, `SLACK_CHANNEL_ID`, `SLACK_USER_ID`
- Validation on read: raises `ValueError` if required vars missing
- Example from `slack_client.py`:
  ```python
  def _get_token() -> str:
      token = os.environ.get("SLACK_BOT_TOKEN")
      if not token:
          raise ValueError("SLACK_BOT_TOKEN environment variable not set")
      return token
  ```

## Testing Approach

**No Test Framework Found:**
- No `pytest.ini`, `setup.cfg`, or `pyproject.toml` test configuration
- No `tests/` directory
- No test files (`*_test.py`, `test_*.py`)

**Manual Testing Strategy:**
- Scripts execute via cron/schedule or Claude Code invocation
- Dead letter queue serves as failure log for manual review
- Health checks provide runtime validation
- Schema validation prevents crashes from malformed input

## File Structure Conventions

**Script Organization:**
- All scripts in `backend/_scripts/` directory
- Each script is standalone executable: `#!/usr/bin/env python3` shebang
- Can be invoked directly or imported by other scripts
- Related imports grouped at top

**State Files:**
- Location: `backend/_scripts/.state/`
- Format: JSON with atomic write pattern
- Naming: `{entity}_mapping.json`, `processed_messages.json`, `last_run.json`

**Vault Structure:**
- Root: `~/SecondBrain/`
- Subdirectories: `people/`, `projects/`, `ideas/`, `admin/`, `daily/`, `_inbox_log/`, `_scripts/.state/`
- Files: Markdown with YAML frontmatter
- Log files: Daily files named `{YYYY-MM-DD}.md` in `_inbox_log/`

---

*Convention analysis: 2026-01-30*
