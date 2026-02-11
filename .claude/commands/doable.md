# /doable — What Can Claude Handle?

Review task list and identify automation opportunities.

## Categorize All Open Tasks

### Can Automate (Claude does it without human input):
- Research tasks (web searches, gathering information)
- First drafts (emails, documents, outlines)
- Data gathering and summarization
- Scheduling coordination
- File organization
- Repetitive updates

### Should Augment (Claude helps human do it):
- Writing review and critique
- Analysis and synthesis
- Brainstorming and ideation
- Decision support
- Complex problem-solving

### Human Only:
- Creative work user wants to own
- Relationship conversations
- Strategic decisions
- Anything user explicitly wants to do themselves
- Tasks requiring physical action

## Process

1. Gather all open tasks (status != done) from `tasks/`, `admin/`, `projects/`
2. For each task, analyze:
   - Can it be completed with available tools?
   - Does it require human judgment?
   - Is it a research/gathering task?
3. Categorize into three buckets
4. For "automate" items, describe what Claude would do
5. For "augment" items, describe how Claude can help

## Output Format

```markdown
# Automation Review — [Date]

## I Can Do These For You
Say "do [number]" to start any:

1. [ ] [task] — I'd [specific action: search for X, draft Y, gather Z]
2. [ ] [task] — I'd [specific action]

## Let's Do Together
1. [ ] [task] — I can help by [specific support]

## Your Call
These need your direct involvement:
- [ ] [task]

---
Automation potential: [X] of [Y] tasks I can fully handle
```

## Prompt

End with:
"Want me to start on any of the automated items? Just say 'do 1' or 'do all' or pick specific numbers."
