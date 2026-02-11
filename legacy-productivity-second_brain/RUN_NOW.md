---
category:
- '[[App Development]]'
- '[[Coding with AI]]'
tags:
- personal
- projects
created: '2026-01-28'
updated: '2026-01-28'
---
# How to Run the macOS App Right Now

## Quick Method (5 minutes)

### 1. Install Python Dependencies
```bash
cd /Users/richardyu/PARA/1_projects/coding/second_brain/_scripts
pip3 install -r requirements.txt
```

### 2. Create Xcode Project

**Option A: Use Xcode GUI (Easiest)**

1. Open **Xcode**
2. **File → New → Project**
3. Select **macOS** tab → **App** → **Next**
4. Fill in:
   - Product Name: `SecondBrain`
   - Team: (select your Apple ID)
   - Organization Identifier: `com.yourname` (or anything)
   - Interface: **SwiftUI**
   - Language: **Swift**
   - Storage: **None** (we'll add files manually)
5. Click **Next**
6. Navigate to: `/Users/richardyu/PARA/1_projects/coding/second_brain/SecondBrain`
7. **Uncheck** "Create Git repository" (optional)
8. Click **Create**

9. **Add Swift Files:**
   - In Xcode, right-click on the `SecondBrain` folder (blue icon) in the left sidebar
   - Select **Add Files to "SecondBrain"...**
   - Navigate to: `SecondBrain/SecondBrain/` folder
   - Select **ALL** the Swift files and folders:
     - `SecondBrainApp.swift`
     - `ContentView.swift`
     - `Models/` folder
     - `Services/` folder
     - `Views/` folder
     - `Resources/Info.plist`
   - Make sure **"Copy items if needed"** is checked
   - **Add to targets:** SecondBrain should be checked
   - Click **Add**

10. **Build Settings:**
    - Click on the project (blue icon) in sidebar
    - Select **SecondBrain** target
    - Go to **General** tab
    - Set **Minimum Deployments** to macOS 12.0

### 3. Build and Run

1. Select your Mac as the run destination (top toolbar, next to the Play button)
2. Press **⌘R** or click the **Play** button
3. If you see signing errors:
   - Select project → **Signing & Capabilities**
   - Choose your **Team** (your Apple ID)
   - Or enable **"Automatically manage signing"**

### 4. Configure the App

When the app launches:

1. **Settings → Slack:**
   - Bot Token: `xoxb-your-token-here`
   - Channel ID: `C0123456789`
   - User ID: `U0123456789`
   - Click **Save**

2. **Settings → LLM:**
   - Select provider (Anthropic, OpenAI, Ollama, or LM Studio)
   - Enter API key/endpoint as needed
   - Click **Save**

3. **Settings → Obsidian:**
   - Click **Browse...**
   - Select your vault folder (usually `~/SecondBrain`)
   - Click **Save**

4. **Dashboard:**
   - Click **Start** to begin background processing

## Alternative: Use Setup Script

```bash
cd /Users/richardyu/PARA/1_projects/coding/second_brain
./setup_macos_app.sh
```

Then follow the instructions it prints.

## Troubleshooting

**"No such module" errors:**
- Make sure all Swift files are added to the target
- Clean build folder: **Product → Clean Build Folder** (⇧⌘K)

**"Python script not found":**
- Make sure `~/SecondBrain/_scripts/` exists
- Copy scripts: `cp -r _scripts ~/SecondBrain/_scripts`

**App crashes on launch:**
- Check Console.app for errors
- Make sure Python dependencies are installed

**Can't find vault:**
- The app looks for `~/SecondBrain` by default
- You can change this in Settings → Obsidian

## What You'll See

- **Dashboard**: System status and quick actions
- **Messages**: View Slack messages from your inbox
- **Vault**: Browse your Obsidian files
- **Logs**: Real-time processing logs
- **Settings**: Configure everything

The app will automatically process messages every 2 minutes once you start the background service!
