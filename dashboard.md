---
type: dashboard
created: 2026-01-09
---

# Second Brain Dashboard

Quick overview of your knowledge system.

---

## Active Projects

Projects currently in progress with their next actions.

```dataview
TABLE
    name as "Project",
    next_action as "Next Action",
    created as "Started"
FROM "projects"
WHERE status = "active" AND type = "project"
SORT created DESC
```

---

## Stale Projects

Projects not touched in 14+ days that may need attention.

```dataview
TABLE
    name as "Project",
    next_action as "Next Action",
    last_touched as "Last Touched"
FROM "projects"
WHERE status = "active"
    AND type = "project"
    AND (date(today) - date(last_touched)).days > 14
SORT last_touched ASC
```

---

## People - Pending Follow-ups

People with outstanding follow-up items.

```dataview
TABLE
    name as "Person",
    follow_ups as "Follow-ups",
    last_touched as "Last Contact"
FROM "people"
WHERE type = "person" AND length(follow_ups) > 0
SORT last_touched ASC
```

---

## Recent Captures

Items added in the last 7 days.

```dataview
TABLE
    type as "Type",
    file.name as "Name",
    created as "Added"
FROM "people" OR "projects" OR "ideas" OR "admin"
WHERE created >= date(today) - dur(7 days)
SORT created DESC
LIMIT 20
```

---

## Stub Files

Auto-created files that need details filled in.

```dataview
LIST
FROM "people" OR "projects"
WHERE contains(tags, "stub")
SORT file.name ASC
```

---

## Orphan Notes

Notes with no incoming links (may need connecting).

```dataview
LIST
FROM "ideas"
WHERE length(file.inlinks) = 0
SORT file.ctime DESC
LIMIT 15
```

---

## Admin Tasks - Pending

Outstanding administrative items.

```dataview
TABLE
    task as "Task",
    due_date as "Due",
    created as "Created"
FROM "admin"
WHERE type = "admin" AND status = "pending"
SORT due_date ASC
```

---

## Quick Stats

- **Total Ideas**: `$= dv.pages('"ideas"').length`
- **Active Projects**: `$= dv.pages('"projects"').where(p => p.status == "active").length`
- **People Tracked**: `$= dv.pages('"people"').length`
- **Pending Admin**: `$= dv.pages('"admin"').where(p => p.status == "pending").length`
