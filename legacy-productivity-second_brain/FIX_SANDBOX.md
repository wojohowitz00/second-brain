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
# Fixing App Sandbox Error

The error "xcrun: error: cannot be used within an App Sandbox" occurs because macOS App Sandbox is blocking Python script execution.

## Solution 1: Disable App Sandbox (Easiest - Recommended for Personal Use)

1. Open Xcode
2. Select your project (blue icon) in the sidebar
3. Select the **SecondBrain** target
4. Go to **Signing & Capabilities** tab
5. Click the **"-"** button next to **App Sandbox** to remove it
6. Build and run again (⌘R)

**Note:** This disables sandboxing entirely. Fine for personal use, but not App Store compliant.

## Solution 2: Add Entitlements (App Store Compatible)

1. Open Xcode
2. Select your project (blue icon) in the sidebar
3. Select the **SecondBrain** target
4. Go to **Signing & Capabilities** tab
5. Click **"+ Capability"** and add:
   - **App Sandbox** (if not already added)
   - **Hardened Runtime**
6. In **App Sandbox**, enable:
   - ✅ **Outgoing Connections (Client)**
   - ✅ **User Selected File** (Read/Write)
7. Go to **Build Settings** tab
8. Search for "Code Signing Entitlements"
9. Set it to: `SecondBrain/SecondBrain/SecondBrain/Resources/SecondBrain.entitlements`
10. Build and run again (⌘R)

## Solution 3: Use Full Disk Access (Alternative)

If the above don't work:

1. Open **System Settings** → **Privacy & Security**
2. Scroll down to **Full Disk Access**
3. Click the **"+"** button
4. Navigate to your app: `/Users/richardyu/Library/Developer/Xcode/DerivedData/SecondBrain-*/Build/Products/Debug/SecondBrain.app`
5. Add it and enable the toggle
6. Restart the app

## Why This Happens

macOS App Sandbox restricts what apps can do for security. Running external scripts (like Python) requires special permissions. For a personal knowledge management app, disabling the sandbox is usually fine.

## After Fixing

Once you've applied one of the solutions above:
1. Restart the app
2. Go to Dashboard
3. Click "Start" to begin background processing
4. The error should be gone!
