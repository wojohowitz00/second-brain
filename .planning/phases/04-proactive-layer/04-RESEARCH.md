# Phase 4: Proactive Layer - Research

**Researched:** 2026-03-15
**Domain:** Insights detection, alert routing, Obsidian Canvas JSON
**Confidence:** HIGH (all three primary domains verified against live system or official spec)

## Summary

Phase 4 adds three capabilities to the existing `/weekly` command and morning briefing skill: a vault-wide insights detector, a severity-based alert router, and a Canvas visual weekly review board. The implementation builds entirely on patterns already established in this codebase — file mtime detection (from session-start.sh), Slack posting (from slack_client.py), and osascript notifications (from notifications.py). No new external dependencies are required.

The highest-risk item was the Obsidian Canvas JSON format. Research confirmed the format is a published open spec (JSON Canvas v1.0) with a fully-documented schema. The canvas folder at `05_AI_Workspace/canvas/` is not blocked by the vault-write-guard hook — writes to `05_AI_Workspace/` are permitted. osascript notifications were tested live and succeed on this macOS instance (macOS 26.3.1). The Slack bot token and channel ID are already configured in `backend/_scripts/.env`.

**Primary recommendation:** All three capabilities can be built as skill instructions + bash commands. No new Python libraries, no new environment variables, no new infrastructure required.

## Standard Stack

### Core (already exists in project)

| Tool | Location | Purpose | Why to Use It |
|------|----------|---------|---------------|
| `stat -f "%Sm" -t "%Y-%m-%d"` | session-start.sh:59 | File mtime detection | Proven pattern; macOS-compatible; no dependencies |
| `osascript -e 'display notification...'` | notifications.py:36-37 | macOS notifications | Already in use; tested live (exit 0 on macOS 26.3.1) |
| `slack_client.post_message()` | backend/_scripts/slack_client.py:170 | Slack channel posting | Full retry + rate-limit handling already built |
| YAML frontmatter frontmatter parsing | session-start.sh:35-40 | Read task/project fields | Same awk/grep pattern works for all .md files |
| JSON Canvas v1.0 | jsoncanvas.org spec | Canvas file format | Official open spec; Obsidian reads natively |

### Supporting

| Tool | Version | Purpose | When to Use |
|------|---------|---------|-------------|
| `date -j -f "%Y-%m-%d"` | macOS built-in | Date arithmetic for threshold checks | Any 14-day/7-day comparison |
| Python `json.dumps` | stdlib | Generate Canvas JSON | When building canvas file in skill |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| `osascript` | `terminal-notifier` | terminal-notifier requires Homebrew install; osascript is zero-dependency and already works |
| `stat` file mtime | frontmatter `last-modified` field | mtime requires no schema change; frontmatter approach requires all notes to have the field (most don't) |
| Python slack_client | raw `curl` | Python client has retry logic, rate limiting, proper error handling already; don't rewrite |

**Installation:** No new packages required.

## Architecture Patterns

### Recommended Project Structure

```
.claude/skills/surfacing/
├── weekly-review/skill.md       # EXTEND this (add insights step)
├── daily-digest/skill.md        # EXTEND this (add alert routing step)
├── insights/skill.md            # NEW: vault-wide pattern detection
└── eod-update/skill.md          # unchanged
05_AI_Workspace/
├── insights/YYYY-MM-DD-insights.md   # NEW: dated insight reports
└── canvas/weekly-review.canvas       # NEW: overwritten each /weekly run
```

### Pattern 1: Insights as a Step Inside /weekly

**What:** Add a new `## 5. Detect Patterns` step to the weekly-review skill, before writing output.
**When to use:** Always — insights are generated as part of weekly, not standalone.

The skill reads tasks/ and projects/ directories, applies four detection rules, and appends an `## Insights` section to the weekly note AND writes a separate dated file to `05_AI_Workspace/insights/`.

Detection logic (all use `stat -f "%Sm" -t "%Y-%m-%d"` for mtime):

```bash
# Source: session-start.sh:59 - same pattern extended to 14 days
THRESHOLD_EPOCH=$(( TODAY_EPOCH - 14 * 86400 ))

# Dormant project: active project with mtime <= threshold
for f in "$PROJECTS_DIR"/*.md; do
  status=$(awk '/^---/{c++;next} c==1{print} c==2{exit}' "$f" | grep '^status:' | ...)
  mod_epoch=$(stat -f "%Sm" -t "%s" "$f")
  [[ "$status" == "active" && "$mod_epoch" -le "$THRESHOLD_EPOCH" ]] && dormant+=("$f")
done
```

### Pattern 2: Alert Routing in Morning Briefing

**What:** The daily-digest skill already collects overdue tasks, due-today tasks, and stale follow-ups. Alert routing adds delivery logic based on severity.
**When to use:** Every `/today` invocation.

Severity-to-channel mapping (locked decision):
- Overdue → Slack + osascript + append to daily-brief note
- Due today → osascript + append to daily-brief note
- Stale follow-ups → append to daily-brief note only

Cap logic: same 5-item cap already in session-start.sh — overdue first, then due-today, then stale.

**Slack posting pattern** (reuses existing slack_client.py):

```python
# Source: backend/_scripts/slack_client.py:170-193
# The post_message function takes channel ID (not name)
# Channel ID is in SLACK_CHANNEL_ID env var: C0A7FJU1SDD
# Token is in SLACK_BOT_TOKEN env var

from slack_client import post_message
post_message(channel=os.environ["SLACK_CHANNEL_ID"], text=alert_text)
```

**osascript pattern** (reuses existing notifications.py approach):

```bash
# Source: notifications.py:22-37, tested live on this system
osascript -e 'display notification "2 overdue tasks" with title "Second Brain" subtitle "Morning Alert"'
```

**Daily note append pattern** (matches idempotent approach from 03-02):
The daily brief file is at `05_AI_Workspace/daily-briefs/YYYY-MM-DD-daily-brief.md`. Append an `## Alerts` section using the Edit tool. Check for existing section first (grep) to stay idempotent.

### Pattern 3: Canvas File Generation

**What:** Generate a JSON Canvas file with swimlanes for Active / Waiting / Blocked project status, each containing project cards and problem-flagged tasks.
**When to use:** End of `/weekly` run. Overwrites `05_AI_Workspace/canvas/weekly-review.canvas`.

**Verified JSON Canvas v1.0 schema:**

```json
{
  "nodes": [
    {
      "id": "unique-16char-hex",
      "type": "text",
      "x": 0,
      "y": 0,
      "width": 300,
      "height": 100,
      "text": "**Project Name**\nNext: do the thing"
    },
    {
      "id": "another-id",
      "type": "group",
      "x": -50,
      "y": -50,
      "width": 700,
      "height": 500,
      "label": "Active",
      "color": "4"
    }
  ],
  "edges": []
}
```

Node types: `text`, `file`, `link`, `group`. All nodes require `id`, `type`, `x`, `y`, `width`, `height`.

**Swimlane layout** (recommended spatial arrangement):

```
x=-700  Active lane (group)
x=0     Waiting lane (group)
x=700   Blocked lane (group)

Each lane: width=600, height grows with card count
Cards inside lane: text nodes, 280px wide, 120px tall, 20px gap
Lane header: part of group label field
```

**ID generation:** Use 16-character lowercase hex. In Python: `import secrets; secrets.token_hex(8)`. In bash: `openssl rand -hex 8`.

**Color presets** (for group nodes):
- `"1"` = red (use for Blocked)
- `"2"` = orange
- `"3"` = yellow (use for Waiting)
- `"4"` = green (use for Active)
- `"5"` = cyan
- `"6"` = purple

### Anti-Patterns to Avoid

- **Writing canvas file as Markdown:** Canvas files MUST have `.canvas` extension and contain valid JSON. Obsidian won't open them as canvas if the extension is wrong.
- **Using `display dialog` instead of `display notification`:** Dialogs block execution. Use `display notification` only.
- **Posting to Slack by channel name:** The API requires channel ID (e.g., `C0A7FJU1SDD`), not `#second-brain`. Channel ID is in `SLACK_CHANNEL_ID` env var.
- **Calling Python slack_client from skill markdown:** Skills run as Claude instructions. The pattern is: skill instructs Claude to use Bash to run `python3 -c "..."` or a helper script, sourcing `.env` first.
- **Including all tasks in Canvas cards:** Decision is problem-focused — only blocked/overdue tasks surface inside project cards.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Slack HTTP request | Custom requests code | `slack_client.post_message()` | Retry logic, rate limiting, error handling already built |
| macOS notifications | terminal-notifier, custom script | `osascript -e 'display notification...'` | Zero deps, already proven in codebase |
| File age calculation | Date parsing library | `stat -f "%Sm" -t "%s"` + epoch math | Exact same pattern in session-start.sh:58-63 |
| Canvas ID generation | Counter or UUID | `openssl rand -hex 8` or `secrets.token_hex(8)` | Matches Obsidian's own format |
| Canvas JSON schema | Custom format | JSON Canvas v1.0 spec exactly | Only format Obsidian recognizes |

**Key insight:** Every primitive needed for Phase 4 already exists in this codebase. The work is wiring them together in skill instructions, not building new infrastructure.

## Common Pitfalls

### Pitfall 1: osascript Notification Permissions

**What goes wrong:** `osascript -e 'display notification...'` exits 0 but no notification appears.
**Why it happens:** The calling application (Terminal or Claude Code's shell) needs notification permissions in System Settings > Notifications. On macOS Sequoia+, this is a common issue.
**How to avoid:** Verify permissions before building. This has been tested on this machine (macOS 26.3.1) and the command exits 0 successfully.
**Warning signs:** Command succeeds (exit 0) but notifications are invisible. Check System Settings > Notifications > Terminal (or the shell host app).

### Pitfall 2: Slack Channel ID vs. Channel Name

**What goes wrong:** Posting to `#second-brain` string fails with `channel_not_found`.
**Why it happens:** The API requires channel ID format (e.g., `C0A7FJU1SDD`), not display name.
**How to avoid:** Always use `os.environ["SLACK_CHANNEL_ID"]` — already set in backend/.env as `C0A7FJU1SDD`.
**Warning signs:** `SlackAPIError: channel_not_found` in stderr.

### Pitfall 3: Canvas File Not Opening as Canvas in Obsidian

**What goes wrong:** Canvas file opens as plain text instead of visual canvas.
**Why it happens:** File saved without `.canvas` extension, or JSON is malformed (trailing comma, missing required field).
**How to avoid:** Filename must end in `.canvas`. Validate JSON before write (`python3 -m json.tool`). Every node requires `id`, `type`, `x`, `y`, `width`, `height`.
**Warning signs:** Obsidian shows the file in the file tree but opens as code/text editor.

### Pitfall 4: Vault Write Guard on Canvas Folder

**What goes wrong:** Attempting to write canvas file triggers hook block.
**Why it happens:** Misremembering which folders are guarded.
**How to avoid:** Confirmed: vault-write-guard.py only blocks `01_Projects`, `02_Areas_of_Interest`, `03_Research`, `04_Archive`. Writing to `05_AI_Workspace/canvas/weekly-review.canvas` is explicitly allowed.
**Warning signs:** Hook error: "VAULT WRITE BLOCKED".

### Pitfall 5: Alert Routing Double-Firing

**What goes wrong:** Alerts sent both from session-start.sh and from `/today` skill.
**Why it happens:** session-start.sh already surfaces overdue/stale tasks in context. If the morning briefing skill also sends Slack/notifications, items are reported twice.
**How to avoid:** Alert routing (Slack + osascript) lives only in the `/today` skill (morning briefing), not in session-start.sh. The session-start.sh hook remains a context injection only (plain text output to Claude context). The morning briefing is where external delivery happens.
**Warning signs:** User receives duplicate Slack messages at session open and again at `/today`.

### Pitfall 6: file mtime vs. User Activity

**What goes wrong:** A file shows as "recent" because Claude wrote to it, even though the human hasn't touched the project.
**Why it happens:** When daily-brief or weekly review writes update a project file, mtime is refreshed.
**How to avoid:** Insights skill reads mtime of project and task files themselves, not derived output files. Do NOT touch project/task files during the insights phase — read-only. The skills that write output (daily-brief, weekly-review.md, canvas) are separate from the source files.
**Warning signs:** Projects that haven't been worked on are classified as "recently active".

## Code Examples

### Generate Canvas JSON (Python approach in skill)

```python
# Source: jsoncanvas.org spec v1.0 (verified)
import json, secrets

def make_id():
    return secrets.token_hex(8)

LANE_WIDTH = 600
CARD_WIDTH = 560
CARD_HEIGHT = 120
CARD_GAP = 20
LANE_TOP_PADDING = 60  # space for lane label
LANE_PADDING = 20

def build_canvas(active_projects, waiting_projects, blocked_projects):
    nodes = []
    edges = []

    lanes = [
        ("Active", "4", active_projects, -700),
        ("Waiting", "3", waiting_projects, 0),
        ("Blocked", "1", blocked_projects, 700),
    ]

    for label, color, projects, x_offset in lanes:
        lane_height = LANE_TOP_PADDING + len(projects) * (CARD_HEIGHT + CARD_GAP) + LANE_PADDING
        lane_id = make_id()
        nodes.append({
            "id": lane_id, "type": "group",
            "x": x_offset, "y": 0,
            "width": LANE_WIDTH, "height": max(lane_height, 200),
            "label": label, "color": color
        })
        for i, proj in enumerate(projects):
            card_y = LANE_TOP_PADDING + i * (CARD_HEIGHT + CARD_GAP)
            nodes.append({
                "id": make_id(), "type": "text",
                "x": x_offset + LANE_PADDING,
                "y": card_y,
                "width": CARD_WIDTH,
                "height": CARD_HEIGHT,
                "text": f"**{proj['name']}**\n{proj.get('note', '')}"
            })

    return json.dumps({"nodes": nodes, "edges": edges}, indent="\t")
```

### Slack Alert Post (from skill via Bash)

```bash
# Source: backend/_scripts/slack_client.py (existing, tested)
# Skills call this via Bash, sourcing the .env first
source /Users/richardyu/PARA/01_Projects/Personal/apps/second-brain/backend/_scripts/.env
python3 -c "
import sys
sys.path.insert(0, '/Users/richardyu/PARA/01_Projects/Personal/apps/second-brain/backend/_scripts')
from slack_client import post_message
import os
post_message(channel=os.environ['SLACK_CHANNEL_ID'], text='$ALERT_TEXT')
"
```

### osascript Notification (from skill via Bash)

```bash
# Source: notifications.py:36-37 pattern, tested live on this system
osascript -e "display notification \"${ALERT_BODY}\" with title \"Second Brain\" subtitle \"${ALERT_TITLE}\""
```

### Daily Note Append (idempotent pattern)

```bash
# Source: pattern from 03-02 EOD Update (idempotent via grep check)
BRIEF="/Users/richardyu/Library/Mobile Documents/iCloud~md~obsidian/Documents/Home/05_AI_Workspace/daily-briefs/$(date +%Y-%m-%d)-daily-brief.md"
if [[ -f "$BRIEF" ]] && ! grep -q "## Alerts" "$BRIEF"; then
    printf '\n## Alerts\n%s\n' "$ALERT_CONTENT" >> "$BRIEF"
fi
```

### mtime-Based Staleness Check

```bash
# Source: session-start.sh:58-63, extended to 14-day threshold
THRESHOLD_EPOCH=$(( $(date +%s) - 14 * 86400 ))
mod_epoch=$(stat -f "%Sm" -t "%s" "$file")
[[ "$mod_epoch" -le "$THRESHOLD_EPOCH" ]] && echo "DORMANT: $file"
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| terminal-notifier (Homebrew) | osascript native | Ongoing | Zero dependency; already works |
| Obsidian Canvas custom JSON | JSON Canvas v1.0 open spec | 2024 | Published spec; Obsidian treats as canonical |
| Full task lists in Canvas | Problem-focused cards only | Phase 4 decision | Reduces noise in visual review |

**Deprecated/outdated:**
- `terminal-notifier`: Requires Homebrew, external dep, unnecessary given osascript works.
- Custom YAML-based canvas format: The `.canvas` extension with JSON Canvas v1.0 is the only format Obsidian's Canvas plugin opens correctly.

## Open Questions

1. **Slack channel name (#second-brain or #alerts)**
   - What we know: Channel ID is `C0A7FJU1SDD`, bot token is configured and working
   - What's unclear: The human-readable channel name — confirmed during implementation by posting a test message
   - Recommendation: Skill instructions say "post to SLACK_CHANNEL_ID env var" — the name doesn't matter for the API call

2. **Goal drift detection: "active tasks that don't map to any active project"**
   - What we know: Task frontmatter has optional `project: "[[ProjectName]]"` field; project files are in projects/
   - What's unclear: Many tasks may have empty `project:` field — this would flag everything as goal drift
   - Recommendation: Only flag tasks where `project:` field is non-empty but the referenced project is not active (or doesn't exist). Tasks with no `project:` field are silently skipped for this check.

3. **Canvas swimlane height for many projects**
   - What we know: Canvas coordinates are free-form; groups can overlap or be any size
   - What's unclear: How Obsidian renders very tall group nodes (no published max-height limit found)
   - Recommendation: Cap displayed projects per lane at 10; add a note card at bottom if more exist. Each card is 120px + 20px gap, so 10 cards = 1400px lane height — acceptable.

## Sources

### Primary (HIGH confidence)
- jsoncanvas.org/spec/1.0/ — Complete JSON Canvas v1.0 schema for nodes, edges, colors
- github.com/obsidianmd/jsoncanvas sample.canvas — Live canonical example with all node types
- /Users/richardyu/PARA/01_Projects/Personal/apps/second-brain/backend/_scripts/notifications.py — osascript pattern in use; tested live on macOS 26.3.1 (exit 0)
- /Users/richardyu/PARA/01_Projects/Personal/apps/second-brain/backend/_scripts/slack_client.py — Slack posting, channel ID, retry pattern
- /Users/richardyu/PARA/01_Projects/Personal/apps/second-brain/.claude/hooks/session-start.sh — mtime detection, date arithmetic, task parsing
- /Users/richardyu/PARA/01_Projects/Personal/apps/second-brain/.claude/hooks/vault-write-guard.py — Confirmed canvas folder is NOT blocked

### Secondary (MEDIUM confidence)
- WebSearch: osascript macOS notification compatibility — Confirmed works on this machine; Sequoia permission issue documented but tested successfully here
- WebSearch: JSON Canvas ecosystem — Confirmed v1.0 is published, stable open spec

### Tertiary (LOW confidence)
- macOS 26.3.1 notification behavior — The specific macOS version here is unusual (26.x). osascript tested and passed, but this version is beyond training data. If notifications break, check System Settings > Notifications.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — all tools verified against live codebase or official spec
- Architecture: HIGH — patterns directly derived from existing session-start.sh and daily-digest skill
- Canvas JSON schema: HIGH — verified against official jsoncanvas.org spec and sample.canvas file
- Pitfalls: HIGH for items verified in code; MEDIUM for macOS notification quirks (OS version unusual)

**Research date:** 2026-03-15
**Valid until:** 2026-04-15 (stable stack; Slack API and Canvas spec are stable)
