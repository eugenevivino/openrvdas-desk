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

The launcher uses its usual WIP and claim directory and checks the pilot and launcher
designs in the pinned checkout. The existing `--` route selects a Mac job. Cloud
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

## Isolated live overlap rehearsal

Run this as the owner or outer launch operator after publishing the reviewed desk
topic. Start in the clean checkout of that approved commit. Use the supervised
pilot's approved product SHA and keep the displayed job directory as evidence.
The owned lock fixture remains occupied through the hosted check and the timestamp
comparison. It represents a local occupied slot without using the live lock,
the installed launcher, or a real Codex process. Interrupting the procedure
before the hosted check starts leaves an incomplete rehearsal.
The state-directory override is reserved for this isolated rehearsal.

```bash
bash <<'BASH'
set -euo pipefail
export TMPDIR=/private/tmp/deepsignal/cloud-verification-dispatch/tmp
export PYTHONDONTWRITEBYTECODE=1
job_dir=$(mktemp -d "$TMPDIR/live-overlap.XXXXXX")
printf 'Evidence directory %s\n' "$job_dir"
read -r -p 'Reviewed desk commit SHA: ' desk_sha </dev/tty
read -r -p 'Approved pilot commit SHA: ' product_sha </dev/tty
test "$(git rev-parse HEAD)" = "$desk_sha"
product="$job_dir/console-supervised-pilot"
git clone --single-branch --branch deepsignal/console-supervised-pilot \
  https://github.com/eugenevivino/openrvdas.git "$product" >"$job_dir/clone.log" 2>&1
test "$(git -C "$product" rev-parse HEAD)" = "$product_sha"

export DS_LAUNCH_STATE_DIR="$job_dir/launcher-state"
export DS_POLL=1
mkdir -p "$DS_LAUNCH_STATE_DIR/.ds-codex.lock"
lock="$DS_LAUNCH_STATE_DIR/.ds-codex.lock"
trap 'rm -f "$lock/pid"; rmdir "$lock"' EXIT
trap 'exit 130' INT
trap 'exit 143' TERM
printf '%s\n' "$$" >"$lock/pid"
printf 'console|/console-supervised-pilot$\n' >"$DS_LAUNCH_STATE_DIR/wip-units.txt"
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
date -u +%FT%TZ >"$job_dir/fixture-held"
rc=0
bash "$launcher" "$product" "$brief" "$job_dir/local-job.log" 2 -- -m gpt-6.2-sol - \
  >"$job_dir/local-baseline.log" 2>&1 || rc=$?
test "$rc" -eq 1
[[ $(<"$job_dir/local-baseline.log") == *"NOT launched after 2s: lock=$$"* ]]

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
test "$(cat "$lock/pid")" = "$$"
kill -0 "$$"
date -u +%FT%TZ >"$job_dir/fixture-releasing"
python3.12 - "$job_dir" "$desk_sha" "$product_sha" <<'PY' | tee "$job_dir/overlap-result.log"
import json
from pathlib import Path
import sys

job, desk_sha, product_sha = Path(sys.argv[1]), sys.argv[2], sys.argv[3]
receipt = json.loads(job.joinpath("cloud.json").read_text())
held = job.joinpath("fixture-held").read_text().strip()
releasing = job.joinpath("fixture-releasing").read_text().strip()
assert receipt["desk_sha"] == desk_sha and receipt["product_sha"] == product_sha
assert receipt["request_ref"] == f"refs/tags/cloud-verification/v1/{product_sha}-{desk_sha}"
assert receipt["conclusion"] == "success"
log = job.joinpath("cloud-launcher.log").read_text()
assert f"request tag confirmed {receipt['request_ref']}" in log
started = receipt["commands"]["console-tests"]["started_at"]
assert held < receipt["created_at"] <= started < releasing, (held, started, releasing)
print(f"PASS held {held}, console-tests started {started}, releasing {releasing}")
print(receipt["url"])
PY
BASH
```

Keep the local baseline, launcher log, JSON receipt and overlap result together.
If the run already executed before the fixture, use another approved pair of commits
for fresh overlap evidence. A queued run or a created tag alone does not prove
overlap. Simulated overlap passes in the workspace. The live rehearsal, actual
hosted timings and sustained Actions capacity remain pending.
