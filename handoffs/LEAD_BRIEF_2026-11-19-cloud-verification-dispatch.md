# Lead brief: 2026-11-19 cloud verification dispatch

## Goal

Prove a hosted check of the approved supervised pilot starts while an isolated Mac
slot is occupied. Submit through the candidate desk launcher.

## Exact state

- Desk admission fix for `deepsignal/cloud-verification-dispatch`, uncommitted on detached
  base `b174fb0cf6c7e8083d7f15fe0d67020255131794`.
- Hosted gate NOT RUN. The worker performed no network operations.
- Local regression and self-review logs are in `/private/tmp/deepsignal/cloud-verification-admission`.

## Done

- Isolated acceptance passed for two pins, launcher refusals, uncertain pushes, concurrent
  submissions and command receipts. Both legacy checks passed in owned fixtures.
- The [operator procedure](../tools/pipe2/CLOUD-VERIFICATION.md) compares observations
  of a real Mac job against the hosted `console-tests` start time.

## Tried and failed

Before the admission fix, the new tests reached the candidate launcher and hid both
refusals with an alternate state directory. The fake host reported success. Both
refusals and the installed policy checks now pass in fixtures.

## Next bounded task

After owner review and publication of the exact desk topic, run the [live overlap
procedure](../tools/pipe2/CLOUD-VERIFICATION.md#live-overlap-rehearsal) once
from the outer launcher. Stop when the procedure records PASS and the exact run URL,
or records a refusal or failed verification. Keep the evidence directory.

## Open questions

Owner review, actual hosted timing and sustained Actions capacity are pending.

## Do not

Use the reviewed launcher with the installed policy. Its canonical job claim and
the authorized Mac fixture use the normal admission rules. Production installation
is a separate decision.
