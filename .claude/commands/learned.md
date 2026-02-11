# /learned — End-of-Session Documentation

Capture what we learned for future context. This is how context files grow organically.

## Process

1. Review the current session's conversation
2. Identify learnings:
   - New facts about user's preferences
   - Workflow patterns that worked well
   - Things user corrected or clarified
   - New terminology or concepts
   - Gotchas discovered with tools/MCPs
   - Style preferences revealed

3. For each learning:
   - Identify which context file it belongs in
   - Draft the addition
   - Show user for approval

4. On approval, update the relevant file(s)

## Context File Targets

| Learning Type | Target File |
|--------------|-------------|
| Writing preferences | `_llm-context/writing/style-guide.md` |
| Personal info | `_llm-context/personal/profile.md` |
| Business context | `_llm-context/business/profile.md` |
| Product details | `_llm-context/business/products/[product].md` |
| Audience insights | `_llm-context/business/audience.md` |
| MCP gotchas | `.claude/claude.md` (MCP Gotchas section) |
| Tag taxonomy | `.claude/claude.md` (Tag Taxonomy section) |
| Workflow patterns | Relevant skill's `skill.md` |

## Output Format

```markdown
# Session Learnings — [Date/Time]

## Summary
[1-2 sentence summary of what we worked on]

## Proposed Updates

### → [target file]
**Add/Clarify:**
[proposed content]

---
Approve these updates? (yes / no / edit [section])
```

## Rules

- Only propose updates for genuinely new information
- Keep additions concise
- Don't duplicate existing content
- Ask for approval before making any changes
- If user says "edit", ask what to change
