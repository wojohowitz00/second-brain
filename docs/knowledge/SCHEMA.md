## Knowledge Entry YAML Schema

Each file in `docs/knowledge/` uses YAML frontmatter with the following fields:

```yaml
type: bug                # Required. Enum: bug | decision | incident | pattern | anti_pattern
slug: 2026-03-15-slack-rate-limit  # Required. Kebab-case identifier, unique per file
title: "Slack rate limit handling in ingestion loop"  # Required. Short human-readable title
area: backend.slack      # Required. Enum-like string: backend.slack | backend.classifier | backend.file_writer | backend.process_inbox | vault.io | interactive.claude | infra.tests | infra.docs | other
status: mitigated        # Required. Enum: open | mitigated | closed
tags: [slack, rate_limit, retry]   # Optional. Array of lowercase strings
test_refs:               # Optional. List of pytest test identifiers that cover this case
  - backend.tests.test_slack_client::test_rate_limit_error_handling
created: 2026-03-15      # Required. ISO date, NO QUOTES
updated: 2026-03-15      # Required. ISO date, NO QUOTES (same as created if never updated)
```

Body sections should follow this order:

1. **Context** — where this showed up, symptoms, environment
2. **Problem** — what was actually wrong
3. **Attempts** — approaches that failed or were discarded
4. **Resolution** — the fix or decision taken
5. **Regressions** — how to detect this in tests or logs

