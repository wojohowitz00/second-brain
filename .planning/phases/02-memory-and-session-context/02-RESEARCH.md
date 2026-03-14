# Phase 2: Memory and Session Context - Research

**Researched:** 2026-03-14
**Domain:** Claude Code memory system, session lifecycle hooks, stale task surfacing
**Confidence:** HIGH

---

## Summary

Phase 2 gives Claude persistent identity across sessions and makes stale work automatically visible. Three deliverables: (1) a seeded MEMORY.md that makes Claude aware of vault conventions, preferences, and reference pointers from the first session without manual prompting, (2) a SessionStart hook that surfaces stale tasks and upcoming deadlines as context at every session open, and (3) a SessionEnd hook that refreshes dashboard files in `05_AI_Workspace/dashboards/` automatically.

The Claude Code memory system is well-documented and the exact mechanism is verified. Auto memory lives at `~/.claude/projects/<project>/memory/MEMORY.md` — first 200 lines load automatically at session start. CLAUDE.md files handle "rules" (loaded in full); MEMORY.md handles "learned facts" (first 200 lines). The distinction matters for what to put where. For post-compaction re-injection of context, SessionStart fires with `source: "compact"` — no separate PostCompact handler is needed for context re-injection since PostCompact does NOT support `additionalContext`.

The key architectural insight: **context injection via SessionStart hooks is the right mechanism for surfacing dynamic data (stale tasks, deadlines)**. The hook script reads task files directly from the filesystem, computes staleness, and writes a compact context summary that is injected into Claude's context window via stdout. SessionEnd hooks handle dashboard refresh, but are constrained to a **1.5-second default timeout** — any dashboard refresh script must complete quickly or use `CLAUDE_CODE_SESSIONEND_HOOKS_TIMEOUT_MS` to increase the timeout.

**Primary recommendation:** Seed MEMORY.md manually with vault profile content. Write a SessionStart hook (bash or Python) that scans `tasks/` for stale items and emits plain-text context. Write a SessionEnd hook that triggers dashboard refresh with an extended timeout. Register both in `~/.claude/settings.json` (global, since they run for all sessions in this project root).

---

## Standard Stack

No external libraries. Everything uses Claude Code built-in mechanisms.

### Core

| Tool | Version | Purpose | Why Standard |
|------|---------|---------|--------------|
| Claude Code auto memory | v2.1.59+ (current: 2.1.74) | Persistent per-project memory via `MEMORY.md` | Native Claude Code feature, loads automatically every session |
| Claude Code SessionStart hook | Current | Inject dynamic context (stale tasks, deadlines) at session open | Only mechanism for programmatic context injection |
| Claude Code SessionEnd hook | Current | Trigger dashboard refresh at session close | Only mechanism for post-session cleanup automation |
| Python 3 (system) | System | Hook script runtime for task scanning | Consistent with existing `vault-write-guard.py` pattern |
| CLAUDE.md import syntax | Current | `@path/to/file` to pull in reference files | Loads content verbatim into session context |

### Supporting

| Tool | Purpose | When to Use |
|------|---------|-------------|
| `jq` | JSON parsing in bash hooks | If hook is bash rather than Python |
| `CLAUDE_CODE_SESSIONEND_HOOKS_TIMEOUT_MS` | Extend SessionEnd timeout beyond 1.5s | Required if dashboard refresh takes >1.5s |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|-----------|-----------|---------|
| MEMORY.md seeding | Only CLAUDE.md | CLAUDE.md is for rules/instructions; MEMORY.md is for learned facts/preferences — semantically correct to use both |
| SessionStart hook for stale tasks | Rely on /today command | /today requires manual invocation; hook fires automatically every session |
| SessionEnd hook for dashboard refresh | Scheduled cron | Hook is simpler, tied to actual usage; cron runs even when not using Claude |

**No npm/pip installs required.** This phase is pure configuration and scripting.

---

## Architecture Patterns

### Recommended File Structure

```
~/.claude/
├── settings.json                    # Global hooks — SessionStart + SessionEnd registered here
│                                    # (registered globally since this project is the primary project)
└── projects/-Users-richardyu-PARA-01-Projects-Personal-apps-second-brain/
    └── memory/
        ├── MEMORY.md                # Root memory file — 200-line limit for auto-load
        ├── vault-conventions.md     # Detailed vault structure (referenced by MEMORY.md)
        └── user-preferences.md     # User preferences (referenced by MEMORY.md)

second-brain/.claude/
├── hooks/
│   ├── vault-write-guard.py        # Phase 1 — already exists
│   ├── session-start.sh            # Phase 2 — surfaces stale tasks
│   └── session-end.sh              # Phase 2 — refreshes dashboards
└── settings.json                   # Phase 1 — already exists (PreToolUse hook)
                                    # Phase 2 — adds SessionStart/SessionEnd

05_AI_Workspace/dashboards/         # Already exists from Phase 1
└── tasks-by-status.md              # Refreshed by SessionEnd hook
```

**Decision: Register SessionStart/SessionEnd in `~/.claude/settings.json` (global) or `.claude/settings.json` (project)?**

The existing `~/.claude/settings.json` already has SessionStart (for `bd prime`). New hooks should be added there as additional entries in the SessionStart/SessionEnd arrays. This follows the established pattern. The project-level `.claude/settings.json` is for the vault write guard.

### Pattern 1: MEMORY.md Structure

**What:** The first 200 lines of `MEMORY.md` load automatically at every session start. Content beyond line 200 is not loaded. Claude keeps MEMORY.md concise and moves detail into topic files.

**Storage path (verified):** `~/.claude/projects/-Users-richardyu-PARA-01-Projects-Personal-apps-second-brain/memory/MEMORY.md`

This directory does NOT exist yet — it must be created by writing the file.

**How to seed manually:** Write the file directly. Claude will then read it and maintain it going forward. Auto memory is on by default (Claude Code 2.1.74 > required 2.1.59).

**What belongs in MEMORY.md (vs CLAUDE.md):**

| Content | CLAUDE.md | MEMORY.md |
|---------|-----------|-----------|
| "Always use bare ISO dates" | Yes (rule) | No |
| "Vault root is at ~/Library/Mobile Documents/..." | Yes (stable fact) | No |
| "User prefers task context stored in note body" | No | Yes (learned preference) |
| "YAML schema is at .planning/phases/01-foundation/yaml-frontmatter-schema.md" | Could be either | Yes (reference pointer) |
| "tasks/ has real files as of 2026-03-14" | No | Yes (learned state) |

**MEMORY.md initial content pattern:**

```markdown
# Second Brain — Memory

Last updated: 2026-03-14

## Vault Profile
- Vault root: /Users/richardyu/Library/Mobile Documents/iCloud~md~obsidian/Documents/Home/
- AI workspace: 05_AI_Workspace/ (only folder Claude writes to)
- PARA structure: 01_Projects, 02_Areas_of_Interest, 03_Research, 04_Archive
- Tasks live in: second-brain project /tasks/ folder (not vault)
- Projects: second-brain project /projects/ folder
- People: /people/, Ideas: /ideas/, Daily notes: /daily/

## Reference Pointers
- YAML schema: .planning/phases/01-foundation/yaml-frontmatter-schema.md
- Vault write policy: enforced by PreToolUse hook (vault-write-guard.py)
- Canonical task status values: backlog | active | waiting | blocked | done | someday
- Canonical task priority values: high | medium | low
- Date format rule: bare ISO (2026-03-14), NEVER quoted

## User Preferences
[Claude populates this as preferences are discovered]

## Key Patterns Learned
[Claude populates this as patterns emerge]
```

Keep MEMORY.md under 200 lines. Link to detail files (`vault-conventions.md`, etc.) for reference.

### Pattern 2: SessionStart Hook — Stale Task Surfacing

**What:** A script that runs at every session open, scans `tasks/` for stale or overdue items, and prints context to stdout. Claude receives this as session context.

**Output mechanism (verified from official docs):**
- Exit 0 + plain text stdout → text added directly as session context
- Exit 0 + JSON with `hookSpecificOutput.additionalContext` → also added as context
- Plain text is simpler; use it unless JSON structure is needed

**What to surface (from success criteria):**
- Overdue tasks: `due_date < today` AND `status != done`
- Stale tasks: last modified more than 7 days ago AND `status` in (active, waiting, blocked)
- Upcoming deadlines: `due_date` in next 7 days AND `status != done`

**Script approach — Python reading YAML frontmatter:**

```python
#!/usr/bin/env python3
"""
session-start.sh — SessionStart hook
Surfaces stale tasks and upcoming deadlines as session context.
"""
import sys
import os
import json
from datetime import date, timedelta
from pathlib import Path

TASKS_DIR = Path("/Users/richardyu/PARA/01_Projects/Personal/apps/second-brain/tasks")
TODAY = date.today()
STALE_DAYS = 7
UPCOMING_DAYS = 7

def parse_frontmatter(filepath):
    """Read YAML frontmatter from a markdown file. Returns dict or None."""
    try:
        content = filepath.read_text(encoding='utf-8')
        if not content.startswith('---'):
            return None
        end = content.find('---', 3)
        if end == -1:
            return None
        import yaml
        return yaml.safe_load(content[3:end])
    except Exception:
        return None
```

**Note on YAML parsing:** Python's `yaml` stdlib doesn't exist — use `pyyaml` (may not be installed) OR implement a minimal frontmatter parser for just the fields needed (`due_date`, `status`, `created`). A lightweight grep-based approach is more reliable in a hook context.

**Simpler approach — use grep/awk for frontmatter fields:**

```bash
#!/bin/bash
# session-start.sh — surfaces stale tasks at session start

TASKS_DIR="/Users/richardyu/PARA/01_Projects/Personal/apps/second-brain/tasks"
TODAY=$(date +%Y-%m-%d)
STALE_CUTOFF=$(date -v -7d +%Y-%m-%d 2>/dev/null || date -d "7 days ago" +%Y-%m-%d)

overdue=()
stale=()
upcoming=()

for f in "$TASKS_DIR"/*.md; do
  [ "$f" = "$TASKS_DIR/README.md" ] && continue
  [ -f "$f" ] || continue

  due_date=$(grep -m1 '^due_date:' "$f" | awk '{print $2}')
  status=$(grep -m1 '^status:' "$f" | awk '{print $2}')
  title=$(grep -m1 '^title:' "$f" | cut -d: -f2- | xargs)
  modified=$(stat -f "%Sm" -t "%Y-%m-%d" "$f" 2>/dev/null || stat -c "%y" "$f" | cut -d' ' -f1)

  [ "$status" = "done" ] && continue

  # Overdue
  if [ -n "$due_date" ] && [ "$due_date" \< "$TODAY" ]; then
    overdue+=("$title (due $due_date)")
  fi

  # Upcoming (due within 7 days, not overdue)
  if [ -n "$due_date" ] && [ "$due_date" \>= "$TODAY" ] && [ "$due_date" \<= "$(date -v +7d +%Y-%m-%d 2>/dev/null || date -d '+7 days' +%Y-%m-%d)" ]; then
    upcoming+=("$title (due $due_date)")
  fi

  # Stale (active/waiting/blocked, not touched in 7+ days, no upcoming due date)
  if [ -z "$due_date" ] && [ "$modified" \< "$STALE_CUTOFF" ]; then
    case "$status" in active|waiting|blocked)
      stale+=("$title (last touched $modified)")
    esac
  fi
done

# Output context
if [ ${#overdue[@]} -gt 0 ] || [ ${#upcoming[@]} -gt 0 ] || [ ${#stale[@]} -gt 0 ]; then
  echo "=== SESSION CONTEXT: Task Status ==="
  echo "Date: $TODAY"
  if [ ${#overdue[@]} -gt 0 ]; then
    echo ""
    echo "OVERDUE (${#overdue[@]} items):"
    for t in "${overdue[@]}"; do echo "  - $t"; done
  fi
  if [ ${#upcoming[@]} -gt 0 ]; then
    echo ""
    echo "DUE SOON — next 7 days (${#upcoming[@]} items):"
    for t in "${upcoming[@]}"; do echo "  - $t"; done
  fi
  if [ ${#stale[@]} -gt 0 ]; then
    echo ""
    echo "STALE — no activity in 7+ days (${#stale[@]} items):"
    for t in "${stale[@]}"; do echo "  - $t"; done
  fi
  echo "==================================="
fi

exit 0
```

**macOS date compatibility note:** `date -v -7d` is macOS BSD syntax. `date -d` is GNU/Linux. Use `date -v` for macOS.

### Pattern 3: SessionEnd Hook — Dashboard Refresh

**What:** A script that fires when a session ends and rewrites the Dataview dashboard files in `05_AI_Workspace/dashboards/`.

**Critical constraint (verified):** SessionEnd default timeout is **1.5 seconds**. This is very short. Dashboard refresh that involves reading multiple vault files will likely exceed this. **Must configure `CLAUDE_CODE_SESSIONEND_HOOKS_TIMEOUT_MS` or keep refresh extremely lightweight.**

**Two approaches:**

Option A — Lightweight: Just write a "last_refreshed" timestamp to dashboard header, triggering Dataview to re-evaluate on next Obsidian open (Dataview re-evaluates live). This takes <1s.

Option B — Regenerate: Fully rewrite dashboard markdown with embedded Dataview queries. Requires reading task files and computing summaries. May exceed 1.5s default timeout.

**Recommended: Option A — write a timestamp update to the dashboard YAML frontmatter.** Dataview dashboards contain `dataview` code blocks that execute live in Obsidian. Refreshing the file is only needed to update static summary sections (e.g., "last refreshed" header). The Dataview queries execute when Obsidian renders them.

```bash
#!/bin/bash
# session-end.sh — marks dashboards as refreshed at session end

VAULT_WORKSPACE="/Users/richardyu/Library/Mobile Documents/iCloud~md~obsidian/Documents/Home/05_AI_Workspace"
DASHBOARD="$VAULT_WORKSPACE/dashboards/tasks-by-status.md"
TODAY=$(date +%Y-%m-%d)

# Update the refreshed_by timestamp in frontmatter
# Use a temp file approach to avoid partial writes
if [ -f "$DASHBOARD" ]; then
  # Replace the refreshed field value in frontmatter
  sed -i '' "s/^refreshed_by: .*/refreshed_by: $TODAY/" "$DASHBOARD" 2>/dev/null || true
fi

exit 0
```

**Note on sed -i '':** On macOS, `sed -i ''` is correct (BSD sed requires empty string argument for in-place edit). GNU sed uses `sed -i` without the argument.

### Pattern 4: Post-Compaction Context Re-injection

**What:** After context compaction, vault conventions must not be lost.

**Mechanism (verified):** SessionStart fires with `source: "compact"` after compaction. No separate PostCompact handler is needed. The existing SessionStart hook already runs. CLAUDE.md is re-read from disk after compaction (official docs confirm this).

**Therefore:** Compaction re-injection works automatically because:
1. CLAUDE.md is re-read in full after every compaction (Claude Code built-in behavior)
2. SessionStart fires with `source: "compact"`, re-running the stale tasks hook
3. MEMORY.md first 200 lines are re-loaded into new context

**No additional hook needed for compaction** — the SessionStart hook handles it. If you want to inject extra context specifically on compaction (e.g., "context was just compacted, here's a summary of what we were doing"), use the `source` field to differentiate:

```bash
INPUT=$(cat)
SOURCE=$(echo "$INPUT" | python3 -c "import json,sys; print(json.load(sys.stdin).get('source',''))" 2>/dev/null)

if [ "$SOURCE" = "compact" ]; then
  echo "NOTE: Context was just compacted. Key vault state refreshed."
fi
```

### Pattern 5: CLAUDE.md Import for Reference Files

**What:** CLAUDE.md files can import other files using `@path/to/file` syntax. Imported files are loaded verbatim into context.

**Use case for Phase 2:** The project CLAUDE.md can reference the YAML schema directly:
```markdown
## YAML Frontmatter Schema
Canonical schema: @.planning/phases/01-foundation/yaml-frontmatter-schema.md
```

This loads the schema into every session without duplicating it in CLAUDE.md. Import depth max is 5 hops.

**Warning:** First time Claude Code sees an external import (outside project root) it shows an approval dialog. Imports within project root do not require approval.

### Anti-Patterns to Avoid

- **Putting dynamic data in MEMORY.md:** Task lists, current counts — these go stale. MEMORY.md should contain structural facts and preferences, not task state. Task state comes from the SessionStart hook.
- **Long SessionEnd hooks:** Default 1.5s timeout. Dashboard writes that read many files will fail silently. Either keep them fast or set `CLAUDE_CODE_SESSIONEND_HOOKS_TIMEOUT_MS`.
- **Trying to inject context via PostCompact:** PostCompact does NOT support `additionalContext`. Use SessionStart with `source: "compact"` check instead.
- **Registering the SessionStart hook in project settings.json instead of global:** The existing global `~/.claude/settings.json` already has SessionStart hooks. Adding to project-level settings is allowed but creates fragmentation. Keep session lifecycle hooks in the global settings file.
- **Duplicating rules across CLAUDE.md and MEMORY.md:** CLAUDE.md is for rules (loaded fully); MEMORY.md is for learned facts (200-line limit). Don't copy instructions from CLAUDE.md into MEMORY.md — it wastes the 200-line budget.
- **Exceeding the 200-line MEMORY.md limit:** Content beyond line 200 is silently not loaded. Keep MEMORY.md under 200 lines; offload detail to topic files that Claude reads on demand.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Cross-session memory | Custom file-based memory system | Claude Code auto memory (`MEMORY.md`) | Native, loads automatically, Claude manages it |
| Context injection at session start | Custom MCP or plugin | SessionStart hook stdout | Built-in mechanism, no dependencies |
| Post-compaction recovery | Custom state serialization | SessionStart fires on `source: "compact"` + CLAUDE.md re-read is automatic | Built-in behavior, already handled |
| YAML frontmatter parsing in hooks | Full YAML parser | grep/awk on known field names | Hooks are fast path; avoid installing pyyaml |

**Key insight:** All four goals of this phase are solvable with built-in Claude Code features. Don't add dependencies or custom infrastructure.

---

## Common Pitfalls

### Pitfall 1: SessionEnd Timeout Too Short

**What goes wrong:** Dashboard refresh script runs, appears to succeed, but output is incomplete or silently truncated because the 1.5-second timeout was exceeded.

**Why it happens:** SessionEnd default timeout is 1.5 seconds. Any script reading from disk (especially iCloud paths with sync latency) can exceed this easily.

**How to avoid:** Either (a) keep SessionEnd hook to a single fast sed substitution (< 100ms), or (b) set `CLAUDE_CODE_SESSIONEND_HOOKS_TIMEOUT_MS=5000` as an environment variable. Note that per-hook `timeout` fields are capped by this environment variable.

**Warning signs:** Dashboard `refreshed_by` date not updating; hook completes on `/clear` but takes too long on session exit.

### Pitfall 2: MEMORY.md Not Auto-Loading

**What goes wrong:** Vault profile is not available at session start even though MEMORY.md was written.

**Why it happens:** (a) Memory directory doesn't exist yet — auto memory creates it on first write, but a manually seeded file requires the directory to exist first. (b) The file is in the wrong location (path must exactly match project slug).

**How to avoid:** Create the directory explicitly (`mkdir -p`) before writing MEMORY.md. Verify path matches: `~/.claude/projects/-Users-richardyu-PARA-01-Projects-Personal-apps-second-brain/memory/MEMORY.md`.

**Warning signs:** Claude starts session without knowledge of vault structure; `/memory` command shows no auto memory files.

### Pitfall 3: 200-Line MEMORY.md Overflow

**What goes wrong:** Context grows over time as Claude adds learnings; lines beyond 200 are silently not loaded.

**Why it happens:** Claude adds facts to MEMORY.md without checking length. Detailed content that should go in topic files ends up in MEMORY.md directly.

**How to avoid:** Write the initial MEMORY.md with the explicit structure: index section (50 lines) + "See detailed notes in topic files." Claude is instructed to maintain this discipline. Audit periodically with `wc -l`.

**Warning signs:** MEMORY.md grows past 200 lines; Claude seems to have lost facts it previously knew.

### Pitfall 4: Hook Output Too Verbose

**What goes wrong:** SessionStart hook dumps all open tasks as context (50+ tasks), consuming a large chunk of the context window and making Claude less effective.

**Why it happens:** The hook scans all tasks without filtering to a compact summary.

**How to avoid:** SessionStart hook output must be concise. Show at most: 5 most overdue, 3 upcoming, 5 most stale. Cap total output at ~30 lines. This is surface-only — Claude can read full task files if needed.

**Warning signs:** Context window appears large from session start; Claude seems slow or forgetful later in sessions.

### Pitfall 5: Hook Registered in Wrong Settings File

**What goes wrong:** SessionStart/SessionEnd hooks added to project `.claude/settings.json` but the project settings file is already being used for the vault write guard. Two settings files for the same project create confusion about precedence.

**Why it happens:** Phase 1 put the vault guard in project-level settings.json. Session lifecycle hooks feel project-specific but also need to fire in all sessions.

**How to avoid:** Add session hooks to `~/.claude/settings.json` (already has `bd prime` SessionStart). This is where session lifecycle hooks live by convention in this project. Project settings.json stays focused on the vault write guard.

**Warning signs:** Hook fires when opening Claude in the second-brain directory but not when opened from vault root.

### Pitfall 6: pyyaml Not Available in Hook Environment

**What goes wrong:** Python hook script `import yaml` fails because pyyaml isn't installed in system Python.

**Why it happens:** pyyaml is a third-party package not in the Python stdlib. Hook environment may not have pip packages available.

**How to avoid:** Use grep/awk/sed for YAML frontmatter parsing in hooks (these are macOS system tools). Alternatively, a minimal Python regex parser that handles `key: value` patterns for simple scalar fields.

**Warning signs:** Hook exits with non-zero status; tasks not surfaced at session start.

---

## Code Examples

### MEMORY.md Initial Seed (verified structure)

```markdown
# Second Brain — Memory

Last updated: 2026-03-14

## Vault Profile
- Vault root: /Users/richardyu/Library/Mobile Documents/iCloud~md~obsidian/Documents/Home/
- AI workspace: 05_AI_Workspace/ (ONLY folder Claude may write to in vault)
- PARA folders: 01_Projects, 02_Areas_of_Interest, 03_Research, 04_Archive (human-only)
- Tasks: /Users/richardyu/PARA/01_Projects/Personal/apps/second-brain/tasks/ (NOT in vault)
- Projects: same project root /projects/
- Daily notes: /daily/, People: /people/, Ideas: /ideas/

## Key Reference Files
- YAML frontmatter schema: .planning/phases/01-foundation/yaml-frontmatter-schema.md
- Vault write guard hook: .claude/hooks/vault-write-guard.py
- Task status enums: backlog | active | waiting | blocked | done | someday
- Date format rule: bare ISO YYYY-MM-DD, NEVER quoted (breaks Dataview date queries)

## System Architecture
- Python backend handles: Slack → classification → vault filing (DO NOT MODIFY)
- Claude Code handles: morning ritual, tasks, writing, research, session context
- Hook system: PreToolUse blocks writes to 01-04 PARA folders
- Sessions: SessionStart surfaces stale tasks; SessionEnd refreshes dashboards

## User Preferences
(Claude updates this section as preferences are discovered)

## Patterns Learned
(Claude updates this section as patterns emerge)
```

Line count: ~35 lines. Well within 200-line limit with room for Claude to add learnings.

### Settings.json Addition (global ~/.claude/settings.json)

Add to the existing SessionStart array and add new SessionEnd array:

```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "",
        "hooks": [{ "type": "command", "command": "bd prime" }]
      },
      {
        "hooks": [{ "type": "command", "command": "node \"/Users/richardyu/.claude/hooks/gsd-check-update.js\"" }]
      },
      {
        "hooks": [{
          "type": "command",
          "command": "bash /Users/richardyu/PARA/01_Projects/Personal/apps/second-brain/.claude/hooks/session-start.sh"
        }]
      }
    ],
    "SessionEnd": [
      {
        "hooks": [{
          "type": "command",
          "command": "bash /Users/richardyu/PARA/01_Projects/Personal/apps/second-brain/.claude/hooks/session-end.sh",
          "timeout": 5000
        }]
      }
    ]
  }
}
```

**Note:** The `timeout` field on the hook is capped by `CLAUDE_CODE_SESSIONEND_HOOKS_TIMEOUT_MS`. Set the env var to 5000 and use `timeout: 5000` on the hook for consistent behavior.

### Stale Task Surfacing Hook (bash — no pip dependencies)

```bash
#!/bin/bash
# .claude/hooks/session-start.sh
# Surfaces stale tasks and upcoming deadlines as session context.
# Output goes to stdout; Claude receives it as session context.

TASKS_DIR="/Users/richardyu/PARA/01_Projects/Personal/apps/second-brain/tasks"
TODAY=$(date +%Y-%m-%d)
UPCOMING_LIMIT=$(date -v +7d +%Y-%m-%d 2>/dev/null || date -d '+7 days' +%Y-%m-%d)
STALE_CUTOFF=$(date -v -7d +%Y-%m-%d 2>/dev/null || date -d '-7 days' +%Y-%m-%d)

overdue_lines=()
upcoming_lines=()
stale_lines=()

for f in "$TASKS_DIR"/*.md; do
  [ -f "$f" ] || continue
  fname=$(basename "$f")
  [ "$fname" = "README.md" ] && continue

  status=$(grep -m1 '^status:' "$f" 2>/dev/null | awk '{print $2}')
  [ "$status" = "done" ] && continue

  title=$(grep -m1 '^title:' "$f" 2>/dev/null | sed 's/^title:[[:space:]]*//' | tr -d '"')
  due=$(grep -m1 '^due_date:' "$f" 2>/dev/null | awk '{print $2}')
  modified=$(stat -f "%Sm" -t "%Y-%m-%d" "$f" 2>/dev/null)

  if [ -n "$due" ] && [[ "$due" < "$TODAY" ]]; then
    overdue_lines+=("  - $title (due $due, status: $status)")
  elif [ -n "$due" ] && [[ "$due" >= "$TODAY" ]] && [[ "$due" <= "$UPCOMING_LIMIT" ]]; then
    upcoming_lines+=("  - $title (due $due)")
  elif [ -z "$due" ] && [ -n "$modified" ] && [[ "$modified" < "$STALE_CUTOFF" ]]; then
    case "$status" in active|waiting|blocked)
      stale_lines+=("  - $title (last modified $modified, status: $status)")
    esac
  fi
done

if [ ${#overdue_lines[@]} -gt 0 ] || [ ${#upcoming_lines[@]} -gt 0 ] || [ ${#stale_lines[@]} -gt 0 ]; then
  echo "=== TASK STATUS ($(date +%Y-%m-%d)) ==="
  if [ ${#overdue_lines[@]} -gt 0 ]; then
    echo "OVERDUE (${#overdue_lines[@]}):"
    # Cap at 5 most recent
    count=0
    for line in "${overdue_lines[@]}"; do
      echo "$line"; ((count++)); [ $count -ge 5 ] && break
    done
  fi
  if [ ${#upcoming_lines[@]} -gt 0 ]; then
    echo "DUE WITHIN 7 DAYS (${#upcoming_lines[@]}):"
    count=0
    for line in "${upcoming_lines[@]}"; do
      echo "$line"; ((count++)); [ $count -ge 5 ] && break
    done
  fi
  if [ ${#stale_lines[@]} -gt 0 ]; then
    echo "STALE 7+ DAYS (${#stale_lines[@]}):"
    count=0
    for line in "${stale_lines[@]}"; do
      echo "$line"; ((count++)); [ $count -ge 5 ] && break
    done
  fi
  echo "==================================="
fi

exit 0
```

### Dashboard Refresh Hook (SessionEnd — fast path)

```bash
#!/bin/bash
# .claude/hooks/session-end.sh
# Updates dashboard refresh timestamp. Fast path: single sed substitution.

VAULT="/Users/richardyu/Library/Mobile Documents/iCloud~md~obsidian/Documents/Home"
DASHBOARD="$VAULT/05_AI_Workspace/dashboards/tasks-by-status.md"
TODAY=$(date +%Y-%m-%d)

if [ -f "$DASHBOARD" ]; then
  sed -i '' "s/^refreshed_by: .*/refreshed_by: $TODAY/" "$DASHBOARD" 2>/dev/null
fi

exit 0
```

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Only CLAUDE.md for memory | CLAUDE.md + MEMORY.md (auto memory) | v2.1.59 | Claude can learn preferences without manual CLAUDE.md edits |
| PostCompact for re-injection | SessionStart with `source: "compact"` | Current | SessionStart is the single handler for all context injection scenarios |
| No session lifecycle hooks | SessionStart + SessionEnd | Current | Enables automatic context at open and cleanup at close |

**Deprecated/outdated:**
- Storing context only in CLAUDE.md: MEMORY.md auto memory is now the right home for learned facts vs rules
- Using PostCompact for context re-injection: PostCompact does NOT support `additionalContext`; use SessionStart `source: "compact"` check

---

## Open Questions

1. **Tasks directory location — project root vs vault**
   - What we know: Tasks live in `/Users/richardyu/PARA/01_Projects/Personal/apps/second-brain/tasks/` (project, not vault). The vault has no top-level `tasks/` folder. The Dataview dashboard queries `FROM "tasks"` which would need a vault-level `tasks/` folder to work — but tasks are in the project, not the vault.
   - What's unclear: Is this intentional? The Dataview dashboard currently has `FROM "tasks"` — does it query the project folder or a vault folder? If the vault doesn't have `tasks/`, these Dataview queries return zero results.
   - Recommendation: The planner should note that the SessionStart hook reads from the project `tasks/` folder directly (filesystem, not Dataview). The Dataview dashboard `FROM "tasks"` issue is a separate concern (Phase 1 may have left this unresolved). For Phase 2, the hook-based surfacing works regardless of Dataview.

2. **SessionEnd hook timeout configuration method**
   - What we know: Default 1.5s, configurable via `CLAUDE_CODE_SESSIONEND_HOOKS_TIMEOUT_MS` env var. Per-hook `timeout` field is capped by env var.
   - What's unclear: How to set `CLAUDE_CODE_SESSIONEND_HOOKS_TIMEOUT_MS` persistently without requiring the user to always launch Claude with this variable set.
   - Recommendation: Keep SessionEnd hook fast (single sed, <100ms) so the default 1.5s is sufficient. Avoid the timeout problem entirely.

3. **Whether tasks are currently empty**
   - What we know: `tasks/` folder exists with only README.md. No actual task files.
   - What's unclear: When will real tasks be added? The SessionStart hook should handle empty `tasks/` gracefully (output nothing, not an error).
   - Recommendation: Hook must handle the empty case gracefully — `for f in *.md; do` with a test ensures this.

---

## Sources

### Primary (HIGH confidence)

- `https://code.claude.com/docs/en/memory` — Auto memory mechanism, storage path, 200-line MEMORY.md limit, CLAUDE.md vs MEMORY.md distinction, import syntax (fetched directly)
- `https://code.claude.com/docs/en/hooks` — SessionStart/SessionEnd full documentation, timeout values, `source` field values, `additionalContext` support, PostCompact limitations (fetched directly)
- Existing `~/.claude/settings.json` inspection — confirmed SessionStart already has `bd prime` hook, pattern for adding new hooks
- `claude --version` output — confirmed version 2.1.74 (auto memory requires 2.1.59+, so enabled)
- Phase 1 RESEARCH.md — confirmed PreToolUse hook pattern, vault paths, task schema

### Secondary (MEDIUM confidence)

- Existing `.claude/hooks/vault-write-guard.py` — confirmed Python hook pattern for this project
- Existing `tasks/` directory inspection — confirmed tasks are in project root, not vault
- Existing `05_AI_Workspace/dashboards/tasks-by-status.md` — confirmed dashboard structure with `refreshed_by` frontmatter field

### Tertiary (LOW confidence)

- macOS `date -v` flag behavior in hook environment — tested pattern but not verified in Claude Code hook runtime specifically
- `sed -i ''` (BSD sed) behavior in hook environment — macOS system standard but hook shell may differ

---

## Metadata

**Confidence breakdown:**
- Auto memory mechanism and MEMORY.md structure: HIGH — official docs fetched and verified
- SessionStart hook mechanism and output format: HIGH — official docs verified
- SessionEnd timeout limits: HIGH — official docs verified (1.5s default)
- PostCompact context injection limitation: HIGH — explicitly documented as not supported
- SessionStart fires on compaction (`source: "compact"`): HIGH — explicitly documented
- Hook script bash syntax for macOS: MEDIUM — standard macOS tools but hook runtime environment not verified
- Tasks being in project root vs vault: HIGH — inspected filesystem directly

**Research date:** 2026-03-14
**Valid until:** 2026-04-14 (Claude Code memory/hooks API is stable; hook timeout values may change in minor releases)
