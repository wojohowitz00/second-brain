## Contributing Knowledge Entries (`docs/knowledge/`)

Use this flow whenever you fix a non-trivial bug, resolve a flaky test, or make a meaningful design decision:

1. **Create a new file** in `docs/knowledge/` with a slugged filename, for example:
   - `2026-03-15-slack-rate-limit.md`
2. **Copy the schema** from `docs/knowledge/SCHEMA.md` and fill in:
   - `type`, `slug`, `title`, `area`, `status`, `tags`, `created`, `updated`
   - `test_refs` should point at one or more pytest tests that cover the case
3. **Write 3–8 paragraphs** using the standard sections:
   - Context → Problem → Attempts → Resolution → Regressions
4. **Update `docs/quality.md`** if this materially changes health for an area.
5. **Link from planning docs**:
   - When starting follow-up work, add a \"Related knowledge\" bullet in the relevant `.planning/*` file with the knowledge slug.

Keep entries short and surgical — they are **maps** for future agents, not postmortem novels.

