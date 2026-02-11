# Brand & Voice Generator

## Description
Generate a personalized brand system and voice profile. Use when user asks to create their brand, define their voice, or personalize the second brain. This is foundational — run before other skills that depend on brand context.

## Triggers
- "help me create my brand"
- "define my voice"
- "personalize my second brain"
- "set up my brand system"
- "create my style guide"

## Workflow

### Phase 1: Discovery
Ask these questions one at a time, waiting for response:

1. What topics do you primarily create content about?
2. Who is your target audience? (Be specific: roles, experience levels, goals)
3. What 3-5 words would you use to describe your ideal tone?
4. What phrases or expressions do you naturally use?
5. What should your content NEVER sound like? (Anti-patterns)
6. Are there creators whose style you admire (not copy)? What do you like about their style?

### Phase 2: Analysis (Optional)
If user has existing content:
- Ask for URL to blog/website/LinkedIn
- Analyze published writing
- Identify patterns in voice, structure, hooks, closings
- Note what's working and what could be refined

### Phase 3: Generation
Based on responses, generate:

1. **Voice Profile** — Tone descriptors, vocabulary preferences, sentence structure
2. **Brand System** — Core themes, content pillars, differentiation points
3. **Style Guide** — Hook patterns, structural preferences, CTA style

### Phase 4: Co-Creation
Present draft to user. Iterate based on feedback.

### Phase 5: Output
Save to two locations:

1. **Brand profile**: `brands/[name]-brand.md`
2. **Style guide**: `_llm-context/writing/style-guide.md`

## Notes

This skill creates foundational context used by other skills:
- Writing Buddy uses the style guide for critiques
- Content skills use the brand profile for voice consistency
- All communication follows these patterns

Run this skill first when setting up a new second brain.
