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
# Create Xcode Project - Step by Step

The Xcode project file is missing. Let's create a proper one:

## Method 1: Create New Project in Xcode (Recommended)

1. **Open Xcode**

2. **File → New → Project** (or ⌘⇧N)

3. **Choose template:**
   - Select **macOS** tab at the top
   - Choose **App**
   - Click **Next**

4. **Configure project:**
   - Product Name: `SecondBrain`
   - Team: (select your Apple ID team)
   - Organization Identifier: `com.yourname` (or anything)
   - Interface: **SwiftUI** ⚠️ Important!
   - Language: **Swift**
   - Storage: **None**
   - Click **Next**

5. **Save location:**
   - Navigate to: `/Users/richardyu/PARA/1_projects/coding/second_brain/SecondBrain/`
   - **IMPORTANT:** Make sure you're saving INSIDE the existing `SecondBrain` folder
   - Click **Create**

6. **Xcode will create a new project structure**

7. **Now add the Swift files:**
   - In Xcode sidebar, right-click on `SecondBrain` folder
   - Select **"Add Files to 'SecondBrain'..."**
   - Navigate to: `SecondBrain/SecondBrain/SecondBrain/`
   - Select: `Models`, `Services`, `Views`, `Resources` folders
   - Check ✅ **"Copy items if needed"**
   - Check ✅ **"Add to targets: SecondBrain"**
   - Select **"Create groups"** (not folder references)
   - Click **Add**

8. **Replace default files:**
   - Delete the default `ContentView.swift` and `SecondBrainApp.swift` that Xcode created
   - The ones in `SecondBrain/SecondBrain/SecondBrain/` are the correct ones

9. **Build Settings:**
   - Click blue project icon → Select **SecondBrain** target
   - **General** tab → Set **Minimum Deployments** to **macOS 12.0**

10. **Build and Run:**
    - Press **⌘B** to build
    - Press **⌘R** to run

## Method 2: Use Command Line (Advanced)

If you prefer command line, you can use `xcodegen` but it requires additional setup. Method 1 above is simpler.

## What Happened?

The `.xcodeproj` folder existed but was missing the `project.pbxproj` file, which is the core project configuration. Creating a new project in Xcode will generate this file properly.

## After Creating Project

Once the project is created and files are added:

1. **Install Python dependencies:**
   ```bash
   cd ~/SecondBrain/_scripts
   pip3 install -r requirements.txt
   ```

2. **Configure app** when it launches:
   - Settings → Slack: Enter credentials
   - Settings → LLM: Select provider
   - Settings → Obsidian: Select vault path

3. **Start background service:**
   - Dashboard → Click "Start"
