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
# Setup with uv

The app now uses `uv` for Python package and environment management, which simplifies setup and avoids Python environment issues.

## Prerequisites

Install `uv` if you haven't already:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Or with Homebrew:

```bash
brew install uv
```

## Setup Steps

### 1. Navigate to scripts directory

```bash
cd ~/SecondBrain/_scripts
```

Or if your scripts are in the project directory:

```bash
cd /Users/richardyu/PARA/1_projects/coding/second_brain/_scripts
```

### 2. Create virtual environment with uv

```bash
uv venv
```

This creates a `.venv` directory automatically.

### 3. Install dependencies

```bash
uv pip install -r requirements.txt
```

That's it! `uv` handles everything automatically.

## How It Works

The app automatically detects and uses `uv` if it's installed. When you run scripts:

1. The app looks for `uv` in common locations (`/opt/homebrew/bin/uv`, `/usr/local/bin/uv`, etc.)
2. If found, it uses `uv run python script.py` which automatically:
   - Uses the virtual environment in `_scripts/.venv`
   - Installs missing packages on-the-fly
   - Handles all Python environment management
3. If `uv` is not found, it falls back to direct Python execution

## Benefits

- ✅ No Python version conflicts
- ✅ Automatic dependency management
- ✅ Works with macOS's protected Python
- ✅ Faster package installation
- ✅ Automatic virtual environment handling

## Verify Setup

After setup, verify everything works:

```bash
cd ~/SecondBrain/_scripts
uv run python -c "import anthropic; print('✓ anthropic installed')"
uv run python -c "import openai; print('✓ openai installed')"
```

## Troubleshooting

**If `uv` is not found:**
- Install it: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- Or add it to your PATH if installed elsewhere

**If scripts still fail:**
- Make sure you're in the `_scripts` directory when running `uv venv`
- Check that `requirements.txt` exists in `_scripts/`
- Try: `uv pip sync requirements.txt` to ensure all packages are installed

## Updating Dependencies

To update packages later:

```bash
cd ~/SecondBrain/_scripts
uv pip install -r requirements.txt --upgrade
```

## App Usage

Once set up, the app will automatically use `uv` to run all Python scripts. No additional configuration needed!
