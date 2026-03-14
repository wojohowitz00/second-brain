# Phase 9: Packaging - Research

**Researched:** 2026-01-31
**Domain:** macOS app packaging, Python distribution, LaunchAgent
**Confidence:** HIGH

## Summary

Phase 9 packages the Second Brain menu bar app as a distributable .pkg installer for non-technical users. The research identifies **py2app** as the recommended tool for packaging rumps-based menu bar apps, with a standard workflow of: py2app → .app bundle → pkgbuild → .pkg installer.

The key insight is that rumps apps require special handling: `LSUIElement: True` to hide from dock, and the `packages` list must include rumps and pyobjc dependencies. LaunchAgent setup for "launch on login" is straightforward but must reference the installed app path.

**Primary recommendation:** Use py2app to create .app bundle, then pkgbuild to create .pkg installer. Include optional LaunchAgent plist that users can install for login startup.

## Standard Stack

### Core
| Tool | Version | Purpose | Why Standard |
|------|---------|---------|--------------|
| py2app | 0.28.9+ | Create .app bundle | Official rumps recommendation, handles pyobjc correctly |
| pkgbuild | macOS builtin | Create .pkg from .app | Apple's native tool, no dependencies |
| productbuild | macOS builtin | Create distribution pkg | For signed/notarized distribution |

### Supporting
| Tool | Version | Purpose | When to Use |
|------|---------|---------|-------------|
| create-dmg | latest | Create DMG disk image | Alternative distribution format |
| codesign | macOS builtin | Sign app bundle | Required for notarization |
| notarytool | macOS builtin | Notarize with Apple | Required for Gatekeeper bypass |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| py2app | PyInstaller | PyInstaller is cross-platform but has rumps/pyobjc issues |
| pkgbuild | Packages.app | GUI tool, less scriptable |
| .pkg | .dmg only | DMG is simpler but .pkg allows custom install logic |

## Architecture Patterns

### Pattern 1: py2app Setup for Menu Bar App
**What:** Configure py2app for rumps-based status bar application
**When to use:** Always for this project
**Example:**
```python
# setup.py
from setuptools import setup

APP = ['menu_bar_app.py']
DATA_FILES = []
OPTIONS = {
    'argv_emulation': False,  # Not needed for menu bar apps
    'plist': {
        'LSUIElement': True,  # Hide from dock
        'CFBundleName': 'Second Brain',
        'CFBundleIdentifier': 'com.secondbrain.app',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'NSHighResolutionCapable': True,
    },
    'packages': [
        'rumps',
        'ollama',
        'requests',
    ],
    'includes': [
        'menu_bar_app',
        'notifications',
        'process_inbox',
        'message_classifier',
        'ollama_client',
        'vault_scanner',
        'slack_client',
        'file_writer',
        'state',
    ],
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
```

### Pattern 2: Building .pkg from .app
**What:** Use pkgbuild to create installer package
**When to use:** After py2app creates .app bundle
**Example:**
```bash
# Build .app bundle
python setup.py py2app

# Create component package
pkgbuild --root dist/ \
         --identifier com.secondbrain.app \
         --version 1.0.0 \
         --install-location /Applications \
         SecondBrain.pkg
```

### Pattern 3: LaunchAgent for Login Startup
**What:** plist file that launches app on login
**When to use:** Optional user preference
**Example:**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.secondbrain.app</string>
    <key>ProgramArguments</key>
    <array>
        <string>/Applications/Second Brain.app/Contents/MacOS/Second Brain</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <false/>
</dict>
</plist>
```

Install to: `~/Library/LaunchAgents/com.secondbrain.app.plist`

### Pattern 4: Build Script
**What:** Automated build pipeline
**When to use:** CI/CD or local builds
**Example:**
```bash
#!/bin/bash
set -e

VERSION="1.0.0"
APP_NAME="Second Brain"

# Clean previous builds
rm -rf build dist

# Install build dependencies
pip install py2app

# Build .app bundle
python setup.py py2app

# Verify bundle
test -d "dist/${APP_NAME}.app" || exit 1

# Create .pkg installer
pkgbuild \
    --root dist/ \
    --identifier com.secondbrain.app \
    --version "$VERSION" \
    --install-location /Applications \
    "SecondBrain-${VERSION}.pkg"

echo "Built: SecondBrain-${VERSION}.pkg"
```

## Common Pitfalls

### Pitfall 1: Missing pyobjc Dependencies
**What goes wrong:** App crashes on launch with import errors
**Why it happens:** py2app doesn't auto-detect pyobjc framework dependencies
**How to avoid:** Explicitly list pyobjc packages in OPTIONS['packages']
**Warning signs:** "No module named 'Foundation'" errors

### Pitfall 2: Wrong LSUIElement Setting
**What goes wrong:** App shows in dock with generic Python icon
**Why it happens:** LSUIElement not set or set to False
**How to avoid:** Set `'LSUIElement': True` in plist options
**Warning signs:** App icon appears in dock

### Pitfall 3: Relative Imports Broken
**What goes wrong:** ModuleNotFoundError for local modules
**Why it happens:** py2app changes module search paths
**How to avoid:** List all local modules in OPTIONS['includes']
**Warning signs:** Import errors only in bundled app, not in dev

### Pitfall 4: Data Files Not Included
**What goes wrong:** Config files, templates missing from bundle
**Why it happens:** DATA_FILES not configured
**How to avoid:** Add data files to DATA_FILES list with proper paths
**Warning signs:** FileNotFoundError for non-Python resources

### Pitfall 5: LaunchAgent Path Wrong
**What goes wrong:** App doesn't start on login
**Why it happens:** ProgramArguments path doesn't match installed location
**How to avoid:** Use `/Applications/APP_NAME.app/Contents/MacOS/APP_NAME`
**Warning signs:** launchctl errors in system.log

## Success Criteria Mapping

| Requirement | Implementation |
|-------------|----------------|
| DIST-01: .pkg installer | pkgbuild from py2app .app bundle |
| DIST-02: Install to /Applications | pkgbuild --install-location /Applications |
| DIST-03: Launch on login | LaunchAgent plist in ~/Library/LaunchAgents |

## Plan Breakdown

Based on this research, Phase 9 should have **2 plans**:

### 09-01-PLAN: py2app Bundle Creation
- Create setup.py with proper py2app configuration
- Build .app bundle with all dependencies
- Test bundle runs standalone
- Verify menu bar functionality works

### 09-02-PLAN: .pkg Installer and LaunchAgent
- Create pkgbuild script for .pkg generation
- Create LaunchAgent plist template
- Create install/uninstall scripts
- Test full installation workflow

## Sources

### Primary (HIGH confidence)
- [rumps: Creating Standalone Applications](https://rumps.readthedocs.io/en/latest/creating.html)
- [py2app Documentation](https://py2app.readthedocs.io/en/stable)
- [Apple pkgbuild man page](https://developer.apple.com/library/archive/documentation/DeveloperTools/Reference/DistributionDefinitionRef/)

### Secondary (MEDIUM confidence)
- [PyInstaller Manual](https://pyinstaller.org/)
- [Packaging PyQt6 applications](https://www.pythonguis.com/tutorials/packaging-pyqt6-applications-pyinstaller-macos-dmg/)

## Metadata

**Confidence breakdown:**
- py2app for rumps: HIGH - Official rumps documentation recommends it
- pkgbuild: HIGH - Apple's native tool, well-documented
- LaunchAgent: HIGH - Standard macOS pattern

**Research date:** 2026-01-31
**Valid until:** 2026-06-30 (6 months - stable patterns)
