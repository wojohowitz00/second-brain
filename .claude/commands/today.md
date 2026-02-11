# /today — Morning Ritual

Run the complete morning startup sequence:

## 1. Process Inbox
- Check Slack #sb-inbox for new messages (if configured)
- Classify and route each message
- Reply with confirmations
- Update inbox log

## 2. Check External Sources
- Query connected MCPs for relevant updates (calendar, email, tasks)
- Note anything requiring attention

## 3. Gather Today's Items

From vault, collect:
- Tasks with due_date = today (search `tasks/` folder)
- Tasks with due_date < today (overdue)
- Ideas with status = in-progress (search `ideas/`)
- People with pending follow_ups (search `people/`)
- Admin items due today (search `admin/`)
- Active projects with next actions (search `projects/`)

Also check PARA vault structure (`~/PARA/`) for items filed by the Python backend.

## 4. Check Research
- Look for new research digest in research/digests/
- Look for papers awaiting summarization

## 5. Generate Daily File

Write to `daily/[YYYY-MM-DD].md` with:
- Overdue items (oldest first)
- Due today
- Items Claude can automate
- Items for collaboration
- In-progress ideas
- People follow-ups
- Research digest link

## 6. Send Slack Summary (if configured)

DM condensed version:
- Top 5 priorities
- "I can handle these for you" section
- Quick prompt: "What should we tackle first?"

## 7. Offer Assistance

End with:
"Good morning! Here's your day. Want me to start on anything I can handle, or dive into something together?"
