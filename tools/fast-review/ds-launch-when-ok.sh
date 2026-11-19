#!/bin/bash
# Launch one ds-codex job when the DeepSignal lock is free. Memory is gated by ds-codex itself
# (--wait-ram: free RAM >= 4 GB and swap used <= 3.8 GB, exit 11 at the deadline). Retries on lock races.
# Usage: ds-launch-when-ok.sh <workdir> <prompt-file> <run-log> <max-wait-seconds> -- <ds-codex args...>
set -u
wd="$1"; prompt="$2"; runlog="$3"; maxwait="$4"; shift 5
# D-PIPE2 preflight: a build job (not read-only) must declare its needs in the brief's front matter, and they must be
# met, before any WIP slot, design check or claim is taken (exit 8). Reviews and design-note jobs are exempt.
case " $* " in *" -s read-only "*|*" --sandbox read-only "*) ;; *)
  pf=$(perl -e 'alarm 130; exec @ARGV' /private/tmp/deepsignal/preflight.sh "$prompt" "$wd" 2>&1) || { echo "NOT launched: $pf"; exit 8; };;
esac
# D-WIP3: WIP cap of 3 path units; a non-path job is refused while all slots are taken (DS_WIP_EXEMPT=reason
# lets an Eugene-requested one-off through, logged). Review routing: the Mac runs only math reviews; a read-only
# job needs DS_REVIEW_ROUTE=math or DS_REVIEW_ROUTE=exempt:<reason>, otherwise it goes to cloud-review.sh.
W3=/private/tmp/deepsignal/wip-units.txt; WIP_CAP=3
onpath=0; nslots=0; unit=""; while IFS="|" read -r un ure; do case "$un" in ""|\#*) continue;; esac; nslots=$((nslots+1)); echo "$wd" | grep -qE "$ure" && { onpath=1; unit=$un; }; done < "$W3"
if [ "$onpath" = 0 ] && [ "$nslots" -ge "$WIP_CAP" ]; then
  if [ -n "${DS_WIP_EXEMPT:-}" ]; then echo "WIP cap exemption for $wd: $DS_WIP_EXEMPT"; else echo "NOT launched: D-WIP3 WIP cap ($nslots of $WIP_CAP path units active; $wd is not on the Nov 25 path)"; exit 4; fi
fi
case " $* " in *" -s read-only "*|*" --sandbox read-only "*)
  case "${DS_REVIEW_ROUTE:-}" in math|exempt:*) echo "review on the Mac: $DS_REVIEW_ROUTE";; *) echo "NOT launched: non-math review; route it to /private/tmp/deepsignal/cloud-review.sh (D-WIP3)"; exit 5;; esac;;
esac
# D-DESIGN1: a build job (anything not read-only) needs the unit's design note on the desk; reviews and
# design-note jobs (read-only) are exempt. Exit 6 with the missing path.
case " $* " in *" -s read-only "*|*" --sandbox read-only "*) ;; *)
  if [ -n "$unit" ] && [ ! -s "/private/tmp/deepsignal/desk-main/docs/designs/$unit.md" ]; then
    echo "NOT launched: D-DESIGN1 design note missing for unit $unit (/private/tmp/deepsignal/desk-main/docs/designs/$unit.md)"; exit 6
  fi;;
esac
# Claim file (D-PIPE1 rule 5): one claim per job (workdir plus prompt), taken atomically with mkdir and released on
# exit, so two loops never launch the same job. A claim whose owner pid is gone is stale and is taken over.
CL=/private/tmp/deepsignal/claims/$(printf "%s|%s" "$wd" "$prompt" | shasum | cut -c1-16); mkdir -p /private/tmp/deepsignal/claims
if ! mkdir "$CL" 2>/dev/null; then
  o=$(cat "$CL/pid" 2>/dev/null); if [ -n "$o" ] && kill -0 "$o" 2>/dev/null; then echo "NOT launched: job already claimed by pid $o ($CL)"; exit 3; fi
  rm -rf "$CL"; mkdir "$CL" || { echo "NOT launched: claim race on $CL"; exit 3; }
fi
echo $$ > "$CL/pid"; printf "%s\n%s\n" "$wd" "$prompt" > "$CL/job"; trap 'rm -rf "$CL"' EXIT
L=/private/tmp/deepsignal/.ds-codex.lock; MIN_SWAP_FREE_MB=${MIN_SWAP_FREE_MB:-2048}; S=$(date +%s); last=""
# Memory is gated by ds-codex; the machine-wide heavy-job cap (D-PIPE1a) is checked here too, read-only.
mem_ok() { local n; n=$(/private/tmp/deepsignal/heavy-jobs.sh 2>/dev/null || echo 0); last="memory gated by ds-codex --wait-ram; heavy jobs $n of cap ${DS_HEAVY_CAP:-$(( ${DS_MACHINE_CAP:-3} - ${DS_KALON_RESERVED:-1} ))}"; [ "$n" -lt "${DS_HEAVY_CAP:-$(( ${DS_MACHINE_CAP:-3} - ${DS_KALON_RESERVED:-1} ))}" ]; }
while :; do
  while { [ -d "$L" ] && kill -0 "$(cat "$L/pid" 2>/dev/null)" 2>/dev/null; } || ! mem_ok; do
    [ $(( $(date +%s)-S )) -gt "$maxwait" ] && { echo "NOT launched after ${maxwait}s: lock=$([ -d "$L" ] && cat "$L/pid" || echo free) $last"; exit 1; }
    sleep ${DS_POLL:-30}
  done
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
