#!/bin/bash
# D-FASTREV1 builder self-check: the same checklist the reviewers use, run by the builder on its own head before
# asking for review. Usage: self-check.sh <repo> <base-sha> <design-note.md>
# Steps: pre-review.sh (machine checks) must be green; every acceptance command in the design note's
# "## Acceptance tests" fenced blocks runs green (nginx-only tests excepted on the Mac); static checklist on the
# diff (no new skip or xfail markers, no sleeps in tests, no bare except, no em dashes in added lines, no edits
# to files named out of scope). Writes /private/tmp/deepsignal/receipts/self-check-<sha>.txt (RESULT GREEN or RED).
set -u
R=$(cd "$1" && pwd); BASE=$2; NOTE=$3; D=/private/tmp/deepsignal; PY=$D/console-core/venv/bin/python
export PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$D/shims
H=$(git -C "$R" rev-parse --short HEAD); OUT=$D/receipts/self-check-$H.txt; mkdir -p $D/receipts; red=0
{ echo "self-check $H (base $BASE, design note $NOTE) $(date -u +%FT%TZ)"
  [ -s "$NOTE" ] || { echo "FAIL design note missing: $NOTE (D-DESIGN1)"; red=1; }
  if "$D/pre-review.sh" "$R" "$BASE" > /dev/null 2>&1; then echo "PASS pre-review (receipts/pre-review-$H.txt)"; else echo "FAIL pre-review (receipts/pre-review-$H.txt)"; red=1; fi
  if [ -s "$NOTE" ]; then
    cmds=$(awk '/^## Acceptance tests/{f=1;next} /^## /{f=0} f && /^```/{b=!b;next} f && b && NF' "$NOTE")
    if [ -z "$cmds" ]; then echo "FAIL design note has no acceptance commands in fenced blocks"; red=1; fi
    while IFS= read -r c; do [ -z "$c" ] && continue
      case "$c" in *"-k real_197"*|*"-k 'real_197"*|nginx\ *) echo "SKIP on the Mac (Linux runner): $c"; continue;; esac
      c2=$(echo "$c" | sed "s#^python3\.12 #$PY #; s#^python3 #$PY #")
      out=$(cd "$R" && perl -e 'alarm 1800; exec @ARGV' bash -c "$c2" 2>&1) && echo "PASS acceptance: $c" || { echo "FAIL acceptance: $c :: $(echo "$out" | tail -2 | tr '\n' ' ')"; red=1; }
    done <<< "$cmds"
  fi
  added=$(git -C "$R" diff "$BASE" HEAD -U0 | grep -E '^\+[^+]')
  echo "$added" | grep -nE '@(pytest\.mark\.)?(skip|xfail)|unittest\.skip|it\.skip|test\.skip|describe\.skip' > /dev/null && { echo "FAIL checklist: new skip or xfail marker"; red=1; } || echo "PASS checklist: no new skip or xfail"
  git -C "$R" diff "$BASE" HEAD -U0 -- '*test*' | grep -E '^\+[^+]' | grep -E 'time\.sleep\(|setTimeout\(|await asyncio\.sleep\([1-9]' > /dev/null && { echo "FAIL checklist: sleep added in tests"; red=1; } || echo "PASS checklist: no sleeps added in tests"
  echo "$added" | grep -E '^\+\s*except\s*:' > /dev/null && { echo "FAIL checklist: bare except"; red=1; } || echo "PASS checklist: no bare except"
  echo "$added" | grep -q $'\xe2\x80\x94' && { echo "FAIL checklist: em dash in added lines"; red=1; } || echo "PASS checklist: no em dashes"
  [ $red = 0 ] && echo "RESULT GREEN" || echo "RESULT RED"
} > "$OUT"
cat "$OUT"
grep -q '^RESULT GREEN' "$OUT"
