# Phase 6: Processing Integration - Research

**Researched:** 2026-01-31
**Domain:** Python scripting, file I/O, polling patterns, integration testing
**Confidence:** HIGH

## Summary

Phase 6 integrates all existing modules (Slack client, classifier, vault scanner, state management) into a processing pipeline that fetches messages, classifies them, and creates .md files in the correct vault location. The research identifies that this is a **simple integration phase** requiring minimal new code - primarily wiring together tested components with a straightforward polling loop.

The standard approach is a **simple while-True loop with time.sleep(120)** for the 2-minute polling, **pathlib for file creation**, and **manual frontmatter string building** (avoiding library dependencies for trivial YAML). The existing codebase already demonstrates the correct patterns: `process_inbox.py` contains most of the logic but needs updating to integrate the new multi-level classifier and write files to the new PARA structure.

**Primary recommendation:** Refactor `process_inbox.py` to use MessageClassifier, write files with domain/PARA/subject paths, and add frontmatter fields. Use simple patterns - no async, no APScheduler, no external frontmatter library. Integration tests should verify end-to-end flow from Slack message to vault file.

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| pathlib | stdlib | File/directory operations | Built-in, cross-platform, modern Python standard |
| time.sleep() | stdlib | Polling interval | Simple, reliable, no dependencies |
| json | stdlib | State file operations | Already used in state.py for atomic writes |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| python-frontmatter | 1.1.0 | YAML frontmatter parsing | Only if complex metadata needs emerge (NOT needed for Phase 6) |
| APScheduler | 3.x | Advanced scheduling | Only for complex multi-job scheduling (NOT needed for Phase 6) |
| atomicwrites | 1.4.0 | Atomic file writes | Only if concurrent writes become a concern (NOT needed for Phase 6) |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| time.sleep() | APScheduler | APScheduler adds complexity for single 2-minute interval; sleep() is sufficient |
| Manual YAML | python-frontmatter | Library overhead for trivial YAML generation; manual strings are clearer |
| pathlib | os.path | pathlib is modern standard, more readable, already used in codebase |

**Installation:**
No new dependencies needed - Phase 6 uses only stdlib and existing dependencies.

## Architecture Patterns

### Recommended Project Structure
```
_scripts/
├── process_inbox.py     # Main processing loop (REFACTOR)
├── file_writer.py       # NEW: Create .md files with frontmatter
├── slack_client.py      # Existing: Fetch messages
├── message_classifier.py # Existing: 4-level classification
├── vault_scanner.py     # Existing: Get vocabulary
├── state.py             # Existing: Track processed messages
└── .state/
    ├── processed_messages.json
    ├── message_mapping.json
    └── last_run.json
```

### Pattern 1: Startup Backlog Processing
**What:** Process all messages since last run on startup
**When to use:** Every script execution (cron/systemd timer)
**Example:**
```python
# Source: Existing process_inbox.py pattern
def fetch_new_messages():
    """Get messages since last processed timestamp."""
    last_ts = LAST_TS_FILE.read_text().strip() if LAST_TS_FILE.exists() else "0"
    return fetch_messages(oldest=last_ts)

# Process oldest first to maintain chronological order
for msg in reversed(messages):
    process_message(msg)
```

### Pattern 2: Simple Polling Loop
**What:** While-True loop with sleep for periodic execution
**When to use:** When script runs continuously (not via cron)
**Example:**
```python
# Source: APScheduler best practices (simplified for single interval)
import time

def main():
    while True:
        try:
            process_all()  # Process backlog since last run
        except Exception as e:
            print(f"Error: {e}")
        time.sleep(120)  # 2 minutes

if __name__ == "__main__":
    main()
```

### Pattern 3: File Creation with Frontmatter
**What:** Create .md files with YAML frontmatter and body
**When to use:** Every classified message
**Example:**
```python
# Source: Python pathlib best practices + existing process_inbox.py pattern
from pathlib import Path

def create_note_file(classification: ClassificationResult, message: str, vault_path: Path):
    # Build file path: domain/PARA/subject/
    folder = vault_path / classification.domain / classification.para_type / classification.subject
    folder.mkdir(parents=True, exist_ok=True)

    # Generate filename (timestamped to avoid collisions)
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    filename = f"{timestamp}-{sanitize(message[:30])}.md"
    filepath = folder / filename

    # Build frontmatter (manual YAML for simplicity)
    frontmatter = f"""---
domain: {classification.domain}
para_type: {classification.para_type}
subject: {classification.subject}
category: {classification.category}
confidence: {classification.confidence}
created: {datetime.now().isoformat()}
---

## Original Capture

{message}

## Classification Reasoning

{classification.reasoning}
"""

    filepath.write_text(frontmatter)
    return filepath
```

### Pattern 4: Integration Testing End-to-End
**What:** Test full pipeline from Slack message to vault file
**When to use:** Phase 6 validation
**Example:**
```python
# Source: pytest integration testing best practices
import pytest
from pathlib import Path

def test_slack_to_vault_integration(tmp_path):
    """Test complete flow: Slack message → classification → file creation."""
    # Setup
    vault_path = tmp_path / "vault"
    mock_message = {"text": "Meeting notes from CCBH client sync", "ts": "1234567890.123456"}

    # Execute
    classifier = MessageClassifier()
    result = classifier.classify(mock_message["text"])
    filepath = create_note_file(result, mock_message["text"], vault_path)

    # Verify
    assert filepath.exists()
    content = filepath.read_text()
    assert "domain: CCBH" in content  # Frontmatter
    assert "Meeting notes" in content  # Body
    assert filepath.parent.name == result.subject  # Correct folder structure
```

### Anti-Patterns to Avoid
- **Asyncio for simple polling:** Adds complexity without benefit for single 2-minute interval
- **External frontmatter library for trivial YAML:** Overkill for simple key-value pairs
- **Complex scheduling:** APScheduler unnecessary for single-interval polling
- **Non-atomic writes without locks:** Already solved in state.py, don't duplicate pattern incorrectly

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| File locking | Custom lock files | fcntl.flock() (already in state.py) | Race conditions, platform-specific edge cases |
| Message deduplication | Custom tracking | state.py is_message_processed() | Already implemented, tested, atomic |
| Slack pagination | Manual cursor handling | slack_client.py fetch_messages() | Already handles rate limits, retries |
| Classification | Prompt engineering inline | message_classifier.py | Already tested, validated, handles fallbacks |
| Vocabulary | Hardcoded lists | vault_scanner.py get_vocabulary() | Already scans vault, caches results |

**Key insight:** Phase 6 is primarily **integration** - the hard parts (classification, state, Slack API) are already solved. Avoid rebuilding existing components.

## Common Pitfalls

### Pitfall 1: Overengineering the Polling Loop
**What goes wrong:** Using async/APScheduler/threads for simple 2-minute polling
**Why it happens:** Assuming "production" requires complex scheduling frameworks
**How to avoid:** Use `while True: ... time.sleep(120)` - simple, debuggable, sufficient
**Warning signs:** Import statements for asyncio, apscheduler, threading in process_inbox.py

### Pitfall 2: Non-Idempotent Processing
**What goes wrong:** Processing the same message multiple times creates duplicate files
**Why it happens:** Not checking `is_message_processed()` before classification
**How to avoid:** Always check state before processing: `if is_message_processed(ts): continue`
**Warning signs:** Duplicate files in vault with same content

### Pitfall 3: File Path Construction Errors
**What goes wrong:** Files created in wrong location (e.g., `Personal/general` instead of `Personal/1_Projects/general`)
**Why it happens:** Missing PARA type in path, incorrect Path joining
**How to avoid:** Use pattern: `vault_path / domain / para_type / subject`
**Warning signs:** Files appearing in domain root instead of PARA subfolders

### Pitfall 4: Frontmatter Format Errors
**What goes wrong:** Invalid YAML breaks Obsidian parsing
**Why it happens:** Unquoted strings with colons, missing delimiters
**How to avoid:** Use triple-dashes `---`, quote values with special chars, test with actual Obsidian
**Warning signs:** Files not rendering in Obsidian, frontmatter appearing as body text

### Pitfall 5: No Graceful Shutdown
**What goes wrong:** Processing interrupted mid-message, state corrupted
**Why it happens:** No SIGTERM handling in while-True loop
**How to avoid:** Add signal handler to set flag, check flag in loop
**Warning signs:** Partial files, state.json corruption after Ctrl-C

### Pitfall 6: Hardcoded Vault Path
**What goes wrong:** Tests fail, script not portable
**Why it happens:** Path hardcoded instead of configurable
**How to avoid:** Use environment variable or config file for VAULT_PATH
**Warning signs:** Tests can't run in tmp_path, breaking on different systems

## Code Examples

Verified patterns from official sources:

### Creating Directories with Parents
```python
# Source: https://docs.python.org/3/library/pathlib.html
from pathlib import Path

# Create nested directories safely
Path("/my/nested/directory").mkdir(parents=True, exist_ok=True)

# For vault files
file_path = vault_path / domain / para_type / subject
file_path.mkdir(parents=True, exist_ok=True)
```

### Simple Polling Loop with Error Handling
```python
# Source: APScheduler patterns (simplified for single interval)
import time
import signal
import sys

# Flag for graceful shutdown
shutdown_flag = False

def signal_handler(sig, frame):
    global shutdown_flag
    print("Shutdown signal received, finishing current cycle...")
    shutdown_flag = True

signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)

def main():
    while not shutdown_flag:
        try:
            process_all()
        except Exception as e:
            print(f"Error in processing: {e}")
            # Log error but continue

        # Sleep in small increments to check shutdown flag
        for _ in range(120):  # 120 seconds = 2 minutes
            if shutdown_flag:
                break
            time.sleep(1)

    print("Graceful shutdown complete")

if __name__ == "__main__":
    main()
```

### Manual YAML Frontmatter Generation
```python
# Source: Existing process_inbox.py pattern + YAML best practices
from datetime import datetime

def build_frontmatter(classification, timestamp):
    """Build YAML frontmatter for Obsidian note."""
    # Use safe YAML formatting
    return f"""---
domain: {classification.domain}
para_type: {classification.para_type}
subject: {classification.subject}
category: {classification.category}
confidence: {classification.confidence:.2f}
created: {timestamp}
tags: []
---
"""

# Full file creation
def create_note(classification, message_text, timestamp):
    frontmatter = build_frontmatter(classification, timestamp)
    body = f"""## Original Capture

{message_text}

## Classification

- **Reasoning:** {classification.reasoning}
- **Confidence:** {classification.confidence:.0%}
"""
    return frontmatter + "\n" + body
```

### Integration Test Pattern
```python
# Source: pytest integration testing best practices
import pytest
from pathlib import Path

@pytest.fixture
def temp_vault(tmp_path):
    """Create temporary vault structure for testing."""
    vault = tmp_path / "vault"
    # Pre-create domain/PARA structure
    (vault / "Personal" / "1_Projects" / "apps").mkdir(parents=True)
    return vault

def test_end_to_end_processing(temp_vault):
    """Test complete Slack → classify → file flow."""
    # Given: A Slack message
    message = {
        "text": "Working on the second-brain app integration",
        "ts": "1234567890.123456"
    }

    # When: Process the message
    classifier = MessageClassifier()
    result = classifier.classify(message["text"])
    filepath = create_note_file(result, message["text"], temp_vault)

    # Then: File created with correct structure
    assert filepath.exists()
    assert filepath.parent.name == result.subject
    assert result.domain in str(filepath)
    assert result.para_type in str(filepath)

    # And: Frontmatter is valid
    content = filepath.read_text()
    assert content.startswith("---")
    assert f"domain: {result.domain}" in content
    assert "Working on the second-brain" in content
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| os.path | pathlib | Python 3.4+ | Cleaner, cross-platform, object-oriented |
| Cron only | Systemd timers preferred | ~2015 | Better logging, dependency management, persistence |
| Custom YAML parsing | python-frontmatter | 2020+ | But manual YAML still valid for simple cases |
| Blocking schedulers | APScheduler BackgroundScheduler | 2018+ | But overkill for single-interval polling |

**Deprecated/outdated:**
- `os.makedirs()`: Use `pathlib.Path.mkdir(parents=True, exist_ok=True)` instead
- `open().read()`: Use `Path.read_text()` for simplicity
- Cron without persistence: Use systemd timers with `Persistent=true` for missed runs

## Open Questions

Things that couldn't be fully resolved:

1. **Should process_inbox.py run continuously or via cron?**
   - What we know: README shows cron setup (`*/2 * * * *`), but code has potential for while-loop
   - What's unclear: User preference for deployment model
   - Recommendation: Start with cron (simpler, already documented), add while-loop option if requested

2. **Should files have unique names or allow overwrites?**
   - What we know: Existing code uses timestamp suffixes to prevent overwriting
   - What's unclear: Whether same message content should merge or create new file
   - Recommendation: Keep timestamp-based unique names (safer, preserves history)

3. **Frontmatter: Manual strings vs python-frontmatter library?**
   - What we know: Manual YAML is 3-4 lines of code, library is external dependency
   - What's unclear: Future complexity of frontmatter fields
   - Recommendation: Start manual (YAGNI), migrate to library only if >10 fields emerge

## Sources

### Primary (HIGH confidence)
- [Python pathlib — Object-oriented filesystem paths](https://docs.python.org/3/library/pathlib.html)
- [Python Frontmatter Documentation](https://github.com/eyeseast/python-frontmatter/blob/main/docs/index.md) - Context7: /eyeseast/python-frontmatter
- [Existing codebase patterns](file:///Users/richardyu/PARA/Personal/1_Projects/apps/second-brain/backend/_scripts/) - process_inbox.py, state.py, message_classifier.py

### Secondary (MEDIUM confidence)
- [Cron vs. Systemd Timers: Which Scheduler Should You Use in 2026?](https://crongen.com/blog/cron-vs-systemd-timers-2026) - Deployment options
- [Python's pathlib Module: Taming the File System – Real Python](https://realpython.com/python-pathlib/) - Best practices
- [Job Scheduling in Python with APScheduler | Better Stack Community](https://betterstack.com/community/guides/scaling-python/apscheduler-scheduled-tasks/) - Scheduling patterns (not needed, but researched)
- [End-to-End Python Integration Testing: A Complete Guide](https://www.testmu.ai/learning-hub/python-integration-testing/) - Testing strategy
- [Good Integration Practices - pytest documentation](https://docs.pytest.org/en/stable/explanation/goodpractices.html) - Test organization

### Tertiary (LOW confidence)
- [Python HTTP Requests: Implementing Long Polling](https://apipark.com/techblog/en/python-http-requests-implementing-long-polling/) - Not applicable (we use simple polling, not long polling)
- [Atomic writes to files - Python.org Discussions](https://discuss.python.org/t/atomic-writes-to-files/24374) - Already solved in state.py

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - stdlib patterns, existing codebase demonstrates correct approach
- Architecture: HIGH - Simple integration of tested components, no novel patterns needed
- Pitfalls: HIGH - Derived from existing code review and common integration mistakes

**Research date:** 2026-01-31
**Valid until:** 2026-03-31 (60 days - stable patterns, minimal ecosystem churn)
