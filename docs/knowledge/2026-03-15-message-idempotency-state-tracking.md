---
type: pattern
slug: 2026-03-15-message-idempotency-state-tracking
title: Idempotent Slack message processing via state store
area: backend.process_inbox
status: mitigated
tags: [state, idempotency, slack, fix]
test_refs:
  - backend.tests.test_integration::test_is_message_processed_returns_false_for_new_message
  - backend.tests.test_integration::test_mark_message_processed_and_check
  - backend.tests.test_integration::test_message_processed_persists_across_checks
  - backend.tests.test_integration::test_different_messages_tracked_independently
  - backend.tests.test_process_inbox::TestProcessMessage::test_skips_already_processed
created: 2026-03-15
updated: 2026-03-15
---

## Context

`process_inbox` polls Slack and calls `process_message()` for each message. To avoid duplicate note creation and to support `fix:` commands that operate on previously filed notes, the backend keeps a simple state store keyed by Slack timestamp (`ts`) that records which messages have been processed and which file path they map to.

## Problem

Without explicit idempotency, transient errors, restarts, or race conditions can cause the same Slack message to be processed multiple times, producing duplicate notes or conflicting `fix:` operations. Conversely, a brittle state implementation could mark messages as processed too early or fail to persist state across runs.

## Attempts

Initial versions mixed state tracking concerns into the inbox processing logic, making it hard to test in isolation and easy to regress. There was no clear contract about when a message should be considered processed, how long state should persist, or how `fix:` should resolve original file locations.

## Resolution

State responsibilities were isolated into the `state` module and locked in with targeted tests:

- `test_is_message_processed_returns_false_for_new_message` and `test_mark_message_processed_and_check` define the basic processed/unprocessed contract.
- `test_message_processed_persists_across_checks` and `test_different_messages_tracked_independently` ensure persistence and independence across message IDs.
- `test_message_to_file_mapping` asserts the mapping from `ts` to file path for `fix:` support.
- `TestProcessMessage.test_skips_already_processed` ensures `process_message()` respects the state store and does not re-file already processed messages.

Together, these tests make message processing idempotent and reliable across runs.

## Regressions

- Any change to how processed state is stored (file layout, retention policy, or keys) must keep the tests above passing and preserve the contract that the same `ts` is never re-processed for filing.
- `fix:` and status commands must continue to rely on the same mapping guarantees, or add new tests if the lookup mechanism changes.

