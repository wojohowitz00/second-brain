#!/usr/bin/env bash
# session-end.sh — Refresh dashboard timestamp at session close
# Runs via SessionEnd hook. Must be fast (well within 5s timeout).
# Always exits 0.

VAULT="/Users/richardyu/Library/Mobile Documents/iCloud~md~obsidian/Documents/Home"
DASHBOARD="$VAULT/05_AI_Workspace/dashboards/tasks-by-status.md"
TODAY=$(date +%Y-%m-%d)

if [[ -f "$DASHBOARD" ]]; then
  sed -i '' "s/^refreshed_by: .*/refreshed_by: $TODAY/" "$DASHBOARD" 2>/dev/null
fi

exit 0
