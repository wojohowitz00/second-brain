#!/usr/bin/env bash
# session-start.sh — Surface stale/overdue tasks at session open
# Injected into Claude context via SessionStart hook.
# Outputs plain-text task status summary to stdout. Always exits 0.

TASKS_DIR="/Users/richardyu/PARA/01_Projects/Personal/apps/second-brain/tasks"
TODAY=$(date +%Y-%m-%d)
TODAY_EPOCH=$(date +%s)

# macOS date arithmetic helper: returns epoch for a YYYY-MM-DD string
date_to_epoch() {
  local d="$1"
  # macOS stat format
  if date -j -f "%Y-%m-%d" "$d" +%s 2>/dev/null; then
    return
  fi
  # GNU date fallback
  date -d "$d" +%s 2>/dev/null || echo "0"
}

SEVEN_DAYS_EPOCH=$(( TODAY_EPOCH + 7 * 86400 ))
SEVEN_DAYS_AGO_EPOCH=$(( TODAY_EPOCH - 7 * 86400 ))

overdue=()
upcoming=()
stale=()

# Process each task file (skip README.md)
for f in "$TASKS_DIR"/*.md; do
  [[ -f "$f" ]] || continue
  fname=$(basename "$f")
  [[ "$fname" == "README.md" ]] && continue

  # Extract frontmatter block (between first two --- lines)
  fm=$(awk '/^---/{c++;next} c==1{print} c==2{exit}' "$f" 2>/dev/null)
  [[ -z "$fm" ]] && continue

  status=$(echo "$fm" | grep -E '^status:' | head -1 | sed 's/^status:[[:space:]]*//' | tr -d '"' | tr -d "'")
  due_date=$(echo "$fm" | grep -E '^due_date:' | head -1 | sed 's/^due_date:[[:space:]]*//' | tr -d '"' | tr -d "'")
  title=$(echo "$fm" | grep -E '^title:' | head -1 | sed 's/^title:[[:space:]]*//' | tr -d '"' | tr -d "'")

  # Fallback title: filename without extension
  [[ -z "$title" ]] && title="${fname%.md}"

  # Skip done tasks
  [[ "$status" == "done" ]] && continue

  if [[ -n "$due_date" && "$due_date" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}$ ]]; then
    due_epoch=$(date_to_epoch "$due_date")
    if [[ "$due_epoch" -lt "$TODAY_EPOCH" ]]; then
      overdue+=("  - $title (due $due_date, status: ${status:-unknown})")
    elif [[ "$due_epoch" -le "$SEVEN_DAYS_EPOCH" ]]; then
      upcoming+=("  - $title (due $due_date)")
    fi
  else
    # No due_date — check if stale (active/waiting/blocked + 7+ days old)
    if [[ "$status" == "active" || "$status" == "waiting" || "$status" == "blocked" ]]; then
      # Get last-modified date via macOS stat
      mod_date=$(stat -f "%Sm" -t "%Y-%m-%d" "$f" 2>/dev/null)
      if [[ -n "$mod_date" ]]; then
        mod_epoch=$(date_to_epoch "$mod_date")
        if [[ "$mod_epoch" -le "$SEVEN_DAYS_AGO_EPOCH" ]]; then
          stale+=("  - $title (last modified $mod_date, status: $status)")
        fi
      fi
    fi
  fi
done

# Nothing to report — silent exit
total=$(( ${#overdue[@]} + ${#upcoming[@]} + ${#stale[@]} ))
[[ "$total" -eq 0 ]] && exit 0

# Cap each bucket at 5 items
cap5() {
  local -n arr=$1
  if [[ ${#arr[@]} -gt 5 ]]; then
    arr=("${arr[@]:0:5}" "  - ... and $(( ${#arr[@]} - 5 )) more")
  fi
}
cap5 overdue
cap5 upcoming
cap5 stale

echo "=== TASK STATUS ($TODAY) ==="

if [[ ${#overdue[@]} -gt 0 ]]; then
  echo "OVERDUE:"
  printf '%s\n' "${overdue[@]}"
fi

if [[ ${#upcoming[@]} -gt 0 ]]; then
  echo "DUE WITHIN 7 DAYS:"
  printf '%s\n' "${upcoming[@]}"
fi

if [[ ${#stale[@]} -gt 0 ]]; then
  echo "STALE (7+ days no activity):"
  printf '%s\n' "${stale[@]}"
fi

echo "==================================="

exit 0
