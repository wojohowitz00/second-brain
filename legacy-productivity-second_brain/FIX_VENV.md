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
# Fix Virtual Environment Creation

The venv creation is failing because Python 3.13 blocks pip installation. Here's how to fix it:

## Solution: Create venv without pip, then install pip manually

```bash
# Remove the broken venv if it exists
rm -rf ~/SecondBrain/_scripts/.venv

# Create venv without pip
python3 -m venv --without-pip ~/SecondBrain/_scripts/.venv

# Activate it
source ~/SecondBrain/_scripts/.venv/bin/activate

# Download and install pip manually
curl https://bootstrap.pypa.io/get-pip.py -o /tmp/get-pip.py
python3 /tmp/get-pip.py --break-system-packages

# Now install dependencies
pip install -r ~/SecondBrain/_scripts/requirements.txt
```

## Alternative: Use uv (Easier)

Since you already have `uv` installed, use it instead:

```bash
# Remove the broken venv
rm -rf ~/SecondBrain/_scripts/.venv

# Create venv with uv
cd ~/SecondBrain/_scripts
uv venv

# Install dependencies
uv pip install -r requirements.txt
```

This is simpler and handles the pip installation automatically.

## Verify

After installing, verify:

```bash
~/SecondBrain/_scripts/.venv/bin/python3 -c "import anthropic; print('✓ anthropic installed')"
```

## After Setup

1. **Restart the SecondBrain app**
2. The app will automatically detect and use the `.venv` Python
3. Go to Dashboard and click "Start"
4. Everything should work!
