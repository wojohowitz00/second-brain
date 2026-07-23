---
type: bug
slug: 2026-03-15-slack-rate-limit
title: Slack rate limit handling in inbox polling
area: backend.slack
status: mitigated
tags: [slack, rate_limit, retry, inbox]
test_refs:
  - backend.tests.test_slack_client::test_rate_limit_error_handling
created: 2026-03-15
updated: 2026-03-15
---

## Context

The Slack inbox poller calls the Web API to fetch messages from the `#sb-inbox` channel. Slack enforces per-workspace and per-method rate limits, returning HTTP 429 with a `Retry-After` header when limits are exceeded. This can happen if the poll interval is too aggressive or multiple tools share the same bot token.

## Problem

If rate limits are not handled explicitly, the inbox loop will either treat 429s as generic errors (no backoff) or silently drop messages while still claiming success. In the worst case, repeated 429s can look like an empty inbox even though new messages exist, breaking the guarantee that everything in `#sb-inbox` gets filed.

## Attempts

Early versions treated any non-200 response as a generic `SlackAPIError` and let the caller decide what to do, with no special handling for 429. That made it hard to distinguish between transient throttling and permanent configuration errors (like `invalid_auth`), and test coverage couldn’t assert on correct backoff behavior.

## Resolution

The Slack client now recognizes HTTP 429 and raises a dedicated `SlackRateLimitError`, using the `Retry-After` header to drive backoff. The test `test_rate_limit_error_handling` mocks a 429 response, patches `time.sleep`, and asserts that `fetch_messages()` raises `SlackRateLimitError("Rate limited")` rather than continuing as normal. Callers can treat this as a signal to pause the polling loop without losing state.

## Regressions

- Unit protection: `backend.tests.test_slack_client::test_rate_limit_error_handling` must continue to assert that 429 responses raise `SlackRateLimitError` and that the retry path calls `time.sleep` with the correct delay.
- Golden behavior: any change to Slack polling (e.g., new client, different HTTP library, or batching) must preserve the contract that 429s do not look like “no messages” and are surfaced distinctly to the scheduler.

