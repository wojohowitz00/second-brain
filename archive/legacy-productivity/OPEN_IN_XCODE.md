---
category:
- '[[App Development]]'
- '[[Coding with AI]]'
tags:
- evergreen
- personal
- projects
created: '2026-01-28'
updated: '2026-01-28'
---
# Open in Xcode - Quick Guide

All Swift files have been created! Here's how to add them to your Xcode project:

## Files Created

✅ **Models/** (2 files)
- AppSettings.swift
- Message.swift

✅ **Services/** (3 files)
- KeychainManager.swift
- PythonBridge.swift
- BackgroundService.swift

✅ **Views/** (8 files)
- SettingsView.swift
- SlackSettingsView.swift
- LLMSettingsView.swift
- ObsidianSettingsView.swift
- DashboardView.swift
- MessagesView.swift
- VaultBrowserView.swift
- LogsView.swift

✅ **Views/Components/** (2 files)
- StatusIndicator.swift
- LogEntryView.swift

✅ **Resources/** (1 file)
- Info.plist

✅ **Root files** (2 files)
- SecondBrainApp.swift (updated)
- ContentView.swift (updated)

## Step-by-Step: Add Files to Xcode

1. **Open Xcode** (if not already open)
   - Open: `/Users/richardyu/PARA/1_projects/coding/second_brain/SecondBrain/SecondBrain.xcodeproj`

2. **In Xcode sidebar**, right-click on the **`SecondBrain`** folder (blue icon)

3. Select **"Add Files to 'SecondBrain'..."**

4. **Navigate to:**
   ```
   /Users/richardyu/PARA/1_projects/coding/second_brain/SecondBrain/SecondBrain/SecondBrain/
   ```

5. **Select these folders:**
   - ✅ `Models` folder
   - ✅ `Services` folder
   - ✅ `Views` folder (includes Components subfolder)
   - ✅ `Resources` folder

6. **Important checkboxes:**
   - ✅ **"Copy items if needed"** (CHECK THIS!)
   - ✅ **"Add to targets: SecondBrain"** (should be checked)
   - ✅ **"Create groups"** (selected, not "Create folder references")

7. Click **"Add"**

## Verify Files Are Added

After adding, you should see in Xcode's file navigator:
```
SecondBrain/
├── SecondBrainApp.swift
├── ContentView.swift
├── Models/
│   ├── AppSettings.swift
│   └── Message.swift
├── Services/
│   ├── KeychainManager.swift
│   ├── PythonBridge.swift
│   └── BackgroundService.swift
├── Views/
│   ├── SettingsView.swift
│   ├── SlackSettingsView.swift
│   ├── LLMSettingsView.swift
│   ├── ObsidianSettingsView.swift
│   ├── DashboardView.swift
│   ├── MessagesView.swift
│   ├── VaultBrowserView.swift
│   ├── LogsView.swift
│   └── Components/
│       ├── StatusIndicator.swift
│       └── LogEntryView.swift
└── Resources/
    └── Info.plist
```

## Build Settings

1. Click on the **blue project icon** at the top of the sidebar
2. Select **SecondBrain** under TARGETS
3. Go to **General** tab
4. Set **Minimum Deployments** to **macOS 12.0**

## Build and Run

1. Select your Mac as the run destination (top toolbar)
2. Press **⌘B** to build
3. Fix any errors (see troubleshooting below)
4. Press **⌘R** to run

## Troubleshooting

**"No such module" or "Cannot find type" errors:**
- Make sure all files are added to the target
- Clean build folder: **Product → Clean Build Folder** (⇧⌘K)
- Build again: **⌘B**

**"PythonBridge" not found:**
- Make sure `Services/PythonBridge.swift` is added to the target
- Check that it's in the correct location

**Signing errors:**
- Go to **Signing & Capabilities** tab
- Select your **Team** (Apple ID)
- Or enable **"Automatically manage signing"**

## Next Steps After Building

1. **Install Python dependencies:**
   ```bash
   cd ~/SecondBrain/_scripts
   pip3 install -r requirements.txt
   ```

2. **Configure the app:**
   - Settings → Slack: Enter credentials
   - Settings → LLM: Select provider
   - Settings → Obsidian: Select vault path

3. **Start background service:**
   - Dashboard → Click "Start"

You're all set! 🎉
