# Skill Creator

## Description
Create new skills for the second brain system. Use when user wants to add a new capability or automate a workflow.

## Triggers
- "create a new skill"
- "I want to add [capability]"
- "build a skill for [X]"
- "help me make a skill"
- "automate [workflow]"

## Workflow

### 1. Discovery

Ask these questions to understand the skill:

1. **What should this skill do?** (The goal/outcome)
2. **When should it be triggered?** (Natural phrases user would say)
3. **What inputs does it need?** (Files, APIs, user input, context)
4. **What outputs should it produce?** (Files, messages, actions)
5. **Does it need external services?** (MCP servers, APIs)
6. **Should it run automatically or on-demand?** (Scheduled vs. triggered)

### 2. Design Progressive Disclosure

Structure the skill with three levels:

**Level 1 — Description** (always visible to Claude): 1-2 sentences explaining what the skill does
**Level 2 — Full skill.md** (loaded when invoked): Complete workflow instructions
**Level 3 — Supporting files** (loaded as needed): Prompts, scripts, reference docs

### 3. Determine Category

| Category | Purpose |
|----------|---------|
| `_meta` | Foundational/system skills |
| `capture` | Input processing and routing |
| `surfacing` | Output generation (digests, reports) |
| `writing` | Content creation support |
| `research` | Information gathering |
| `mcp-client` | External service integration |
| `[custom]` | User-defined categories |

### 4. Create Files

Create skill folder structure:
```
.claude/skills/[category]/[skill-name]/
├── skill.md           # Required: Main instructions
├── [prompt].md        # Optional: Specific prompts
├── [script].py        # Optional: Code to execute
└── [reference].md     # Optional: Supporting docs
```

### 5. Write skill.md

Use this template:

```markdown
# [Skill Name]

## Description
[1-2 sentence description]

## Triggers
- [trigger phrase 1]
- [trigger phrase 2]

## Dependencies
[Required: APIs, MCPs, other skills, files, context]

## Workflow

### Step 1: [Name]
[What to do]

## Output
[What, where, format]

## Error Handling
[How to handle failures]
```

### 6. Test and Iterate

1. Invoke with a trigger phrase
2. Run through the complete workflow
3. Fix issues, document gotchas
4. Ask: "How did that work? What should we adjust?"

## Best Practices

1. **Keep descriptions short** — They're loaded into every conversation
2. **Be specific in workflows** — Vague instructions produce inconsistent results
3. **Include error handling** — Things will go wrong
4. **Test with real use cases** — Not just happy path
5. **Iterate based on usage** — Skills improve over time
