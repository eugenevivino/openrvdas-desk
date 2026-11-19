# Lead brief: 2026-11-19 cloud verification dispatch

## Goal

Prove a hosted check of the approved supervised pilot starts while an isolated Mac
slot is occupied. Submit through the candidate desk launcher.

## Exact state

- Desk candidate for `deepsignal/cloud-verification-dispatch`, uncommitted on detached
  base `ba5d4074c5e6de0746bffa3cc482297d6758a2b2`.
- Hosted gate NOT RUN. The worker performed no network operations.
- Local test results are in `/private/tmp/deepsignal/cloud-verification-dispatch/tmp`
  under `red-route-*.log` and `green-*.log`.

## Done

- Isolated acceptance passed for two pins, launcher refusals, uncertain pushes, concurrent
  submissions and command receipts. Both legacy checks passed in owned fixtures.
- The [operator procedure](../tools/pipe2/CLOUD-VERIFICATION.md) includes an occupied-slot
  local baseline and a comparison against the hosted `console-tests` start time.

## Tried and failed

The locking tests reached the candidate launcher and failed at the missing dispatcher
before implementation. No hosted attempt was made.

## Next bounded task

After owner review and publication of the exact desk topic, run the [live overlap
procedure](../tools/pipe2/CLOUD-VERIFICATION.md#isolated-live-overlap-rehearsal) once
from the outer launcher. Stop when the procedure records PASS and the exact run URL,
or records a refusal or failed verification. Keep the evidence directory.

## Open questions

Owner review, actual hosted timing and sustained Actions capacity are pending.

## Do not

Keep the live launcher, live claims, installed policy, default branch and product
fork outside this rehearsal's writes. Production installation is a separate decision.
