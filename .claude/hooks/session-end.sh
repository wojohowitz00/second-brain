#!/usr/bin/env bash
# session-end.sh — Day Summary append + dashboard refresh at session close
# Runs via SessionEnd hook. Must be fast (well within 5s timeout).
# Always exits 0.

VAULT="/Users/richardyu/Library/Mobile Documents/iCloud~md~obsidian/Documents/Home"
TODAY=$(date +%Y-%m-%d)
NOW=$(date "+%Y-%m-%d %H:%M")

# --- Day Summary append ---
BRIEF="$VAULT/05_AI_Workspace/daily-briefs/${TODAY}-daily-brief.md"
if [[ -f "$BRIEF" ]] && ! grep -q "## Day Summary" "$BRIEF" 2>/dev/null; then
  cat >> "$BRIEF" << EOF

## Day Summary

*Session closed: ${NOW}*

EOF
fi

# --- Dashboard refresh ---
TASK_DASH="$VAULT/05_AI_Workspace/dashboards/tasks-by-status.md"
if [[ -f "$TASK_DASH" ]]; then
  sed -i '' "s/^refreshed_by: .*/refreshed_by: $TODAY/" "$TASK_DASH" 2>/dev/null
fi

PROJECT_DASH="$VAULT/05_AI_Workspace/dashboards/projects-health.md"
if [[ -f "$PROJECT_DASH" ]]; then
  sed -i '' "s/^refreshed_by: .*/refreshed_by: $TODAY/" "$PROJECT_DASH" 2>/dev/null
fi

exit 0
