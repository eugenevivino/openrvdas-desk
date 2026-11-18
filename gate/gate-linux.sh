#!/usr/bin/env bash
# Exit codes: 0 GREEN, 1 RED, 2 REFUSED. The receipt directory must be new.
set -euo pipefail

if [[ $# -ne 3 ]]; then
  echo 'REFUSED: usage: bash gate/gate-linux.sh <40-hex sha> <fork> <receipt-dir>' >&2
  exit 2
fi
here=$(cd -- "$(dirname -- "$0")" && pwd)
sha=$1
fork=$2
if ! mkdir -- "$3"; then
  echo 'REFUSED: could not create a new receipt directory' >&2
  exit 2
fi
rec=$(cd -- "$3" && pwd)
results=$rec/results.tsv
expected=$here/expected-failures.txt
host=${RUNNER_NAME:-$(hostname)}
reason='gate stopped before completing the run'

finish() {
  local status=$? verdict_status=0
  trap - EXIT
  if (( status != 0 )); then
    printf 'REFUSED: %s\n' "$reason" | tee "$rec/REFUSED.txt" >&2
  fi
  python3 -I "$here/gate_lib.py" verdict "$results" "$expected" \
    "$rec/receipt.json" "$sha" "$host" || verdict_status=$?
  if [[ ! -s "$rec/receipt.json" ]]; then
    echo 'REFUSED: could not write receipt.json' >&2
    exit 2
  fi
  exit "$verdict_status"
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

record_suite() {
  local suite=$1 status=$2 rows=$3
  [[ -f "$rows" ]] || refuse "$suite produced no test rows"
  cat "$rows" >> "$results"
  [[ $(tail -n 1 "$rows") == "$suite"$'::__COMPLETE__\tPASS' ]] \
    || refuse "$suite results are incomplete"
  if grep -q $'\tFAIL$' "$rows"; then
    [[ "$status" == 1 ]] || refuse "$suite exit $status disagrees with its rows"
  else
    [[ "$status" == 0 ]] || refuse "$suite exit $status disagrees with its rows"
  fi
}

trap finish EXIT
: > "$results"
[[ "$sha" =~ ^[0-9a-f]{40}$ ]] || refuse 'need a full 40-hex sha'
[[ $(uname -s) == Linux ]] || refuse 'Linux runner required'
version=$(python3 -I -c 'import sys; print(sys.version.split()[0]);
sys.exit(sys.version_info[:2] != (3, 12))') || refuse 'Python 3.12 required'
[[ -n "$fork" ]] || refuse 'fork checkout unavailable'
fork=$(cd -- "$fork" && pwd) || refuse 'cannot enter fork checkout'
verify_checkout
[[ -r "$expected" ]] || refuse 'expected-failures.txt is unavailable'
printf 'sha=%s\nhost=%s\npython=%s\n' "$sha" "$host" "$version" > "$rec/meta.txt"

base=$(git -C "$fork" merge-base "$sha" refs/remotes/origin/dev) \
  || refuse 'no merge base with origin/dev'
git -C "$fork" diff --name-only -z --diff-filter=AMR "$base" "$sha" -- '*.py' \
  > "$rec/changed.paths" || refuse 'cannot list changed Python files'

cd -- "$fork"
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
"$python" -m pip install -e '.[dev,mqtt]' flake8 pytest-timeout \
  > "$rec/pip.log" 2>&1 || refuse 'dependency install failed (see pip.log)'

status=0
"$python" -m pytest test/ --ignore=test/django_gui -q -p no:cacheprovider \
  --timeout=300 --junitxml="$rec/pytest.xml" > "$rec/pytest.log" 2>&1 || status=$?
(( status <= 1 )) || refuse "pytest exited $status (see pytest.log)"
python3 -I "$here/gate_lib.py" junit "$rec/pytest.xml" "$rec/pytest.log" \
  > "$rec/pytest.tsv" || refuse 'could not parse pytest evidence'
record_suite pytest "$status" "$rec/pytest.tsv"

status=0
PYTHONPATH="$here" ORV_DJ_ROWS="$rec/django.tsv" "$python" manage.py test \
  test.django_gui --noinput --testrunner=orv_django_runner.Runner \
  > "$rec/django.log" 2>&1 || status=$?
(( status <= 1 )) || refuse "Django exited $status (see django.log)"
record_suite django "$status" "$rec/django.tsv"

: > "$rec/flake8.log"
while IFS= read -r -d '' file; do
  status=0
  "$python" -m flake8 --format='%(code)s %(path)s:%(row)d:%(col)d: %(text)s' \
    "./$file" > "$rec/flake8.out" 2>> "$rec/flake8.log" || status=$?
  cat "$rec/flake8.out" >> "$rec/flake8.log"
  if (( status <= 1 )) && grep -Eq '^[A-Z]+[0-9]+ ' "$rec/flake8.out"; then
    printf 'flake8::%s\tFAIL\n' "$file" >> "$results"
  elif (( status == 0 )) && [[ ! -s "$rec/flake8.out" ]]; then
    printf 'flake8::%s\tPASS\n' "$file" >> "$results"
  else
    refuse "flake8 did not complete for $file (see flake8.log)"
  fi
done < "$rec/changed.paths"
verify_checkout
printf 'flake8::__COMPLETE__\tPASS\n__END__\tPASS\n' >> "$results"
