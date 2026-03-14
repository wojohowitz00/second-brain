---
plan: 01-02
status: complete
phase: 01-foundation
subsystem: safety
tags: [hooks, vault-guard, PreToolUse, python, settings]
depends_on: []
provides:
  - PreToolUse hook blocking vault writes to human PARA folders (01-04)
  - Hook registration in settings.json covering Write, Edit, and Bash tools
affects:
  - All future plans: vault write safety enforced from this point forward
  - 01-03 and beyond: Bash commands and Write/Edit calls to blocked paths will be intercepted
tech-stack:
  added: []
  patterns:
    - Claude Code PreToolUse hook pattern (stdin JSON -> exit 0/2)
    - $CLAUDE_PROJECT_DIR for portable hook path resolution
key-files:
  created:
    - .claude/hooks/vault-write-guard.py
    - .claude/settings.json
  modified: []
decisions:
  - "Hook registered in settings.json (committed), not settings.local.json (machine-local)"
  - "Bash blocking is best-effort; Write/Edit are primary enforcement"
  - "$CLAUDE_PROJECT_DIR used instead of hardcoded path for portability"
metrics:
  duration: "~79 seconds"
  completed: "2026-03-14"
---

# Phase 1 Plan 2: Vault Write Guard Summary

One-liner: PreToolUse hook in Python that blocks Write/Edit/Bash to Obsidian's human PARA folders (01-04) via exit code 2, with $CLAUDE_PROJECT_DIR-based registration in settings.json.

## What Was Built

- `.claude/hooks/vault-write-guard.py` — Python PreToolUse hook that reads JSON from stdin, checks tool_name and tool_input, and exits 2 with a clear stderr message if any Write, Edit, or MultiEdit targets a blocked vault prefix, or if a Bash command contains a blocked prefix with a write-indicating shell pattern
- `.claude/settings.json` — Hook registration file (committed, not machine-local) that maps the PreToolUse event for Write|Edit|Bash tools to the guard script using `$CLAUDE_PROJECT_DIR` for portable path resolution

## Tasks Completed

| Task | Commit | Files |
|------|--------|-------|
| Task 1: Create vault-write-guard.py hook | 6408264 | `.claude/hooks/vault-write-guard.py` |
| Task 2: Create settings.json hook registration | 82ae52c | `.claude/settings.json` |

## Verification Results

All test cases passed:
- Blocked path (`01_Projects/test.md`): exit 2, stderr "VAULT WRITE BLOCKED"
- Allowed AI workspace (`05_AI_Workspace/test.md`): exit 0
- Non-vault path (`second-brain/README.md`): exit 0
- Bash write to blocked path: exit 2

## Deviations

None — plan executed exactly as written.

## Human Verification Required

The hook will activate the next time Claude Code starts a session in this project directory. To verify it's live:
1. Attempt a Write to any path under the vault's `01_Projects/`, `02_Areas_of_Interest/`, `03_Research/`, or `04_Archive/`
2. Confirm Claude receives the "VAULT WRITE BLOCKED" error and does not proceed
3. Confirm writes to `05_AI_Workspace/` and non-vault paths succeed normally

## Next Phase Readiness

This hook is the foundational safety boundary for all subsequent phases. Phases 01-03 onwards can safely use Write/Edit tools in `05_AI_Workspace/` knowing human PARA folders are protected.
