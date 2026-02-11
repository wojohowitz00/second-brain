# LLM Context Index

This directory contains all persistent context about me, my work, and my preferences.

## How to Use This

1. Based on my request, identify which context category is relevant
2. Load the appropriate profile/index file
3. From that index, load only the specific files needed
4. **Never load everything** — be selective

## Available Context

### Personal
`personal/profile.md` — Personal background, preferences, non-work context

### Business
`business/profile.md` — Company overview, products, audience, marketing

### Writing
`writing/style-guide.md` — Voice, tone, structure, phrases

## Loading Rules

| Request Type | Load |
|-------------|------|
| Personal/life questions | `personal/profile.md` |
| Work/business tasks | `business/profile.md` |
| Writing critique/help | `writing/style-guide.md` |
| Specific product work | `business/products/[product].md` |

## Philosophy

**Too much irrelevant context hurts performance.**

- One topic = one file
- Index files point to specific files
- Load only what's needed for current task
- Files grow organically through the `/learned` command
