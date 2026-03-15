## docs/knowledge/ — Compound Engineering Knowledge

This directory stores **short, structured knowledge entries** that make future work on Second Brain easier:

- Past bugs and incidents
- Design decisions and their tradeoffs
- Patterns and anti-patterns discovered over time

Each entry is a small markdown file with YAML frontmatter. See `SCHEMA.md` in this folder for full field definitions.

Minimal example:

```yaml
type: bug
slug: 2026-03-15-slack-rate-limit
title: Slack rate limit handling in ingestion loop
area: backend.slack
status: mitigated        # open | mitigated | closed
tags: [slack, rate_limit, retry]
test_refs:
  - backend.tests.test_slack_pipeline::test_handles_rate_limit_gracefully
created: 2026-03-15
updated: 2026-03-15
```

The body should briefly explain:

- Context
- Problem
- Attempts
- Final fix
- How to detect and prevent regressions

