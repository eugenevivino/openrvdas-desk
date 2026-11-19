#!/bin/bash
# Refuse both missing and unmet needs before creating a claim.
set -eu
cd "$(dirname "$0")/../../.."
export TMPDIR=/private/tmp/deepsignal/cloud-verification-dispatch/tmp
T=$(mktemp -d "$TMPDIR/preflight-launch.XXXXXX")
trap 'rm -rf "$T"' EXIT
export DS_LAUNCH_STATE_DIR="$T" DS_POLL=1
L=tools/fast-review/ds-launch-when-ok.sh
: > "$T/wip-units.txt"
printf '# brief without needs\n' > "$T/p.md"
printf -- '---\nneeds:\n  tools: nosuchtool-zz\n---\n' > "$T/q.md"
for kind in missing unmet; do
  brief="$T/p.md"
  expected="no needs block"
  if [ "$kind" = unmet ]; then brief="$T/q.md"; expected="tool nosuchtool-zz missing"; fi
  rc=0
  out=$(bash "$L" "$T" "$brief" "$T/r.log" 1 -- -m gpt-6.2-sol - 2>&1) || rc=$?
  [ "$rc" = 8 ] && [ ! -e "$T/claims" ] && [[ "$out" == *"$expected"* ]] ||
    { echo "FAIL $kind needs rc=$rc: $out"; exit 1; }
  echo "PASS $kind needs refused with exit 8 before any claim: $out"
done
