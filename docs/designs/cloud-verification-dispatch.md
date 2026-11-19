# Cloud verification dispatch

Design approved by Eugene on 2026-11-19. This is desk tooling for the supervised pilot.

## Fixed target

An operator submits a Linux verification job through the desk launcher while a Mac build is running. After preflight, design, work-in-progress, claim and commit checks pass, the launcher dispatches the approved workflow to the fork desk's GitHub Actions runner. Remote execution can begin before the Mac build releases its slot. Retain the existing Mac route for data-correctness builds and Mac-specific verification.

Record the product repository and commit, the trusted workflow revision, run ID, URL, terminal result and per-command outcomes. A repeated submission for the same claimed job must reuse the existing run or report the claim. A refusal must end before dispatch. Interrupted submissions must reconcile any matching run before retrying.

## Acceptance tests

Proposed new regression commands, to run through the desk launcher from an isolated desk checkout:

```sh
bash tools/pipe2/tests/cloud-verification-dispatch.sh overlap
bash tools/pipe2/tests/cloud-verification-dispatch.sh preflight-and-claims
bash tools/pipe2/tests/cloud-verification-dispatch.sh reconcile-and-receipts
bash tools/pipe2/tests/pinned-head-and-single-launch.sh
bash tools/pipe2/tests/preflight-refuses-before-claim.sh
```

Exercise the normal submission entry point with an owned Mac fixture occupying its slot. Verify dispatch before the fixture releases it, then repeat with a second valid pinned commit. Cover missing needs, an active claim, a moved commit, and a failed cloud check. Each refusal must produce zero dispatches. Prove overlap once on the fork with timestamps and the exact upstream launcher receipt and downstream Actions run.

## Prerequisites and out of scope

Requires an approved desk workflow, fork access, an unclaimed admitted job, GitHub Actions capacity and a recorded baseline wait. The observed hardening self-check waited 1,261 seconds for its local job to start. Cloud quota and achievable sustained concurrency still need measurement. This proposal covers Linux verification dispatch. Changing module priorities, raising local resource caps, moving data-correctness builds, deploying scanner policy, merging critical code and running the soak are separate decisions.
