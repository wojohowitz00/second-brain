# Canonical YAML Frontmatter Schema

This is the single source of truth for YAML frontmatter field names, types, and allowed values used across the Obsidian vault.

Schema is additive over existing templates — all existing fields are preserved with their original names. No existing fields are removed or renamed.

---

## Task Schema (`type: task`)

```yaml
type: task                    # Required. Literal "task"
title: ""                     # Required. Free text
due_date: 2026-03-14          # Optional. ISO date, NO QUOTES (Dataview types as date)
status: backlog               # Required. Enum: backlog | active | waiting | blocked | done | someday
priority: medium              # Optional. Enum: high | medium | low
project: "[[ProjectName]]"    # Optional. Obsidian wikilink (quoted in YAML, Dataview reads as link)
domain: admin                 # Optional. Enum: sales | content | product | admin | research | people
context: ""                   # Optional. Enum: quick | deep | collab
tags: []                      # Optional. Array of strings
created: 2026-03-14           # Required. ISO date, NO QUOTES
```

---

## Project Schema (`type: project`)

```yaml
type: project                 # Required. Literal "project"
name: ""                      # Required. Free text
status: active                # Required. Enum: active | on-hold | done | archived
deadline: 2026-06-01          # Optional. ISO date, NO QUOTES
health: green                 # Optional. Enum: green | yellow | red
domain: admin                 # Optional. Enum: sales | content | product | admin | research | people
next_action: ""               # Optional. Free text — next concrete step
tags: []                      # Optional. Array of strings
created: 2026-03-14           # Required. ISO date, NO QUOTES
```

---

## Person Schema (`type: person`)

```yaml
type: person                  # Required. Literal "person"
name: ""                      # Required. Free text
relationship: ""              # Optional. Enum: client | friend | colleague | vendor | other
last_contact: 2026-03-14      # Optional. ISO date, NO QUOTES
follow_up_date: 2026-04-01    # Optional. ISO date, NO QUOTES — drives CRM alerts
context: ""                   # Optional. Free text
follow_ups: []                # Optional. Array of strings
tags: []                      # Optional. Array of strings
last_touched: 2026-03-14      # Keep for backward compat with existing templates
```

---

## Dataview Typing Rules

These rules govern how Dataview interprets YAML field values. Violations break date queries.

| Rule | Correct | Wrong | Effect of Wrong |
|------|---------|-------|-----------------|
| Bare ISO dates are typed as `date` | `due_date: 2026-03-14` | `due_date: "2026-03-14"` | Typed as TEXT — date comparisons break |
| Quoted dates are typed as TEXT | (avoid) | `"2026-03-14"` | Cannot use `> date(today)` |
| Wikilinks must be quoted in YAML | `project: "[[Name]]"` | `project: [[Name]]` | YAML parse error |
| Empty strings are valid | `title: ""` | (omit field) | Dataview treats as null/empty |
| Arrays are valid | `tags: []` | (omit field) | Dataview supports list operations |

**Key rule:** NEVER quote date fields. Quoted dates become text and break all date-based queries.

---

## Enum Reference Table

| Field | Allowed Values |
|-------|---------------|
| `status` (task) | `backlog` \| `active` \| `waiting` \| `blocked` \| `done` \| `someday` |
| `status` (project) | `active` \| `on-hold` \| `done` \| `archived` |
| `priority` | `high` \| `medium` \| `low` |
| `domain` | `sales` \| `content` \| `product` \| `admin` \| `research` \| `people` |
| `context` (task) | `quick` \| `deep` \| `collab` |
| `relationship` | `client` \| `friend` \| `colleague` \| `vendor` \| `other` |
| `health` | `green` \| `yellow` \| `red` |

---

## Backward Compatibility

Existing templates use a subset of these fields. This schema is purely additive:

| Note Type | Existing Fields (preserved) | New Fields Added |
|-----------|----------------------------|-----------------|
| Tasks | `type`, `title`, `due_date`, `status`, `tags`, `created` | `priority`, `project`, `domain`, `context` |
| Projects | `type`, `name`, `status`, `next_action`, `tags`, `created` | `deadline`, `health`, `domain` |
| People | `type`, `name`, `context`, `follow_ups`, `last_touched`, `tags` | `relationship`, `last_contact`, `follow_up_date` |

No existing fields are removed or renamed. New fields are optional unless marked Required above.
