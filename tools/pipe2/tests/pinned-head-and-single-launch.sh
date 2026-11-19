#!/bin/bash
# Check both Mac build pin guards and refuse a second launch through the desk launcher.
set -eu
cd "$(dirname "$0")/../../.."
export TMPDIR=/private/tmp/deepsignal/cloud-verification-dispatch/tmp
T=$(mktemp -d "$TMPDIR/pinned-launch.XXXXXX")
first=""
cleanup() {
  if [ -n "$first" ]; then
    kill "$first" 2>/dev/null || true
    wait "$first" 2>/dev/null || true
  fi
  rm -rf "$T"
}
trap cleanup EXIT
grep -q 'NOT LAUNCHED (pinned head' tools/pipe2/mac-build.sh
grep -q 'NOT PUSHED (pinned head' tools/pipe2/mac-build.sh
echo "PASS mac-build pins HEAD at launch and push"
export DS_LAUNCH_STATE_DIR="$T" DS_REVIEW_ROUTE=exempt:test DS_POLL=1
mkdir "$T/.ds-codex.lock"
printf '%s\n' "$$" > "$T/.ds-codex.lock/pid"
: > "$T/wip-units.txt"
printf 'x\n' > "$T/p.md"
L=tools/fast-review/ds-launch-when-ok.sh
bash "$L" "$T" "$T/p.md" "$T/r.log" 15 -- -m gpt-6.2-sol -s read-only - > "$T/first" 2>&1 &
first=$!
claim="$T/claims/$(printf '%s|%s' "$T" "$T/p.md" | shasum | cut -c1-16)"
for ((i=0; i<5; i++)); do
  [ -s "$claim/pid" ] && break
  sleep 1
done
[ "$(cat "$claim/pid")" = "$first" ] || { echo "FAIL first launch did not claim the job"; cat "$T/first"; exit 1; }
rc=0
out=$(bash "$L" "$T" "$T/p.md" "$T/r2.log" 1 -- -m gpt-6.2-sol -s read-only - 2>&1) || rc=$?
[ "$rc" = 3 ] && [[ "$out" == *"already claimed by pid $first"* ]] || { echo "FAIL second launch rc=$rc: $out"; exit 1; }
echo "PASS second launch of the same job refused: $out"
