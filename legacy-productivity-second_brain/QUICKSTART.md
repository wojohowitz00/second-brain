---
category:
- '[[Coding with AI]]'
- '[[App Development]]'
tags:
- personal
- projects
created: '2026-01-28'
updated: '2026-01-28'
---
# Quick Start Guide - Running Second Brain macOS App

## Prerequisites

1. **Xcode** (14.0 or later)
   - Install from Mac App Store or [developer.apple.com](https://developer.apple.com/xcode/)

2. **Python 3.9+** (you have Python 3.13.9 ✅)

3. **Python dependencies**
   ```bash
   cd ~/SecondBrain/_scripts
   pip3 install -r requirements.txt
   ```

## Step 1: Create Xcode Project

Since we created the Swift files but need a proper Xcode project, you have two options:

### Option A: Create New Xcode Project (Recommended)

1. Open Xcode
2. File → New → Project
3. Choose **macOS** → **App**
4. Product Name: `SecondBrain`
5. Interface: **SwiftUI**
6. Language: **Swift**
7. Save location: Choose `/Users/richardyu/PARA/1_projects/coding/second_brain/SecondBrain`
8. Click **Create**

9. **Replace the default files:**
   - Delete the default `ContentView.swift` and `SecondBrainApp.swift` if they exist
   - Drag all files from `SecondBrain/SecondBrain/` into the Xcode project
   - Make sure "Copy items if needed" is checked
   - Add to target: SecondBrain

### Option B: Use Command Line (Faster)

```bash
cd /Users/richardyu/PARA/1_projects/coding/second_brain/SecondBrain

# Create Xcode project using xcodegen or manually
# For now, let's use Xcode GUI method above
```

## Step 2: Install Python Dependencies

```bash
cd ~/SecondBrain/_scripts
pip3 install -r requirements.txt
```

If you don't have `~/SecondBrain` yet:
```bash
mkdir -p ~/SecondBrain/_scripts
cp -r /Users/richardyu/PARA/1_projects/coding/second_brain/_scripts/* ~/SecondBrain/_scripts/
cd ~/SecondBrain/_scripts
pip3 install -r requirements.txt
```

## Step 3: Build and Run

1. In Xcode, select your Mac as the run destination (top toolbar)
2. Press **⌘R** (or click the Play button)
3. If you see signing errors:
   - Select the project in navigator
   - Go to "Signing & Capabilities"
   - Select your Apple ID team (or enable "Automatically manage signing")

## Step 4: Configure the App

When the app launches:

1. **Go to Settings → Slack:**
   - Enter your Slack Bot Token (starts with `xoxb-`)
   - Enter your Channel ID (starts with `C`)
   - Enter your User ID (starts with `U`)

2. **Go to Settings → LLM:**
   - Select your provider (Anthropic, OpenAI, Ollama, or LM Studio)
   - Enter API key if needed
   - For local models: Enter endpoint and select model

3. **Go to Settings → Obsidian:**
   - Click "Browse..." and select your Obsidian vault folder
   - Usually `~/SecondBrain` or wherever your vault is

4. **Click "Save" in each settings tab**

## Step 5: Start Background Service

1. Go to **Dashboard**
2. Click **"Start"** button
3. The app will now automatically:
   - Process inbox every 2 minutes
   - Run fix handler every 5 minutes
   - Check health every hour

## Troubleshooting

### "Python script not found"
- Make sure `~/SecondBrain/_scripts/` exists and contains all Python files
- Check that PythonBridge.swift is looking in the right location

### "Module not found" errors
- Run: `pip3 install -r ~/SecondBrain/_scripts/requirements.txt`

### Signing errors in Xcode
- Go to Signing & Capabilities
- Select your team or enable "Automatically manage signing"

### App won't start
- Check Console.app for error messages
- Make sure Python 3 is accessible: `which python3`

## Testing

1. **Test Slack connection:**
   - Settings → Slack → "Test Connection"

2. **Test LLM:**
   - Settings → LLM → "Test Connection"

3. **Manual processing:**
   - Dashboard → "Process Inbox" button

4. **View logs:**
   - Logs tab → See real-time processing

## Next Steps

- Post a message to your `#wry_sb` Slack channel
- Watch it get processed in the Messages view
- Check the Vault Browser to see the created file
- View logs to see what's happening
