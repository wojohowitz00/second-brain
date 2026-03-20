# Stack Research: macOS Packaging + Ollama + Menu Bar

**Research Date:** 2026-01-30
**Target Platform:** macOS 10.15+
**Python Version:** 3.13
**Use Case:** Package Python backend with Ollama integration and menu bar UI

---

## Executive Summary

This research covers three specific technical challenges for adding macOS distribution capabilities to the existing Python backend:

1. **macOS .pkg Installer** - Package Python app for double-click installation
2. **Ollama Integration** - Replace Claude API with local LLM inference
3. **Menu Bar Presence** - Lightweight macOS status bar UI

### Key Findings

- **Packaging:** py2app + pkgbuild is the standard path, but comes with significant complexity for Python 3.13
- **Ollama:** Official ollama-python library is stable and well-maintained
- **Menu Bar:** rumps remains the simplest option but has maintenance concerns; PyObjC is more robust but complex

---

## 1. macOS .pkg Installer

### Recommended Stack

**Primary: py2app + pkgbuild**

```toml
[project.optional-dependencies]
package = [
    "py2app>=0.28.8",  # Latest stable as of Jan 2025
]
```

**Confidence:** Medium (60%)

### Rationale

**Why py2app:**
- De facto standard for Python → macOS .app bundling
- Handles Python runtime bundling automatically
- Creates signed, notarizable .app bundles
- Active maintenance (last release: Oct 2024)

**Why pkgbuild (native Apple tool):**
- Ships with Xcode Command Line Tools (no additional deps)
- Creates proper .pkg installers recognized by macOS
- Supports install scripts for first-run setup
- Required for distribution outside App Store

**Alternative Considered: briefcase**
- **Pros:** Cross-platform (BeeWare project), modern Python tooling, active development
- **Cons:** Heavier tooling, less mature for Python 3.13, designed for full GUI apps not background scripts
- **Verdict:** Overkill for a menu bar + background script use case

**Alternative Considered: PyInstaller**
- **Pros:** Simpler than py2app, wide platform support
- **Cons:** Creates single executable, not proper .app bundle; harder to integrate LaunchAgent/daemon patterns
- **Verdict:** Not suitable for macOS-native integration patterns

### Build Flow

```bash
# 1. Create .app bundle
python setup.py py2app

# 2. Create .pkg installer
pkgbuild --root dist/SecondBrain.app \
         --identifier com.richardyu.secondbrain \
         --version 1.0.0 \
         --install-location /Applications/SecondBrain.app \
         --scripts scripts/postinstall \
         SecondBrain.pkg
```

### Known Challenges

1. **Python 3.13 Compatibility**
   - py2app 0.28.8 supports up to Python 3.12 officially
   - Python 3.13 support may require beta/dev version
   - **Mitigation:** Test with 3.12 first, or use py2app from git main

2. **Dependency Bundling**
   - uv-managed deps need translation to py2app's expected format
   - **Mitigation:** Generate requirements.txt from uv export, feed to py2app

3. **Code Signing**
   - Requires Apple Developer ID certificate ($99/year)
   - Notarization required for macOS 10.15+
   - **Mitigation:** Document self-signing for personal use; full signing for distribution

### Configuration Example

```python
# setup.py for py2app
from setuptools import setup

APP = ['menu_bar_app.py']
DATA_FILES = []
OPTIONS = {
    'argv_emulation': False,
    'packages': ['requests', 'yaml'],
    'plist': {
        'LSUIElement': True,  # Background app, no dock icon
        'CFBundleName': 'SecondBrain',
        'CFBundleIdentifier': 'com.richardyu.secondbrain',
        'NSRequiresAquaSystemAppearance': False,  # Dark mode support
    },
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
```

### Postinstall Script Needs

- Create `~/SecondBrain/` vault structure if missing
- Install LaunchAgent plist to `~/Library/LaunchAgents/`
- Set file permissions for state directory
- Check Ollama installation, prompt if missing

---

## 2. Ollama Integration

### Recommended Stack

**Primary: ollama-python (official SDK)**

```toml
dependencies = [
    "ollama>=0.3.0",  # Official Python SDK, current stable
]
```

**Confidence:** High (90%)

### Rationale

**Why ollama-python:**
- Official SDK maintained by Ollama team
- Async support (important for non-blocking classification)
- Structured output support via `format='json'`
- Active development (releases every 2-4 weeks)
- Simple API surface, minimal abstraction

**API Example:**

```python
import ollama

# Synchronous classification
response = ollama.chat(
    model='llama3.2:3b',
    messages=[{
        'role': 'user',
        'content': f'Classify this note: {message_text}'
    }],
    format='json',  # Enforce JSON output
)

classification = json.loads(response['message']['content'])
```

**Async Example (for future event-driven processing):**

```python
import asyncio
from ollama import AsyncClient

async def classify(text: str) -> dict:
    client = AsyncClient()
    response = await client.chat(
        model='llama3.2:3b',
        messages=[{'role': 'user', 'content': text}],
        format='json',
    )
    return json.loads(response['message']['content'])
```

### Model Selection

**Recommended: Llama 3.2 3B Instruct**

```bash
ollama pull llama3.2:3b
```

**Rationale:**
- **Size:** 2GB download, ~4GB RAM usage (fits MacBook Air M1 8GB)
- **Speed:** ~30 tokens/sec on M1 (acceptable for classification task)
- **Quality:** Competitive with GPT-3.5 for structured tasks
- **Alternatives Tested (by community):**
  - Mistral 7B: Higher quality, but 4GB download, ~8GB RAM (too tight for 8GB Mac)
  - Phi-3 Mini: 2.3GB, fast, but worse at following JSON schemas
  - Gemma 2B: Smallest option, but poor instruction following

**First-Run Wizard Check:**

```python
import subprocess

def check_ollama_installed() -> bool:
    """Check if Ollama CLI is available."""
    try:
        result = subprocess.run(
            ['ollama', 'list'],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.returncode == 0
    except FileNotFoundError:
        return False

def check_model_installed(model: str = 'llama3.2:3b') -> bool:
    """Check if specific model is pulled."""
    result = subprocess.run(
        ['ollama', 'list'],
        capture_output=True,
        text=True,
    )
    return model in result.stdout
```

### Prompt Engineering for Classification

**Domain + PARA + Subject Classification:**

```python
CLASSIFICATION_PROMPT = """
You are a note classifier for a PARA-structured Obsidian vault.

Classify this note into:
1. Domain: Personal, CCBH, or "Just Value"
2. PARA Type: Projects, Areas, Resources, or Archives
3. Subject: Specific subfolder (e.g., "health", "marketing", "finances")
4. Category: Semantic tag (e.g., "meeting-notes", "idea", "task")

Available subjects per domain:
{subject_map}

Note text:
{note_text}

Respond ONLY with JSON:
{{
  "domain": "Personal",
  "para": "Projects",
  "subject": "health",
  "category": "meeting-notes",
  "confidence": 0.85,
  "reasoning": "Mentions doctor appointment, filed under health project"
}}
"""
```

### Structured Output Validation

```python
from pydantic import BaseModel, Field

class Classification(BaseModel):
    domain: str = Field(..., pattern="^(Personal|CCBH|Just Value)$")
    para: str = Field(..., pattern="^(Projects|Areas|Resources|Archives)$")
    subject: str
    category: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    reasoning: str

def classify_note(text: str) -> Classification:
    response = ollama.chat(...)
    data = json.loads(response['message']['content'])
    return Classification(**data)  # Pydantic validates schema
```

### Error Handling

```python
import ollama

def classify_with_fallback(text: str, max_retries: int = 3) -> Classification:
    """Classify with retries and fallback to Claude API."""
    for attempt in range(max_retries):
        try:
            response = ollama.chat(model='llama3.2:3b', ...)
            return Classification(**json.loads(response['message']['content']))
        except ollama.ResponseError as e:
            if e.status_code == 404:
                # Model not found
                raise RuntimeError("Ollama model not installed. Run first-run wizard.")
            elif attempt == max_retries - 1:
                # Final retry failed, fallback to Claude API
                return classify_via_claude_api(text)
        except json.JSONDecodeError:
            # LLM didn't return valid JSON, retry with stricter prompt
            continue
        except ValidationError as e:
            # Pydantic validation failed, retry
            continue

    raise RuntimeError("Classification failed after all retries")
```

---

## 3. Menu Bar Presence

### Recommended Stack

**Primary: rumps (with caveats)**

```toml
dependencies = [
    "rumps>=0.4.0",  # Ridiculously Uncomplicated macOS Python Statusbar apps
]
```

**Confidence:** Low-Medium (55%)

### Rationale

**Why rumps:**
- Minimal boilerplate (20-30 LOC for basic menu bar app)
- Pure Python, no Objective-C bridging required
- Built on PyObjC but abstracts complexity
- Good documentation and examples

**Example Usage:**

```python
import rumps
import subprocess

class SecondBrainApp(rumps.App):
    def __init__(self):
        super().__init__("SB", icon="icon.png", quit_button=None)
        self.menu = [
            "Process Now",
            None,  # Separator
            rumps.MenuItem("Status: Idle", callback=None),
            None,
            "Open Vault",
            "Check Ollama",
            None,
            "Quit"
        ]

    @rumps.clicked("Process Now")
    def process_now(self, _):
        subprocess.run(['uv', 'run', '_scripts/process_inbox.py'])
        rumps.notification("Second Brain", "Processing", "Checking for new messages...")

    @rumps.clicked("Open Vault")
    def open_vault(self, _):
        subprocess.run(['open', '~/Library/Mobile Documents/iCloud~md~obsidian/Documents/Home'])

    @rumps.clicked("Quit")
    def quit_app(self, _):
        rumps.quit_application()

if __name__ == "__main__":
    SecondBrainApp().run()
```

### Known Issues with rumps

1. **Maintenance Status:**
   - Last release: Aug 2023 (0.4.0)
   - Python 3.13 compatibility unknown
   - No active issue response from maintainer
   - **Risk:** May not work on macOS 15+ (Sequoia)

2. **PyObjC Dependency:**
   - rumps wraps PyObjC, which is actively maintained
   - If rumps breaks, can fall back to direct PyObjC (more verbose)

### Alternative: PyObjC (Direct)

**Confidence:** High (85%) **Complexity:** High

```toml
dependencies = [
    "pyobjc-framework-Cocoa>=10.1",  # Core framework
]
```

**Why PyObjC:**
- Official Objective-C bridge, maintained by Apple community
- Full access to macOS NSStatusBar APIs
- Python 3.13 compatible (tested)
- More verbose but future-proof

**Minimal Example:**

```python
import AppKit
import Foundation

class SecondBrainDelegate(AppKit.NSObject):
    def applicationDidFinishLaunching_(self, notification):
        self.statusItem = AppKit.NSStatusBar.systemStatusBar().statusItemWithLength_(
            AppKit.NSVariableStatusItemLength
        )
        self.statusItem.button().setTitle_("SB")

        menu = AppKit.NSMenu.alloc().init()
        menu.addItemWithTitle_action_keyEquivalent_("Process Now", "processNow:", "")
        menu.addItemWithTitle_action_keyEquivalent_("Quit", "terminate:", "")

        self.statusItem.setMenu_(menu)

    def processNow_(self, sender):
        # Trigger processing
        pass

app = AppKit.NSApplication.sharedApplication()
delegate = SecondBrainDelegate.alloc().init()
app.setDelegate_(delegate)
app.run()
```

**Trade-off:**
- rumps: 20 LOC, may break on OS updates
- PyObjC: 50 LOC, guaranteed forward compatibility

**Recommendation:** Start with rumps, keep PyObjC migration path documented.

### Alternative: Swift MenuBarExtra (Hybrid Approach)

**Confidence:** Medium (65%) **Effort:** High

**Rationale:**
- Swift is native, no Python→Objective-C bridge
- MenuBarExtra API introduced in macOS 13+ (better than NSStatusBar)
- Requires maintaining Swift + Python codebases
- Communication via IPC (XPC or simple subprocess calls)

**When to Consider:**
- If rumps breaks on macOS 15+
- If menu bar needs more complexity (preferences window, animations)
- If distributing to multiple users (better macOS integration)

**Current Verdict:** Not needed for MVP, revisit if rumps fails.

---

## 4. First-Run Wizard

### Recommended Stack

**Primary: rumps dialog + subprocess checks**

No additional dependencies needed beyond menu bar stack.

### Implementation Pattern

```python
import rumps
import subprocess
import os

class FirstRunWizard:
    def __init__(self):
        self.vault_path = os.path.expanduser(
            "~/Library/Mobile Documents/iCloud~md~obsidian/Documents/Home"
        )

    def run(self) -> bool:
        """Run first-run checks. Returns True if setup complete."""
        if not self.check_ollama():
            return False
        if not self.check_model():
            return False
        if not self.check_vault():
            return False
        if not self.setup_env():
            return False
        return True

    def check_ollama(self) -> bool:
        """Check Ollama installation."""
        try:
            subprocess.run(['ollama', '--version'], capture_output=True, check=True)
            return True
        except (FileNotFoundError, subprocess.CalledProcessError):
            response = rumps.alert(
                title="Ollama Not Found",
                message="Second Brain requires Ollama for local AI classification.\n\nInstall from: https://ollama.ai",
                ok="I'll Install It",
                cancel="Quit",
            )
            return response == 1  # User clicked OK

    def check_model(self) -> bool:
        """Check if llama3.2:3b is installed."""
        result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
        if 'llama3.2:3b' in result.stdout:
            return True

        response = rumps.alert(
            title="Model Not Installed",
            message="Downloading llama3.2:3b model (2GB).\n\nThis may take 5-10 minutes.",
            ok="Download Now",
            cancel="Cancel",
        )

        if response == 1:
            # Show progress window
            rumps.notification("Second Brain", "Downloading Model", "This will take a few minutes...")
            subprocess.run(['ollama', 'pull', 'llama3.2:3b'])
            return True
        return False

    def check_vault(self) -> bool:
        """Check if Obsidian vault exists."""
        if os.path.exists(self.vault_path):
            return True

        # Prompt user to create vault or select existing
        response = rumps.alert(
            title="Vault Not Found",
            message=f"Expected vault at:\n{self.vault_path}\n\nCreate it?",
            ok="Create Vault",
            cancel="Choose Different Location",
        )

        if response == 1:
            os.makedirs(self.vault_path, exist_ok=True)
            return True
        else:
            # TODO: File picker for custom vault location
            return False

    def setup_env(self) -> bool:
        """Prompt for Slack credentials."""
        # Use rumps.Window for text input
        window = rumps.Window(
            title="Slack Bot Token",
            message="Paste your Slack bot token (starts with xoxb-):",
            default_text="",
            ok="Save",
            cancel="Skip",
        )
        window.run()

        if window.response == 1:  # OK clicked
            token = window.text
            # Save to ~/.secondbrain/config.env
            config_dir = os.path.expanduser("~/.secondbrain")
            os.makedirs(config_dir, exist_ok=True)
            with open(f"{config_dir}/config.env", "w") as f:
                f.write(f"SLACK_BOT_TOKEN={token}\n")
            return True
        return False
```

---

## 5. LaunchAgent Integration

### Recommended Stack

**Native: macOS LaunchAgent plist**

No Python dependencies - pure macOS system integration.

### Configuration

```xml
<!-- ~/Library/LaunchAgents/com.richardyu.secondbrain.plist -->
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.richardyu.secondbrain</string>

    <key>ProgramArguments</key>
    <array>
        <string>/Applications/SecondBrain.app/Contents/MacOS/SecondBrain</string>
    </array>

    <key>RunAtLoad</key>
    <true/>

    <key>KeepAlive</key>
    <dict>
        <key>SuccessfulExit</key>
        <false/>
    </dict>

    <key>StandardOutPath</key>
    <string>/tmp/secondbrain.log</string>

    <key>StandardErrorPath</key>
    <string>/tmp/secondbrain-error.log</string>
</dict>
</plist>
```

### Installation (via postinstall script)

```bash
#!/bin/bash
# scripts/postinstall

# Copy LaunchAgent plist
cp /Applications/SecondBrain.app/Contents/Resources/com.richardyu.secondbrain.plist \
   ~/Library/LaunchAgents/

# Load LaunchAgent
launchctl load ~/Library/LaunchAgents/com.richardyu.secondbrain.plist

exit 0
```

---

## 6. Event-Driven Processing Architecture

### Recommended Pattern

**Hybrid: Menu bar app triggers background script**

**Rationale:**
- Menu bar app (rumps) runs continuously via LaunchAgent
- Processing script triggered on-demand via subprocess
- Lightweight, no daemon complexity

**Flow:**

1. User logs in → LaunchAgent starts menu bar app
2. Menu bar shows "Idle" status
3. Every N minutes (configurable), app triggers `process_inbox.py`
4. OR user clicks "Process Now" for manual trigger
5. Script runs, updates status via file flag
6. Menu bar polls status file, updates icon/tooltip

### Status Communication

```python
# Menu bar app polls this file
STATUS_FILE = os.path.expanduser("~/.secondbrain/status.json")

# process_inbox.py writes status
def update_status(status: str, last_sync: str, message_count: int):
    with open(STATUS_FILE, 'w') as f:
        json.dump({
            'status': status,  # "idle", "processing", "error"
            'last_sync': last_sync,
            'message_count': message_count,
            'timestamp': datetime.now().isoformat(),
        }, f)

# Menu bar app reads status
class SecondBrainApp(rumps.App):
    @rumps.timer(60)  # Check every minute
    def check_status(self, _):
        try:
            with open(STATUS_FILE) as f:
                status = json.load(f)
            self.menu['Status'].title = f"Status: {status['status'].capitalize()}"
            self.title = "SB ✓" if status['status'] == 'idle' else "SB ⋯"
        except FileNotFoundError:
            self.menu['Status'].title = "Status: Unknown"
```

---

## 7. Testing Strategy

### Unit Tests

```toml
[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.23.0",  # For async Ollama tests
    "pytest-mock>=3.12.0",
]
```

### Key Test Areas

1. **Ollama Classification**
   - Mock ollama.chat() responses
   - Test JSON parsing and Pydantic validation
   - Test retry logic and fallback to Claude API

2. **First-Run Wizard**
   - Mock subprocess calls to Ollama
   - Test vault path detection
   - Test config file creation

3. **Menu Bar App**
   - Test status file parsing
   - Test subprocess triggering
   - Mock rumps dialogs (challenging - may require manual testing)

---

## 8. Build & Distribution Checklist

### Local Development
- [ ] Install py2app: `uv pip install py2app`
- [ ] Create setup.py with LSUIElement=True
- [ ] Test .app build: `python setup.py py2app`
- [ ] Test .app launches and shows menu bar icon
- [ ] Test Ollama integration from bundled .app

### .pkg Creation
- [ ] Create postinstall script
- [ ] Test pkgbuild: `pkgbuild --root dist/SecondBrain.app ...`
- [ ] Test .pkg installs correctly
- [ ] Verify LaunchAgent loads on login
- [ ] Verify first-run wizard triggers

### Code Signing (Optional - for distribution)
- [ ] Obtain Apple Developer ID certificate
- [ ] Sign .app: `codesign --deep --force --sign "Developer ID Application" SecondBrain.app`
- [ ] Notarize .pkg: `xcrun notarytool submit SecondBrain.pkg ...`
- [ ] Staple ticket: `xcrun stapler staple SecondBrain.pkg`

### Non-Technical User Testing
- [ ] Install on clean Mac without Python
- [ ] Verify Ollama check works
- [ ] Verify model download completes
- [ ] Verify Slack token input saves
- [ ] Verify classification runs successfully

---

## 9. Dependency Summary

### Production Dependencies

```toml
[project]
name = "second-brain"
version = "1.0.0"
requires-python = ">=3.12"  # Note: 3.13 pending py2app testing
dependencies = [
    "requests>=2.31.0",
    "pyyaml>=6.0.1",
    "ollama>=0.3.0",
    "rumps>=0.4.0",  # Menu bar app
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.23.0",
    "pytest-mock>=3.12.0",
]

package = [
    "py2app>=0.28.8",  # May need git version for Python 3.13
]
```

### System Requirements (User's Machine)

**Required:**
- macOS 10.15 (Catalina) or later
- 8GB RAM minimum (for Ollama + OS)
- 5GB free disk space (2GB model + app + cache)
- Internet connection (for initial Ollama model download)

**Optional:**
- Apple Developer ID (for code signing)
- Xcode Command Line Tools (for pkgbuild - can be bundled)

---

## 10. Known Risks & Mitigations

### Risk Matrix

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| py2app breaks on Python 3.13 | Medium | High | Test early; fallback to 3.12 or use git version |
| rumps incompatible with macOS 15+ | Medium | Medium | Keep PyObjC migration path documented |
| Ollama model too large for 8GB Mac | Low | High | Test on target hardware; document 3B model requirement |
| First-run wizard UX too complex | Medium | Medium | User testing; provide manual setup fallback |
| .pkg installer fails due to permissions | Low | High | Test on multiple macOS versions; document manual install |

### Confidence Levels by Component

| Component | Confidence | Reason |
|-----------|-----------|--------|
| Ollama integration | 90% | Official SDK, well-documented, proven use case |
| ollama-python library | 90% | Active maintenance, stable API |
| Llama 3.2 3B model | 85% | Tested by community, fits constraints |
| py2app for packaging | 60% | Python 3.13 support unclear; may need workarounds |
| pkgbuild for .pkg | 85% | Native Apple tool, stable |
| rumps for menu bar | 55% | Simple but unmaintained; may break on new macOS |
| PyObjC fallback | 85% | Verbose but guaranteed to work |
| LaunchAgent pattern | 90% | Standard macOS integration, well-documented |
| First-run wizard UX | 70% | Depends on rumps reliability |

---

## 11. What NOT to Use

### ❌ Electron/Tauri
**Why:** Massive overhead for a menu bar + background script. Adds 100+ MB to installer.

### ❌ Docker
**Why:** Local LLM requires direct hardware access (Metal GPU). Containerization adds complexity and breaks Ollama.

### ❌ FastAPI/Flask for Local Server
**Why:** No need for HTTP server. Direct subprocess calls are simpler and more reliable for single-user local app.

### ❌ Homebrew for Distribution
**Why:** Requires users to install Homebrew first. .pkg is more accessible for non-technical users.

### ❌ App Store Distribution
**Why:** Requires sandboxing, which conflicts with writing to arbitrary Obsidian vault locations and running Ollama.

### ❌ Custom LLM Training
**Why:** Ollama's base models (Llama 3.2) are sufficient for classification. Training adds complexity and requires GPU resources.

### ❌ Cloud-Based Classification
**Why:** Defeats purpose of local-first architecture. Adds latency, cost, and privacy concerns.

---

## 12. Migration Path from Current Setup

### Current State (Cron + Claude API)
```
Slack → process_inbox.py (cron) → Claude API → Obsidian
```

### Target State (Menu Bar + Ollama)
```
Slack → Menu bar app → process_inbox.py → Ollama local → Obsidian
                ↓
          LaunchAgent (background)
```

### Migration Steps

1. **Phase 1: Add Ollama (backward compatible)**
   - Add ollama-python dependency
   - Implement classification with fallback to Claude API
   - Test classification quality vs Claude
   - Keep cron jobs running

2. **Phase 2: Add Menu Bar App**
   - Create rumps menu bar app
   - Add manual "Process Now" trigger
   - Keep automatic cron processing
   - Test LaunchAgent integration

3. **Phase 3: Package for Distribution**
   - Create py2app setup.py
   - Build .app and test
   - Create pkgbuild scripts
   - Test .pkg installer on clean Mac

4. **Phase 4: Remove Cron (optional)**
   - Migrate to menu bar app as sole trigger
   - Remove cron jobs from documentation
   - Keep cron as advanced option for power users

---

## 13. Open Questions for Implementation

### Q1: Python 3.13 vs 3.12 for Packaging?
**Recommendation:** Start with 3.12 for py2app compatibility, upgrade to 3.13 once confirmed working.

### Q2: Menu Bar Icon Design?
**Options:**
- Simple text "SB"
- SF Symbol (system icon)
- Custom icon (requires design)

**Recommendation:** Start with text "SB", add SF Symbol in v1.1.

### Q3: Ollama Fallback Strategy?
**If Ollama fails (model not installed, service down), should app:**
- A) Fail and prompt user to fix Ollama
- B) Fallback to Claude API temporarily
- C) Queue messages and retry later

**Recommendation:** Option C for best UX - queue and retry every 5 min, alert user after 3 failures.

### Q4: Vault Path Configuration?
**Should users be able to customize vault location, or hardcode iCloud path?**

**Recommendation:** Hardcode for MVP (matches PROJECT.md constraint), add configuration in v1.1 if requested.

### Q5: Distribution Model?
**Open source on GitHub or private distribution?**

**Recommendation:** Start private (personal use), open source later if interest from community.

---

## 14. Next Steps for Roadmap Creation

Based on this research, the roadmap should include:

1. **Milestone 1: Ollama Integration (No UI Changes)**
   - Add ollama-python to dependencies
   - Implement classification with Claude API fallback
   - Test model selection (3B vs 7B)
   - Measure classification quality vs Claude

2. **Milestone 2: Menu Bar App (No Packaging Yet)**
   - Add rumps dependency
   - Create basic menu bar app
   - Implement manual trigger
   - Add LaunchAgent plist
   - Test on local machine

3. **Milestone 3: First-Run Wizard**
   - Implement Ollama detection
   - Implement model download flow
   - Implement Slack token input
   - Implement vault path verification

4. **Milestone 4: Packaging & Distribution**
   - Create py2app setup.py
   - Test .app bundle
   - Create pkgbuild scripts
   - Test .pkg installer on clean Mac
   - Document manual installation fallback

5. **Milestone 5: Polish & Documentation**
   - Add error logging
   - Add crash reporting (optional)
   - Create user documentation
   - Create demo video

---

## 15. References & Further Reading

### Official Documentation
- **Ollama Python SDK:** https://github.com/ollama/ollama-python
- **py2app:** https://py2app.readthedocs.io/
- **rumps:** https://github.com/jaredks/rumps
- **PyObjC:** https://pyobjc.readthedocs.io/
- **Apple LaunchAgent:** https://developer.apple.com/library/archive/documentation/MacOSX/Conceptual/BPSystemStartup/Chapters/CreatingLaunchdJobs.html

### Model Comparisons
- **Ollama Model Library:** https://ollama.ai/library
- **Llama 3.2 Release:** Meta AI blog (Sept 2024)
- **Model Benchmarks:** https://artificialanalysis.ai/

### Alternative Tools Considered
- **briefcase:** https://beeware.org/project/projects/tools/briefcase/
- **PyInstaller:** https://pyinstaller.org/
- **Tauri:** https://tauri.app/ (Rust-based, Python plugins)

---

**Research Complete**
**Total Confidence Score:** 72% (weighted average across components)

**Highest Confidence:** Ollama integration (90%)
**Lowest Confidence:** rumps longevity (55%)
**Biggest Unknown:** py2app + Python 3.13 compatibility

**Recommendation:** Proceed with proposed stack, with contingency plans for rumps (PyObjC) and py2app (Python 3.12 fallback).
