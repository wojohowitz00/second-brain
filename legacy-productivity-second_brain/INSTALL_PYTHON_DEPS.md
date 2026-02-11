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
# Install Python Dependencies

The error "ModuleNotFoundError: No module named 'anthropic'" means Python dependencies aren't installed.

## Quick Fix

Open Terminal and run:

```bash
# Install dependencies
pip3 install -r ~/SecondBrain/_scripts/requirements.txt
```

Or if your scripts are in the project directory:

```bash
cd /Users/richardyu/PARA/1_projects/coding/second_brain/_scripts
pip3 install -r requirements.txt
```

## What Gets Installed

- `requests` - HTTP requests for Slack API
- `PyYAML` - YAML parsing for Obsidian frontmatter
- `anthropic` - Anthropic Claude API client
- `openai` - OpenAI API client
- `keyring` - macOS Keychain access (optional)

## Verify Installation

After installing, verify:

```bash
python3 -c "import anthropic; print('✓ anthropic installed')"
python3 -c "import openai; print('✓ openai installed')"
python3 -c "import yaml; print('✓ PyYAML installed')"
```

## After Installing

1. Restart the SecondBrain app
2. Go to Dashboard
3. Click "Start" to begin background processing
4. The error should be gone!

## Troubleshooting

**If pip3 doesn't work:**
- Try `pip` instead of `pip3`
- Or `python3 -m pip install -r requirements.txt`

**If you get permission errors:**
- Use `pip3 install --user -r requirements.txt` to install for your user only

**If modules still not found:**
- Check which Python the app is using: The app uses `/usr/bin/python3` by default
- You might need to install to that specific Python: `/usr/bin/python3 -m pip install -r requirements.txt`
