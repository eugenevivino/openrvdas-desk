# Machine-wide heavy-job cap (D-PIPE1 rule 8, D-PIPE1a)

Installed copies live in `/private/tmp/deepsignal/` on the MacBook; these are the desk copies.

- `heavy-patterns.txt`: the one list of process patterns that count as a heavy job, any project (codex exec,
  xcodebuild, swift-build). Edit here, then copy to the Mac.
- `heavy-jobs.sh`: prints the machine-wide count (`--list` shows the matches). Read-only: process list only.
- `test-heavy-jobs-guard.sh`: guard test. Runs the counter in a macOS sandbox that denies writes outside
  `/private/tmp/deepsignal` and signals to other processes, plus a negative control and a static check.
- Gates: `~/bin/ds-codex` exits 12 (or waits with `--wait-ram`) when the count reaches `DS_HEAVY_CAP` (default 2);
  `ds-launch-when-ok.sh` waits while the count is at the cap. Kalon still yields first; DeepSignal only waits more.
