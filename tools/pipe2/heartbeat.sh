#!/bin/bash
# Detached DeepSignal heartbeat (survives the Claude session). Every 15 min appends one status line to heartbeat.log
# and restarts autopilot.sh if it has died. A session cron reads this log and posts the check-in as a turn.
D=/private/tmp/deepsignal; H=$D/heartbeat.log
# D-PIPE2 rule 8: single instance. A second heartbeat exits if the recorded one is alive.
o=$(cat $D/.heartbeat.pid 2>/dev/null); if [ -n "$o" ] && [ "$o" != $$ ] && kill -0 "$o" 2>/dev/null && ps -o command= -p "$o" | grep -q heartbeat.sh; then echo "heartbeat: already running as $o"; exit 0; fi
echo $$ > $D/.heartbeat.pid
while true; do
  if ! pgrep -f "$D/autopilot.sh" >/dev/null; then nohup $D/autopilot.sh >> $D/autopilot.out 2>&1 < /dev/null & echo "$(date -u +%TZ) heartbeat: autopilot restarted pid $!" >> $H; fi
  job=$(cat $D/.ds-codex.lock/pid 2>/dev/null); cur=$( [ -n "$job" ] && kill -0 $job 2>/dev/null && ps -o command= -p $job | grep -oE 'gpt-6[^ ]*' | head -1 )
  orph=$(ps -axo ppid=,etime=,command= | awk '$1==1 && /harness.fixture|logger_runner.py:|logger_manager.py --database memory/' | wc -l | tr -d ' '); [ "$orph" != 0 ] && echo "$(date -u +%TZ) heartbeat: $orph orphaned fixture processes (ppid 1); lead checks (D-PIPE1 rule 9)" >> $H
  echo "$(date -u +%TZ) alive; mac job: ${cur:-none}; last: $(tail -1 $D/mac-builds.log | cut -c1-90)" >> $H
  sleep 900
done
