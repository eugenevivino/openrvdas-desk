# Connecting engineering adapters

An adapter is a trusted executable invoked for one immutable job. It may wrap an existing build, test runner, independent review workflow, or approved merge train. Relay handles scheduling and durable handoffs. The adapter must establish the engineering truth of its result.

## Plan and identity

The demonstration writes a complete reference plan to its state directory's `plan.json`. Plans declare:

- `schema: 1`, `project`, `workspace`, `policy_version`, and `environment_id`.
- Named `capacities`, `max_parallel`, and named `adapters`.
- `pieces` with immutable `identity`, adapter name, and inputs.
- `modules` with all required pieces, assemble/test/review adapters, acceptance criteria, optional `depends_on`, and `compatibility_key`.
- A batch adapter, `max_size`, and `integration_mode`.

Each adapter declares an argv `command`, explicit `version`, timeout, resources, and actor. Optional settings include `approval_required`, `max_attempts`, `retry_exit_codes`, and priority. Module stages and batching require receipts. Assembly and review must name distinct actors; the reviewer cannot be a configured piece author. **Actor labels alone do not verify actual reviewer independence.** Your adapter must enforce that requirement.

Jobs are content-addressed from declared specifications and dependencies. Accepted identical jobs can be reused. This is not automatic semantic dependency inference. Declare exact source revisions or content hashes, relevant dependencies, acceptance-policy versions, environment identities, and adapter versions. A file changed without updating its declared identity can cause stale reuse. Adapters must verify declarations against the actual source and artifacts. Do not hash only a friendly branch name or mutable path.

## Invocation and input

Relay executes the argv list directly with `shell=False`, in the configured working directory, inheriting the local environment and setting:

| Variable | Meaning |
| --- | --- |
| `RELAY_INPUT_FILE` | Absolute `input.json` path |
| `RELAY_RESULT_FILE` | Absolute path for `adapter-result.json` |
| `RELAY_ATTEMPT_DIR` | Absolute directory for this attempt |

Do not put credentials into a plan or receipt. Keep adapter output free of secrets because stdout/stderr are retained in `output.log`.

The input object contains `schema`, `job_id`, `attempt`, monotonic fencing `token`, immutable `spec`, `dependencies`, and `input_digest`. `dependencies` maps each prerequisite ID to its **full stored worker result**; the validated adapter receipt is normally at `dependencies[id]["receipt"]`. Review receives assembly and test results. Batch receives reviewed module results.

`input_digest` is SHA-256 of canonical JSON excluding that field: sorted keys, compact separators, UTF-8, non-ASCII characters preserved, and non-finite numbers rejected. Copy the supplied digest into the receipt. It binds the receipt to this attempt, not merely to a module name.

## Required receipt

Write one JSON object to `RELAY_RESULT_FILE`, preferably through atomic replacement:

```json
{
  "schema": 1,
  "outcome": "pass",
  "input_digest": "COPY_FROM_INPUT",
  "summary": "Exact candidate passed the required checks",
  "evidence": ["test-report.json"],
  "data": {
    "candidate_commit": "EXACT_COMMIT",
    "artifact_sha256": "VERIFIED_ARTIFACT_HASH"
  }
}
```

`outcome` is `pass`, `fail`, or `blocked`; `summary` is a string; `evidence` is a list of existing paths; `data` is an object. Evidence paths are absolute or relative to the attempt directory. Data fields above are illustrative, not built-in verification.

Exit 0 alone cannot pass a receipt-required job. Relay validates schema, digest, field types, and evidence existence. **It does not interpret tests, hash evidence automatically, authenticate approvals, or prove review quality.** Implement those checks in reviewed adapters. Pass requires a valid passing receipt, exit 0, and no timeout or cancellation.

Assemble the declared pieces into an exact candidate; test that candidate; independently review it with its test evidence; batch-test the compatible candidates together. Preserve mandatory gates. A test-only adapter must not claim publication. Publishing or merging requires the already authorized project workflow and a receipt proving the actual result.
