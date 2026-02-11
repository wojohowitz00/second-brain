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

**Level 1 — Description** (always visible to Claude)
- 1-2 sentences explaining what the skill does
- Used to decide IF this skill is relevant

**Level 2 — Full skill.md** (loaded when invoked)
- Complete workflow instructions
- HOW to execute the skill

**Level 3 — Supporting files** (loaded as needed)
- Prompts for specific steps
- Scripts for execution
- Reference documentation

### 3. Determine Category

Place skill in appropriate folder:

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
[1-2 sentence description — this is Level 1, always visible to Claude]

## Triggers
- [trigger phrase 1]
- [trigger phrase 2]
- [trigger phrase 3]

## Dependencies
[List any required: APIs, MCPs, other skills, files, context]

## Workflow

### Step 1: [Name]
[What to do, be specific]

### Step 2: [Name]
[What to do]

### Step 3: [Name]
[What to do]

## Output
[What the skill produces]
[Where it goes]
[What format]

## Error Handling
[How to handle common failures]
[Fallback behaviors]
```

### 6. Test

1. Invoke the skill with a trigger phrase
2. Verify it loads correctly (check Level 1 → Level 2 transition)
3. Run through the complete workflow
4. Check outputs are created correctly
5. Fix any issues in skill.md
6. Document gotchas discovered

### 7. Iterate

After first real use, ask:
"How did that work? What should we adjust?"

Update skill.md based on feedback.

## Skill Template (Copy-Paste Ready)

```markdown
# [Skill Name]

## Description
[One-two sentence description of what this skill does and when to use it.]

## Triggers
- "[natural phrase 1]"
- "[natural phrase 2]"
- "[natural phrase 3]"

## Dependencies
- [Dependency 1]
- [Dependency 2]

## Workflow

### 1. [First Step Name]
[Detailed instructions]

### 2. [Second Step Name]
[Detailed instructions]

### 3. [Third Step Name]
[Detailed instructions]

## Output
**Location:** [where output goes]
**Format:** [file type, structure]

## Error Handling
- If [error condition]: [what to do]
- If [error condition]: [what to do]
```

## Best Practices

1. **Keep descriptions short** — They're loaded into every conversation
2. **Be specific in workflows** — Vague instructions produce inconsistent results
3. **Include error handling** — Things will go wrong
4. **Test with real use cases** — Not just happy path
5. **Iterate based on usage** — Skills improve over time
6. **Document gotchas** — Save future frustration
