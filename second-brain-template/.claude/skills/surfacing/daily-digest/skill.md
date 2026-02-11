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
- Obsidian vault structure with tasks/, projects/, ideas/, people/, admin/ folders
- Template structure with YAML frontmatter
- Optional: Slack API for DM delivery

## Workflow

### 1. Gather Data

Query Obsidian vault for:

**Tasks due today:**
- Search `tasks/` for frontmatter `due_date` = today's date
- Sort by any priority indicators

**Overdue tasks:**
- Search `tasks/` for `due_date` < today AND `status` ≠ done
- Sort oldest first (most overdue at top)

**In-progress ideas:**
- Search `ideas/` for `status` = active or in-progress

**People follow-ups:**
- Search `people/` for non-empty `follow_ups` array

**Admin due today:**
- Search `admin/` for `due_date` = today

**Active projects:**
- Search `projects/` for `status` = active
- Extract `next_action` field

**Research digest:**
- Check `research/digests/` for today's file

### 2. Categorize by Automation Potential

For each item, classify:

**Automate** (Claude can complete without human input):
- Research and information gathering
- First drafts of documents/emails
- Data summarization
- File organization
- Scheduling coordination

**Augment** (Claude helps human do it):
- Writing review and critique
- Analysis and synthesis
- Brainstorming sessions
- Decision support

**Human only** (User should do):
- Creative work user wants to own
- Relationship conversations
- Strategic decisions
- Physical actions

### 3. Generate Digest

Create markdown file with structure:

```markdown
# Today: [YYYY-MM-DD, Day of Week]

## 🔴 Overdue ([count])
- [ ] [task] *(due [date], [X] days ago)* #tags
- [ ] [task] *(due [date])* #tags

## 📅 Due Today ([count])
- [ ] [task] #tags
- [ ] [task] #tags

## 🚀 Claude Can Handle
*Say "do [number]" to start any:*
1. [ ] [task] — I'd [specific action]
2. [ ] [task] — I'd [specific action]

## 🤝 Let's Do Together
1. [ ] [task] — I can help by [how]
2. [ ] [task] — I can help by [how]

## 🎯 Active Projects
| Project | Next Action |
|---------|-------------|
| [name] | [next_action] |

## 💡 Ideas in Progress
- [ ] [idea title] — [oneliner]

## 👥 People Follow-ups
- [ ] **[Person]**: [follow-up item]

## 📚 Research
[Link to today's research digest if exists, or "No new research today"]

---
*Generated [timestamp]*
```

### 4. Output

**Obsidian:**
- Write to `daily/[YYYY-MM-DD].md`
- Overwrite if already exists (re-running updates it)

**Slack DM (if configured):**
Send condensed version:
```
Good morning! Here's your [Day]:

🔴 [X] overdue items
📅 [Y] due today
🚀 [Z] items I can handle for you

Top 3 priorities:
1. [item]
2. [item]
3. [item]

Want me to start on anything?
```

### 5. Prompt for Action

End digest display with:

"Good morning! Here's your day. Want me to:
- Start on any items I can handle? (say 'do 1, 3')
- Dive into something together?
- Walk through the overdue items?"

## Output Constraints

- Overdue section: Show ALL items, sorted oldest first
- Due today: Show ALL items
- Claude can handle: Max 5 items
- Ideas in progress: Max 4 items
- Projects: Max 5 active projects
- Total digest: Should be scannable on phone screen (~200 words for main sections)

## Error Handling

- If a folder doesn't exist: Skip that section, note in output
- If no items in a category: Show "[category]: All clear! 🎉"
- If frontmatter is malformed: Log warning, skip that file
