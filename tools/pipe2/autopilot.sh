#!/bin/bash
# Autopilot: every 3 min, find tracked cloud tasks that finished and are not yet accepted, and run accept.sh on each,
# one at a time (accept.sh waits for the RAM gate). Results append to accept-results.log. Never commits or pushes.
# Skips: tasks with 0 files (logged as EMPTY), the ignored old #111 task, and the diag task (logged for the lead).
set -u
# D-PIPE2 rule 8: single instance; a second autopilot exits at once.
for o in $(pgrep -f "/private/tmp/deepsignal/autopilot.sh"); do [ "$o" != $$ ] && [ "$o" != "$PPID" ] && { echo "autopilot: already running as $o"; exit 0; }; done
D=/private/tmp/deepsignal; DONE=$D/accept-done.txt; LOG=$D/accept-results.log; touch "$DONE"
P=$D/desk-main/briefs/cloud
# Per-id status (the cloud list shows only 20 tasks, so older ones fell off it before).
scan_tasks() {
  local f kind id name branch n st word files
  for f in $D/console-cloud/submitted.tsv $D/p2-cloud/submitted.tsv; do
    kind=p2; [[ "$f" == *console-cloud* ]] && kind=console
    awk -F'\t' -v k=$kind '$4 ~ /^task_e_/ {print $4, $1, $2, $3, k}' "$f"
  done | while read -r id name branch n kind; do
    grep -qx "$id" "$DONE" && continue
    st=$(cd $D/cloud-logs && CODEX_HOME=$HOME/.codex-deepsignal perl -e 'alarm 30; exec @ARGV' codex cloud status "$id" 2>/dev/null | head -3 | tr '\n' ' ')
    [ -z "$st" ] && continue
    if echo "$st" | grep -qE '^\[(PENDING|RUNNING|IN_PROGRESS|QUEUED)\]'; then continue; fi
    word=$(echo "$st" | sed -nE 's/^\[([A-Z_]+)\].*/\1/p' | tr 'A-Z' 'a-z'); files=$(echo "$st" | grep -oE '[0-9]+ files?' | grep -oE '[0-9]+' | head -1)
    echo "$id $name $branch $n ${word:-unknown} ${files:-0} $kind"
  done
  rm -f $D/cloud-logs/error.log
}
S=$(date +%s)
while [ $(( $(date +%s)-S )) -lt 21600 ]; do
  git -C $D/desk-main pull -q --ff-only 2>/dev/null
  list=$(scan_tasks)
  while read -r id name branch n status files kind; do
    [ -z "$id" ] && continue
    echo "$id" >> "$DONE"
    base=$(echo "$name" | sed -E 's/-(r|v)[0-9]+$//')
    case "$name" in
      diag) echo "$(date -u +%TZ) DIAG $id status=$status files=$files (lead reads it)" >> "$LOG"; continue;;
      met-reports) echo "$(date -u +%TZ) SKIP $id old #111 task (superseded)" >> "$LOG"; continue;;
    esac
    if [ "$files" = 0 ]; then echo "$(date -u +%TZ) EMPTY $name $id status=$status" >> "$LOG"; continue; fi
    if [ "$kind" = console ]; then prompt=$P/console-$base.md; [ "$base" = p2-cast-view ] && prompt=$P/p2-cast-view.md; [ "$base" = charts ] && prompt=$P/console-charts.md
    else prompt=$P/p2-$base.md; fi
    [ -f "$prompt" ] || prompt=$D/desk-main/briefs/mac/$base-fix1.md
    [ -f "$prompt" ] || prompt=$D/desk-main/briefs/deepsignal-$base.md
    [ -f "$prompt" ] || prompt=$D/$base/prompt.md
    [ -f "$prompt" ] || { echo "$(date -u +%TZ) NOPROMPT $name $id ($prompt)" >> "$LOG"; continue; }
    echo "$(date -u +%TZ) ACCEPT $name $id branch=$branch attempts=$n files=$files" >> "$LOG"
    AUTOPUSH=1 "$D/accept.sh" "$base" "$id" "$n" "$branch" "$prompt" >> "$LOG" 2>&1
  done <<< "$list"
  sleep 180
done
echo "$(date -u +%TZ) autopilot stopped after 6h" >> "$LOG"
