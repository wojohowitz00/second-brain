# Veritas Kanban Integration

Optional integration with [Veritas Kanban](https://github.com/BradGroux/veritas-kanban) so that `todo:` and `kanban:` captures in Second Brain also create tasks on your Veritas board.

## Research summary

- **Project**: Veritas Kanban — local-first, markdown-backed Kanban with REST API and MCP.
- **API**: REST at `http://localhost:3001` (server). Versioned paths: `/api/v1/tasks` or `/api/tasks`.
- **Auth**: `X-API-Key: <key>` or `Authorization: Bearer <key>`. Keys from Veritas server `.env`: `VERITAS_ADMIN_KEY` or `VERITAS_API_KEYS` (name:key:role).
- **Create task**: `POST /api/tasks` with JSON body: `title`, `type` (e.g. `code`, `task`), `status` (`todo`, `in-progress`, `blocked`, `done`), optional `priority`, `project`.
- **Rate limiting**: Default 300 req/min per IP; localhost often exempt. Stricter limit on auth/settings.
- **MCP**: Veritas provides an MCP server; Second Brain uses the REST API for push-on-capture only.

## Second Brain integration

- **Mode**: Push on capture. When you post `todo:` or `kanban:` to Slack, Second Brain creates the note in your vault **and** (if enabled) creates a task in Veritas with the same title and status.
- **Config** (in `backend/_scripts/.env` or environment):
  - `VERITAS_BASE_URL` — Veritas API base (default: `http://localhost:3001`).
  - `VERITAS_API_KEY` — API key (admin or agent role). Generate in Veritas or use `VERITAS_ADMIN_KEY` from its `.env`.
  - `VERITAS_PUSH_ENABLED` — Set to `true` or `1` to enable push; unset or `false` to disable.
- **Status mapping**: Second Brain `backlog` → Veritas `todo`; `in_progress` → `in-progress`; `blocked` → `blocked`; `done` → `done`.
- **Source of truth**: Vault note is the content source; Veritas is the board for status/sprint/time. Optional future: sync status from Veritas back to vault.

## Usage

1. Run Veritas Kanban (e.g. `pnpm dev` in its repo; API on port 3001).
2. Create an API key in Veritas (Settings → Security, or use `VERITAS_ADMIN_KEY` from server `.env`).
3. Set `VERITAS_BASE_URL`, `VERITAS_API_KEY`, and `VERITAS_PUSH_ENABLED=true` for Second Brain.
4. Post `todo: My task` or `kanban: My task` to your Slack inbox; the note is filed and a task is created on the Veritas board (if push is enabled).

## Limits

- Push is best-effort. If Veritas is down or returns an error, Second Brain still files the note; the failure is logged.
- No sync of status from Veritas to vault in this release.
- No MCP usage from Second Brain; integration is REST-only.
