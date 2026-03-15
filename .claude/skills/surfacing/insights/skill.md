# Vault-Wide Insights Detection

## Description

Scan all vault-external content folders (tasks/, projects/) and surface patterns the user would otherwise miss: dormant projects, overcommitment, goal drift, and neglected domains. Produces a dated insights report.

This is an instruction document for Claude. It defines how to perform the analysis when invoked — it does not query Dataview and does not run automatically.

## Triggers

- Part of /weekly workflow (primary invocation path — not standalone)
- "vault insights"
- "pattern detection"

**Do NOT invoke on session start.** Runs only as part of /weekly.

## Output

File: `05_AI_Workspace/insights/YYYY-MM-DD-insights.md`

Frontmatter:
```yaml
---
type: insights
date: YYYY-MM-DD
generated_by: claude
---
```

Sections (omit any section with zero findings):
- `## Goal Drift`
- `## Neglected Areas`
- `## Overcommitment`
- `## Dormant Projects`

Each insight: one-line observation + one-line recommendation, with `[[wikilinks]]` to specific notes.

Hard cap: **5–10 items total.** If more than 10 insights are found, prioritize:
1. Overcommitment (most actionable)
2. Goal drift (misaligned effort)
3. Dormant projects (hidden weight)
4. Neglected areas (awareness gaps)

If no insights found, write a brief note: "No significant patterns detected this week."

**Do NOT quote dates in frontmatter.** Bare ISO format only.

## Detection Rules

All four rules use the tag `PROACT-01`.

---

### Rule 1 — Dormant Projects (PROACT-01)

**What to scan:** `projects/*.md` (skip README.md and any file named README*)

**How to check staleness:**

For each file:
```bash
stat -f "%Sm" -t "%s" "$file"
```

This returns the modification time as a Unix epoch. Compare to current epoch. Difference > 1,209,600 seconds (14 days) = dormant.

**What to flag:** Files where frontmatter `status: active` AND last modified > 14 days ago.

**Output format:**
```
[[project-name]] dormant for N days — consider archiving or adding a next task
```

**Skip:** projects with status: done, someday, archived, or any non-active status.

---

### Rule 2 — Neglected Areas (PROACT-01)

**What to scan:** `tasks/*.md` frontmatter for domain tags (sales, content, product, admin, research, people)

**How to compare:**

1. For each domain, find the most recently modified task file in that domain (using `stat`)
2. Identify which domains have ANY task modified in the past 14 days (active domains)
3. Identify which domains have NO task modified in the past 14 days (neglected domains)
4. Flag only if: at least one domain is active AND at least one domain is neglected

**Output format:**
```
#domain has had no activity in N days while #other-domain is active
```

**Skip:** domains with zero tasks (no files tagged for that domain). Silence > absence.

---

### Rule 3 — Overcommitment (PROACT-01)

**What to scan:** `tasks/*.md` frontmatter for `status: active`

**Threshold:** 10 or more active tasks triggers a warning.

**How to count:**
```bash
grep -l "status: active" tasks/*.md | wc -l
```

**Output format:**
```
N active tasks — consider deferring or completing some before adding more
```

This is a single line, not a per-task breakdown.

---

### Rule 4 — Goal Drift (PROACT-01)

**What to scan:** `tasks/*.md` where `status: active`

**What to check:**

For each active task:
1. Extract the `project` field from frontmatter
2. If the `project` field is **empty or missing**: skip silently (tasks without a project are valid)
3. If the `project` field is **non-empty**: check whether a corresponding file exists in `projects/`
   - If the project file does not exist: flag it
   - If the project file exists but has `status` != `active`: flag it

**Output format:**
```
[[task-name]] references project [[project-name]] which is inactive/missing
```

---

## Execution Order

Run detection rules in this order to support prioritized capping:
1. Overcommitment (single line, always include if triggered)
2. Goal drift
3. Dormant projects
4. Neglected areas

If the total count of findings reaches 10, stop and omit remaining rules.

---

## Error Handling

- **Missing directories** (`tasks/`, `projects/`): Skip that detection rule entirely, continue with others
- **Malformed frontmatter** (can't parse YAML): Skip that file, continue
- **No active tasks**: Overcommitment and goal drift rules produce zero findings — normal
- **stat command fails on a file**: Skip that file, continue

---

## Anti-Patterns

- Do NOT run on session start
- Do NOT use Dataview queries — this is a Claude analysis skill, Claude reads files directly
- Do NOT quote dates in frontmatter output
- Do NOT produce unbounded lists — enforce the 5–10 item cap
- Do NOT flag tasks with empty project field — absence of project linkage is not drift
