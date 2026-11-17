#!/usr/bin/env bash
# OpenRVDAS gate. Runs on the Mac Mini against one exact commit of the fork.
#   bash gate/gate.sh <40-hex sha>
# Exit 0 GREEN, 1 RED, 2 REFUSED (did not run or incomplete; never green, never red).
# Receipts: ~/OpenRVDAS-Work/receipts/<sha>/<utc>/ (results.tsv, receipt.json, logs). Never deleted by the gate.
# Locking test: python3 -I gate/tests/test_gate.py
# Bash 3.2 compatible (macOS /bin/bash).
set -u

here=$(cd "$(dirname "$0")" && pwd)
sha=${1:-}
WORK=${ORV_WORK:-$HOME/OpenRVDAS-Work}
REPO=$WORK/openrvdas
VENV=${ORV_VENV:-$WORK/venv-3.12}
KALON_HOME=${ORV_KALON_HOME:-$HOME/KalonWork}
MIN_FREE_KB=${ORV_MIN_FREE_KB:-10485760}   # 10 GB, the Mini floor shared with Kalon
GATE_HOST=${ORV_GATE_HOST:-EugeneMacMini}
EXPECTED=$here/expected-failures.txt
rec=""
wt=""
lock=""

refuse() {
  echo "REFUSED: $*"
  if [ -n "$rec" ]; then printf 'REFUSED: %s\n' "$*" > "$rec/REFUSED.txt"; fi
  exit 2
}

cleanup() {
  if [ -n "$wt" ] && [ -d "$wt" ]; then git -C "$REPO" worktree remove --force "$wt" >/dev/null 2>&1; fi
  if [ -n "$lock" ]; then rm -rf "$lock"; fi
}

# 1. Inputs and machine identity (LocalHostName, never hostname).
echo "$sha" | grep -Eq '^[0-9a-f]{40}$' || refuse "need a full 40-hex sha, got '${sha}'"
real_name=$(scutil --get LocalHostName 2>/dev/null || echo unset)
if [ -n "${ORV_LOCALHOSTNAME:-}" ]; then
  # Test seam only. Using it on the real gate host would bypass the identity check.
  [ "$real_name" = "$GATE_HOST" ] && refuse "test seam ORV_LOCALHOSTNAME set on the gate host"
  name=$ORV_LOCALHOSTNAME
else
  name=$real_name
fi
[ "$name" = "$GATE_HOST" ] || refuse "WRONG MACHINE: LocalHostName=$name, gate host is $GATE_HOST"

# 2. Kalon has priority on the Mini.
if ls -d "$KALON_HOME"/lock-w* >/dev/null 2>&1; then refuse "Kalon gate holds the Mini ($KALON_HOME/lock-w*)"; fi
if [ -z "${ORV_SKIP_PGREP:-}" ] && pgrep -f 'mini-gate-suite\.sh' >/dev/null 2>&1; then refuse "Kalon mini-gate-suite.sh is running"; fi

# 3. Disk floor.
mkdir -p "$WORK/receipts" "$WORK/wt"
free_kb=$(df -Pk "$WORK" | awk 'NR==2 {print $4}')
[ "${free_kb:-0}" -ge "$MIN_FREE_KB" ] || refuse "free disk ${free_kb}KB below floor ${MIN_FREE_KB}KB"

# 4. One OpenRVDAS gate at a time. A lock whose owner is dead is taken over.
lock=$WORK/gate.lock
if ! mkdir "$lock" 2>/dev/null; then
  owner=$(cat "$lock/pid" 2>/dev/null || echo "")
  if [ -n "$owner" ] && kill -0 "$owner" 2>/dev/null; then lock=""; refuse "another gate is running (pid $owner)"; fi
  rm -rf "$lock"; mkdir "$lock" 2>/dev/null || { lock=""; refuse "could not take the gate lock"; }
fi
echo $$ > "$lock/pid"
trap cleanup EXIT

# 5. The exact commit, in a fresh worktree.
[ -d "$REPO/.git" ] || refuse "no clone at $REPO (see mini/SETUP.md)"
[ -x "$VENV/bin/python" ] || refuse "no venv at $VENV (see mini/SETUP.md)"
git -C "$REPO" fetch -q origin '+refs/heads/*:refs/remotes/origin/*' 2>/dev/null || echo "warning: fetch failed, using local objects"
git -C "$REPO" cat-file -e "$sha^{commit}" 2>/dev/null || refuse "commit $sha not in $REPO after fetch (push it to eugenevivino/openrvdas)"
rec=$WORK/receipts/$sha/$(date -u +%Y%m%dT%H%M%SZ)
mkdir -p "$rec"
wt=$WORK/wt/$sha
if [ -d "$wt" ]; then git -C "$REPO" worktree remove --force "$wt" >/dev/null 2>&1 || rm -rf "$wt"; fi
git -C "$REPO" worktree prune
git -C "$REPO" worktree add --detach -q "$wt" "$sha" || refuse "worktree add failed"
for f in database/settings.py database/influxdb/settings.py django_gui/settings.py; do
  [ -f "$wt/$f.dist" ] && [ ! -f "$wt/$f" ] && cp "$wt/$f.dist" "$wt/$f"
done

# 6. Environment. Dependencies are installed only by mini/SETUP.md; a changed
#    pyproject.toml refuses instead of installing silently.
stamp=$(shasum -a 256 "$wt/pyproject.toml" | awk '{print $1}')
have=$(cat "$VENV/.orv-deps-stamp" 2>/dev/null || echo none)
if [ "$stamp" != "$have" ] && [ -z "${ORV_ALLOW_DEPS_DRIFT:-}" ]; then
  refuse "pyproject.toml changed (deps stamp $have, commit $stamp). Run the deps step in mini/SETUP.md, then rerun."
fi
"$VENV/bin/python" -m pip install -q --no-deps --no-build-isolation -e "$wt" >"$rec/pip.log" 2>&1 \
  || refuse "editable install of the worktree failed (see $rec/pip.log)"
desk_sha=$(git -C "$here/.." rev-parse HEAD 2>/dev/null || echo unknown)
{
  echo "sha=$sha"; echo "desk_sha=$desk_sha"; echo "host=$name"
  echo "python=$("$VENV/bin/python" -V 2>&1)"; echo "started=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
} > "$rec/meta.txt"

results=$rec/results.tsv
: > "$results"
cd "$wt" || refuse "cannot enter worktree"

# 7a. pytest, everything except the Django GUI tests.
echo "gate: pytest ..."
nice -n 10 "$VENV/bin/python" -m pytest test/ --ignore=test/django_gui -q -p no:cacheprovider \
  --timeout=300 --junitxml="$rec/pytest.xml" >"$rec/pytest.log" 2>&1
if [ -f "$rec/pytest.xml" ]; then
  "$VENV/bin/python" -I "$here/gate_lib.py" junit "$rec/pytest.xml" "$rec/pytest.log" >> "$results" \
    || echo "pytest::__JUNIT_UNREADABLE__	FAIL" >> "$results"
fi

# 7b. Django GUI tests, through a recording runner (one row per test).
echo "gate: django ..."
PYTHONPATH="$here" ORV_DJ_ROWS="$rec/django.tsv" nice -n 10 "$VENV/bin/python" manage.py test test.django_gui \
  --noinput --testrunner=orv_django_runner.Runner >"$rec/django.log" 2>&1
[ -f "$rec/django.tsv" ] && cat "$rec/django.tsv" >> "$results"

# 7c. flake8 on Python files changed versus the fork's dev.
echo "gate: flake8 ..."
if base=$(git -C "$REPO" merge-base "$sha" origin/dev 2>/dev/null); then
  git -C "$REPO" diff --name-only --diff-filter=AMR "$base" "$sha" -- '*.py' > "$rec/changed.txt"
  : > "$rec/flake8.log"
  while IFS= read -r f; do
    [ -n "$f" ] || continue
    if "$VENV/bin/python" -m flake8 "$f" >> "$rec/flake8.log" 2>&1; then
      printf 'flake8::%s\tPASS\n' "$f" >> "$results"
    else
      printf 'flake8::%s\tFAIL\n' "$f" >> "$results"
    fi
  done < "$rec/changed.txt"
  printf 'flake8::__COMPLETE__\tPASS\n' >> "$results"
else
  printf 'flake8::__NO_BASE__ origin/dev\tFAIL\n' >> "$results"
fi

# 8. __END__ only when every stage left complete evidence. Then the verdict.
if grep -q '^pytest::__COMPLETE__	PASS$' "$results" \
  && grep -q '^django::__COMPLETE__	PASS$' "$results" \
  && grep -q '^flake8::__COMPLETE__	PASS$' "$results"; then
  printf '__END__\tPASS\n' >> "$results"
fi
echo "finished=$(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "$rec/meta.txt"
"$VENV/bin/python" -I "$here/gate_lib.py" verdict "$results" "$EXPECTED" "$rec/receipt.json" "$sha" "$name"
rc=$?
echo "receipt: $rec"
exit $rc
