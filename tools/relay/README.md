# Kalon Relay

Relay is a small deterministic coordinator for **pieces → module assembly → tests → independent review → compatible integration batches**. Python makes scheduling decisions; it does not ask an AI lead to authorize each routine handoff. Your configured adapters perform the engineering work and produce evidence.

This package is implemented and tested with executable fixtures. It has **not been connected to l2audio, qualified production modules, or been tested on a Mac**. The fixture review is a structural demonstration, not production review. Existing project requirements, required independent reviews, and merge protections remain in force.

## Run the demonstration

Requires Python 3.10+ and a local Linux or macOS machine. It uses the standard library; no `pip install` is needed. From the extracted package directory:

```bash
python3 -m relay --state ./demo-state demo
python3 -m relay --state ./demo-state status
python3 -m unittest discover -s tests -v
```

The demo builds four actual Python pieces, assembles two modules, checks their behavior, performs fixture reviews, and tests available compatible modules in integration batches. Source artifacts and evidence remain in `demo-state/attempts/`; `demo-state/demo-report.json` records the outcome. It does not publish, merge a repository, modify your normal player, or require credentials.

Repeat the same demo command to reuse its accepted job identities. Changing a declared input creates a different identity. See [ADAPTERS.md](ADAPTERS.md) before connecting real work.

## Operate a project queue

```bash
python3 -m relay validate project-plan.json
python3 -m relay --state ./project-state submit project-plan.json
python3 -m relay --state ./project-state run
python3 -m relay --state ./project-state status --json
python3 -m relay --state ./project-state events --limit 30
```

`run` drains safely runnable work and returns when quiescent. Exit code 0 means all recorded jobs passed; 2 means unresolved work or an error. A successful test-only integration adapter produces `batch_tested`, not a claim that a release shipped.

For ongoing operation, use `run --watch` under your existing service manager. This is a foreground controller, not an installed launchd/systemd service. It can keep dispatching without a conversation, but cannot run while its host is asleep or unavailable.

Use one stable local state directory per project. Keep the SQLite database, plan, and attempt files together. One controller holds the state directory's lock. Resource capacities apply to that controller's queue, not to every program on the machine. Partition budgets explicitly when two projects share a Mac.

The plan declares adapters, source identities, module membership, required stages, capacities, and batch compatibility. A module must assemble and pass its test and review stages before batching. Batches contain currently eligible compatible modules, up to `max_size`; there is no minimum-fill wait. The required `integration: 1` resource serializes integration. A failed batch retains its membership for diagnosis rather than being silently retried or marked accepted.

## Approval, failure, and recovery

Copy exact job IDs from `status`:

```bash
python3 -m relay --state ./project-state approve JOB_ID --actor OWNER --note "Verified required authorization"
python3 -m relay --state ./project-state cancel JOB_ID
python3 -m relay --state ./project-state retry JOB_ID --note "Diagnosed transient failure"
```

Approval records a decision; it does not authenticate the actor or bypass external authorization. Cancellation is a durable request. A running controller delivers it to the verified supervisor; restart the controller if it is stopped. Retry accepts terminal failed jobs only and cannot exceed `max_attempts`. Automatic retries require explicitly listed exit codes.

Stopping the controller leaves detached worker supervisors running. Each supervisor owns its command's timeout, output, heartbeat, and terminal receipt. Restart with the same state directory. Relay imports matching completed results first, then observes workers with fresh heartbeats and verified process identity.

Expired leases never authorize duplicate execution. Missing or unverifiable liveness produces `uncertain`, retaining the resource reservation. Do not delete state or resubmit the work under another identity to bypass uncertainty. Diagnose the original attempt; a later valid terminal result can resolve that same attempt. Relay deliberately provides no automatic retry of uncertain work.

## Read the measurements honestly

`eligible_to_claim_s` measures recorded readiness to controller claim, including approval wait where applicable. It is not worker launch latency. `dependency_finish_to_worker_start_s` measures the interval from the latest prerequisite supervisor's completion to the next supervisor's start, including result collection and dispatch. The supervisor starts just before launching its configured command. `stage_wall_s` includes claim through imported completion. These measurements do not prove all machine time was idle or that an entire release is qualified.

`complete` describes the active plan. `history_complete` also includes retained obsolete failures. Correcting an integration adapter can require a new batch while preserving still-applicable module reviews; the old failed receipt remains visible.

Adapters are trusted local programs with the launching user's access. `shell=False` prevents implicit shell parsing, not malicious program behavior. Process-group cleanup covers ordinary descendants; children deliberately creating new sessions require external containment.
