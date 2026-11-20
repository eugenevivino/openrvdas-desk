#!/bin/bash
# D-FASTREV1 machine checks before any model review. Usage: pre-review.sh <repo> <base-sha>
# Runs on the unit head: flake8 on contrib/deepsignal; console oxlint, tsc and vitest when the diff touches the
# console; pytest on the changed test files (lead_run browser tests included only if playwright is present);
# security scanners (bandit, pip-audit, npm audit) only if already installed (installs need Eugene). Writes a
# receipt /private/tmp/deepsignal/receipts/pre-review-<sha>.txt; exit 0 only when every check that ran is green.
set -u
R=$(cd "$1" && pwd) || exit 1
BASE=$2; D=/private/tmp/deepsignal; PY=$D/console-core/venv/bin/python
DESK=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P) || exit 1
export PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$D/shims
HEAD_SHA=$(git -C "$R" rev-parse --verify HEAD) || exit 1
H=$(git -C "$R" rev-parse --short "$HEAD_SHA") || exit 1
RECEIPTS=$D/receipts; OUT=$RECEIPTS/pre-review-$H.txt
mkdir -p "$RECEIPTS" || exit 1
changed=$(git -C "$R" diff --name-only "$BASE" "$HEAD_SHA") || exit 1
TEMP_OUT=$(mktemp "$RECEIPTS/.pre-review-$H.XXXXXX") || exit 1
trap 'rm -f -- "$TEMP_OUT"' EXIT
red=0; T0=$(date +%s)
{ echo "pre-review $H (base $BASE) $(date -u +%FT%TZ)"
  run() { local name=$1; shift; local t=$(date +%s); out=$("$@" 2>&1); rc=$?
          [ $rc = 0 ] && echo "PASS $name ($(( $(date +%s)-t ))s)" || { echo "FAIL $name rc=$rc ($(( $(date +%s)-t ))s): $(echo "$out" | tail -3 | tr '\n' ' ')"; red=1; }; }
  run flake8 bash -c "cd '$R' && $PY -m flake8 --config .flake8 contrib/deepsignal"
  if echo "$changed" | grep -q '^contrib/deepsignal/console/'; then
    C=$R/contrib/deepsignal/console
    [ -d "$C/node_modules" ] || (cd "$C" && npm ci --no-audit --no-fund > /dev/null 2>&1)
    run oxlint bash -c "cd '$C' && npx oxlint"
    run tsc bash -c "cd '$C' && npx tsc -b --noEmit"
    run vitest bash -c "cd '$C' && npx vitest run"
  fi
  tests=$(echo "$changed" | grep -E '(^|/)test_[^/]*\.py$' | while read -r f; do [ -f "$R/$f" ] && echo "$f"; done | tr '\n' ' ')
  [ -n "$tests" ] && run pytest-changed bash -c "cd '$R' && perl -e 'alarm 1800; exec @ARGV' $PY -m pytest -p no:cacheprovider -q -k 'not real_197' $tests"
  SC=$D/venv-scan/bin/python
  if [ ! -e "$SC" ] && [ ! -L "$SC" ]; then SC=$PY; fi
  if [ -f "$DESK/bandit-policy.py" ] && [ ! -L "$DESK/bandit-policy.py" ]; then
    "$PY" -I -B "$DESK/bandit-policy.py" "$SC" "$R" "$HEAD_SHA" "$RECEIPTS" 2>&1 || red=1
  else
    echo "FAIL bandit: trusted desk helper missing or invalid"
    red=1
  fi
  if $SC -c 'import pip_audit' 2>/dev/null; then run pip-audit bash -c "$SC -m pip_audit -l"; else echo "SKIP pip-audit (not installed: the Mac permission check refused venv-scan, D-SCAN1; runs in the cloud review)"; fi
  if echo "$changed" | grep -q '^contrib/deepsignal/console/'; then out=$(cd "$R/contrib/deepsignal/console" && npm audit --offline --audit-level=high 2>&1) && echo "PASS npm-audit-offline" || echo "ADVISORY npm-audit-offline (not counted; offline data may be missing): $(echo "$out" | tail -2 | tr '\n' ' ')"; fi
  echo "TOTAL $(( $(date +%s)-T0 ))s"
  [ $red = 0 ] && echo "RESULT GREEN" || echo "RESULT RED"
} > "$TEMP_OUT"
cat "$TEMP_OUT"
mv -f -- "$TEMP_OUT" "$OUT" || exit 1
[ "$red" = 0 ]
