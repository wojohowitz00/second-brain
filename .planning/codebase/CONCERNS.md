# Codebase Concerns

**Analysis Date:** 2026-01-30

## Tech Debt

**Placeholder Claude API Integration:**
- Issue: `process_inbox.py`, `daily_digest.py`, and `weekly_review.py` contain stub functions that return placeholder classification/digest/review data instead of calling Claude API
- Files: `backend/_scripts/process_inbox.py` (line 83-98), `backend/_scripts/daily_digest.py` (line 90-120), `backend/_scripts/weekly_review.py` (line 82-114)
- Impact: System cannot actually classify incoming thoughts or generate AI-powered digests without these implementations; these scripts will only process fixed default values
- Fix approach: Implement actual Claude API calls using `anthropic` SDK. Replace `classify_thought()`, `generate_digest()`, and `generate_review()` with real API invocations. Consider adding prompt engineering and response streaming.

**File Extension in Wikilink Generation:**
- Issue: In `process_inbox.py` line 226, filename has `.md` stripped for wikilink creation, but this is fragile if filenames don't always end with `.md`
- Files: `backend/_scripts/process_inbox.py` (line 226), `backend/_scripts/fix_handler.py` (line 35)
- Impact: Wikilink creation could break if file naming conventions change
- Fix approach: Use `Path.stem` property consistently instead of string manipulation; standardize all filename handling through `Path` objects

**Loose Frontmatter Parsing:**
- Issue: Multiple scripts (state.py, fix_handler.py, wikilinks.py, daily_digest.py, weekly_review.py) manually parse YAML frontmatter by splitting on "---" without robust error handling
- Files: `backend/_scripts/state.py` (line 257-267), `backend/_scripts/fix_handler.py` (line 48-56), `backend/_scripts/wikilinks.py` (line 74-95), `backend/_scripts/daily_digest.py` (line 24-45), `backend/_scripts/weekly_review.py` (line 38-45)
- Impact: Malformed frontmatter (missing closing ---, extra ---, etc.) will cause silent parsing failures or index errors
- Fix approach: Create a centralized frontmatter parser utility in a new module that handles edge cases, validates structure, and logs parsing failures clearly

**Hardcoded Vault Path:**
- Issue: All scripts assume `VAULT_PATH = Path.home() / "SecondBrain"` with no configurability
- Files: `backend/_scripts/process_inbox.py` (line 36), `backend/_scripts/fix_handler.py` (line 19), `backend/_scripts/state.py` (line 225), and all other scripts
- Impact: System only works if vault is at exactly `~/SecondBrain`; cannot support alternative vault locations or test environments
- Fix approach: Move vault path to `.env` config file; read via `os.environ.get("VAULT_PATH", Path.home() / "SecondBrain")` with fallback

---

## Known Bugs

**Retry Loop State File Corruption:**
- Symptoms: In rare cases with concurrent writes, temporary `.tmp` files might not be cleaned up or might leave inconsistent state
- Files: `backend/_scripts/state.py` (line 42-55), `backend/_scripts/fix_handler.py` (line 46-67)
- Trigger: Simultaneous writes to state files from multiple cron jobs or manual invocations
- Root cause: File locking with `fcntl` is used but temp file cleanup on exception is not guaranteed; rename (line 55) could fail leaving `.tmp` files
- Workaround: Manually delete `.state/*.tmp` files if found
- Fix approach: Wrap `temp_path.rename()` in try/finally; implement cleanup method; consider atomic writes using `os.open()` with `O_EXCL` flag

**Missing Error File Logging:**
- Symptoms: Dead letter queue entries may not be created if `_inbox_log` directory is read-only or missing
- Files: `backend/_scripts/state.py` (line 228-274)
- Trigger: Manual deletion of `_inbox_log` directory between runs, or permission changes
- Workaround: Create directory manually: `mkdir -p ~/SecondBrain/_inbox_log`
- Fix approach: Add explicit error handling and automatic directory creation in `log_to_dead_letter()`; verify directory permissions at startup in health check

**Confidence Score Clamping Not Logged:**
- Symptoms: Classification confidence values outside 0-1 range are silently clamped without warning user
- Files: `backend/_scripts/schema.py` (line 80-82)
- Trigger: Claude returns invalid confidence value (e.g., 1.5 or -0.1)
- Impact: User unaware that classification may be degraded or unexpected
- Fix approach: Log warnings when clamping occurs; include in validation error message

---

## Security Considerations

**Slack Token Exposure Risk:**
- Risk: Bot token stored in plaintext `.env` file on filesystem
- Files: `backend/_scripts/.env` (via `slack_client.py` line 35)
- Current mitigation: README warns against committing `.env` to git; `.env` is in `.gitignore`
- Recommendations:
  - Encrypt `.env` file at rest (consider using `python-dotenv` with encryption or macOS Keychain)
  - Document that `.env` should have restrictive permissions: `chmod 600 ~/.SecondBrain/_scripts/.env`
  - Implement token rotation support (add ability to update token without script restart)
  - Add startup validation to warn if `.env` permissions are too loose

**Path Traversal in Filename Sanitization:**
- Risk: Although `schema.py` sanitizes filenames by removing "/" and "..", this only protects from some attack vectors
- Files: `backend/_scripts/schema.py` (line 129-131)
- Current mitigation: Path separators are replaced; ".." is stripped
- Recommendations:
  - Add explicit blocklist of dangerous patterns ("CON", "PRN", "AUX" on Windows)
  - Test with edge cases like "....", "//", "\\"
  - Consider using `pathlib.Path.is_relative_to()` to validate final path stays in vault

**Unvalidated External Wikilinks:**
- Risk: User-provided entity names from Slack are inserted directly into wikilinks with minimal sanitization
- Files: `backend/_scripts/wikilinks.py` (line 202-232)
- Current mitigation: File creation uses sanitized names; regex escaping in link replacement
- Recommendations:
  - Add whitelist of allowed characters in entity names before link generation
  - Log any names that required heavy sanitization for audit trail
  - Add option to require user confirmation for entities with special characters

---

## Performance Bottlenecks

**Inefficient Entity Search on Every Capture:**
- Problem: `find_existing_entity()` in wikilinks.py performs full directory scan and YAML parse of every file in the category folder every time a single message is processed
- Files: `backend/_scripts/wikilinks.py` (line 38-97), called from `process_inbox.py` line 115
- Cause: No caching or indexing; naive glob + read + parse for every entity lookup
- Scaling limit: System will slow dramatically when vault reaches thousands of files (e.g., >5000 people/project files)
- Improvement path:
  - Implement in-memory cache of entity names → file paths (rebuild on startup)
  - Add optional persistent cache file (`.entity_index.json`) updated incrementally
  - Consider full-text search library if vault grows large

**Daily and Weekly Review File I/O:**
- Problem: `gather_week_data()` and `gather_active_items()` read ALL files in multiple directories on each run
- Files: `backend/_scripts/daily_digest.py` (line 14-47), `backend/_scripts/weekly_review.py` (line 14-60)
- Cause: No filtering by date before reading; all files processed even if outside date range
- Scaling limit: Script time increases linearly with vault size
- Improvement path: Filter files by modification time before reading; parse only metadata fields needed; add caching

**Slack API Rate Limiting Not Adaptive:**
- Problem: Retry backoff uses fixed exponential delays; no awareness of actual rate limit window
- Files: `backend/_scripts/slack_client.py` (line 49-116)
- Cause: `Retry-After` header is read but backoff state is not adjusted based on actual rate limit pressure
- Scaling limit: With frequent cron runs + high message volume, rate limiting failures will cascade
- Improvement path: Track rate limit window expiry; implement token bucket algorithm; queue requests if approaching limit

---

## Fragile Areas

**Message Timestamp Ordering Dependency:**
- Files: `backend/_scripts/process_inbox.py` (line 337), `backend/_scripts/fix_handler.py` (line 85-131)
- Why fragile: Code assumes messages are returned in timestamp order from Slack and reverses list (line 337). If Slack changes ordering or pagination, FIFO processing breaks.
- Safe modification: Store explicit sort order; don't rely on API ordering guarantees
- Test coverage gaps: No tests for out-of-order message processing

**State File Format Assumptions:**
- Files: `backend/_scripts/state.py` (entire file), `backend/_scripts/fix_handler.py` (line 46-67)
- Why fragile: Code assumes JSON state files always have specific structure; adding new fields or migrating format would require careful updates across all references
- Safe modification: Add migration layer; validate state structure on read with clear error messages for schema mismatches
- Test coverage gaps: No migration tests; no schema validation tests

**Frontmatter Type Mapping Magic:**
- Files: `backend/_scripts/fix_handler.py` (line 74-82), `backend/_scripts/process_inbox.py` (line 118-156)
- Why fragile: Type-to-destination mappings (people→person, projects→project) are hardcoded in multiple places; inconsistencies between `_get_type_for_destination()` in fix_handler vs frontmatter generation in process_inbox
- Safe modification: Centralize type mapping in schema module; reference single source of truth
- Test coverage gaps: No tests for type mapping consistency; no round-trip tests (write → fix → verify type)

---

## Test Coverage Gaps

**No Unit Tests for Core Functions:**
- What's not tested: Classification validation (`schema.py`), state management atomic operations, wikilink generation, frontmatter parsing
- Files: `backend/_scripts/schema.py`, `backend/_scripts/state.py`, `backend/_scripts/wikilinks.py`
- Risk: High-risk areas (validation, state, data generation) have zero test coverage; bugs go undetected until production
- Priority: High - these are the most critical functions

**No Integration Tests:**
- What's not tested: End-to-end flow (fetch message → classify → write file → update state); fix command flow; concurrent processing
- Files: All of `backend/_scripts/`
- Risk: Individual functions may pass tests but fail when combined; race conditions in concurrent cron execution undetected
- Priority: High

**No Error Scenario Tests:**
- What's not tested: Slack API failures, malformed JSON responses, file I/O errors, missing state files, corrupted vault
- Files: `backend/_scripts/slack_client.py`, `backend/_scripts/process_inbox.py`
- Risk: Error handling code is untested; failures in production are unpredictable
- Priority: Medium

---

## Missing Critical Features

**Duplicate Message Detection:**
- Problem: If Slack API returns duplicate messages (edge case) or processing is retried, system will create duplicate files with different timestamps
- Current workaround: Message timestamp tracking prevents re-processing, but doesn't prevent Slack API returning same message twice
- Recommendation: Add deduplication by content hash; implement "last message ts" not just "last processed ts"

**Message Deletion Handling:**
- Problem: If user deletes a message in Slack after it's been processed, system has no way to delete or mark the corresponding file
- Current state: Deleted messages are orphaned in the vault indefinitely
- Recommendation: Implement optional sync that checks if original messages still exist in Slack

**Confidence-Based Review Queue:**
- Problem: Low-confidence classifications (< 0.6) are flagged but require manual review; no systematic review workflow
- Current state: User must manually check daily logs and correct
- Recommendation: Create "pending_review" category or tag for easy filtering; add weekly summary of items pending review

**Handling of Multi-Message Threads:**
- Problem: If user replies in thread instead of posting to channel, system doesn't capture it
- Current limitation: Only processes channel-level messages, not thread replies
- Recommendation: Implement thread processing option; handle nested classifications

---

## Dependencies at Risk

**No Specified Python Version Constraint:**
- Risk: `pyproject.toml` requires `python >= 3.9` but doesn't pin; code uses Python 3.9+ syntax that may break on newer versions
- Files: `backend/pyproject.toml` (line 6)
- Current mitigation: Setup script checks for Python 3.9+
- Recommendation: Test and pin to specific Python version (e.g., `>=3.9,<4.0` or `>=3.13,<3.14`); add CI testing

**Minimal Dependency Set (Strength & Risk):**
- Current dependencies: only `requests` and `pyyaml`
- Strength: Small dependency tree reduces supply chain risk
- Risk: No alternative if `requests` or `pyyaml` have critical security issues; no built-in testing framework or linting
- Recommendation: Add optional dev dependencies for testing (`pytest`, `pytest-cov`) and linting (`ruff`, `mypy`)

**Slack API Python SDK Not Used:**
- Risk: Custom HTTP wrapper (`slack_client.py`) reimplements rate limiting and retries; could diverge from official `slack-sdk` best practices
- Current state: Using `requests` directly with custom retry logic
- Consideration: Official SDK is more maintained but adds dependency; current approach is lightweight
- Recommendation: If moving to official SDK, audit changes to retry and error handling carefully

---

## Scaling Limits

**Processed Messages TTL Only 30 Days:**
- Current limit: Processed message entries cleaned up after 30 days (PROCESSED_MESSAGE_TTL_DAYS)
- Problem: After 30 days, a message could be processed again if Slack returns it (unlikely but possible edge case)
- Files: `backend/_scripts/state.py` (line 109, 135-148)
- Scaling consideration: After 1 year, system could potentially have issues with very old backlog
- Recommendation: Consider longer TTL (90-180 days) or persistent dedupe based on content hash instead of timestamp

**No Pagination for Large File Lists:**
- Problem: Reading all files in a category with `glob("*.md")` will slow down for >10k files
- Files: `backend/_scripts/daily_digest.py`, `backend/_scripts/weekly_review.py`, `backend/_scripts/wikilinks.py`
- Current limit: System usable up to ~5k files per category, then response time degrades
- Scaling path: Implement directory sharding (e.g., `people/a-c/`, `people/d-f/`) or use database instead of file system

**No Vault Compression/Archival:**
- Problem: Vault grows indefinitely; old captures and stubs accumulate
- Files: All of `backend/_scripts/`
- Current mitigation: None
- Recommendation: Add archival script to move old files to archive folder; implement periodic cleanup

---

## Missing Documentation

**No API Contract Documentation:**
- Missing: Schema documentation for classification response format, state file structure, and frontmatter requirements
- Impact: Future modifications risky; no reference for expected data structure
- Recommendation: Document in `backend/_scripts/SCHEMA.md` or docstrings

**No Testing Guide:**
- Missing: How to run tests, what manual testing is needed, edge cases to test
- Impact: Hard for future contributors to ensure changes work
- Recommendation: Add `TESTING.md` in backend directory with manual test procedures

---

*Concerns audit: 2026-01-30*
