# Canvas Visual Weekly Review

## Description

Generate a JSON Canvas v1.0 file that provides a spatial overview of active work — what's moving, what's stuck, what's blocked — organized into swimlanes by project status.

## Triggers

- Part of /weekly workflow (not standalone)
- "canvas review"
- "visual review"

## Dependencies

- projects/*.md with frontmatter (status, name, health)
- tasks/*.md with frontmatter (status, project, title, due_date)
- Canvas folder at 05_AI_Workspace/canvas/ (created in Phase 1)

## Output

**File:** `05_AI_Workspace/canvas/weekly-review.canvas`

The canvas is overwritten on each run — it is a fresh snapshot, not an evolving document.

## Data Collection

### Step 1: Scan Projects

Read all `projects/*.md` files (skip README.md). Extract from frontmatter:
- `status` (active | waiting | blocked)
- `name` or derive from filename
- `health` (good | at-risk | blocked)

Skip projects with status: done or archived.

Group into three buckets: active, waiting, blocked.

Cap at 10 projects per lane. If more, add an overflow text node: "... and N more"

### Step 2: Scan Tasks (Problem-Focused)

Read all `tasks/*.md` files (skip README.md). Extract from frontmatter:
- `status`
- `project` (which project this belongs to)
- `title` or derive from filename
- `due_date`

For each project, collect ONLY:
- Tasks with status: blocked
- Tasks with due_date in the past (overdue)

Do NOT collect all tasks — this board shows problems, not full workload.

## Canvas Layout

### File Format

Valid JSON Canvas v1.0:

```json
{
  "nodes": [...],
  "edges": []
}
```

Edges are always an empty array. This is a spatial layout, not a graph.

### Swimlane Configuration

| Lane    | X position | Color | Label     |
|---------|-----------|-------|-----------|
| Active  | -700      | "4"   | "Active"  |
| Waiting | 0         | "3"   | "Waiting" |
| Blocked | 700       | "1"   | "Blocked" |

Color codes are JSON Canvas v1.0 color values: "1"=red, "3"=yellow, "4"=green.

### Group Node (Swimlane)

Each lane is a group node:

```json
{
  "id": "lane-active",
  "type": "group",
  "label": "Active",
  "color": "4",
  "x": -700,
  "y": 0,
  "width": 600,
  "height": 200
}
```

Height is calculated: base 200 + (140 × number of project cards in lane).

### Project Card (Text Node)

Each project is a text node inside its lane group:

```json
{
  "id": "proj-my-project-filename",
  "type": "text",
  "text": "**[[My Project Name]]**\nHealth: good\n- Overdue Task Title (due 2026-03-01) — OVERDUE\n- Blocked Task Title — BLOCKED",
  "x": -680,
  "y": 20,
  "width": 560,
  "height": 120
}
```

**Card text format:**

```
**[[Project Name]]**
Health: good/at-risk/blocked
- Task Title (due YYYY-MM-DD) — OVERDUE
- Task Title — BLOCKED
```

If no blocked/overdue tasks: show only the project name and health line. No task lines.

**Card height:** 120px base. Add 20px per additional task line beyond the first.

**Card stacking:** Cards are stacked vertically inside the group with 20px padding from group edges and 20px gap between cards.

Position calculation:
- First card: y = group_y + 20
- Each subsequent card: y = previous_card_y + previous_card_height + 20

### ID Generation

Use deterministic IDs (makes canvas diffable across weeks):
- Lane groups: `lane-active`, `lane-waiting`, `lane-blocked`
- Project cards: `proj-{filename-without-extension}` (e.g., `proj-client-portal`)

### Full Canvas JSON Structure

```json
{
  "nodes": [
    {
      "id": "lane-active",
      "type": "group",
      "label": "Active",
      "color": "4",
      "x": -700,
      "y": 0,
      "width": 600,
      "height": 480
    },
    {
      "id": "proj-my-project",
      "type": "text",
      "text": "**[[My Project]]**\nHealth: good",
      "x": -680,
      "y": 20,
      "width": 560,
      "height": 120
    },
    {
      "id": "lane-waiting",
      "type": "group",
      "label": "Waiting",
      "color": "3",
      "x": 0,
      "y": 0,
      "width": 600,
      "height": 200
    },
    {
      "id": "lane-blocked",
      "type": "group",
      "label": "Blocked",
      "color": "1",
      "x": 700,
      "y": 0,
      "width": 600,
      "height": 200
    }
  ],
  "edges": []
}
```

## Error Handling

- **No projects found:** Generate a minimal canvas with a single text node: `"No active projects this week"` at x: -100, y: 0, width: 400, height: 80.
- **Malformed project frontmatter:** Skip that project, continue with remaining.
- **Canvas folder missing:** Create `05_AI_Workspace/canvas/` before writing. (Should already exist from Phase 1 setup.)
- **No blocked/overdue tasks for a project:** Show project name and health only — no task lines.

## Anti-Patterns

- Do NOT use `.md` extension — file must be `.canvas`
- Do NOT include completed or archived projects
- Do NOT include all tasks — only blocked/overdue (problem-focused)
- Do NOT add edges — this is a spatial layout, not a graph
- Do NOT include a "Wins" or "Completed" lane — board shows active work only
- Do NOT emit pretty-printed JSON with excessive whitespace — compact is fine

## Integration

This skill is invoked as Step 5b in the `/weekly` workflow, after the insights detection step (5a) and before "Generate Review" (Step 6).

After writing the canvas file, output:
"Visual board updated — open weekly-review.canvas in Obsidian for spatial overview."
