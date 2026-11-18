#!/bin/bash
# Launch one ds-codex job only when the DeepSignal lock is free AND memory is normal
# (kern.memorystatus_vm_pressure_level == 1 and at least MIN_SWAP_FREE_MB swap free). Retries on lock races.
# Usage: ds-launch-when-ok.sh <workdir> <prompt-file> <run-log> <max-wait-seconds> -- <ds-codex args...>
set -u
wd="$1"; prompt="$2"; runlog="$3"; maxwait="$4"; shift 5
L=/private/tmp/deepsignal/.ds-codex.lock; MIN_SWAP_FREE_MB=${MIN_SWAP_FREE_MB:-2048}; S=$(date +%s); last=""
mem_ok() {
  local lvl free; lvl=$(sysctl -n kern.memorystatus_vm_pressure_level)
  free=$(sysctl -n vm.swapusage | sed -E 's/.*free = ([0-9.]+)M.*/\1/'); free=${free%.*}
  last="pressure_level=$lvl swap_free_MB=$free"
  [ "$lvl" = 1 ] && [ "$free" -ge "$MIN_SWAP_FREE_MB" ]
}
while :; do
  while { [ -d "$L" ] && kill -0 "$(cat "$L/pid" 2>/dev/null)" 2>/dev/null; } || ! mem_ok; do
    [ $(( $(date +%s)-S )) -gt "$maxwait" ] && { echo "NOT launched after ${maxwait}s: lock=$([ -d "$L" ] && cat "$L/pid" || echo free) $last"; exit 1; }
    sleep 30
  done
  echo "launching after $(( $(date +%s)-S ))s ($last) at $(date -u +%FT%TZ)"
  cd "$wd" || exit 2
  T0=$(date +%s)
  perl -e 'alarm 2700; exec @ARGV' ~/bin/ds-codex "$@" < "$prompt" > "$runlog" 2>&1 &
  job=$!; peak=0
  while kill -0 "$job" 2>/dev/null; do
    # peak RSS of the ds-codex wrapper's process tree (codex child included)
    r=$(ps -axo pid=,ppid=,rss= | awk -v root="$job" '{p[$1]=$2; r[$1]=$3} END {s=0; for (i in p) {x=i; while (x!="" && x!=root && x in p && x!=1) x=p[x]; if (x==root) s+=r[i]} print int(s/1024)}')
    [ "${r:-0}" -gt "$peak" ] && peak=$r; sleep 10
  done
  wait "$job"; rc=$?
  echo "rc=$rc wall=$(( $(date +%s)-T0 ))s peak_rss_MB=$peak end=$(date -u +%FT%TZ)"
  [ "$rc" != 10 ] && exit 0
  sleep 5
done
