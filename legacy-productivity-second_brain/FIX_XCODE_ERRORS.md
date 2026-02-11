---
category:
- '[[Coding with AI]]'
- '[[App Development]]'
tags:
- evergreen
- personal
- projects
created: '2026-01-28'
updated: '2026-01-28'
---
# Fix Xcode "Cannot find in scope" Errors

The errors mean the View files aren't added to your Xcode project target. Here's how to fix it:

## Quick Fix

### Option 1: Add Files to Target (Recommended)

1. **In Xcode**, look at the file navigator (left sidebar)
2. **Find the Views files** - they might be there but grayed out (not in target)
3. **Select each View file** (DashboardView.swift, MessagesView.swift, etc.)
4. **Open the File Inspector** (right sidebar, or View → Inspectors → File)
5. **Under "Target Membership"**, check ✅ **SecondBrain**
6. **Do this for ALL View files:**
   - DashboardView.swift
   - MessagesView.swift
   - VaultBrowserView.swift
   - LogsView.swift
   - SettingsView.swift
   - SlackSettingsView.swift
   - LLMSettingsView.swift
   - ObsidianSettingsView.swift

7. **Also check Models and Services:**
   - Models/AppSettings.swift
   - Models/Message.swift
   - Services/KeychainManager.swift
   - Services/PythonBridge.swift
   - Services/BackgroundService.swift

8. **Build again** (⌘B)

### Option 2: Re-add Files

If Option 1 doesn't work:

1. **Remove files from project** (right-click → Delete → "Remove Reference")
2. **Re-add them** using "Add Files to 'SecondBrain'..."
3. **Make sure "Add to targets: SecondBrain" is checked**

### Option 3: Check File Location

Make sure files are in the right place:
- Views should be in: `SecondBrain/SecondBrain/SecondBrain/Views/`
- Models should be in: `SecondBrain/SecondBrain/SecondBrain/Models/`
- Services should be in: `SecondBrain/SecondBrain/SecondBrain/Services/`

## Verify Files Are in Target

After fixing, you should see:
- Files are **not grayed out** in the navigator
- When you select a file, File Inspector shows ✅ SecondBrain checked
- Build succeeds without "Cannot find in scope" errors

## If Still Not Working

Try cleaning the build:
1. **Product → Clean Build Folder** (⇧⌘K)
2. **Build again** (⌘B)
