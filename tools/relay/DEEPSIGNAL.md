# DeepSignal Relay pilot

This adapts the supplied Relay controller. It does not replace the existing desk
supervisors. `UPSTREAM.json` records the archive hash and modified components.

Run with Python 3.12 from this directory. All project state and candidate files stay
under `/private/tmp/deepsignal`. Example:

```
python3.12 -m dsrelay pilot --root /private/tmp/deepsignal/relay-20261120/new-pilot
```

A passing test stage means only its declared checks passed. An incomplete/held run
exits 2. `report --state PATH` reads state without launching jobs. `run --plan PATH
--state PATH` resumes an existing immutable plan. Edit neither the runtime nor its
contracts while a controller or detached worker is using it. Runtime code changes
require compiling a new plan; immutable identities then invalidate affected jobs.

The adapter exports pinned Git sources, creates separate detached candidates and
copies existing lockfile dependencies into each. It hashes source, dependencies,
policy and evidence. Added source files and changed dependencies invalidate reuse.
Only named generated cache directories are excluded. Commands inherit a minimal
environment and a private HOME/TMPDIR. Tests use existing fixtures; no ship services,
production observations or MCP write tools are enabled by this integration.
Pytest's cache provider is disabled so acceptance tests do not add files to frozen
candidates. An optional Console build runs before the source manifest is sealed;
only generated distribution changes may enter its derived commit. Subsequent tests
and reviews bind to that derived commit, not merely its source parent.

Relay handles readiness, allocations within its budget, fenced execution, completion,
retry and immediate compatible batching. Local tests preserve the installed
DeepSignal RAM/heavy-job thresholds with a nonmutating sampler and compatible
execution claim. The launcher's destructive dry-run is never called. A complete
claim is published atomically without replacing a competing claim. Project-owned
SQLite observations reuse only fresh, same-boot swap measurements; they contain
no allocation or job state. Transient prelaunch resource
refusals wait for at most six minutes per attempt and use bounded exit-75 retries.
Engineering HOLDs never retry as infrastructure failures. Each worker and each test
log has an 8 MiB cap. Ambiguous worker liveness retains its reservation.

A batch can combine reviewed modules from the same exact candidate and execute the
union of their checks. Different candidates require explicit current-base assembly
and qualification first. No merge or release action is implemented here.

## Gates and current limits

Gate imports fail closed. No production passing-gate parser is qualified yet;
nonempty reviewer labels and a hand-written PASS cannot approve a module. Existing
HOLD and missing evidence become exact blockers and an inspectable review-request
record. That record is an outbox, not a claim that an AI review was dispatched.
Scientific changes require readable hashed independent-reference evidence and still
owe the governing independent scientific judgment.

Both real product workflows have run through this controller. Initial Console and
Stream Health frontend checks passed, with their actual review/integration holds
preserved. Console fixes and the Stream Health re-cut have separate exact source
and evidence. See the owning run directory's report and current project handoff.
The passing core fixture batch is not product integration credit.

Core regression command: `python3.12 -m unittest discover -s tests -v`.
Project regression command: `python3.12 -m unittest discover -s ds_tests -v`.
Tests cover bounded output, source/evidence mutation, held reviews, compatible
batch checks, atomic activation, detached-worker recovery and duplicate prevention.
Current evidence audits include Git identity, file modes and the copied dependency
tree. Invalid evidence blocks its affected graph while independent work proceeds;
read-only reports revalidate evidence. Completion and automatic retry are one
transaction, so a controller restart cannot strand an eligible retry.

The Kalon lead owns the only shared resource allocator. `dsrelay/capacity.py` is a
shadow client of its shared API, not another scheduler. Normal transport permits
read-only status only. Production mutations remain disabled until both project
hooks, trusted host reporters, fencing and cleanup evidence are independently
qualified. No authority production state, service or network listener is installed.
The Mini lightweight policy is a pinned call into the Kalon owner's common memory
implementation, with a 1 GiB floor and retained job-peak, pressure, swap, freshness
and reservation requirements. MacBook admission remains at 3 GiB. A staged client
policy result cannot grant execution. The owner must publish verified live policy
and compatible resources before the first Mini job runs.

Before production transfer: finish exact-candidate product checks and independent
reviews; qualify native gate import/dispatch; prove the real combined batch and
adapter restart/reuse; finish Linux checks; qualify host cleanup and shared leases;
then perform the existing owners' deliberate transfer. Existing supervisors retain
ownership until those requirements are met. This pilot is not unattended production.
The existing local directory/PID execution guard also needs verified recovery from
forced worker termination before ownership transfer. An ambiguous old claim stays
reserved; this implementation does not erase claims based only on elapsed time.
