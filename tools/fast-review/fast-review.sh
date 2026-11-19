#!/bin/bash
# D-FASTREV1 fast review round. Usage: fast-review.sh <unit> <fork-branch> <base-sha> <design-note.md> <out-dir>
# 1. Refuses unless the head has a GREEN self-check receipt (which includes a GREEN pre-review receipt).
# 2. Splits the diff by path into parts: logic, ui, install-security (empty parts are skipped).
# 3. Runs one Codex cloud reviewer per part in parallel, each writing only REVIEW-<part>.md, judged only against
#    the design note's acceptance tests plus the D-P1DEF1 list. First pass is Sol low; a part that flags
#    ESCALATE, and the install-security part always, gets an Astra pass.
# 4. Merges: HOLD if any part reports a blocking P1, else PASS. Tickets go to <out-dir>/tickets.md for
#    docs/TICKETS.md. Timings (queue, per part, merge, total) go to <out-dir>/timing.txt.
set -u
UNIT=$1; BR=$2; BASE=$3; NOTE=$4; O=$5; D=/private/tmp/deepsignal; mkdir -p "$O"; T0=$(date +%s)
W=$O/repo; rm -rf "$W"; git clone -q --filter=blob:none --single-branch --branch "$BR" https://github.com/eugenevivino/openrvdas "$W" || exit 1
for k in "gc.auto 0" "maintenance.auto false" "core.hooksPath $D/hooks"; do git -C "$W" config $k; done; git -C "$W" checkout -q --detach
H=$(git -C "$W" rev-parse --short HEAD)
if ! grep -q '^RESULT GREEN' "$D/receipts/self-check-$H.txt" 2>/dev/null; then
  echo "fast-review: REFUSED: no GREEN self-check receipt for $H (run self-check.sh first; D-FASTREV1)" | tee "$O/verdict.txt"; exit 7; fi
grep -q '^RESULT GREEN' "$D/receipts/pre-review-$H.txt" 2>/dev/null || { echo "fast-review: REFUSED: pre-review not GREEN for $H" | tee "$O/verdict.txt"; exit 7; }
files=$(git -C "$W" diff --name-only "$BASE" HEAD | grep -v '/dist/')
sec=$(echo "$files" | grep -E 'console/install/|/security/|^server/|nginx|supervisor|test_install|test/server/' )
ui=$(echo "$files" | grep -E '^contrib/deepsignal/console/src/|^contrib/deepsignal/test/console/' | grep -vE 'test_install')
logic=$(echo "$files" | grep -vxF -e "$sec" -e "$ui" 2>/dev/null | grep . )
note=$(cat "$NOTE"); T1=$(date +%s)
prompt() { # part, file list, extra
  cat <<EOP
FAST REVIEW (D-FASTREV1), part "$1" of unit $UNIT, fork branch $BR at $H (checked out). Review ONLY these files in
\`git diff $BASE..$H\`:
$2
Judge ONLY against (a) the design note below (its acceptance tests and its fixed target) and (b) the D-P1DEF1 list:
a P1 blocks only if it shows an operator wrong or misleading data with valid inputs in normal operation, is a security
or install-gate hole, or crashes or hangs on inputs the real CDS can produce. Everything else is a TICKET.
Machine checks already passed (tests, linters, scanners that are installed); do not repeat them, do not restyle code.
$3
Write REVIEW-$1.md with: a list of blocking P1s (each: file:line, one sentence, the valid input that triggers it,
VERIFIED or INFERRED); a list of TICKET lines (each line starting with "TICKET: "); then exactly one line
"ESCALATE: yes" if any security, concurrency or math question needs a stronger reviewer, else "ESCALATE: no";
then exactly one final line "Verdict: PASS" (no blocking P1) or "Verdict: HOLD". Under 40 lines. No em dashes.

## Design note
$note
EOP
}
review_part() { # part, files, model args, suffix
  local p=$1 fl=$2 args=$3 sfx=$4 t=$(date +%s)
  prompt "$p" "$fl" "${5:-}" > "$O/prompt-$p$sfx.md"
  CR_FILE="REVIEW-$p.md" CR_ARGS="$args" "$D/cloud-review.sh" "$BR" "$O/prompt-$p$sfx.md" "$O/REVIEW-$p$sfx.md" 2>> "$O/cloud.log"
  echo "$p$sfx $(( $(date +%s)-t ))s" >> "$O/timing-parts.txt"
}
SOL='-c model="gpt-6.2-sol" -c model_reasoning_effort="low"'; ASTRA='-c model="gpt-6.2-astra" -c model_reasoning_effort="high"'
: > "$O/timing-parts.txt"; parts=""
[ -n "$logic" ] && { review_part logic "$logic" "$SOL" "" & parts="$parts logic"; }
[ -n "$ui" ] && { review_part ui "$ui" "$SOL" "" & parts="$parts ui"; }
[ -n "$sec" ] && { review_part install-security "$sec" "$ASTRA" "" "This part is security code: read it as a security reviewer." & parts="$parts install-security"; }
wait; T2=$(date +%s)
for p in $parts; do  # escalation: a Sol part that asks for it gets one Astra pass
  [ "$p" = install-security ] && continue
  grep -qi '^ESCALATE: yes' "$O/REVIEW-$p.md" 2>/dev/null && { fl=$(eval echo "\$$p"); review_part "$p" "$fl" "$ASTRA" "-astra" "First-pass reviewer escalated this part." & }
done
wait; T3=$(date +%s)
verdict=PASS; : > "$O/tickets.md"
for p in $parts; do
  f="$O/REVIEW-$p.md"; [ -s "$O/REVIEW-$p-astra.md" ] && f="$O/REVIEW-$p-astra.md"
  v=$(grep -oE 'Verdict: (PASS|HOLD)' "$f" 2>/dev/null | tail -1); [ "$v" = "Verdict: PASS" ] || verdict=HOLD
  echo "$p: ${v:-no verdict} ($(basename "$f"))" >> "$O/parts.txt"
  grep -h '^TICKET: ' "$O"/REVIEW-$p*.md 2>/dev/null | sed "s/^TICKET: /- [$UNIT $p] /" >> "$O/tickets.md"
done
T4=$(date +%s)
{ echo "unit $UNIT head $H base $BASE"; echo "queue/setup $((T1-T0))s"; cat "$O/timing-parts.txt"; echo "first pass wall $((T2-T1))s"; echo "escalation wall $((T3-T2))s"; echo "merge $((T4-T3))s"; echo "total $((T4-T0))s"; } > "$O/timing.txt"
echo "Verdict: $verdict" > "$O/verdict.txt"; cat "$O/parts.txt" >> "$O/verdict.txt"
cat "$O/verdict.txt" "$O/timing.txt"
