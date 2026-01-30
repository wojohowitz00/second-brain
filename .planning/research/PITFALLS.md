# Common Pitfalls: macOS Packaging + Ollama Integration

**Research Date:** 2026-01-30
**Project:** Second Brain - macOS .pkg installer with Ollama classification

## Overview

This document identifies domain-specific pitfalls when packaging Python apps for macOS distribution and integrating Ollama for local LLM classification. Each pitfall includes warning signs for early detection, prevention strategies, and recommended phases for addressing them.

---

## 1. macOS Python App Packaging Pitfalls

### 1.1 Dependency Bundling Hell

**What goes wrong:**
Projects assume PyInstaller/py2app will "just work" and bundle all dependencies correctly. In reality:
- Native extensions (compiled .so files) get missed or corrupted
- Dynamic imports fail because the bundler can't trace them statically
- System libraries conflict with bundled versions (especially OpenSSL, libffi)
- uv-managed dependencies may not be recognized by PyInstaller's hooks

**Warning signs:**
- App works in development but crashes on launch after bundling
- Import errors for modules that are definitely installed
- Segfaults or dyld library loading errors
- "ModuleNotFoundError" for pyyaml, requests, or other C-extension libraries

**Prevention strategies:**
1. Test bundling early (don't wait until the end)
2. Use PyInstaller's `--hidden-import` for dynamic imports (like pydantic validators)
3. Create custom .spec file to explicitly include data files and dependencies
4. Test on clean macOS without development tools installed
5. Use `--onefile` cautiously - it's slower and more prone to extraction issues

**Phase to address:** Infrastructure Setup (Phase 1)
- Create test bundle script early
- Document bundling process in UV_USAGE.md
- Test on non-development Mac if available

**Project-specific concern:**
- `uv` creates isolated environments that PyInstaller may not discover automatically
- State files in `~/SecondBrain/_scripts/.state/` need explicit path handling (not relative to bundle)
- Cron scripts won't work from bundled app - need LaunchAgent approach instead

---

### 1.2 Code Signing and Notarization Misunderstandings

**What goes wrong:**
Developers think codesigning is "just run `codesign -s`" and notarization is optional. Reality:
- macOS 10.15+ enforces notarization for downloaded apps (Gatekeeper)
- Unsigned apps trigger scary warnings users won't bypass
- Signing must happen at every nesting level (frameworks, dylibs, main executable)
- Ad-hoc signing (`-`) won't work for distribution
- Notarization requires Apple Developer account ($99/year)
- Hardened runtime requirements break some Python behaviors (like fork())

**Warning signs:**
- "App is damaged and can't be opened" on other Macs
- Gatekeeper blocks execution even with right-click open
- Users see "unidentified developer" warnings
- App works on your Mac but fails on fresh installs

**Prevention strategies:**
1. Get Apple Developer account early if targeting non-technical users
2. Use Developer ID Application certificate (not Mac App Distribution)
3. Sign with entitlements file that includes hardened runtime exceptions
4. Test notarization process with a minimal app first
5. Budget 30+ minutes per build for upload/notarization/stapling cycle
6. Automate with `xcrun notarytool` (new) not `altool` (deprecated)

**Phase to address:** Packaging + Distribution (Phase 3)
- Don't wait until launch to discover you need paid account
- Test signed builds on different Mac early

**Project-specific concern:**
- Cron-based architecture won't work from signed/sandboxed app
- Need LaunchAgent that can run scripts with full disk access
- State files need to be in user-accessible location, not app bundle
- May need com.apple.security.files.user-selected.read-write entitlement for vault access

---

### 1.3 File System Access Permissions (TCC)

**What goes wrong:**
Apps assume they can read/write anywhere. macOS Transparency, Consent, and Control (TCC) blocks:
- Reading from iCloud Documents folder (where Obsidian vault lives)
- Writing to ~/Library locations
- Accessing .env files in user home directory
- LaunchAgent reading credentials from keychain

**Warning signs:**
- "Operation not permitted" errors when accessing vault
- Works in development but fails after installation
- App can't find .env file or state JSON files
- Obsidian files aren't being created/updated

**Prevention strategies:**
1. Request Full Disk Access in System Preferences early
2. Provide clear first-run instructions for granting permissions
3. Use NSOpenPanel for user to explicitly select vault location (stores permission)
4. Store credentials in Keychain, not .env files, for production
5. Add TCC permission checks to first-run wizard

**Phase to address:** First-Run Setup (Phase 2)
- Wizard should check vault access before proceeding
- Provide visual guide for System Preferences → Security → Full Disk Access

**Project-specific concern:**
- Vault path: `~/Library/Mobile Documents/iCloud~md~obsidian/Documents/Home` requires special permission
- LaunchAgent needs Full Disk Access to function
- State files in `~/SecondBrain/_scripts/.state/` are fine, but iCloud vault access is critical

---

### 1.4 LaunchAgent vs Cron Job Confusion

**What goes wrong:**
Developers port cron jobs directly to LaunchAgents without understanding differences:
- LaunchAgents don't source .env files automatically
- PATH is minimal (doesn't include /usr/local/bin where uv lives)
- Working directory defaults to / not project root
- Stdout/stderr need explicit redirect paths
- No email on failure like cron's MAILTO

**Warning signs:**
- LaunchAgent plist loads but script never runs
- Script runs but fails with "command not found" for uv/python
- Environment variables are undefined
- Can't find log output anywhere

**Prevention strategies:**
1. Hardcode full paths to executables (`/Users/user/.local/bin/uv`)
2. Explicitly set WorkingDirectory in plist
3. Use StandardOutPath and StandardErrorPath for logging
4. Load environment variables in script itself, not relying on shell
5. Test with `launchctl start` before installing permanently

**Phase to address:** Infrastructure Setup (Phase 1)
- Convert cron jobs to LaunchAgent plists early
- Test startup behavior immediately

**Project-specific concern:**
- Current cron approach: `cd ~/second-brain-setup/backend && source _scripts/.env && uv run`
- LaunchAgent needs: ProgramArguments with full paths, WorkingDirectory set, env vars loaded differently
- Three separate plists: process_inbox (2min), fix_handler (5min), health_check (1hr)

---

### 1.5 Installer (.pkg) False Assumptions

**What goes wrong:**
Developers think .pkg is "just a zip with install script". Common mistakes:
- Putting everything in /Applications when scripts need ~/Library
- Not setting correct ownership/permissions on installed files
- Missing postinstall script for LaunchAgent registration
- Hardcoding user paths instead of using $USER variable
- Not validating Ollama/dependencies before completing install

**Warning signs:**
- App installs but doesn't appear in Applications
- LaunchAgent doesn't load after installation
- Permission denied errors on state files
- Installer succeeds but app doesn't run

**Prevention strategies:**
1. Use pkgbuild + productbuild toolchain (not just zip)
2. Split payload: app bundle in /Applications, support files in ~/Library/Application Support
3. Write postinstall script for LaunchAgent registration
4. Test installation on clean user account
5. Include uninstall script from day one

**Phase to address:** Packaging + Distribution (Phase 3)
- Design install layout before building
- Test install/uninstall cycle thoroughly

**Project-specific concern:**
- State files must go to `~/Library/Application Support/SecondBrain/` not in app bundle
- LaunchAgent plists go to `~/Library/LaunchAgents/`
- .env file handling: need to prompt user for Slack tokens during first run
- Installer should check for Ollama before completing

---

## 2. Ollama Integration Pitfalls

### 2.1 Assuming Ollama API Compatibility with OpenAI

**What goes wrong:**
Developers think Ollama's OpenAI-compatible API is truly drop-in. Differences:
- Different error response formats
- Timeout behaviors vary (Ollama can be slower for first inference)
- Streaming responses have different chunk formats
- Model names don't match OpenAI conventions (llama3.2:3b not gpt-4)
- No moderation endpoint
- Function calling support differs

**Warning signs:**
- JSON parsing errors on responses
- Timeouts on first call after model load
- Unexpected null fields in response
- Client library errors about missing fields

**Prevention strategies:**
1. Don't use OpenAI client library directly - wrap Ollama's API manually
2. Add explicit timeout handling (60s+ for first inference)
3. Test cold start behavior (first call after restart)
4. Use `requests` library directly, not OpenAI SDK
5. Parse responses defensively with try/except

**Phase to address:** LLM Classification (Phase 2)
- Build Ollama client abstraction from scratch
- Test with model loaded vs unloaded state

**Project-specific concern:**
- Current code uses Claude API - don't assume Ollama swap is simple
- Classification validation in schema.py must adapt to Ollama's response structure
- Consider keeping Claude as fallback for edge cases

---

### 2.2 Model Size vs Available RAM Miscalculations

**What goes wrong:**
8GB parameter models don't fit in 8GB RAM because:
- Quantization reduces size but still needs headroom
- System + other apps consume 2-3GB baseline
- Inference requires additional scratch memory
- Multiple concurrent requests compound memory usage
- Swap thrashing makes inference unbearably slow

**Warning signs:**
- Model loads but inference takes 30+ seconds
- System becomes unresponsive during classification
- Ollama crashes with OOM errors
- Swap usage spikes to 4GB+

**Prevention strategies:**
1. Target 3B parameter models maximum for 8GB RAM
2. Test on actual MacBook Air M1 (8GB) not development machine
3. Measure memory usage: `ollama ps` shows loaded models
4. Use quantized models (Q4 or Q5) not full precision
5. Implement model unloading after idle period (Ollama does this automatically)
6. Set keep_alive parameter in API calls

**Phase to address:** Model Selection (Phase 2)
- Test candidates: Llama 3.2 3B, Phi-3 Mini, Gemma 2B
- Benchmark memory usage and inference speed on target hardware

**Project-specific concern:**
- MacBook Air M1 8GB is target platform - must test there
- Classification happens every 2 minutes - can't tolerate 30s inference
- Consider keeping model loaded with keep_alive for faster response
- Acceptable latency: <5s per classification

---

### 2.3 Ollama Not Running Detection

**What goes wrong:**
App assumes Ollama is always running and ready. Reality:
- Ollama starts on demand (first API call) which delays first inference
- Ollama may not be installed at all
- Ollama service may crash and need restart
- Port 11434 may be blocked or used by other service
- Model may not be downloaded yet

**Warning signs:**
- Connection refused errors to localhost:11434
- App hangs on first classification attempt
- Error: "model not found" even after installation
- Intermittent failures that resolve after restart

**Prevention strategies:**
1. Check Ollama availability before starting processing loop
2. Implement health check: GET http://localhost:11434/api/tags
3. Auto-start Ollama if installed but not running (via `launchctl` or `open -a Ollama`)
4. Graceful degradation: queue messages if Ollama unavailable
5. First-run wizard verifies Ollama + model installation

**Phase to address:** First-Run Setup (Phase 2) + Error Handling (ongoing)
- Wizard checks Ollama installation
- Health check verifies model availability
- Process_inbox.py should fail gracefully if Ollama down

**Project-specific concern:**
- Current health_check.py monitors script success - extend to check Ollama health
- Messages should queue in Slack if Ollama down (don't lose data)
- Alert user via DM if Ollama unavailable for >1 hour

---

### 2.4 Prompt Engineering for Small Models

**What goes wrong:**
Developers copy prompts from Claude/GPT-4 and expect same results from 3B model:
- Small models need simpler instructions
- Few-shot examples are critical (zero-shot fails)
- JSON output requires explicit formatting
- Complex multi-step reasoning fails
- Context window limitations (2-4K tokens vs 100K)

**Warning signs:**
- Model returns partial JSON or malformed responses
- Classification accuracy <70%
- Model ignores schema requirements
- Verbose outputs that don't match expected format

**Prevention strategies:**
1. Use structured output format with examples in prompt
2. Keep prompts under 500 tokens
3. One task per call (don't combine domain + PARA + subject in one prompt)
4. Validate and retry with corrected prompt on failures
5. Test with actual vault structure examples in few-shot

**Phase to address:** LLM Classification (Phase 2)
- Redesign classification prompts for small models
- Add extensive few-shot examples
- Consider breaking into separate calls: domain → PARA → subject

**Project-specific concern:**
- Current classifier returns complex nested structure - may need simplification
- Test with actual Slack messages from project history
- Vault structure knowledge must be injected as context (no training)
- Measure classification accuracy against Claude baseline

---

### 2.5 Model Updates Breaking Compatibility

**What goes wrong:**
Ollama models update automatically and change behavior:
- Output format changes
- Response time increases
- Model size increases (breaks RAM constraint)
- Breaking API changes in Ollama itself

**Warning signs:**
- Classification starts failing after Ollama update
- Inference becomes slower over time
- Memory usage increases unexpectedly
- JSON parsing errors appear suddenly

**Prevention strategies:**
1. Pin specific model version in code (llama3.2:3b-q4 not llama3.2)
2. Test new Ollama versions before auto-updating
3. Document model version in first-run setup
4. Provide model rollback instructions
5. Monitor Ollama release notes

**Phase to address:** Model Selection (Phase 2) + Documentation
- Pin model version explicitly
- Document in README which model versions tested
- Add model version check to health_check.py

**Project-specific concern:**
- First-run wizard should install specific pinned model version
- Don't rely on "latest" tag
- Test with specific: llama3.2:3b-instruct-q4_0 (example)

---

## 3. LLM Classification System Pitfalls

### 3.1 Vault Structure Drift

**What goes wrong:**
Classification assumes static vault structure, but users add new folders:
- New PARA subjects created manually in Obsidian
- Model doesn't know about new categories
- Classifier defaults to generic "resources" folder
- Wikilinks to new entities fail to resolve

**Warning signs:**
- Increasing "needs-review" classifications
- Files consistently misrouted to catch-all folders
- New subjects not appearing in classifications
- User reports frequent "fix:" corrections needed

**Prevention strategies:**
1. Implement dynamic vault scanner (already planned)
2. Refresh vault map before each classification
3. Include vault structure in prompt context
4. Fall back gracefully to parent PARA folder if subject unknown
5. Log when new subjects are detected

**Phase to address:** Vault Scanner (Phase 2)
- Periodic refresh (daily) not just one-time scan
- Include vault map in classification prompt
- Handle new folders appearing mid-run

**Project-specific concern:**
- Three domains × four PARA types × N subjects = growing context
- Must fit in small model's context window
- Scanner must handle iCloud sync conflicts (duplicate folders)
- Test with actual vault: `~/Library/Mobile Documents/iCloud~md~obsidian/Documents/Home`

---

### 3.2 Entity Extraction Overload

**What goes wrong:**
Aggressive entity extraction creates noise:
- Every capitalized word becomes a wikilink
- Stub files proliferate for non-entities (job titles, product names)
- Graph view becomes cluttered and useless
- Performance degrades with thousands of stubs

**Warning signs:**
- Hundreds of single-line stub files
- Wikilinks to "Monday", "Q2", "Phase 1"
- Graph view is spaghetti
- Users complain about clutter

**Prevention strategies:**
1. Use allowlist for entity types (only people and projects)
2. Require 2+ mentions before creating stub
3. Check if entity already exists before creating
4. Implement entity disambiguation (Sarah vs Sarah Chen)
5. Let user configure entity extraction aggressiveness

**Phase to address:** Entity Extraction (ongoing)
- Tune wikilinks.py extraction rules
- Add entity confidence threshold
- Test with real message corpus

**Project-specific concern:**
- Current wikilinks.py may be too aggressive
- Three domains mean entity disambiguation is critical (work Sarah vs friend Sarah)
- Consider domain-specific entity lists

---

### 3.3 Confidence Score Misinterpretation

**What goes wrong:**
Confidence scores from small models are uncalibrated:
- Model outputs 0.95 confidence on wrong answers
- Scores don't correlate with actual accuracy
- Developers set thresholds based on wrong assumptions
- Users lose trust when "high confidence" classifications are wrong

**Warning signs:**
- High confidence scores but frequent "fix:" corrections
- No correlation between confidence and accuracy
- Users ignore confidence scores
- Threshold tuning doesn't improve results

**Prevention strategies:**
1. Calibrate confidence scores against validation set
2. Use "needs review" category for uncertain classifications
3. Track fix rate per confidence band
4. Don't rely solely on model's reported confidence
5. Add heuristic confidence adjustments (e.g., penalize if multiple domains plausible)

**Phase to address:** Model Evaluation (Phase 2)
- Collect ground truth data (100+ messages with correct classifications)
- Measure calibration curve
- Adjust confidence thresholds based on data

**Project-specific concern:**
- Current system uses Claude confidence - may not translate to Ollama
- Fix rate is proxy for accuracy - track this metric
- Target: <10% fix rate overall

---

### 3.4 Cold Start Latency

**What goes wrong:**
First classification after app launch takes 30+ seconds:
- Model needs to load from disk
- First inference is slower (warmup)
- User experience degraded if messages queue
- Cron job may timeout before completion

**Warning signs:**
- First run after restart times out
- Messages process quickly after first, slow on first
- LaunchAgent reports failures on startup
- Users report "app not working" after Mac wake

**Prevention strategies:**
1. Keep model loaded with keep_alive parameter
2. Pre-warm model during first-run wizard
3. Add startup delay to LaunchAgent (wait 60s after login)
4. Set generous timeout for first API call
5. Queue messages and process batch after warmup

**Phase to address:** Infrastructure Setup (Phase 1)
- Test cold start behavior explicitly
- Document expected latency in README
- Set LaunchAgent StartInterval appropriately

**Project-specific concern:**
- MacBook Air M1 may have slower cold starts
- Ollama default keep_alive is 5 minutes - extend to 1 hour for frequent processing
- First run after Mac wake is critical use case

---

### 3.5 Multi-Domain Classification Ambiguity

**What goes wrong:**
Thought could belong to multiple domains:
- "Meeting with Sarah about Just Value project" - Personal or Just Value?
- Model picks wrong domain because prompt doesn't prioritize
- Users waste time fixing domain misclassifications
- Wikilinks point to wrong domain's entity files

**Warning signs:**
- High fix rate specifically for domain corrections
- Same entities duplicated across domains
- Users report "it always picks wrong domain"
- Personal domain becomes catch-all

**Prevention strategies:**
1. Add domain hints to prompt (keywords, entity names)
2. Use explicit rules for domain precedence
3. Let user tag messages with domain prefix in Slack
4. Track entity→domain mapping to inform future classifications
5. Consider asking user when ambiguous (via Slack button)

**Phase to address:** Multi-Domain Routing (Phase 2)
- Test with ambiguous messages explicitly
- Define domain precedence rules
- Add optional Slack tagging syntax

**Project-specific concern:**
- Three domains: Personal, CCBH, Just Value
- Some entities span domains (same person in work and personal life)
- Consider prefixing filenames with domain: `Personal/people/sarah.md` vs `CCBH/people/sarah.md`
- Vault scanner must handle domain-specific subject lists

---

## 4. First-Run Setup Wizard Pitfalls

### 4.1 Assuming Dependencies Are Installed

**What goes wrong:**
Wizard assumes Ollama, Python, etc. are present:
- No installation check before proceeding
- Breaks halfway through when dependency missing
- User left in broken state with unclear recovery

**Warning signs:**
- Wizard crashes with "command not found"
- Setup completes but app doesn't work
- No clear error messages
- Users report "followed instructions but doesn't work"

**Prevention strategies:**
1. Check all dependencies before starting setup
2. Provide download links if missing
3. Offer to open installer if Ollama not present
4. Validate at each step before proceeding
5. Provide rollback if setup fails

**Phase to address:** First-Run Setup (Phase 2)
- Dependency checks are first step
- Clear error messages with actionable instructions

**Project-specific concern:**
- Check: Ollama installed, model downloaded, vault path exists, Slack token valid
- Don't check for Python/uv - bundled in app
- Offer to download Ollama if missing (open ollama.ai)

---

### 4.2 Non-Obvious Model Installation

**What goes wrong:**
Wizard says "install model" but doesn't explain how:
- User doesn't know what command to run
- Model name is unclear (which llama3.2 variant?)
- Download progress not visible
- Model download fails partway through (large files)

**Warning signs:**
- Support requests: "what model do I install?"
- Users install wrong model version
- Setup stalls waiting for model that never downloads
- Model download times out on slow connections

**Prevention strategies:**
1. Provide exact command to copy/paste: `ollama pull llama3.2:3b-instruct-q4_0`
2. Show download progress in wizard UI
3. Verify model downloaded before proceeding
4. Handle download failures gracefully
5. Offer alternative models if first choice unavailable

**Phase to address:** First-Run Setup (Phase 2)
- Wizard runs ollama pull command directly
- Shows progress bar
- Validates model availability after download

**Project-specific concern:**
- Model size ~2GB - could take 5-10 minutes on slow connection
- User may close laptop during download (handle resume)
- Verify exact model variant works before hardcoding

---

### 4.3 Slack Token Configuration UX

**What goes wrong:**
Wizard asks for "Slack Bot Token" with no context:
- User doesn't know where to get it
- Copies wrong token type (user token vs bot token)
- Doesn't know how to create Slack app
- Token validation fails with unclear error

**Warning signs:**
- Support requests: "where do I find the token?"
- Token validation fails repeatedly
- Users give up on setup
- Error messages don't explain what's wrong

**Prevention strategies:**
1. Provide step-by-step Slack app creation guide in wizard
2. Link to Slack API console with pre-filled scopes
3. Validate token format before proceeding (starts with xoxb-)
4. Test token by calling conversations.list API
5. Show example token format (redacted)

**Phase to address:** First-Run Setup (Phase 2)
- Wizard includes visual guide or video
- Token validation is explicit step
- Clear error: "Token invalid - must start with xoxb-"

**Project-specific concern:**
- Requires: SLACK_BOT_TOKEN, SLACK_CHANNEL_ID, SLACK_USER_ID
- Wizard could auto-detect channel/user ID after token validated
- Test token permissions (channels:history, chat:write, im:write)

---

### 4.4 Vault Path Validation

**What goes wrong:**
User enters vault path but:
- Path contains spaces and breaks shell commands
- Path doesn't exist yet (Obsidian not configured)
- iCloud sync not enabled
- Permissions denied to access path

**Warning signs:**
- Setup completes but no files appear in vault
- Permission errors in logs
- Path with spaces causes LaunchAgent failures
- Vault on external drive that's sometimes unmounted

**Prevention strategies:**
1. Use file picker dialog, don't ask user to type path
2. Validate path exists and is writable
3. Check for required vault structure (folders)
4. Offer to create structure if missing
5. Warn if path is on external/network drive

**Phase to address:** First-Run Setup (Phase 2)
- Use NSOpenPanel for path selection
- Test write access before proceeding
- Create PARA folders if missing

**Project-specific concern:**
- Default path: `~/Library/Mobile Documents/iCloud~md~obsidian/Documents/Home`
- Must handle iCloud sync state (downloading from cloud)
- Validate three domain folders exist: Personal/, CCBH/, Just Value/

---

### 4.5 Incomplete Setup Persistence

**What goes wrong:**
Setup partially completes then crashes:
- No state tracking of what's configured
- Re-running setup duplicates LaunchAgents
- Unclear which steps completed
- User doesn't know if safe to restart

**Warning signs:**
- Multiple LaunchAgents with same name
- Cron job runs twice
- Config file has duplicate entries
- Users afraid to re-run wizard

**Prevention strategies:**
1. Track setup progress in state file
2. Make wizard idempotent (safe to re-run)
3. Check what's already configured before proceeding
4. Allow skipping completed steps
5. Provide setup verification command

**Phase to address:** First-Run Setup (Phase 2)
- Setup state in `~/Library/Application Support/SecondBrain/setup_state.json`
- Wizard detects partial completion and resumes
- Verification: Health check confirms all components working

**Project-specific concern:**
- LaunchAgent plists must be unloaded before re-installing
- Don't duplicate message processing if re-run
- Verify setup with: ollama health, vault access, Slack connectivity

---

## Phase Mapping Summary

| Phase | Key Pitfalls to Address |
|-------|------------------------|
| **Phase 1: Infrastructure Setup** | LaunchAgent conversion, dependency bundling testing, cold start latency, model pinning |
| **Phase 2: LLM + First-Run** | Model size constraints, Ollama detection, prompt engineering, all wizard UX issues, vault scanner |
| **Phase 3: Packaging** | Code signing, notarization, TCC permissions, .pkg installer design |
| **Ongoing:** | Entity extraction tuning, confidence calibration, domain ambiguity, vault drift handling |

---

## Quality Checklist

- [x] Pitfalls are specific to macOS packaging + Ollama integration (not generic)
- [x] Warning signs provided for early detection
- [x] Prevention strategies are actionable
- [x] Phase mapping included for each category
- [x] Project-specific concerns referenced with actual paths/constraints
- [x] Memory constraints (8GB RAM) explicitly addressed
- [x] Target user profile (moderate technical ability) considered

---

*Research completed: 2026-01-30*
*Sources: Domain knowledge of macOS packaging, Ollama integration patterns, LLM classification systems*
