# EOD Update Skill

**Description:**
End-of-day update skill. Captures session learnings and patterns into Claude Code memory for cross-session continuity. Invoked manually before closing a session, or when Claude detects a substantial session is ending.

## Triggers

- "end of day"
- "EOD update"
- "wrap up"
- "session learnings"

## Workflow

### Step 1: Auto-detect session activity

Check what happened in this session:
- List task files modified today: check modification times in `tasks/`
- Note any new files created in `tasks/`, `projects/`, `people/`
- Summarize briefly: "This session, we [did X, Y, Z]"

### Step 2: Ask ONE reflection question

Ask the user exactly one optional question:

> "Any decisions or patterns from today's session I should remember for next time?"

This is optional — if user says "no", "skip", or similar, proceed to Step 5 without capturing anything. Keep it to ONE question, not a multi-turn dialog.

### Step 3: Check MEMORY.md line count before writing

```bash
MEMORY="$HOME/.claude/projects/-Users-richardyu-PARA-01-Projects-Personal-apps-second-brain/memory/MEMORY.md"
wc -l < "$MEMORY"
```

- If >170 lines: warn the user — "MEMORY.md is at N lines (target: <150). Consider consolidating before adding more."
- If <=170 lines: proceed to capture

### Step 4: Append learnings to MEMORY.md

IMPORTANT: Do NOT overwrite MEMORY.md. Read it first, then use the Edit tool to append to the appropriate section. Preserve all existing content.

Determine the right section based on what was learned:

- **Decisions/rationale** → append to `## Patterns Learned` section
  - Example: `- User prefers X over Y because Z (discovered 2026-03-14)`
- **New preferences** → append to `## User Preferences` section
  - Example: `- User wants task titles in sentence case (discovered 2026-03-14)`
- **System facts / new conventions** → append to `## System Architecture` or `## Conventions` section

Append format: `- [learning] (discovered YYYY-MM-DD)`

### Step 5: Update daily-brief Day Summary (if applicable)

Check if today's daily-brief exists and already has a `## Day Summary` section:

Target: `$VAULT/05_AI_Workspace/daily-briefs/YYYY-MM-DD-daily-brief.md`

If the `## Day Summary` section exists AND there are session learnings to record, append them under it:

```markdown
### Session Learnings
- [learning 1]
- [learning 2]
```

If the Day Summary section does not yet exist (hook hasn't fired), skip this step — the session-end.sh hook will create it automatically at session close.

### Step 6: Confirm and close

Respond with one of:
- "Session learnings captured. MEMORY.md at N/200 lines."
- "No new learnings to capture. Have a good one!"

## Anti-patterns

- Do NOT ask multiple reflection questions (ONE only)
- Do NOT overwrite MEMORY.md (append to sections only)
- Do NOT create the Day Summary section (that is the session-end.sh hook's job)
- Do NOT prompt if user says "skip" or "no"
- Do NOT write to vault PARA folders (01_Projects through 04_Archive are write-guarded)

## Context

- MEMORY.md path: `~/.claude/projects/-Users-richardyu-PARA-01-Projects-Personal-apps-second-brain/memory/MEMORY.md`
- VAULT: `/Users/richardyu/Library/Mobile Documents/iCloud~md~obsidian/Documents/Home`
- Line count target: keep MEMORY.md under 150 lines, warn above 170
- The session-end.sh hook handles mechanical writes (Day Summary timestamp); this skill handles reflection and learning capture
