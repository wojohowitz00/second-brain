---
category:
- '[[App Development]]'
- '[[Coding with AI]]'
- '[[Writing]]'
tags:
- personal
- projects
created: '2026-01-28'
updated: '2026-01-28'
---
# Second Brain macOS App

Native macOS GUI application for the Second Brain system.

## Building

1. Open `SecondBrain.xcodeproj` in Xcode
2. Select your development team in Signing & Capabilities
3. Build and run (⌘R)

## Requirements

- macOS 12.0 or later
- Python 3.9+ (system Python or via Homebrew)
- Xcode 14.0 or later

## Setup

1. Install Python dependencies:
   ```bash
   cd ~/SecondBrain/_scripts
   pip install -r requirements.txt
   ```

2. Configure the app:
   - Open the app
   - Go to Settings → Slack: Enter your Slack bot token, channel ID, and user ID
   - Go to Settings → LLM: Select your LLM provider and configure API keys/endpoints
   - Go to Settings → Obsidian: Select your vault path

3. Start the background service:
   - Go to Dashboard
   - Click "Start" to begin automatic processing

## Features

- **Dashboard**: System status, quick actions, and background service control
- **Messages**: View and manage Slack messages from your inbox channel
- **Vault Browser**: Browse your Obsidian vault files
- **Logs**: Real-time log viewing with filtering and search
- **Settings**: Configure Slack, LLM providers, and Obsidian vault

## Architecture

The app uses a hybrid approach:
- **SwiftUI**: Native macOS UI and system integration
- **Python Backend**: Existing scripts handle all business logic
- **Communication**: Subprocess execution with JSON data exchange

This preserves the proven Python logic while providing a modern native macOS experience.
