#!/usr/bin/env python3
"""
vault-write-guard.py — PreToolUse hook
Blocks Claude from writing to human PARA folders (01-04) in the Obsidian vault.
Exit code semantics: 0=proceed, 2=block (stderr sent to Claude as explanation).
Note: Bash blocking is best-effort — Write/Edit are the primary enforcement points.
"""
import json
import sys
import re

VAULT_ROOT = "/Users/richardyu/Library/Mobile Documents/iCloud~md~obsidian/Documents/Home"
BLOCKED_PREFIXES = [
    f"{VAULT_ROOT}/01_Projects",
    f"{VAULT_ROOT}/02_Areas_of_Interest",
    f"{VAULT_ROOT}/03_Research",
    f"{VAULT_ROOT}/04_Archive",
]

def is_blocked_path(file_path: str) -> bool:
    """Return True if file_path targets a human PARA folder."""
    return any(file_path.startswith(prefix) for prefix in BLOCKED_PREFIXES)

def block(reason: str) -> None:
    """Print reason to stderr and exit 2 (blocking)."""
    print(f"VAULT WRITE BLOCKED\n{reason}\nAI writes must target 05_AI_Workspace/ only.", file=sys.stderr)
    sys.exit(2)

input_data = json.load(sys.stdin)
tool_name = input_data.get("tool_name", "")
tool_input = input_data.get("tool_input", {})

# Write and Edit: file_path is explicit
if tool_name in ("Write", "Edit", "MultiEdit"):
    file_path = tool_input.get("file_path", "")
    if is_blocked_path(file_path):
        block(f"Attempted path: {file_path}")

# Bash: check command string for vault write patterns (best-effort)
if tool_name == "Bash":
    command = tool_input.get("command", "")
    for prefix in BLOCKED_PREFIXES:
        if prefix in command and re.search(r"(>|>>|\btee\b|\bcp\b|\bmv\b|\btouch\b|\bmkdir\b)", command):
            block(f"Bash command references blocked path: {prefix}")

sys.exit(0)
