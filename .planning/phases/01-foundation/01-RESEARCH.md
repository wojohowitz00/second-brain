# Phase 1: Foundation - Research

**Researched:** 2026-03-14
**Domain:** Claude Code hooks, Obsidian vault structure, Dataview YAML schema
**Confidence:** HIGH

---

## Summary

Phase 1 creates the safety boundary and data schema that everything else builds on. Three deliverables: (1) a safe AI-only write zone in the Obsidian vault, (2) a PreToolUse hook that blocks Claude from writing to human PARA folders, and (3) a canonical YAML frontmatter schema compatible with Dataview 0.5.68 (installed).

The Claude Code hook system is well-documented and the exact mechanism for blocking file writes is verified. The PreToolUse hook receives a JSON payload via stdin containing `tool_name` and `tool_input` (with `file_path` for Write/Edit or `command` for Bash), and exits with code 2 to hard-block the tool call. The vault already has no 05_AI_Workspace folder — it must be created. Existing templates reveal the current frontmatter conventions, which should be preserved and extended (not replaced) in the canonical schema.

**Primary recommendation:** Implement the hook as a single Python script (matching Write|Edit|Bash) that checks file_path against the vault's human PARA prefix; create 05_AI_Workspace/ with a CLAUDE.md in each subfolder as the write policy; keep the canonical schema additive on top of existing templates.

---

## Standard Stack

### Core

| Tool/Library | Version | Purpose | Why Standard |
|---|---|---|---|
| Claude Code hooks | Current | PreToolUse write boundary enforcement | Native Claude Code feature, no external dependencies |
| Dataview | 0.5.68 (installed) | Vault queries and dashboards | Already installed in vault, confirmed active |
| Python 3 (uv) | System python / uv | Hook script runtime | Existing project uses `uv run` pattern |
| YAML frontmatter | Obsidian native | Structured metadata storage | Obsidian-native, Dataview reads it automatically |

### Supporting

| Tool | Purpose | When to Use |
|---|---|---|
| `jq` | JSON parsing in bash hooks | Alternative to Python if simpler hook preferred |
| Obsidian Tasks plugin | 7.22.0 (installed) | Alternative task query syntax (uses inline `due:: date` syntax) | Only if Dataview tasks prove insufficient |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|---|---|---|
| Python hook script | Bash + jq | Bash is simpler but harder to test; Python is more readable and already the project convention |
| YAML frontmatter | Obsidian Tasks inline syntax | Inline syntax conflicts with YAML; stick with frontmatter for Dataview compatibility |

---

## Architecture Patterns

### Recommended Project Structure

```
second-brain/.claude/
├── hooks/
│   └── vault-write-guard.py      # PreToolUse hook script
└── settings.json                  # Hook registration (new file — currently only settings.local.json exists)

Obsidian vault (iCloud~md~obsidian/Documents/Home/):
├── 01_Projects/                   # Human PARA — BLOCKED for AI writes
├── 02_Areas_of_Interest/          # Human PARA — BLOCKED for AI writes
├── 03_Research/                   # Human PARA — BLOCKED for AI writes
├── 04_Archive/                    # Human PARA — BLOCKED for AI writes
└── 05_AI_Workspace/               # AI writes ONLY
    ├── CLAUDE.md                  # Top-level write policy
    ├── dashboards/
    │   └── CLAUDE.md              # Subfolder write policy
    ├── insights/
    │   └── CLAUDE.md
    ├── canvas/
    │   └── CLAUDE.md
    └── daily-briefs/
        └── CLAUDE.md
```

### Pattern 1: PreToolUse Hook in settings.json

**What:** Hook registered in `.claude/settings.json` (project-level, not settings.local.json) fires before Write, Edit, and Bash tool calls. Script reads JSON from stdin, checks file path, exits 2 to block.

**When to use:** Any write boundary enforcement.

**Exact settings.json format (verified from official docs):**

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Write|Edit|Bash",
        "hooks": [
          {
            "type": "command",
            "command": "python3 .claude/hooks/vault-write-guard.py"
          }
        ]
      }
    ]
  }
}
```

**Key detail:** The project currently only has `settings.local.json` (permissions only, no hooks). A new `settings.json` must be created for the hooks. Both files coexist — settings.json is committed to git, settings.local.json is machine-local.

### Pattern 2: Hook Script — Exit Code 2 Blocking

**What:** Script reads stdin JSON, extracts `tool_name` + `tool_input`, checks path against blocked prefix list, exits 2 with stderr explanation.

**Verified exit code semantics (official docs):**
- Exit 0 → tool proceeds (optionally parse JSON from stdout for permissionDecision)
- Exit 2 → tool BLOCKED, stderr is sent to Claude as explanation
- Any other exit code → non-blocking error, stderr shown in verbose mode only

**Hook stdin payload structure (verified):**

```json
{
  "session_id": "abc123",
  "transcript_path": "/path/to/transcript.jsonl",
  "cwd": "/current/working/dir",
  "hook_event_name": "PreToolUse",
  "tool_name": "Write",
  "tool_input": {
    "file_path": "/path/to/file.md",
    "content": "..."
  },
  "tool_use_id": "toolu_..."
}
```

**For Bash tool, tool_input is:**
```json
{
  "command": "echo hello",
  "description": "Print hello",
  "timeout": 120000,
  "run_in_background": false
}
```

**Verified Python hook pattern:**

```python
#!/usr/bin/env python3
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

input_data = json.load(sys.stdin)
tool_name = input_data.get("tool_name", "")
tool_input = input_data.get("tool_input", {})

# Check Write/Edit — file_path is directly available
if tool_name in ("Write", "Edit", "MultiEdit"):
    file_path = tool_input.get("file_path", "")
    for prefix in BLOCKED_PREFIXES:
        if file_path.startswith(prefix):
            print(
                f"BLOCKED: Claude may not write to human PARA folders.\n"
                f"Attempted path: {file_path}\n"
                f"AI writes must go to {VAULT_ROOT}/05_AI_Workspace/ only.",
                file=sys.stderr
            )
            sys.exit(2)

# Check Bash — parse command for vault write patterns
if tool_name == "Bash":
    command = tool_input.get("command", "")
    for prefix in BLOCKED_PREFIXES:
        # Detect shell redirections, tee, cp, mv targeting blocked paths
        if prefix in command and re.search(r'(>|>>|tee|cp|mv|touch|mkdir)', command):
            print(
                f"BLOCKED: Bash command targets a human PARA folder.\n"
                f"Command: {command}\n"
                f"AI writes must go to 05_AI_Workspace/ only.",
                file=sys.stderr
            )
            sys.exit(2)

sys.exit(0)
```

**Important nuance on Bash blocking:** Bash is harder to block exhaustively — a regex on the command string is imperfect. The vault boundary is enforced primarily via Write/Edit (the explicit write tools). Bash checking is a best-effort secondary guard. The planner should note this limitation.

### Pattern 3: Dataview-Compatible YAML Frontmatter

**What:** Canonical field names that Dataview auto-indexes from YAML frontmatter. Dataview infers types from YAML syntax: ISO dates → date type, numbers → number type, quoted strings → text.

**Existing templates to extend (not replace):**

Current task template fields: `type, title, due_date, status, tags, created`
Current project template fields: `type, name, status, next_action, tags, created`
Current person template fields: `type, name, context, follow_ups, last_touched, tags`

**Canonical schema additions for Dataview compatibility:**

Tasks — add to existing:
```yaml
---
type: task
title: ""
due_date: 2026-03-14        # ISO date — Dataview reads as date type
status: backlog             # backlog | active | waiting | blocked | done | someday
priority: medium            # high | medium | low
project: "[[ProjectName]]"  # Obsidian link — Dataview reads as link type
domain: admin               # sales | content | product | admin | research | people
context: ""                 # quick | deep | collab
tags: []
created: 2026-03-14
---
```

Projects — add to existing:
```yaml
---
type: project
name: ""
status: active              # active | on-hold | done | archived
deadline: 2026-06-01        # ISO date
health: green               # green | yellow | red
domain: admin               # sales | content | product | admin | research | people
next_action: ""
tags: []
created: 2026-03-14
---
```

People — add to existing (canonical v3 schema for future CRM, but define now):
```yaml
---
type: person
name: ""
relationship: ""            # client | friend | colleague | vendor | other
last_contact: 2026-03-14    # ISO date
follow_up_date: 2026-04-01  # ISO date — drives CRM alerts
context: ""
follow_ups: []
tags: []
last_touched: 2026-03-14    # Keep existing field for backward compat
---
```

**Dataview field naming rules (verified):**
- Hyphens work: `due-date` → referenced as `due-date` or `due_date` (Dataview normalizes)
- Underscores work: `due_date` → standard, preferred for readability
- Spaces work in YAML, but use `simple-field` or `simple_field` format in queries
- ISO date format `YYYY-MM-DD` without quotes → automatically typed as date
- ISO date with quotes `"YYYY-MM-DD"` → typed as text, NOT a date (must not quote dates)
- Links: `"[[PageName]]"` in YAML → Dataview reads as link type (must be quoted in YAML)

**Critical pitfall:** The existing templates use `due_date: ` (empty, no value) and `created: "{{date}}"` (quoted). For Dataview date queries to work, dates must be unquoted ISO format. The schema doc should specify this explicitly.

### Pattern 4: Minimum Viable Dataview Dashboard

**Verified DQL query block syntax:**

````markdown
```dataview
TABLE status, priority, due_date, project
FROM "tasks"
WHERE status != "done"
SORT due_date ASC
```
````

**Tasks by status dashboard:**

````markdown
```dataview
TABLE without id
  file.link AS Task,
  priority AS Priority,
  due_date AS Due,
  project AS Project
FROM "tasks"
WHERE type = "task" AND status = "active"
SORT due_date ASC
```
````

**Project status dashboard:**

````markdown
```dataview
TABLE without id
  file.link AS Project,
  status AS Status,
  health AS Health,
  deadline AS Deadline,
  next_action AS "Next Action"
FROM "projects"
WHERE type = "project" AND status = "active"
SORT health ASC
```
````

**Important Dataview quirk:** `FROM "tasks"` queries the folder named `tasks` relative to vault root. For 05_AI_Workspace dashboards querying across the vault, use `FROM "tasks" OR FROM "projects"` or use tag-based `FROM #active`.

### Anti-Patterns to Avoid

- **Quoting ISO dates in YAML:** `created: "2026-03-14"` makes Dataview treat it as text, breaking date comparisons. Use bare `created: 2026-03-14`.
- **Registering hooks in settings.local.json:** That file is machine-local and won't be committed. Hooks belong in `settings.json`.
- **Blocking all Bash comprehensively:** Regex on arbitrary shell commands is brittle. Focus hook enforcement on Write/Edit tools; Bash is secondary.
- **Creating empty placeholder directories in iCloud vault:** iCloud syncs directories only if they contain files. Use a CLAUDE.md policy file in each subdirectory (serves dual purpose: policy document + ensures directory is synced).
- **Using `mkdir` alone for iCloud vault folders:** The folder may not sync if empty. Always write at least one file into each new directory.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---|---|---|---|
| Hook input parsing | Custom stdin reader | `json.load(sys.stdin)` | Standard Python stdlib |
| Dataview query syntax | Custom templating | Standard DQL | Dataview parses it natively |
| Date formatting in YAML | String manipulation | Bare ISO dates | Dataview type inference |

**Key insight:** The hook script is genuinely simple — it is 20-30 lines of Python. Don't over-engineer it with classes or abstractions.

---

## Common Pitfalls

### Pitfall 1: Hook Registered in Wrong Settings File

**What goes wrong:** Hook added to `settings.local.json` instead of `settings.json`. File is not committed, hook doesn't run in new sessions or for other users.

**Why it happens:** The project currently only has `settings.local.json`. Developer defaults to editing existing file.

**How to avoid:** Create a new `settings.json` for hooks. Keep `settings.local.json` for permissions only.

**Warning signs:** Hook not firing; checking `.claude/` and seeing no `settings.json`.

### Pitfall 2: iCloud Sync Conflicts on Vault Writes

**What goes wrong:** Claude writes a file while iCloud is syncing; iCloud creates a conflict copy like `Note (iCloud conflict).md`.

**Why it happens:** iCloud Drive does not support simultaneous writes from multiple sources. If Obsidian app is open on another device, conflict risk increases.

**How to avoid:** Write-then-verify pattern — write atomically (full file content in one Write tool call, not Edit). Avoid appending to files that are open in Obsidian on other devices. The `05_AI_Workspace/` folder being AI-only reduces human edit conflicts significantly.

**Warning signs:** Files appearing with "(iCloud conflict)" suffix in vault.

### Pitfall 3: Dataview Date Field Not Typed as Date

**What goes wrong:** Queries like `WHERE due_date <= date(today)` return no results even when tasks have due dates.

**Why it happens:** Dates are stored as quoted strings `"2026-03-14"` instead of bare ISO `2026-03-14`. Dataview reads quoted values as text.

**How to avoid:** Canonical schema document must explicitly call out: no quotes on date fields. Verify with a test note.

**Warning signs:** Dataview query returns empty set; type check `WHERE typeof(due_date) = "date"` returns false.

### Pitfall 4: Hook Path Not Executable or Not Found

**What goes wrong:** Hook silently fails or errors with "command not found".

**Why it happens:** Script path is relative to project root, but if `$CLAUDE_PROJECT_DIR` isn't set or cwd differs, the path breaks.

**How to avoid:** Use absolute path or `$CLAUDE_PROJECT_DIR` in hook command. Or use `python3 $CLAUDE_PROJECT_DIR/.claude/hooks/vault-write-guard.py`. Ensure script has execute permissions if running directly as a command.

**Warning signs:** No blocking behavior; hook-related errors in verbose mode.

### Pitfall 5: Hook Blocks Claude's Own 05_AI_Workspace Writes

**What goes wrong:** Hook is too aggressive and blocks writes to `05_AI_Workspace/` — the very place Claude should write.

**Why it happens:** Incorrect path matching logic (blocking vault root instead of just 01-04 prefixes).

**How to avoid:** Hook must match ONLY `01_Projects`, `02_Areas_of_Interest`, `03_Research`, `04_Archive` prefixes. Anything else (including `05_AI_Workspace/`) passes through.

**Warning signs:** Claude can't create daily briefs or dashboards.

---

## Code Examples

### Complete Hook Script (Recommended Implementation)

```python
#!/usr/bin/env python3
"""
vault-write-guard.py — PreToolUse hook
Blocks Claude from writing to human PARA folders (01-04) in the Obsidian vault.
Exits with code 2 (blocking) if violation detected; 0 otherwise.
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
```

### Minimal settings.json with Hook

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Write|Edit|Bash",
        "hooks": [
          {
            "type": "command",
            "command": "python3 $CLAUDE_PROJECT_DIR/.claude/hooks/vault-write-guard.py"
          }
        ]
      }
    ]
  }
}
```

### CLAUDE.md Write Policy (for 05_AI_Workspace subfolders)

```markdown
# AI Write Policy

This folder is the **AI workspace** for Claude Code operations in the second-brain system.

## Who writes here
- Claude Code agents (authorized)
- Automated scripts via second-brain project

## Who does NOT write here
- Human users — use 01_Projects, 02_Areas_of_Interest, 03_Research, or 04_Archive instead
- External apps (except Obsidian sync)

## What lives here
- [dashboards/] Dataview query dashboards auto-refreshed by Claude
- [insights/] AI-generated weekly analysis and synthesis
- [canvas/] Visual weekly review boards
- [daily-briefs/] Morning briefing notes (one per day)

## File naming conventions
- Daily briefs: YYYY-MM-DD-daily-brief.md
- Dashboards: [topic]-dashboard.md
- Insights: YYYY-[WW]-weekly-insight.md

## Write rules
- Atomic writes only (full file content in one operation)
- Never modify files another process has open
- Append-only for logs; overwrite for dashboards (idempotent)
```

---

## State of the Art

| Old Approach | Current Approach | Impact |
|---|---|---|
| Top-level `decision: block` JSON in hook stdout | `hookSpecificOutput.permissionDecision` in stdout OR exit code 2 | Exit code 2 is simpler and verified working |
| Global hooks only | Per-project hooks via `.claude/settings.json` | Hooks can be project-scoped |
| Obsidian Bases (new) | Dataview 0.5.68 | Dataview is installed and stable; Bases is not in use |

**Deprecated/outdated:**
- Top-level `decision: block` JSON response: replaced by `hookSpecificOutput.permissionDecision`; exit code 2 is simpler and equally valid

---

## Open Questions

1. **settings.json vs settings.local.json hook registration**
   - What we know: settings.local.json exists, contains permissions. settings.json does not exist yet.
   - What's unclear: Whether adding `hooks` to `settings.local.json` works (local) vs creating a new `settings.json` (committed).
   - Recommendation: Create `settings.json` for hooks — this should be committed to git so the hook is always active. Settings.local.json is for machine-specific permissions.

2. **Bash hook comprehensiveness**
   - What we know: Bash command is a raw string; path detection via regex is imperfect.
   - What's unclear: Whether indirect writes (via Python scripts, subshells) would be caught.
   - Recommendation: Accept the limitation — Write/Edit are the primary enforcement points. Note this in hook script comments.

3. **iCloud sync timing for folder creation**
   - What we know: iCloud syncs files, not empty directories.
   - What's unclear: Exact timing of iCloud sync after file creation (could be seconds or minutes).
   - Recommendation: Create CLAUDE.md files in each subfolder simultaneously; don't rely on sequential creation.

4. **Obsidian Tasks plugin conflict with Dataview**
   - What we know: Both plugins are installed (Dataview 0.5.68, Tasks 7.22.0). Tasks plugin uses its own inline syntax.
   - What's unclear: Whether existing tasks in the vault use Tasks plugin syntax vs Dataview YAML syntax.
   - Recommendation: The canonical schema should use YAML frontmatter (Dataview-native). The Tasks plugin can coexist since it uses checkbox syntax in note bodies, not frontmatter.

---

## Sources

### Primary (HIGH confidence)
- `https://code.claude.com/docs/en/hooks` — Exact settings.json format, stdin payload structure, exit code semantics, environment variables (fetched directly)
- `/disler/claude-code-hooks-mastery` (Context7) — PreToolUse hook examples, settings.json format, exit code 2 behavior
- `/websites/blacksmithgu_github_io_obsidian-dataview` (Context7) — DQL query syntax, YAML field types, TABLE/TASK queries
- Dataview manifest.json in vault: confirmed version 0.5.68
- Existing templates in `backend/_templates/`: confirmed current frontmatter field names

### Secondary (MEDIUM confidence)
- Existing vault structure inspection: confirmed 01-04 PARA folders exist, no 05_AI_Workspace yet
- community-plugins.json: confirmed Dataview and Tasks plugin both installed

### Tertiary (LOW confidence)
- iCloud sync behavior for empty directories: based on general macOS/iCloud knowledge, not officially documented for this use case

---

## Metadata

**Confidence breakdown:**
- Hook format and exit codes: HIGH — verified from official Claude Code docs (live fetch)
- Hook stdin payload fields: HIGH — verified from official docs + Context7
- Dataview DQL syntax: HIGH — verified from official Dataview docs via Context7
- YAML date typing rules: HIGH — verified from Dataview docs (no quotes = date type)
- iCloud sync behavior: MEDIUM — general knowledge, not officially documented for empty dirs
- Bash hook comprehensiveness: MEDIUM — known limitation, documented honestly

**Research date:** 2026-03-14
**Valid until:** 2026-04-14 (Claude Code hook format is stable; Dataview schema is stable)
