# Daily Digest

## Description
Generate a morning digest with today's tasks, overdue items, in-progress ideas, automation opportunities, and items Claude can handle autonomously. Output to Obsidian daily file and optionally Slack DM.

## Triggers
- Part of /today command
- "daily digest"
- "what's on for today"
- "morning briefing"
- "what do I have today"

## Dependencies
- Folder structure with tasks/, projects/, ideas/, people/, admin/
- Template structure with YAML frontmatter
- Optional: Slack API for DM delivery

## Workflow

### 1. Gather Data

Query vault for:
- **Tasks due today:** Search `tasks/` for frontmatter `due_date` = today
- **Overdue tasks:** Search `tasks/` for `due_date` < today AND `status` != done
- **In-progress ideas:** Search `ideas/` for `status` = active or in-progress
- **People follow-ups:** Search `people/` for non-empty `follow_ups`
- **Admin due today:** Search `admin/` for `due_date` = today
- **Active projects:** Search `projects/` for `status` = active, extract `next_action`
- **Research digest:** Check `research/digests/` for today's file

### 2. Categorize by Automation Potential

**Automate** (Claude completes without human input):
- Research and information gathering
- First drafts of documents/emails
- Data summarization
- File organization

**Augment** (Claude helps human):
- Writing review and critique
- Analysis and synthesis
- Brainstorming sessions

**Human only:**
- Creative work user wants to own
- Relationship conversations
- Strategic decisions
- Physical actions

### 3. Generate Digest

Write to `daily/[YYYY-MM-DD].md`:

```markdown
# Today: [YYYY-MM-DD, Day of Week]

## Overdue ([count])
- [ ] [task] *(due [date], [X] days ago)* #tags

## Due Today ([count])
- [ ] [task] #tags

## Claude Can Handle
Say "do [number]" to start any:
1. [ ] [task] — I'd [specific action]

## Let's Do Together
1. [ ] [task] — I can help by [how]

## Active Projects
| Project | Next Action |
|---------|-------------|
| [name] | [next_action] |

## Ideas in Progress
- [ ] [idea title] — [oneliner]

## People Follow-ups
- [ ] **[Person]**: [follow-up item]

## Research
[Link to today's digest or "No new research today"]
```

### 4. Prompt for Action

End with:
"Good morning! Here's your day. Want me to start on any items I can handle, or dive into something together?"

## Output Constraints

- Overdue section: Show ALL items, sorted oldest first
- Due today: Show ALL items
- Claude can handle: Max 5 items
- Total digest: Scannable on phone (~200 words for main sections)

## Error Handling

- If a folder doesn't exist: Skip that section, note in output
- If no items in a category: Show "[category]: All clear!"
- If frontmatter is malformed: Log warning, skip that file
