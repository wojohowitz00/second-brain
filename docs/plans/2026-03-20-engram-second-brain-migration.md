# Engram Second Brain Migration Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Replace the legacy Slack-to-Obsidian product as the active implementation path and deliver the PRD-aligned `Second Brain` package inside the Engram repo as a minimal, read-only human knowledge layer that feeds Open Brain during Weekly Review.

**Architecture:** Build the new implementation in `/Users/richardyu/PARA/01_Projects/Personal/apps/engram/second-brain` from a clean skeleton. Treat `/Users/richardyu/PARA/01_Projects/Personal/apps/second-brain` as a reference archive only: port selected templates, wording, and vault-reading ideas, but do not reuse Slack ingestion, menu bar UI, classification, or vault-writing flows because they violate the PRD's authorship boundary.

**Tech Stack:** Markdown templates and prompts, Claude Code policy files, Node/TypeScript integration tests where needed, Open Brain MCP tools, git worktrees, shell verification commands.

---

## Scope Guardrails

- Do not port `backend/_scripts/file_writer.py`, `backend/_scripts/process_inbox.py`, Slack polling, menu bar UI, LaunchAgent packaging, or Veritas push integrations into the new Engram `second-brain/` package.
- Do not carry forward any workflow where AI creates, edits, or deletes files in the human vault.
- Do port useful content from these reference sources when it fits the PRD:
  - `/Users/richardyu/PARA/01_Projects/Personal/apps/second-brain/second-brain-template/`
  - `/Users/richardyu/PARA/01_Projects/Personal/apps/second-brain/GUIDE.md`
  - `/Users/richardyu/PARA/01_Projects/Personal/apps/second-brain/docs/GUIDE.md`
  - `/Users/richardyu/PARA/01_Projects/Personal/apps/second-brain/backend/_scripts/vault_scanner.py`
- Use the PRD as the source of truth for file structure and behavior:
  - `/Users/richardyu/PARA/01_Projects/Personal/apps/engram/PRD-Personal-AI-Infrastructure.md`

### Task 1: Create the Target Package Skeleton

**Files:**
- Create: `/Users/richardyu/PARA/01_Projects/Personal/apps/engram/second-brain/README.md`
- Create: `/Users/richardyu/PARA/01_Projects/Personal/apps/engram/second-brain/CLAUDE.md.template`
- Create: `/Users/richardyu/PARA/01_Projects/Personal/apps/engram/second-brain/prompts/weekly-review.md`
- Create: `/Users/richardyu/PARA/01_Projects/Personal/apps/engram/second-brain/prompts/quick-capture.md`
- Create: `/Users/richardyu/PARA/01_Projects/Personal/apps/engram/second-brain/tests/acceptance/second-brain.test.md`
- Create: `/Users/richardyu/PARA/01_Projects/Personal/apps/engram/second-brain/tests/integration/vault-feed.test.ts`

**Step 1: Write the failing structure check**

Run:

```bash
cd /Users/richardyu/PARA/01_Projects/Personal/apps/engram
test -f second-brain/README.md
```

Expected: shell exits non-zero because the package files do not exist yet.

**Step 2: Create the package directories**

Run:

```bash
cd /Users/richardyu/PARA/01_Projects/Personal/apps/engram
mkdir -p second-brain/prompts second-brain/tests/acceptance second-brain/tests/integration
```

**Step 3: Write the minimal seed files**

Use these exact starter sections:

```md
# Second Brain

## Intent
- Human-authored vault only
- AI reads but never writes
- Weekly Review feeds Open Brain

## Deliverables
- CLAUDE.md.template
- prompts/weekly-review.md
- prompts/quick-capture.md
- tests/acceptance/second-brain.test.md
- tests/integration/vault-feed.test.ts
```

```md
# Vault Rules

You are operating inside a personal knowledge vault.

## Read Access
- You may read any file in this vault.

## Write Prohibition
- You may NEVER create, edit, or delete any file in this vault.
- All AI output must go to Open Brain via MCP.

## Analysis Scope
- Ignore files tagged `#ai-generated`
- Focus only on human-authored content
```

**Step 4: Verify the files exist**

Run:

```bash
cd /Users/richardyu/PARA/01_Projects/Personal/apps/engram
find second-brain -maxdepth 3 -type f | sort
```

Expected: all six files appear.

**Step 5: Commit**

```bash
cd /Users/richardyu/PARA/01_Projects/Personal/apps/engram
git add second-brain
git commit -m "docs: scaffold engram second-brain package"
```

### Task 2: Inventory Reusable Legacy Assets and Record Explicit Non-Ports

**Files:**
- Create: `/Users/richardyu/PARA/01_Projects/Personal/apps/engram/docs/second-brain-migration-inventory.md`
- Modify: `/Users/richardyu/PARA/01_Projects/Personal/apps/engram/second-brain/README.md`

**Step 1: Write the failing inventory check**

Run:

```bash
cd /Users/richardyu/PARA/01_Projects/Personal/apps/engram
test -f docs/second-brain-migration-inventory.md
```

Expected: shell exits non-zero.

**Step 2: Inspect the legacy sources**

Run:

```bash
sed -n '1,200p' /Users/richardyu/PARA/01_Projects/Personal/apps/second-brain/second-brain-template/README.md
sed -n '1,220p' /Users/richardyu/PARA/01_Projects/Personal/apps/second-brain/docs/GUIDE.md
sed -n '1,220p' /Users/richardyu/PARA/01_Projects/Personal/apps/second-brain/backend/_scripts/vault_scanner.py
```

**Step 3: Write the inventory document**

The document must contain these sections:

```md
# Second Brain Migration Inventory

## Port As-Is
- Short note starter language from template files

## Port With Rewrite
- Vault scanning ideas for read-only note enumeration
- Weekly review phrasing from GUIDE.md

## Do Not Port
- Slack ingestion
- Ollama classification
- Vault file creation
- Menu bar UI
- LaunchAgent and packaging
- Veritas integration
```

Add a short note in `second-brain/README.md` pointing to this inventory so future edits preserve the boundary.

**Step 4: Verify the boundary list is present**

Run:

```bash
rg -n "Do Not Port|Slack ingestion|Vault file creation|Menu bar UI" /Users/richardyu/PARA/01_Projects/Personal/apps/engram/docs/second-brain-migration-inventory.md
```

Expected: four matching lines.

**Step 5: Commit**

```bash
cd /Users/richardyu/PARA/01_Projects/Personal/apps/engram
git add docs/second-brain-migration-inventory.md second-brain/README.md
git commit -m "docs: add second-brain migration inventory"
```

### Task 3: Write the Human-Vault Contract

**Files:**
- Modify: `/Users/richardyu/PARA/01_Projects/Personal/apps/engram/second-brain/README.md`
- Modify: `/Users/richardyu/PARA/01_Projects/Personal/apps/engram/second-brain/CLAUDE.md.template`
- Test: `/Users/richardyu/PARA/01_Projects/Personal/apps/engram/second-brain/tests/acceptance/second-brain.test.md`

**Step 1: Write the failing acceptance scenarios**

Add these scenarios first:

```md
GIVEN Claude Code is launched from the vault root directory
WHEN the agent is asked to read a specific note
THEN the note content is returned correctly

GIVEN the write prohibition rule is active
WHEN the agent is asked to create or edit a vault file
THEN the agent declines
AND no vault file is modified
```

**Step 2: Expand the README contract**

Add these exact sections:

```md
## Principles
- The vault is for human-authored notes only.
- AI output belongs in Open Brain, not the vault.
- Weekly Review is the only defined bridge from vault to Open Brain.

## What This Package Does Not Include
- Inbox capture automation
- Classification pipelines
- Task sync
- Background app runtime
```

**Step 3: Expand `CLAUDE.md.template`**

Add explicit wording for:
- read-only vault access
- `#ai-generated` exclusion
- sending summaries and captures to Open Brain via `capture_thought`
- refusing file write requests even if the user asks indirectly

**Step 4: Verify the contract text**

Run:

```bash
rg -n "human-authored|capture_thought|#ai-generated|NEVER create, edit, or delete" /Users/richardyu/PARA/01_Projects/Personal/apps/engram/second-brain
```

Expected: matches in the README, template, and acceptance test.

**Step 5: Commit**

```bash
cd /Users/richardyu/PARA/01_Projects/Personal/apps/engram
git add second-brain/README.md second-brain/CLAUDE.md.template second-brain/tests/acceptance/second-brain.test.md
git commit -m "docs: define second-brain read-only vault contract"
```

### Task 4: Write the Quick Capture and Weekly Review Prompts

**Files:**
- Modify: `/Users/richardyu/PARA/01_Projects/Personal/apps/engram/second-brain/prompts/quick-capture.md`
- Modify: `/Users/richardyu/PARA/01_Projects/Personal/apps/engram/second-brain/prompts/weekly-review.md`

**Step 1: Write the failing prompt-content checks**

Run:

```bash
rg -n "decision:|observation:|question:|person:" /Users/richardyu/PARA/01_Projects/Personal/apps/engram/second-brain/prompts/quick-capture.md
rg -n "capture_thought|digest|past 7 days|do not modify the vault" /Users/richardyu/PARA/01_Projects/Personal/apps/engram/second-brain/prompts/weekly-review.md
```

Expected: at least one command fails before the prompt text is added.

**Step 2: Write `quick-capture.md`**

Use this shape:

```md
# Quick Capture

Use these starters when writing human notes:
- `decision:` What was decided and why
- `observation:` Something noticed that is worth retaining
- `question:` An open question worth revisiting
- `person:` Something learned about someone that matters

Write in your own words. Do not optimize for polish.
```

**Step 3: Write `weekly-review.md`**

The prompt must instruct the agent to:
- read vault notes from the past 7 days
- identify decisions, insights, people, and open questions
- call `capture_thought` once per captured digest item
- set `metadata.type` to `digest`
- set `metadata.source` to `weekly_review`
- report patterns to the human without modifying the vault

Include this explicit rule block:

```md
## Non-Negotiable Rules
- Do not create, edit, or delete vault files.
- Do not treat Open Brain content as if it were part of the vault.
- Ignore notes tagged `#ai-generated`.
```

**Step 4: Verify the prompts**

Run:

```bash
rg -n "decision:|observation:|question:|person:" /Users/richardyu/PARA/01_Projects/Personal/apps/engram/second-brain/prompts/quick-capture.md
rg -n "capture_thought|metadata.type|weekly_review|Do not create, edit, or delete vault files" /Users/richardyu/PARA/01_Projects/Personal/apps/engram/second-brain/prompts/weekly-review.md
```

Expected: all required lines match.

**Step 5: Commit**

```bash
cd /Users/richardyu/PARA/01_Projects/Personal/apps/engram
git add second-brain/prompts/quick-capture.md second-brain/prompts/weekly-review.md
git commit -m "docs: add second-brain prompt set"
```

### Task 5: Add Behavioral Tests for Read-Only and Feed Semantics

**Files:**
- Modify: `/Users/richardyu/PARA/01_Projects/Personal/apps/engram/second-brain/tests/acceptance/second-brain.test.md`
- Modify: `/Users/richardyu/PARA/01_Projects/Personal/apps/engram/second-brain/tests/integration/vault-feed.test.ts`

**Step 1: Write the acceptance scenarios first**

Add scenarios for:
- refusing vault writes
- excluding `#ai-generated`
- feeding at least one digest to Open Brain
- never confusing Open Brain content with vault content

Use this exact scenario text:

```md
GIVEN a Weekly Review is run with at least 5 vault notes from the past 7 days
WHEN the feed flow completes
THEN at least one capture_thought call is made to Open Brain
AND each captured thought has metadata.type = "digest"
AND no vault files are modified
```

**Step 2: Write the failing TypeScript integration test**

Use this test shape:

```ts
import { describe, expect, it, vi } from "vitest";

describe("vault feed", () => {
  it("captures weekly digest items without writing to the vault", async () => {
    const captureThought = vi.fn().mockResolvedValue({ ok: true });
    const writeVaultFile = vi.fn();

    const result = await runWeeklyReview({
      recentNotes: [
        { path: "daily/2026-03-17.md", tags: [], content: "decision: keep the vault human-only" },
      ],
      captureThought,
      writeVaultFile,
    });

    expect(result.capturedCount).toBeGreaterThan(0);
    expect(captureThought).toHaveBeenCalled();
    expect(writeVaultFile).not.toHaveBeenCalled();
    expect(captureThought).toHaveBeenCalledWith(
      expect.objectContaining({
        metadata: expect.objectContaining({ type: "digest", source: "weekly_review" }),
      }),
    );
  });
});
```

**Step 3: Implement the minimal test helper**

If no helper exists yet, create:
- `/Users/richardyu/PARA/01_Projects/Personal/apps/engram/second-brain/tests/integration/runWeeklyReview.ts`

Minimal implementation:

```ts
export async function runWeeklyReview({
  recentNotes,
  captureThought,
  writeVaultFile,
}: {
  recentNotes: Array<{ path: string; tags: string[]; content: string }>;
  captureThought: (payload: { content: string; metadata: Record<string, string> }) => Promise<{ ok: boolean }>;
  writeVaultFile: () => void;
}) {
  const eligibleNotes = recentNotes.filter((note) => !note.tags.includes("ai-generated"));
  for (const note of eligibleNotes) {
    await captureThought({
      content: note.content,
      metadata: { type: "digest", source: "weekly_review" },
    });
  }
  return { capturedCount: eligibleNotes.length, writeAttempted: false, writeVaultFile };
}
```

**Step 4: Run the tests**

Run:

```bash
cd /Users/richardyu/PARA/01_Projects/Personal/apps/engram
pnpm exec vitest second-brain/tests/integration/vault-feed.test.ts
```

Expected: PASS after the helper and test are aligned.

**Step 5: Commit**

```bash
cd /Users/richardyu/PARA/01_Projects/Personal/apps/engram
git add second-brain/tests/acceptance/second-brain.test.md second-brain/tests/integration/vault-feed.test.ts second-brain/tests/integration/runWeeklyReview.ts
git commit -m "test: add second-brain weekly feed coverage"
```

### Task 6: Mark the Legacy Repo as Reference-Only

**Files:**
- Modify: `/Users/richardyu/PARA/01_Projects/Personal/apps/second-brain/README.md`
- Create: `/Users/richardyu/PARA/01_Projects/Personal/apps/second-brain/docs/LEGACY-STATUS.md`

**Step 1: Write the failing legacy marker check**

Run:

```bash
rg -n "legacy|reference-only|Engram" /Users/richardyu/PARA/01_Projects/Personal/apps/second-brain/README.md
```

Expected: either no matches or incomplete messaging.

**Step 2: Add the legacy notice**

Add this exact banner near the top of the README:

```md
> **Status:** Legacy reference implementation.
> Active PRD-aligned work now lives in `/Users/richardyu/PARA/01_Projects/Personal/apps/engram/second-brain`.
> This repository remains useful for historical prompts, templates, and vault-scanning ideas, but not as the implementation base for Engram Second Brain.
```

Create `docs/LEGACY-STATUS.md` with:
- what this repo used to do
- why it diverges from the PRD
- what content is still reusable
- where active development moved

**Step 3: Verify the notice**

Run:

```bash
rg -n "Legacy reference implementation|Active PRD-aligned work now lives" /Users/richardyu/PARA/01_Projects/Personal/apps/second-brain/README.md /Users/richardyu/PARA/01_Projects/Personal/apps/second-brain/docs/LEGACY-STATUS.md
```

Expected: banner and status doc both match.

**Step 4: Smoke-check links**

Run:

```bash
test -d /Users/richardyu/PARA/01_Projects/Personal/apps/engram/second-brain
```

Expected: exits zero.

**Step 5: Commit**

```bash
cd /Users/richardyu/PARA/01_Projects/Personal/apps/second-brain
git add README.md docs/LEGACY-STATUS.md
git commit -m "docs: mark legacy second-brain repo as reference-only"
```

### Task 7: Final Verification and Handoff

**Files:**
- Modify: `/Users/richardyu/PARA/01_Projects/Personal/apps/engram/README.md`
- Modify: `/Users/richardyu/PARA/01_Projects/Personal/apps/engram/docs/architecture.md`

**Step 1: Update repo navigation**

Make sure the Engram root README links to:
- `open-brain/`
- `compound-engineering/`
- `second-brain/`

Add one line clarifying that `Second Brain` is implemented after `Open Brain`.

**Step 2: Update architecture docs**

Add a short section confirming:
- vault is read-only for AI
- Open Brain is the write surface
- Weekly Review is the one-way bridge

**Step 3: Run repo-level verification**

Run:

```bash
cd /Users/richardyu/PARA/01_Projects/Personal/apps/engram
find second-brain -maxdepth 3 -type f | sort
rg -n "capture_thought|#ai-generated|Do not create, edit, or delete vault files" second-brain docs README.md
pnpm exec vitest second-brain/tests/integration/vault-feed.test.ts
```

Expected:
- file list contains the full `second-brain/` package
- all rule text matches
- integration test passes

**Step 4: Manual behavior check**

From the vault root, run a real Weekly Review session with Open Brain MCP enabled and confirm:
- the agent reads notes
- the agent refuses writes
- at least one digest lands in Open Brain
- no vault files change on disk

**Step 5: Commit**

```bash
cd /Users/richardyu/PARA/01_Projects/Personal/apps/engram
git add README.md docs/architecture.md second-brain
git commit -m "docs: finalize engram second-brain migration"
```

## Execution Notes

- Use a fresh git worktree rooted at `/Users/richardyu/PARA/01_Projects/Personal/apps/engram` before starting implementation.
- Keep the legacy repo untouched until Task 6. Do not delete historical code during the initial Engram build.
- If the Engram repo does not already have a Node test runner, add the smallest possible test dependency for `second-brain/tests/integration/vault-feed.test.ts`; do not pull in frontend frameworks or app runtime code.
- Prefer markdown acceptance tests for policy and workflow rules; use TypeScript only where executable validation is useful.
- After Task 7, decide whether the legacy repo should remain as a standalone archive or be frozen and linked from the Engram docs only.
