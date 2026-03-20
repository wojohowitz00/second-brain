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
# Manual Setup - Run These Commands

Since the script isn't running, here are the exact commands to run manually:

## Step 1: Install Python Dependencies

```bash
cd /Users/richardyu/PARA/1_projects/coding/second_brain/_scripts
pip3 install -r requirements.txt
```

This will install:
- requests
- PyYAML
- anthropic
- openai
- keyring

## Step 2: Verify Everything is Ready

```bash
# Check Python
python3 --version

# Check scripts exist
ls -la /Users/richardyu/PARA/1_projects/coding/second_brain/_scripts/*.py

# Check Swift files exist
ls -la /Users/richardyu/PARA/1_projects/coding/second_brain/SecondBrain/SecondBrain/
```

## Step 3: Create Xcode Project

**Open Xcode and follow these steps:**

1. **File → New → Project**
2. Choose **macOS** → **App** → **Next**
3. Fill in:
   - Product Name: `SecondBrain`
   - Team: (select your Apple ID)
   - Organization Identifier: `com.yourname`
   - Interface: **SwiftUI** ⚠️ Important!
   - Language: **Swift**
   - Storage: **None**
4. Click **Next**
5. Navigate to: `/Users/richardyu/PARA/1_projects/coding/second_brain/SecondBrain`
6. Click **Create**

## Step 4: Add Swift Files to Xcode

1. In Xcode, you'll see a `SecondBrain` folder (blue icon) in the left sidebar
2. **Right-click** on it → **Add Files to "SecondBrain"...**
3. Navigate to: `SecondBrain/SecondBrain/` folder
4. **Select ALL** these items:
   - `SecondBrainApp.swift`
   - `ContentView.swift`
   - `Models` folder (entire folder)
   - `Services` folder (entire folder)
   - `Views` folder (entire folder)
   - `Resources` folder (entire folder)
5. **Important checkboxes:**
   - ✅ **Copy items if needed** (check this!)
   - ✅ **Add to targets: SecondBrain** (should be checked)
6. Click **Add**

## Step 5: Configure Build Settings

1. Click on the **blue project icon** at the top of the sidebar
2. Select **SecondBrain** under TARGETS
3. Go to **General** tab
4. Set **Minimum Deployments** to **macOS 12.0**

## Step 6: Build and Run

1. At the top toolbar, select your Mac as the destination (next to the Play button)
2. Press **⌘R** (or click the Play button)
3. If you see signing errors:
   - Still in the project settings, go to **Signing & Capabilities** tab
   - Select your **Team** (your Apple ID)
   - Or check **"Automatically manage signing"**

## Step 7: Configure the App

When the app launches:

1. **Settings → Slack:**
   - Enter your Slack Bot Token
   - Enter Channel ID
   - Enter User ID
   - Click **Save**

2. **Settings → LLM:**
   - Select provider
   - Enter API key/endpoint
   - Click **Save**

3. **Settings → Obsidian:**
   - Click **Browse...**
   - Select your vault folder
   - Click **Save**

4. **Dashboard:**
   - Click **Start** button

## Troubleshooting

**If you see "No such module" errors:**
- Make sure all files were added to the target
- Try: **Product → Clean Build Folder** (⇧⌘K)
- Then build again (⌘B)

**If Python scripts aren't found:**
- The app looks for `~/SecondBrain/_scripts/`
- Copy scripts: `cp -r /Users/richardyu/PARA/1_projects/coding/second_brain/_scripts ~/SecondBrain/_scripts`

**If the app crashes:**
- Check Console.app for error messages
- Make sure Python dependencies are installed

## Quick Test

After setup, test that Python scripts work:

```bash
cd ~/SecondBrain/_scripts
python3 -c "from llm_provider import get_provider; print('LLM provider OK')"
python3 -c "from slack_client import fetch_messages; print('Slack client OK')"
```

If both print "OK", you're ready to go!
