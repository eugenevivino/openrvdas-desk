# Pilot cloud verification

Use the desk launcher from the reviewed, clean desk checkout. The hosted profile verifies
`refs/heads/deepsignal/console-supervised-pilot` on `eugenevivino/openrvdas`. It checks the
exact checkout, installs the console's lockfile dependencies on Ubuntu, runs its unit tests,
and runs its TypeScript check. These receipts cover those checks. The pilot release gate
and the installed Mac security policy have their own evidence.

## Operator invocation

The owner publishes the reviewed desk commit to
`refs/heads/deepsignal/cloud-verification-dispatch` and approves its full SHA. Use that exact
commit locally. GitHub Actions must be enabled on `eugenevivino/openrvdas-desk`. The
operator needs Git credentials for creating tags on that repository, read access to its
Actions runs through `gh` with `--slurp` support, and an HTTPS checkout of the readable
pilot fork with the approved product SHA at HEAD. Git and `gh` use the operator's existing
authentication. The pilot fork must be public for cross-repo checkout from Actions.
The workflow uses a read-only token and drops checkout credentials.

From the desk checkout, set `product` to the root of the pilot checkout, `brief` to the
approved brief with D-PIPE2 needs, and `job_dir` to an existing job directory. Set
`desk_sha` and `product_sha` to the approved full SHAs.

```sh
bash tools/fast-review/ds-launch-when-ok.sh "$product" "$brief" "$job_dir/cloud.json" 900 --cloud-verify "$desk_sha" "$product_sha"
```

The launcher reads the installed preflight, WIP slots and design notes under
`/private/tmp/deepsignal` and uses that desk's claims. A reservation at
`claims/unit-console` refuses hosted submission with exit 3. Coordinate with its desk
owner. The reviewed checkout supplies the dispatcher and the pinned workflow. The
existing `--` route selects a Mac job. Cloud
verification exits 0 for complete success, 1 for a failed run or incomplete success
evidence, 75 while the exact run or its evidence is pending, and 9 for a pin, trust,
or transport error. The launcher keeps its existing admission exit
codes. Check the launcher output together with the JSON receipt. Missing command rows
mean Actions has supplied no outcome for them. Failed, skipped and cancelled steps
retain their actual conclusions and timestamps.

The request is a lightweight tag named `refs/tags/cloud-verification/v1/<product-sha>-<desk-sha>`.
A direct Git push creates the tag on the approved desk commit and triggers that commit's
`push` workflow. Setup on the default branch is unnecessary. Keep request tags intact.
Repeat the same submission on exit 75. The launcher checks the tag, finds the original
attempt by its full request ref in the Actions run title and its desk SHA, then refreshes
the receipt. The same pair of pins groups submissions across job directories. The
dispatcher never asks Actions to rerun a verification. An operator rerun of the same
Actions run will produce a trust refusal on reconciliation.

## Live overlap rehearsal

Run this as the owner or outer launch operator after publishing the reviewed desk
topic. Start an approved, bounded Mac fixture job for another admitted unit
through the installed launcher, using its own workdir and brief. Wait for its
`ds-codex` process to hold the real Mac lock and run `codex exec`. Use that fixture's wrapper PID and
its workdir below. Use the approved supervised pilot SHA and a pilot checkout whose
absolute path matches the installed console WIP slot. Keep the rehearsal evidence
outside the candidate desk checkout. The existing 1,261-second local wait is the
baseline recorded in the design note.

```bash
bash <<'BASH'
set -euo pipefail
export PYTHONDONTWRITEBYTECODE=1
job_dir=$(mktemp -d /private/tmp/deepsignal/cloud-verification-dispatch/tmp/live-overlap.XXXXXX)
printf 'Evidence directory %s\n' "$job_dir"
read -r -p 'Reviewed desk commit SHA: ' desk_sha </dev/tty
read -r -p 'Approved pilot commit SHA: ' product_sha </dev/tty
read -r -p 'Pilot checkout workdir: ' product </dev/tty
read -r -p 'Approved Mac fixture workdir: ' mac_cwd </dev/tty
read -r -p 'Approved Mac fixture ds-codex PID: ' mac_pid </dev/tty
test "$(git rev-parse HEAD)" = "$desk_sha"
test -z "$(git status --porcelain --untracked-files=all)"
product=$(cd "$product" && pwd -P)
mac_cwd=$(cd "$mac_cwd" && pwd -P)
test "$(git -C "$product" rev-parse HEAD)" = "$product_sha"
[[ "$mac_pid" =~ ^[1-9][0-9]*$ ]]
brief="$job_dir/brief.md"
cat >"$brief" <<'BRIEF'
---
needs:
  network: yes
  tools: git, gh, python3.12
  required_files: contrib/deepsignal/console/package-lock.json
---
# Verify the approved supervised pilot over the hosted Linux lane
BRIEF
launcher=tools/fast-review/ds-launch-when-ok.sh
lock=/private/tmp/deepsignal/.ds-codex.lock/pid
find_codex() {
  local node
  pgrep -x -P "$mac_pid" codex && return 0
  node=$(pgrep -x -P "$mac_pid" node) || return 1
  [[ "$node" =~ ^[1-9][0-9]*$ ]] || return 1
  pgrep -x -P "$node" codex
}
codex_pid=$(find_codex)
[[ "$codex_pid" =~ ^[1-9][0-9]*$ ]]
mac_launcher_pid=$(ps -p "$mac_pid" -o ppid= | tr -d ' ')
[[ "$mac_launcher_pid" =~ ^[1-9][0-9]*$ ]]
mac_launcher=$(ps -ww -p "$mac_launcher_pid" -o command=)
[[ "$mac_launcher" == *"/private/tmp/deepsignal/ds-launch-when-ok.sh "* ]]
mac_processes() {
  ps -p "$mac_launcher_pid,$mac_pid,$codex_pid" -o pid=,ppid=,lstart=
}
identity=$(mac_processes)
observe_mac() {
  local wrapper child cwd
  wrapper=$(ps -ww -p "$mac_pid" -o command=) || return 1
  child=$(ps -ww -p "$codex_pid" -o command=) || return 1
  cwd=$(lsof -a -p "$mac_pid" -d cwd -Fn | sed -n 's/^n//p') || return 1
  [[ "$wrapper" == *"$HOME/bin/ds-codex --wait-ram="* ]] || return 1
  [[ "$child" == *"/codex exec "* ]] || return 1
  [ "$cwd" = "$mac_cwd" ] && [ "$(cat "$lock")" = "$mac_pid" ] &&
    [ "$(find_codex)" = "$codex_pid" ] &&
    [ "$(mac_processes)" = "$identity" ] || return 1
  date -u +%FT%TZ
}
printf '%s\n%s\n' "$mac_cwd" "$identity" >"$job_dir/mac-fixture.txt"
observations="$job_dir/mac-observations.log"
observe_mac >"$observations"
(while sleep 2 && observe_mac; do :; done) >>"$observations" &
watch_pid=$!
stop_watch() {
  kill "$watch_pid" 2>/dev/null || true
  wait "$watch_pid" 2>/dev/null || true
}
trap stop_watch EXIT
trap 'exit 130' INT
trap 'exit 143' TERM

receipt="$job_dir/cloud.json"
# An existing run is useful on retry, but only a fresh tag proves a new dispatch.
# The comparison below requires the Actions test to start during this fixture run.
while :; do
  rc=0
  bash "$launcher" "$product" "$brief" "$receipt" 900 --cloud-verify "$desk_sha" "$product_sha" \
    >>"$job_dir/cloud-launcher.log" 2>&1 || rc=$?
  test "$rc" -ne 75 || continue
  break
done
test "$rc" -eq 0
stop_watch
trap - EXIT
python3.12 - "$job_dir" "$desk_sha" "$product_sha" <<'PY' | tee "$job_dir/overlap-result.log"
import json
from pathlib import Path
import sys

job, desk_sha, product_sha = Path(sys.argv[1]), sys.argv[2], sys.argv[3]
receipt = json.loads(job.joinpath("cloud.json").read_text())
observations = job.joinpath("mac-observations.log").read_text().splitlines()
first, last = observations[0], observations[-1]
assert receipt["desk_sha"] == desk_sha and receipt["product_sha"] == product_sha
assert receipt["request_ref"] == f"refs/tags/cloud-verification/v1/{product_sha}-{desk_sha}"
assert receipt["conclusion"] == "success"
log = job.joinpath("cloud-launcher.log").read_text()
assert f"request tag confirmed {receipt['request_ref']}" in log
started = receipt["commands"]["console-tests"]["started_at"]
assert first < receipt["created_at"] <= started < last, (first, started, last)
print(f"PASS Mac job observed at {first} and {last}, console-tests started {started}")
print(receipt["url"])
PY
BASH
```

Keep the Mac fixture launch receipt, process observations, hosted launcher log, JSON
receipt and overlap result together. A fresh pair of approved commits is required
when the existing run predates the Mac fixture. PASS requires the hosted test step
to start between two observations of the same real Mac job. The live rehearsal
and sustained Actions capacity remain pending.
