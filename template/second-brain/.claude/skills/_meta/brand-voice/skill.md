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
- Identify patterns in:
  - Voice and tone
  - Sentence structure
  - Headline style
  - Opening hooks
  - Closing patterns
- Note what's working and what could be refined

### Phase 3: Generation
Based on responses, generate:

**1. Voice Profile**
- Tone descriptors (3-5 words)
- Vocabulary preferences (technical level, jargon policy)
- Sentence structure tendencies
- Phrases to use regularly
- Phrases to avoid always

**2. Brand System**
- Core themes (3-5 pillars)
- Content pillars
- Differentiation points (what makes this voice unique)
- Values expressed through content

**3. Style Guide**
- Hook patterns that work
- Structural preferences (long-form vs. punchy)
- Call-to-action style
- Formatting preferences

### Phase 4: Co-Creation
Present draft to user. Iterate based on feedback:
- "That's right" → Keep it
- "That's not quite right, here's what I mean..." → Refine
- "Add this..." → Expand
- "Remove this..." → Simplify

### Phase 5: Output
Save to two locations:

1. **Brand profile**: `brands/[name]-brand.md`
2. **Style guide**: `_llm-context/writing/style-guide.md`

## Output Format

```yaml
---
type: brand-profile
name: [Brand Name]
created: [date]
last_updated: [date]
---

# [Brand Name] Brand Profile

## Voice Profile

### Tone Descriptors
- [Word 1]
- [Word 2]
- [Word 3]

### What This Voice Sounds Like
[Paragraph description]

### What This Voice NEVER Sounds Like
[Anti-patterns]

## Vocabulary

### Technical Level
[Description of jargon usage, complexity]

### Phrases to Use
- "[phrase]" — [when/why]
- "[phrase]" — [when/why]

### Phrases to Avoid
- "[phrase]" — [why]
- "[phrase]" — [why]

## Brand System

### Core Themes
1. **[Theme 1]**: [Description]
2. **[Theme 2]**: [Description]
3. **[Theme 3]**: [Description]

### Content Pillars
- [Pillar 1]
- [Pillar 2]
- [Pillar 3]

### Differentiation
What makes this voice unique:
[Description]

## Style Guide

### Hooks
Effective patterns:
- [Pattern 1]
- [Pattern 2]

### Structure
[Long-form vs. short, paragraph length, etc.]

### Headlines
[Preferences for titles and headers]

### Calls to Action
[Style for CTAs]

## Audience

### Primary Audience
[Description]

### What They Care About
- [Concern 1]
- [Concern 2]

### What They Already Know
[Baseline knowledge level]

### What They're Trying to Achieve
[Goals]
```

## Notes

This skill creates foundational context used by other skills:
- Writing Buddy uses the style guide for critiques
- Content skills use the brand profile for voice consistency
- All communication follows these patterns

Run this skill first when setting up a new second brain.
