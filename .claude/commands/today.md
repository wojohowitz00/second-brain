# /today — Morning Briefing

Run the morning briefing to start your day.

## What It Does

1. **Scan tasks, people, and projects** for overdue items, items due today, upcoming deadlines, and follow-ups
2. **Write a daily brief note** to `05_AI_Workspace/daily-briefs/YYYY-MM-DD-daily-brief.md`
3. **Summarize in session** with orient-first counts and top priorities
4. **Offer automation opportunities** — things Claude can act on right now
5. **Route alerts by severity** — overdue items post to Slack and trigger macOS notification; due-today items trigger macOS notification only; stale follow-ups appear in daily brief only

## How to Use

Just run `/today` at the start of any session. The briefing is also triggered by:
- "morning briefing"
- "what's on today"
- "daily brief"

## Alert Routing

The morning briefing delivers urgent items through external channels based on severity:

| Item Type | Slack | macOS Notification | Daily Brief |
|-----------|-------|--------------------|-------------|
| Overdue task | Yes | Yes | Yes |
| Due today | No | Yes | Yes |
| Stale follow-up (7+ days) | No | No | Yes |

- Maximum 5 alert items per briefing (overdue prioritized first, then due-today, then stale)
- Slack alerts go to the configured channel (`SLACK_CHANNEL_ID` in `backend/_scripts/.env`)
- macOS notification is a single consolidated alert (not one per item)
- Delivery failures (network, auth) are logged in the session but do not block the briefing

## Skill Reference

This command invokes the **daily-digest** skill at:
`.claude/skills/surfacing/daily-digest/skill.md`
