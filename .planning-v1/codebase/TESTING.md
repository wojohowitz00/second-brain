# Testing Patterns

**Analysis Date:** 2026-01-30

## Test Framework

**Status:** No formal test framework detected

**Test Configuration Files:**
- None found
- No `pytest.ini`, `setup.cfg`, `tox.ini`, `pyproject.toml` test section
- No test dependencies in `pyproject.toml`

**Test Directory:**
- No `/tests` or `/test` directory
- No `__tests__` directory
- No test files (`*_test.py`, `test_*.py`, `*_spec.py`)

**Testing Strategy:**
This is a production script system without unit tests. Validation happens through:
1. Schema validation at runtime
2. Dead-letter queue logging for failures
3. Health check monitoring
4. Manual verification in Obsidian vault

## Validation as Testing

**Schema Validation (Primary Test Mechanism):**
Location: `backend/_scripts/schema.py`

**How it works:**
- `validate_classification()` performs runtime validation of AI classification responses
- Acts as a contract enforcement mechanism
- Prevents invalid data from reaching the Obsidian vault

**Validation Rules:**
```python
def validate_classification(data: dict) -> dict:
    """
    Validate a classification response from Claude.

    Validates:
    - destination: must be in {people, projects, ideas, admin}
    - confidence: number between 0.0 and 1.0 (clamped if outside range)
    - filename: converted to kebab-case, sanitized for path safety
    - extracted: must be dict (defaults to {})
    - linked_entities: list of {name, type} dicts, filters invalid
    """
```

**Sanitization Functions:**
Location: `backend/_scripts/schema.py`

Example: `sanitize_filename()` validates and transforms filenames:
```python
def sanitize_filename(filename: str) -> str:
    # Remove path traversal attempts: "../" -> "-"
    # Convert to lowercase
    # Replace spaces/underscores with hyphens
    # Remove invalid chars: [^a-z0-9-]
    # Collapse multiple hyphens
    # Strip leading/trailing hyphens
    # Limit to 100 chars
    # Return "untitled" if empty
```

This tests:
- Path safety (prevents ../../../etc/passwd attacks)
- Case normalization
- Filename validity for Obsidian
- Maximum path length

## Error Path Testing

**Dead-Letter Queue (Failure Logging):**
Location: `backend/_scripts/state.py` function `log_to_dead_letter()`

Acts as capture of error cases for manual review:
```python
def log_to_dead_letter(
    message_ts: str,
    message_text: str,
    error: str,
    error_type: str = "processing"
):
    """
    Log a failed message to the dead letter queue.
    Creates/appends to _inbox_log/FAILED-{date}.md
    """
```

**Error Types Captured:**
- Validation errors
- Processing exceptions
- Network failures (after retries exhausted)
- JSON parsing failures
- State corruption

**Location:** `~/SecondBrain/_inbox_log/FAILED-{YYYY-MM-DD}.md`

**Format:** Markdown with sections:
- Time
- Error type (uppercase)
- Message timestamp
- Original message text (first 200 chars)
- Full error traceback

**Example Usage from `process_inbox.py`:**
```python
try:
    raw_classification = classify_thought(text)
    classification = validate_classification(raw_classification)
except ValidationError as e:
    print(f"Validation error for message {ts}: {e}")
    classification = create_fallback_classification(text, error=str(e))

except Exception as e:
    import traceback
    error_details = traceback.format_exc()
    log_to_dead_letter(ts, text, error_details, error_type="processing")
    return False
```

## Fallback Testing

**Fallback Classification (Graceful Degradation):**
Location: `backend/_scripts/schema.py` function `create_fallback_classification()`

Tests system resilience by providing safe defaults:
```python
def create_fallback_classification(
    thought: str,
    error: Optional[str] = None
) -> dict:
    """
    Create a fallback classification when Claude's response is invalid.
    Defaults to 'ideas' category with low confidence (0.3) so user can review.
    """
    return {
        "destination": "ideas",
        "confidence": 0.3,
        "filename": sanitize_filename(filename) or "unclassified",
        "extracted": {
            "title": thought[:50] + ("..." if len(thought) > 50 else ""),
            "oneliner": "Auto-classified due to validation error",
            "_validation_error": error
        },
        "linked_entities": []
    }
```

**Tests:**
- Invalid JSON responses
- Missing required fields
- Malformed confidence values
- Path traversal attempts in filenames

**Recovery:** Files still created (won't crash), but marked for user review (confidence: 0.3)

## Network Resilience Testing

**Retry Logic (Implicit Testing):**
Location: `backend/_scripts/slack_client.py` function `_request_with_retry()`

Tests system behavior under network failure:
```python
def _request_with_retry(
    method: str,
    url: str,
    headers: dict,
    retries: int = MAX_RETRIES,
    **kwargs
) -> dict:
    """
    Make HTTP request with exponential backoff retry.
    Handles:
    - Network errors (retry)
    - 429 rate limits (wait and retry)
    - 5xx server errors (retry)
    - Slack API errors (raise)
    """
```

**Retry Configuration:**
- `MAX_RETRIES = 3`
- `INITIAL_BACKOFF = 1.0` seconds
- `MAX_BACKOFF = 30.0` seconds
- Exponential backoff: backoff * 2 up to max

**Tested Failure Modes:**
1. Network timeouts: `requests.exceptions.RequestException`
2. HTTP 429 (rate limit): Extract retry-after, sleep, retry
3. HTTP 5xx (server error): Exponential backoff retry
4. HTTP 4xx (client error): Fail fast, raise
5. Slack API error: Check `response["ok"]`, raise with details

**Example Exception Hierarchy:**
```python
class SlackAPIError(Exception):
    def __init__(self, error: str, response: dict = None):
        self.error = error
        self.response = response or {}
        super().__init__(f"Slack API error: {error}")

class SlackRateLimitError(SlackAPIError):
    def __init__(self, retry_after: int):
        self.retry_after = retry_after
        super().__init__(f"Rate limited. Retry after {retry_after}s")
```

## Idempotency Testing

**Processed Message Tracking (Prevents Duplicates):**
Location: `backend/_scripts/state.py`

Tests idempotency by tracking processed messages:
```python
def is_message_processed(message_ts: str) -> bool:
    """Check if a message has already been processed."""
    processed = _atomic_json_read(PROCESSED_MESSAGES_FILE)
    return message_ts in processed

def mark_message_processed(message_ts: str):
    """Mark a message as processed."""
    processed = _atomic_json_read(PROCESSED_MESSAGES_FILE)
    processed[message_ts] = datetime.now().isoformat()
    _atomic_json_write(PROCESSED_MESSAGES_FILE, processed)
```

**Usage from `process_inbox.py`:**
```python
if is_message_processed(ts):
    return True  # Already processed, skip

# ... do processing ...

mark_message_processed(ts)
```

**TTL Cleanup (Memory Test):**
```python
PROCESSED_MESSAGE_TTL_DAYS = 30

def cleanup_old_processed_messages():
    """Remove entries older than TTL to prevent unbounded growth."""
    processed = _atomic_json_read(PROCESSED_MESSAGES_FILE)
    cutoff = datetime.now() - timedelta(days=PROCESSED_MESSAGE_TTL_DAYS)
    # Remove old entries...
```

Called periodically to test that state doesn't grow unbounded.

## Atomic File Operations Testing

**File Locking & Atomic Writes (Concurrency Test):**
Location: `backend/_scripts/state.py`

Tests thread-safe concurrent access:
```python
def _atomic_json_read(filepath: Path) -> dict:
    """Read JSON file with locking."""
    with open(filepath, "r") as f:
        fcntl.flock(f.fileno(), fcntl.LOCK_SH)
        try:
            return json.load(f)
        finally:
            fcntl.flock(f.fileno(), fcntl.LOCK_UN)

def _atomic_json_write(filepath: Path, data: dict):
    """Write JSON file with locking."""
    temp_path = filepath.with_suffix(".tmp")
    with open(temp_path, "w") as f:
        fcntl.flock(f.fileno(), fcntl.LOCK_EX)
        try:
            json.dump(data, f, indent=2, default=str)
        finally:
            fcntl.flock(f.fileno(), fcntl.LOCK_UN)
    temp_path.rename(filepath)  # Atomic on POSIX
```

**Tests:**
- Readers don't block writers (`LOCK_SH` vs `LOCK_EX`)
- Writes are atomic (temp file then rename)
- No corruption if process crashes mid-write
- Concurrent cron jobs won't collide

## Health Monitoring (Operational Testing)

**Health Check Script:**
Location: `backend/_scripts/health_check.py`

Tests system operational status:
```python
def check_health(max_age_minutes: int = 60, alert: bool = True) -> tuple[bool, list[str]]:
    """
    Run all health checks.

    Checks:
    - Last run is recent (< 60 minutes)
    - Failure count today
    - State files readable
    """
```

**Checks Performed:**
1. `is_system_healthy()` - Last success < max_age_minutes
2. `get_failed_count_today()` - Count failed messages
3. `get_last_run_status()` - Can read state

**Usage:**
```bash
python health_check.py --max-age 60 --no-alert --quiet
```

## Validation Coverage

**What's Tested:**
- ✓ Classification response schema validation
- ✓ Filename path safety
- ✓ Network retry logic
- ✓ Idempotency (no duplicates)
- ✓ File atomicity
- ✓ Health monitoring
- ✓ Dead-letter error capture
- ✓ Fallback classifications

**What's NOT Tested:**
- ✗ Unit tests for individual functions
- ✗ Integration tests with real Slack API
- ✗ Integration tests with real Obsidian vault
- ✗ Claude API classification results
- ✗ Wikilink generation accuracy
- ✗ YAML frontmatter formatting
- ✗ Concurrent access under load

## Manual Verification Workflow

**User Verification Steps:**

1. **Inbox Log Review:** `_inbox_log/{YYYY-MM-DD}.md`
   - Table with: Time, Original text, Destination, Filename, Confidence
   - User scans for low-confidence entries

2. **Failed Messages Review:** `_inbox_log/FAILED-{YYYY-MM-DD}.md`
   - Appears only if processing failed
   - Contains full error traceback
   - User can manually process or retry

3. **Obsidian Vault Inspection:**
   - User opens vault and verifies files created
   - Checks frontmatter correctness
   - Verifies wikilinks are correct
   - Adjusts/refines for future runs

4. **Fix Command Workflow:**
   - User replies with `fix: destination` in Slack thread
   - `fix_handler.py` moves file to correct folder
   - Updates frontmatter and message mapping
   - User gets confirmation

## Testing Philosophy

This codebase follows a **runtime validation + manual inspection** approach:

- **No unit tests** because scripts are integration points (depend on external APIs)
- **Schema validation** prevents invalid data from reaching storage
- **Dead-letter queue** captures all error cases for manual review
- **Monitoring** via health checks and state tracking
- **Operator verification** via Obsidian vault inspection and fix commands

This is appropriate for:
- Small personal systems
- High trust in Claude API output
- Manual intervention acceptable
- Low failure rate expected

---

*Testing analysis: 2026-01-30*
