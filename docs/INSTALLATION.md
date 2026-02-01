# Second Brain Installation Guide

Step-by-step instructions for installing and configuring Second Brain.

---

## Table of Contents

1. [System Requirements](#system-requirements)
2. [Prerequisites](#prerequisites)
3. [Installation Methods](#installation-methods)
4. [Slack Setup](#slack-setup)
5. [Vault Setup](#vault-setup)
6. [First Run](#first-run)
7. [Launch on Login](#launch-on-login)
8. [Updating](#updating)
9. [Uninstalling](#uninstalling)

---

## System Requirements

| Requirement | Minimum | Recommended |
|-------------|---------|-------------|
| macOS | 11 Big Sur | 14 Sonoma+ |
| RAM | 8 GB | 16 GB |
| Disk Space | 5 GB free | 10 GB free |
| Architecture | Intel or Apple Silicon | Apple Silicon |

**Note**: Apple Silicon (M1/M2/M3) provides significantly faster AI classification.

---

## Prerequisites

### 1. Ollama

Ollama runs the local AI model. Install it first:

```bash
# Using Homebrew (recommended)
brew install ollama

# Or download from website
open https://ollama.ai
```

After installation, start Ollama:
```bash
ollama serve
```

Download the required model:
```bash
ollama pull llama3.2:latest
```

Verify it's working:
```bash
ollama list
# Should show: llama3.2:latest
```

### 2. Obsidian Vault

You need an Obsidian vault with PARA folder structure:

```
~/PARA/                          # or your vault location
├── Personal/
│   ├── 1_Projects/
│   ├── 2_Areas/
│   ├── 3_Resources/
│   └── 4_Archives/
├── Work/
│   ├── 1_Projects/
│   ├── 2_Areas/
│   ├── 3_Resources/
│   └── 4_Archives/
└── .obsidian/                   # required for vault detection
```

**Creating a new vault:**
```bash
mkdir -p ~/PARA/{Personal,Work}/{1_Projects,2_Areas,3_Resources,4_Archives}
mkdir ~/PARA/.obsidian
```

Then open in Obsidian: **File → Open folder as vault → Select ~/PARA**

### 3. Slack Workspace

You need a Slack workspace where you can create apps/bots.

---

## Installation Methods

### Method A: Package Installer (Recommended)

1. **Download the installer:**
   ```bash
   # From project directory
   ls pkg/SecondBrain-1.0.0.pkg
   ```

2. **Run the installer:**
   - Double-click `SecondBrain-1.0.0.pkg`
   - Follow the prompts
   - Enter your password when asked

   Or via command line:
   ```bash
   sudo installer -pkg pkg/SecondBrain-1.0.0.pkg -target /
   ```

3. **Verify installation:**
   ```bash
   ls /Applications/Second\ Brain.app
   ```

### Method B: Build from Source

1. **Clone the repository:**
   ```bash
   git clone https://github.com/wojohowitz00/second-brain.git
   cd second-brain
   ```

2. **Install dependencies:**
   ```bash
   cd backend
   uv sync
   ```

3. **Build the app:**
   ```bash
   cd ..
   ./scripts/build_app.sh
   ```

4. **Build the installer (optional):**
   ```bash
   ./scripts/build_pkg.sh
   ```

5. **Run directly (development):**
   ```bash
   cd backend
   uv run python _scripts/menu_bar_app.py
   ```

---

## Slack Setup

### Create a Slack App

1. Go to https://api.slack.com/apps
2. Click **Create New App**
3. Choose **From scratch**
4. Name: `Second Brain`
5. Select your workspace
6. Click **Create App**

### Configure Bot Permissions

1. In your app settings, go to **OAuth & Permissions**
2. Under **Scopes → Bot Token Scopes**, add:
   - `channels:history` — Read messages from channels
   - `channels:read` — Access channel info
   - `chat:write` — Post replies
   - `im:write` — Send direct messages (optional)

3. Click **Install to Workspace**
4. Copy the **Bot User OAuth Token** (starts with `xoxb-`)

### Create Inbox Channel

1. In Slack, create a new channel: `#sb-inbox`
2. Make it private (recommended for privacy)
3. Invite your bot: `/invite @Second Brain`
4. Get the Channel ID:
   - Right-click channel name → **View channel details**
   - Scroll down to find Channel ID (starts with `C`)

### Get Your User ID

1. Click your profile in Slack
2. Click **Profile**
3. Click **More** (three dots)
4. **Copy member ID** (starts with `U`)

### Save Credentials

Create the environment file:
```bash
cd /Applications/Second\ Brain.app/Contents/Resources/backend/_scripts/
# Or for source install:
cd second-brain/backend/_scripts/

cp .env.example .env
chmod 600 .env
```

Edit `.env`:
```bash
SLACK_BOT_TOKEN=xoxb-your-actual-token-here
SLACK_CHANNEL_ID=C0123456789
SLACK_USER_ID=U0123456789
```

---

## Vault Setup

### Default Location

Second Brain looks for your vault at `~/PARA` by default.

### Custom Location

During first run, the setup wizard will ask for your vault path. You can:
1. Accept the default (`~/PARA`)
2. Browse to select a different location
3. Type a custom path

### Vault Requirements

Your vault must have:
- A `.obsidian/` folder (confirms it's an Obsidian vault)
- At least one domain folder (e.g., `Personal/`)
- PARA subfolders are optional but recommended

### Multiple Domains

Second Brain discovers domains automatically from your top-level folders:
```
~/PARA/
├── Personal/     # Domain: Personal
├── Work/         # Domain: Work
├── Side_Projects/# Domain: Side_Projects
└── .obsidian/
```

---

## First Run

### Launch the App

```bash
open /Applications/Second\ Brain.app
```

Or find **Second Brain** in Spotlight (Cmd+Space).

### Setup Wizard

The wizard walks through:

1. **Welcome** — Introduction
2. **Ollama Check** — Verifies Ollama is installed and running
3. **Model Download** — Downloads llama3.2 if needed (~2GB)
4. **Vault Config** — Set or confirm vault path
5. **Slack Credentials** — Enter and validate tokens
6. **Complete** — Ready to use

### After Setup

- Menu bar icon appears (🧠)
- App starts polling Slack every 2 minutes
- Post a test message to `#sb-inbox`
- Click **Sync Now** to process immediately
- Check **Recent Activity** to verify filing

---

## Launch on Login

### Enable Auto-Start

Run the install script:
```bash
./scripts/install_launchagent.sh
```

This copies the LaunchAgent plist to `~/Library/LaunchAgents/` and loads it.

### Verify

```bash
launchctl list | grep secondbrain
# Should show: com.secondbrain.app
```

### Disable Auto-Start

```bash
./scripts/uninstall.sh --launchagent-only
```

This removes the LaunchAgent but keeps the app installed.

---

## Updating

### Package Update

1. Download the new `.pkg` file
2. Run the installer (it will overwrite the old version)
3. Restart the app

### Source Update

```bash
cd second-brain
git pull origin main
./scripts/build_app.sh
```

### Preserving Settings

Your settings are stored in:
- `backend/_scripts/.env` — Slack credentials
- `backend/_scripts/.state/` — Processing state

These are preserved during updates.

---

## Uninstalling

### Complete Removal

```bash
./scripts/uninstall.sh
```

This removes:
- The application from `/Applications`
- The LaunchAgent (if installed)
- Log files in `/tmp`

### What's Preserved

The uninstaller does NOT remove:
- Your Obsidian vault files
- Your `.env` credentials (manual backup recommended)
- Your `.state/` processing history

### Manual Cleanup

If needed:
```bash
# Remove app manually
rm -rf /Applications/Second\ Brain.app

# Remove LaunchAgent manually
launchctl unload ~/Library/LaunchAgents/com.secondbrain.app.plist
rm ~/Library/LaunchAgents/com.secondbrain.app.plist

# Remove logs
rm /tmp/secondbrain.*.log
```

---

## Verifying Installation

### Quick Checks

1. **App launches:**
   ```bash
   open /Applications/Second\ Brain.app
   ```
   Menu bar icon should appear.

2. **Ollama running:**
   ```bash
   curl http://localhost:11434/api/tags
   ```
   Should return JSON with model list.

3. **Slack connected:**
   Click menu bar icon → **Health**
   Should show "Slack: ✓ Connected"

4. **Test message:**
   Post to `#sb-inbox`: "Test message from installation"
   Click **Sync Now**
   Check **Recent Activity**

### Troubleshooting

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for common issues.

---

*Last updated: 2026-01-31 | Version: v1.0.0*
