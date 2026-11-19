# DeepSignal standing build rules (adopted 2026-11-18/19)

Copy-paste block for another chat. These rules govern every DeepSignal build.

1. **D-UNITS1, whole units.** Each module ships as one unit on its own branch: one build job of at most three slices, one review pass of at most two rounds on the whole diff, one approval mark, one gate, one merge. No new small-piece branches or tasks; pieces already in flight finish as they are and are folded into their unit.

2. **D-PIPE1, nine pipeline rules (adopted from Kalon's pipeline).** (1) Whole units only. (2) A finish line of five stamps per unit, each proven at the unit's current head: moved (on the integration branch), tested (unit and acceptance tests green), fixed (review passed with no open P1), in the app (served by the console or installed in the test fixture), tested in the app (a browser or black-box test passes against it). (3) Old small branches never block a unit; they are listed as superseded and retired after the unit lands. (4) Check a unit's prerequisites on the integration branch before starting it. (5) Launches never depend on a live chat session: one detached launcher runs approved jobs and takes a claim per job so two loops never launch the same job. (6) The gate of record is the unit's Linux CI job; local scripts are pre-checks. (7) Brief done-lines must work on macOS. (8) Shared machine: the heavy-job cap counts every project's jobs, and we never touch another project's jobs or folders. (9) Every snag gets a permanent guard and an incident line. **D-PIPE1a:** the cap is two heavy jobs machine-wide, and Kalon's running jobs count toward it; they are read from the process list only, never signalled or touched. Kalon still yields first, so DeepSignal only waits more.

3. **D-P1DEF1, what blocks.** A P1 blocks only if it shows an operator wrong or misleading data from valid inputs in normal operation, is a security or install-gate hole, or crashes or hangs on inputs the real data server can produce. Hardening for invalid inputs becomes a ticket. **D-UNITS1a and D-UNITS1b** were one-time exceptions that gave the console MVP two extra rounds past the two-round limit; there are no further exceptions.

4. **D-WIP3, three units in progress.** At most three units are in progress, all on the Nov 25 path: the console (pilot candidate and follow-ups), the security redesign, and the 24 h soak. Everything else is paused: nothing new launches for it, in-flight jobs finish, and the launcher refuses other units while all three slots are taken.

5. **Review routing.** Non-math reviews run in Codex cloud, read-only (the reviewer writes only its review file). The Mac runs only math reviews and build work.

6. **D-DESIGN1, design first.** Before Sol builds a unit, Astra writes a one-page testable design note: a fixed target, acceptance tests as commands, an out-of-scope list, prerequisites, and who judges. Sol builds against it and reviewers judge against it; a finding outside its scope is a ticket unless it meets D-P1DEF1. The launcher refuses a build for a unit with no design note; reviews and design-note jobs are exempt.

7. **Progress counts.** Progress is reported as three numbers computed by script from the unit manifest, never from PR or branch counts: LANDED (moved), QUALIFIED (tested and fixed) and FINISHED (all five stamps).
