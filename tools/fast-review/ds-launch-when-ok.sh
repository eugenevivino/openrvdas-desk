#!/bin/bash
# Launch one ds-codex job when the DeepSignal lock is free. Memory is gated by ds-codex itself
# (--wait-ram: free RAM >= 4 GB and swap used <= 3.8 GB, exit 11 at the deadline). Retries on lock races.
# Usage: ds-launch-when-ok.sh <workdir> <prompt-file> <run-log> <max-wait-seconds> -- <ds-codex args...>
# Hosted pilot checks: ds-launch-when-ok.sh <workdir> <brief> <receipt.json> <max-wait-seconds>
#                       --cloud-verify <trusted-desk-sha> <product-sha>
set -u
usage() { echo "NOT launched: expected -- <ds-codex args...> or --cloud-verify <desk-sha> <product-sha>" >&2; exit 2; }
[ "$#" -ge 5 ] || usage
wd="$1"; prompt="$2"; runlog="$3"; maxwait="$4"; route="$5"; shift 5
cloud=0
case "$route" in
  --) ;;
  --cloud-verify) [ "$#" = 2 ] || usage; cloud=1 ;;
  *) usage ;;
esac
state=${DS_LAUNCH_STATE_DIR:-/private/tmp/deepsignal}
desk=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
preflight="$state/preflight.sh"
designs="$state/desk-main/docs/designs"
if [ "$cloud" = 1 ] || [ -n "${DS_LAUNCH_STATE_DIR:-}" ]; then
  preflight="$desk/tools/pipe2/preflight.sh"
  designs="$desk/docs/designs"
fi
readonly_job=0
if [ "$cloud" = 0 ]; then
  case " $* " in *" -s read-only "*|*" --sandbox read-only "*) readonly_job=1 ;; esac
fi
# D-PIPE2 preflight: a build job (not read-only) must declare its needs in the brief's front matter, and they must be
# met, before any WIP slot, design check or claim is taken (exit 8). Reviews and design-note jobs are exempt.
if [ "$readonly_job" = 0 ]; then
  pf=$(perl -e 'alarm 130; exec @ARGV' "$preflight" "$prompt" "$wd" 2>&1) || { echo "NOT launched: $pf"; exit 8; }
fi
# D-WIP3: WIP cap of 3 path units; a non-path job is refused while all slots are taken (DS_WIP_EXEMPT=reason
# lets an Eugene-requested one-off through, logged). Review routing: the Mac runs only math reviews; a read-only
# job needs DS_REVIEW_ROUTE=math or DS_REVIEW_ROUTE=exempt:<reason>, otherwise it goes to cloud-review.sh.
W3="$state/wip-units.txt"; WIP_CAP=3
if [ "$cloud" = 1 ] && [ ! -r "$W3" ]; then echo "NOT launched: D-WIP3 WIP file unavailable ($W3)"; exit 4; fi
onpath=0; nslots=0; unit=""
while IFS="|" read -r un ure || [ -n "$un" ]; do
  case "$un" in ""|\#*) continue ;; esac
  nslots=$((nslots+1))
  if [ "$cloud" = 1 ] && [ -z "$ure" ]; then
    echo "NOT launched: D-WIP3 WIP entry has no path pattern ($un)"; exit 4
  fi
  if printf '%s\n' "$wd" | grep -qE -- "$ure"; then
    unit=$un
    if [ "$cloud" = 0 ] || [ "$un" = console ]; then onpath=1; fi
  fi
done < "$W3"
if [ "$onpath" = 0 ] && [ "$nslots" -ge "$WIP_CAP" ]; then
  if [ -n "${DS_WIP_EXEMPT:-}" ]; then echo "WIP cap exemption for $wd: $DS_WIP_EXEMPT"; else echo "NOT launched: D-WIP3 WIP cap ($nslots of $WIP_CAP path units active; $wd is not on the Nov 25 path)"; exit 4; fi
fi
if [ "$readonly_job" = 1 ]; then
  case "${DS_REVIEW_ROUTE:-}" in math|exempt:*) echo "review on the Mac: $DS_REVIEW_ROUTE";; *) echo "NOT launched: non-math review; route it to /private/tmp/deepsignal/cloud-review.sh (D-WIP3)"; exit 5;; esac
fi
# D-DESIGN1: a build job (anything not read-only) needs the unit's design note on the desk; reviews and
# design-note jobs (read-only) are exempt. Exit 6 with the missing path.
if [ "$readonly_job" = 0 ] && [ -n "$unit" ] && [ ! -s "$designs/$unit.md" ]; then
  echo "NOT launched: D-DESIGN1 design note missing for unit $unit ($designs/$unit.md)"; exit 6
fi
if [ "$cloud" = 1 ]; then
  for required in console cloud-verification-dispatch; do
    if [ ! -s "$designs/$required.md" ]; then
      echo "NOT launched: D-DESIGN1 design note missing ($designs/$required.md)"; exit 6
    fi
  done
fi
# Claim file (D-PIPE1 rule 5): one claim per job (workdir plus prompt), taken atomically with mkdir and released on
# exit, so two loops never launch the same job. A claim whose owner pid is gone is stale and is taken over.
CL="$state/claims/$(printf "%s|%s" "$wd" "$prompt" | shasum | cut -c1-16)"
mkdir -p "$state/claims" || exit 3
if ! mkdir "$CL" 2>/dev/null; then
  if [ ! -d "$CL" ] || [ -L "$CL" ]; then
    echo "NOT launched: invalid claim directory ($CL)"; exit 3
  fi
  o=$(cat "$CL/pid" 2>/dev/null)
  case "$o" in ''|*[!0-9]*|0) echo "NOT launched: job already claimed ($CL)"; exit 3 ;; esac
  if kill -0 "$o" 2>/dev/null; then echo "NOT launched: job already claimed by pid $o ($CL)"; exit 3; fi
  mkdir "$CL/reap" 2>/dev/null || { echo "NOT launched: claim race on $CL"; exit 3; }
  if [ "$(cat "$CL/pid" 2>/dev/null)" != "$o" ]; then
    rmdir "$CL/reap" 2>/dev/null
    echo "NOT launched: claim race on $CL"; exit 3
  fi
  rm -rf "$CL"
  mkdir "$CL" || { echo "NOT launched: claim race on $CL"; exit 3; }
fi
trap 'rm -rf "$CL"' EXIT
trap 'exit 130' INT
trap 'exit 143' TERM
echo $$ > "$CL/pid" && printf "%s\n%s\n" "$wd" "$prompt" > "$CL/job" || exit 3
if [ "$cloud" = 1 ]; then
  python3.12 -IB "$desk/tools/pipe2/cloud-verification-dispatch.py" "$desk" "$wd" "$runlog" "$maxwait" "$@"
  exit $?
fi
L="$state/.ds-codex.lock"; MIN_SWAP_FREE_MB=${MIN_SWAP_FREE_MB:-2048}; S=$(date +%s); last=""
# Memory is gated by ds-codex; the machine-wide heavy-job cap (D-PIPE1a) is checked here too, read-only.
mem_ok() { local n; n=$("$state/heavy-jobs.sh" 2>/dev/null || echo 0); last="memory gated by ds-codex --wait-ram; heavy jobs $n of cap ${DS_HEAVY_CAP:-$(( ${DS_MACHINE_CAP:-3} - ${DS_KALON_RESERVED:-1} ))}"; [ "$n" -lt "${DS_HEAVY_CAP:-$(( ${DS_MACHINE_CAP:-3} - ${DS_KALON_RESERVED:-1} ))}" ]; }
while :; do
  while { [ -d "$L" ] && kill -0 "$(cat "$L/pid" 2>/dev/null)" 2>/dev/null; } || ! mem_ok; do
    [ $(( $(date +%s)-S )) -gt "$maxwait" ] && { echo "NOT launched after ${maxwait}s: lock=$([ -d "$L" ] && cat "$L/pid" || echo free) $last"; exit 1; }
    sleep ${DS_POLL:-30}
  done
  if [ -n "${DS_LAUNCH_STATE_DIR:-}" ]; then
    echo "NOT launched: isolated launcher state cannot start a Mac job"
    exit 2
  fi
  echo "launching after $(( $(date +%s)-S ))s ($last) at $(date -u +%FT%TZ)"
  cd "$wd" || exit 2
  T0=$(date +%s)
  perl -e 'alarm 9900; exec @ARGV' ~/bin/ds-codex --wait-ram=7200 "$@" < "$prompt" > "$runlog" 2>&1 &
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
