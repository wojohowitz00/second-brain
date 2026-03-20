---
type: pattern
slug: 2026-03-15-process-inbox-ordering
title: Process Slack inbox messages oldest-first
area: backend.process_inbox
status: mitigated
tags: [slack, ordering, inbox, idempotency]
test_refs:
  - backend.tests.test_process_inbox::TestProcessAll::test_processes_messages_oldest_first
created: 2026-03-15
updated: 2026-03-15
---

## Context

`process_all()` fetches a batch of new Slack messages and hands each one to `process_message()`, which handles classification, file creation, and status updates. The Slack API returns messages in reverse chronological order by default (newest first).

## Problem

If the poller processes messages newest-first, edits and corrections (like `fix:` or status commands) can run before the original capture note has been written, especially when multiple messages share close timestamps. This can also break assumptions about stateful operations that expect earlier events (like initial task creation) to precede later ones (like `!done`).

## Attempts

An early implementation implicitly relied on Slack’s default ordering and didn’t reverse the message list before processing. This “mostly worked” during light usage but left edge cases where newer messages were handled before older ones when backlog bursts arrived or when clock skew affected message timestamps.

## Resolution

`process_all()` now explicitly reverses the fetched list so that messages are processed oldest-first. The test `TestProcessAll.test_processes_messages_oldest_first` mocks `fetch_new_messages()` to return two messages in newest-first order and asserts that `process_message()` is called on the older message first. This locks in the ordering contract for future refactors.

## Regressions

- Unit protection: `backend.tests.test_process_inbox::TestProcessAll::test_processes_messages_oldest_first` must continue to assert that the first call to `process_message()` receives the oldest message by `ts`.
- Future changes to batching, pagination, or Slack client behavior must preserve the invariant that the inbox is processed in ascending timestamp order, even if the underlying API call order changes.

