---
type: decision
slug: 2026-03-15-note-frontmatter-para-schema
title: Standardized PARA frontmatter for captured notes
area: backend.file_writer
status: mitigated
tags: [frontmatter, para, vault, schema]
test_refs:
  - backend.tests.test_integration::test_create_note_file_frontmatter_has_required_fields
  - backend.tests.test_file_writer::TestBuildFrontmatter::test_contains_all_required_fields
created: 2026-03-15
updated: 2026-03-15
---

## Context

Captured Slack messages are turned into Obsidian notes with YAML frontmatter that encodes PARA classification (domain, para_type, subject, category) and metadata for Dataview queries. The `file_writer` module is the single entry point for building this frontmatter across multiple flows (Slack capture, YouTube ingest, tasks).

## Problem

Without a stable frontmatter schema, Dataview queries and downstream automation (dashboards, reviews, people/CRM views) become brittle. Inconsistent field names or missing keys make it hard to write reliable queries like “all active Personal projects in 1_Projects/apps” or “all notes in CCBH/2_Areas/clients”.

## Attempts

Early experiments used ad-hoc frontmatter with partially filled fields, and some integrations wrote their own frontmatter directly. This created drift between different note types and made it unclear which fields were required vs. optional. Tests existed but did not fully lock in the schema.

## Resolution

The project standardized on a PARA-aware frontmatter schema implemented in `build_frontmatter()` and exercised via both unit and integration tests:

- `TestBuildFrontmatter.test_contains_all_required_fields` asserts that `domain`, `para_type`, `subject`, `category`, `confidence`, and `created` are present.
- `test_create_note_file_frontmatter_has_required_fields` in the integration suite asserts the same guarantees when writing real files into a temporary vault.

Together, these tests define the contract for any future frontmatter changes and ensure that new sources (like YouTube notes) remain compatible with the core PARA model.

## Regressions

- Any change to the frontmatter schema (renaming fields, changing types, or removing keys) must update the tests above and be reflected in Obsidian Dataview queries and the canonical YAML schema docs.
- New capture flows must call `build_frontmatter()` rather than hand-writing YAML to avoid schema drift.

