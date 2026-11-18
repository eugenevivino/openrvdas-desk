#!/usr/bin/env bash
# Exit codes: 0 GREEN, 1 RED, 2 REFUSED. The receipt directory must be new.
# The same job runs fork code and writes the receipts. A hostile fork could
# forge them, so this gate is suitable only for our own fork.
set -euo pipefail

if [[ $# -ne 3 ]]; then
  echo 'REFUSED: usage: bash gate/gate-linux.sh <40-hex sha> <fork> <receipt-dir>' >&2
  exit 2
fi
if ! here=$(cd -- "$(dirname -- "$0")" && pwd); then
  echo 'REFUSED: could not locate the gate directory' >&2
  exit 2
fi
sha=$1
fork=$2
if ! mkdir -- "$3"; then
  echo 'REFUSED: could not create a new receipt directory' >&2
  exit 2
fi
if ! rec=$(cd -- "$3" && pwd); then
  echo 'REFUSED: could not enter the receipt directory' >&2
  exit 2
fi
results=$rec/results.tsv
expected=$here/expected-failures.txt
host=${RUNNER_NAME:-unknown}
reason='gate stopped before completing the run'
initial_index=

finish() {
  trap - EXIT HUP INT TERM
  if [[ -f "$rec/rows-before-end" ]]; then
    mv -- "$rec/rows-before-end" "$results" \
      || echo 'REFUSED: could not restore results.tsv before __END__' >&2
  fi
  printf 'REFUSED: %s\n' "$reason" >&2
  printf 'REFUSED: %s\n' "$reason" > "$rec/REFUSED.txt" \
    || echo 'REFUSED: could not write REFUSED.txt' >&2
  local status=0
  python3 -I "$here/gate_lib.py" refused "$results" "$expected" \
    "$rec/receipt.json" "$sha" "$host" "$reason" || status=$?
  if (( status != 2 )) || [[ ! -s "$rec/receipt.json" ]]; then
    echo 'REFUSED: could not write receipt.json' >&2
  fi
  exit 2
}

refuse() {
  reason=$1
  exit 2
}

verify_checkout() {
  local actual
  actual=$(git -C "$fork" rev-parse --verify HEAD) || refuse 'cannot read fork HEAD'
  [[ "$actual" == "$sha" ]] || refuse "fork HEAD $actual does not match $sha"
}

verify_lint_file() {
  [[ -f "$1" && ! -L "$1" ]] \
    || refuse "changed Python path is not a regular file: $1"
  [[ -r "$1" ]] || refuse "cannot read changed Python file: $1"
}

verify_tracked() {
  local stage=$1 changes index error
  verify_checkout
  git -C "$fork" diff --quiet --no-ext-diff --ignore-submodules=none HEAD -- \
    || refuse "tracked files differ $stage"
  changes=$(git -C "$fork" status --porcelain=v1 --untracked-files=no \
    --ignore-submodules=none) || refuse "cannot check tracked status $stage"
  [[ -z "$changes" ]] || refuse "tracked files are modified $stage"
  index=$(git -C "$fork" ls-files -s -z | shasum -a 256) \
    || refuse "cannot hash tracked index $stage"
  printf '%s\t%s\n' "$stage" "${index%% *}" >> "$rec/tracked.txt"
  [[ "$index" == "${initial_index:-$index}" ]] \
    || refuse "tracked index changed $stage"
  initial_index=$index
  error=$(python3 -I "$here/gate_lib.py" verify-tree "$rec/head-tree" "$fork" 2>&1) \
    || refuse "cannot verify tracked files $stage: $error"
}

validate_suite() {
  local suite=$1 status=$2 error
  error=$(python3 -I "$here/gate_lib.py" suite "$suite" "$status" \
    "$rec/$suite.tsv" 2>&1 > "$rec/$suite.valid") \
    || refuse "${error:-could not validate $suite results}"
}

trap finish EXIT
trap 'refuse "gate interrupted"' HUP INT TERM
: > "$results"
export GIT_OPTIONAL_LOCKS=0 GIT_NO_REPLACE_OBJECTS=1
host=${RUNNER_NAME:-$(hostname)} || refuse 'cannot identify runner host'
[[ "$sha" =~ ^[0-9a-f]{40}$ ]] || refuse 'need a full 40-hex sha'
[[ $(uname -s) == Linux ]] || refuse 'Linux runner required'
version=$(python3 -I -c 'import sys; print(sys.version.split()[0]);
sys.exit(sys.version_info[:2] != (3, 12))') || refuse 'Python 3.12 required'
ID= VERSION_ID=
source /etc/os-release || refuse 'cannot read /etc/os-release'
printf 'sha=%s\nhost=%s\npython=%s\nID=%s\nVERSION_ID=%s\n' \
  "$sha" "$host" "$version" "$ID" "$VERSION_ID" > "$rec/meta.txt"
[[ "$ID" == ubuntu && "$VERSION_ID" == 22.04 ]] || refuse 'Ubuntu 22.04 required'
[[ -n "$fork" ]] || refuse 'fork checkout unavailable'
fork=$(cd -- "$fork" && pwd) || refuse 'cannot enter fork checkout'
verify_checkout
[[ -r "$expected" ]] || refuse 'expected-failures.txt is unavailable'

# The workflow fetches fork branches into refs/remotes/origin/ before checkout.
origin_ref=$(git -C "$fork" for-each-ref --contains "$sha" --count=1 \
  --format='%(refname)' refs/remotes/origin/) || refuse 'cannot check fork origin branches'
[[ -n "$origin_ref" ]] || refuse "$sha is not reachable from any fork origin branch"
base=$(git -C "$fork" merge-base "$sha" refs/remotes/origin/dev) \
  || refuse 'no merge base with origin/dev'
git -C "$fork" diff --name-only -z --no-renames --no-relative \
  --ignore-submodules=none "$base" "$sha" -- \
  > "$rec/changed.txt" || refuse 'cannot list changed files'
git -C "$fork" ls-tree -r -t -z --full-tree "$base" > "$rec/base-tree" \
  || refuse 'cannot read base commit tree'
git -C "$fork" ls-tree -r -t -z --full-tree "$sha" > "$rec/head-tree" \
  || refuse 'cannot read requested commit tree'
error=$(python3 -I "$here/gate_lib.py" changed-python "$rec/changed.txt" \
  "$rec/base-tree" "$rec/head-tree" 2>&1 > "$rec/lint-paths.txt") \
  || refuse "${error:-could not classify changed files}"

cd -- "$fork"
while IFS= read -r -d '' file; do
  verify_lint_file "$file"
done < "$rec/lint-paths.txt"
verify_tracked 'before install'
for file in database/settings.py database/influxdb/settings.py django_gui/settings.py; do
  if [[ -f "$file.dist" && ! -e "$file" ]]; then
    cp -- "$file.dist" "$file" || refuse "could not copy $file.dist"
  fi
done

# Keep credentials out of the checkouts and workflow command files out of
# the subprocess environment while running fork code and dependencies.
unset GITHUB_ENV GITHUB_OUTPUT GITHUB_PATH GITHUB_STATE GITHUB_STEP_SUMMARY
python3 -m venv "$rec/venv" > "$rec/venv.log" 2>&1 \
  || refuse 'virtual environment setup failed (see venv.log)'
python=$rec/venv/bin/python
# Pins from the Mini's ~/OpenRVDAS-Work/venv-3.12 on 2026-11-18.
"$python" -m pip install -e '.[dev,mqtt]' flake8==7.5.0 pytest-timeout==2.4.0 \
  > "$rec/pip.log" 2>&1 || refuse 'dependency install failed (see pip.log)'
verify_tracked 'after install'
"$python" -m pip freeze > "$rec/pip-freeze.txt" 2>> "$rec/pip.log" \
  || refuse 'could not record pip freeze (see pip.log)'
verify_tracked 'after pip freeze'

status=0
"$python" -m pytest test/ --ignore=test/django_gui -q -p no:cacheprovider \
  --timeout=300 --junitxml="$rec/pytest.xml" > "$rec/pytest.log" 2>&1 || status=$?
(( status <= 1 )) || refuse "pytest exited $status (see pytest.log)"
verify_tracked 'after pytest'
python3 -I "$here/gate_lib.py" junit "$rec/pytest.xml" "$rec/pytest.log" \
  > "$rec/pytest.tsv" || refuse 'could not parse pytest evidence'
validate_suite pytest "$status"

status=0
PYTHONPATH="$here" ORV_DJ_ROWS="$rec/django.tsv" "$python" manage.py test \
  test.django_gui --noinput --testrunner=orv_django_runner.Runner \
  > "$rec/django.log" 2>&1 || status=$?
(( status <= 1 )) || refuse "Django exited $status (see django.log)"
verify_tracked 'after Django'
validate_suite django "$status"
cat "$rec/pytest.valid" "$rec/django.valid" >> "$results"

export_dir=$rec/lint-export
mkdir -- "$export_dir"
git -C "$fork" archive --format=tar "$sha" | tar -xf - -C "$export_dir" \
  || refuse 'cannot export the requested commit for flake8'
verify_export() {
  local error
  error=$(python3 -I "$here/gate_lib.py" verify-tree "$rec/head-tree" \
    "$export_dir" 2>&1) || refuse "cannot verify flake8 export: $error"
}
verify_export
verify_tracked 'before lint'
cd -- "$export_dir"

: > "$rec/flake8.log"
while IFS= read -r -d '' file; do
  verify_lint_file "$file"
  # With --exit-zero, only a zero exit and a matching final --count prove
  # completion. Flake8 7.5.0 reserves exit 1 for a catastrophic failure here.
  status=0
  "$python" -m flake8 --exit-zero --count \
    --format='%(code)s %(path)s:%(row)d:%(col)d: %(text)s' \
    "./$file" > "$rec/flake8.out" 2>> "$rec/flake8.log" || status=$?
  cat "$rec/flake8.out" >> "$rec/flake8.log"
  (( status == 0 )) || refuse "flake8 did not complete for $file (see flake8.log)"
  row=$(python3 -I "$here/gate_lib.py" lint-row "$file" "$rec/flake8.out" 2>&1) \
    || refuse "${row:-could not validate flake8 result for $file}"
  printf '%s\n' "$row" >> "$results"
done < "$rec/lint-paths.txt"
verify_export
verify_tracked 'after lint'

# Only this path can publish a GREEN or RED receipt.
printf 'flake8::__COMPLETE__\tPASS\n' >> "$results"
cp -- "$results" "$rec/rows-before-end"
printf '__END__\tPASS\n' >> "$results"
verdict_status=0
python3 -I "$here/gate_lib.py" verdict "$results" "$expected" \
  "$rec/receipt.pending" "$sha" "$host" || verdict_status=$?
[[ -s "$rec/receipt.pending" && "$verdict_status" =~ ^[012]$ ]] \
  || refuse 'could not write receipt.json'
mv -- "$rec/receipt.pending" "$rec/receipt.json"
trap - EXIT HUP INT TERM
exit "$verdict_status"
