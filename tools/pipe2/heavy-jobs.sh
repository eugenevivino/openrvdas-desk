#!/bin/bash
# Count heavy jobs machine-wide, every project (D-PIPE1 rule 8, D-PIPE1a). Read-only: reads `ps` and the pattern
# file, writes nothing but stdout. Usage: heavy-jobs.sh [--list]   prints the count (or the matching lines).
set -u
PS=${DS_HEAVY_PS:-ps}   # test hook: a ps stand-in (the guard test runs the counter in a sandbox that cannot exec setuid ps)
P=${DS_HEAVY_PATTERNS:-/private/tmp/deepsignal/heavy-patterns.txt}
re=$(grep -vE '^[[:space:]]*(#|$)' "$P" | paste -sd '|' -)
[ -n "$re" ] || { echo 0; exit 0; }
if [ "${1:-}" = "--list" ]; then $PS -axo pid=,command= | grep -E -- "$re" | grep -v -- 'heavy-jobs.sh'; exit 0; fi
$PS -axo command= | grep -E -- "$re" | grep -vc -- 'heavy-jobs.sh'
exit 0
