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
# Fix Python Dependencies Installation

macOS is blocking system Python package installation. Here are two solutions:

## Solution 1: Quick Fix (Use --break-system-packages)

Run this command:

```bash
pip3 install --break-system-packages --user -r ~/SecondBrain/_scripts/requirements.txt
```

The `--break-system-packages` flag bypasses the protection, and `--user` installs to your user directory (safer).

## Solution 2: Better Long-term Solution (Use Virtual Environment)

Update the app to use a virtual environment. This is the recommended approach.

### Step 1: Create/Use Virtual Environment

```bash
# Create venv in your vault directory
python3 -m venv ~/SecondBrain/_scripts/.venv

# Activate it
source ~/SecondBrain/_scripts/.venv/bin/activate

# Install dependencies
pip install -r ~/SecondBrain/_scripts/requirements.txt
```

### Step 2: Update PythonBridge to Use Venv

The app needs to be updated to use the virtual environment's Python. I can help update the code to detect and use the venv automatically.

## Verify Installation

After installing (either method), verify:

```bash
# For Solution 1 (system Python):
/usr/bin/python3 -c "import anthropic; print('✓ anthropic installed')"

# For Solution 2 (venv):
~/SecondBrain/_scripts/.venv/bin/python3 -c "import anthropic; print('✓ anthropic installed')"
```

## After Installing

1. **Restart the SecondBrain app**
2. Go to Dashboard
3. Click "Start"
4. The error should be gone!

## Why This Happens

macOS protects system Python to prevent breaking system tools. Using a virtual environment is the recommended approach, but `--break-system-packages --user` is safe for user-level installations.
