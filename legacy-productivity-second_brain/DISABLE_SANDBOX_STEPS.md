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
# How to Disable App Sandbox in Xcode

## Method 1: Via Project Settings (Most Common)

1. **Open Xcode**
2. **Click on the blue project icon** at the very top of the left sidebar (it says "SecondBrain" or your project name)
3. **In the main editor area**, you should see tabs at the top:
   - General
   - **Signing & Capabilities** ← Click this tab
   - Build Settings
   - Build Phases
   - Build Rules
   - Info
4. If you don't see "Signing & Capabilities", try:
   - Make sure you clicked the **blue project icon** (not a folder)
   - Make sure you selected the **SecondBrain** target in the TARGETS list (below PROJECTS)
   - The tabs might be hidden - try clicking "Show" if there's a toggle

## Method 2: Via Build Settings (Alternative)

1. **Open Xcode**
2. **Click on the blue project icon** at the top of the left sidebar
3. **Select "SecondBrain"** under TARGETS (not PROJECTS)
4. Click the **"Build Settings"** tab
5. **Search for "sandbox"** in the search box
6. Find **"Enable App Sandbox"**
7. **Change it from "Yes" to "No"** (double-click the value)

## Method 3: Direct Edit (If UI Doesn't Work)

If you can't find it in the UI, you can edit the project file directly:

1. **Close Xcode** (important!)
2. Open Terminal
3. Run:
   ```bash
   cd /Users/richardyu/PARA/1_projects/coding/second_brain/SecondBrain/SecondBrain/SecondBrain.xcodeproj
   sed -i '' 's/ENABLE_APP_SANDBOX = YES;/ENABLE_APP_SANDBOX = NO;/g' project.pbxproj
   ```
4. **Reopen Xcode**
5. Build and run again

## Visual Guide

When you click the blue project icon, you should see something like:

```
┌─────────────────────────────────────────┐
│ PROJECTS          TARGETS                │
│ SecondBrain       SecondBrain            │
│                  ┌─────────────────────┐ │
│                  │ General            │ │
│                  │ Signing &          │ │ ← Click here
│                  │   Capabilities     │ │
│                  │ Build Settings     │ │
│                  └─────────────────────┘ │
└─────────────────────────────────────────┘
```

## What to Look For

Once you're in "Signing & Capabilities":
- You should see a section called **"App Sandbox"**
- It will have a **"-"** button on the left
- Click that **"-"** button to remove it
- Or uncheck **"App Sandbox"** if it's a checkbox

## Still Can't Find It?

Try this:
1. **Product → Scheme → Edit Scheme...**
2. Click **"Run"** on the left
3. Go to **"Options"** tab
4. Look for sandbox-related settings there

Or:
1. **File → Project Settings...**
2. Look for sandbox settings

## After Disabling

1. **Clean build folder**: Product → Clean Build Folder (⇧⌘K)
2. **Build**: Product → Build (⌘B)
3. **Run**: Product → Run (⌘R)

The error should be gone!
