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
# Add Files to Xcode - Quick Guide

The Swift files have been created. Now add them to your Xcode project:

## Step-by-Step:

1. **In Xcode**, right-click on the **`SecondBrain`** folder (blue icon) in the left sidebar

2. Select **"Add Files to 'SecondBrain'..."**

3. Navigate to: `/Users/richardyu/PARA/1_projects/coding/second_brain/SecondBrain/SecondBrain/SecondBrain/`

4. **Select these folders and files:**
   - ✅ `Models` folder (entire folder)
   - ✅ `Services` folder (entire folder) 
   - ✅ `Views` folder (entire folder)
   - ✅ `Resources` folder (entire folder)

5. **Important checkboxes:**
   - ✅ **"Copy items if needed"** (check this!)
   - ✅ **"Add to targets: SecondBrain"** (should be checked)
   - ✅ **"Create groups"** (not "Create folder references")

6. Click **"Add"**

## Verify:

After adding, you should see in Xcode:
- `Models/` folder with AppSettings.swift and Message.swift
- `Services/` folder with KeychainManager.swift, PythonBridge.swift, BackgroundService.swift
- `Views/` folder with all the view files
- `Resources/` folder with Info.plist

## Build:

Press **⌘B** to build. If you see errors, make sure all files are added to the target.
