#!/bin/bash
# Non-math review in Codex cloud (D-WIP3 routing rule; the Mac runs only math reviews and work).
# Usage: cloud-review.sh <fork-branch> <prompt-file> <out-answer.md>
# Codex cloud returns only a diff, so the reviewer writes its whole review to REVIEW.md at the repo root and
# changes nothing else; any other path in the diff rejects the review. Uses the DeepSignal cloud env.
set -u
D=/private/tmp/deepsignal; BR=$1; PROMPT=$2; OUT=$3; RF=${CR_FILE:-REVIEW.md}   # D-FASTREV1: per-part review file name
CR_ARGS=${CR_ARGS:-}                                                   # extra codex cloud -c overrides (model, effort)
F=$(mktemp $D/cloud-review.XXXXXX); { cat $D/desk-main/briefs/cloud/_HEADER.md; echo; echo "READ-ONLY REVIEW TASK. Do not change any code or test. Write your complete review, and nothing else, to a new file $RF at the repository root. Create no other file."; echo; cat "$PROMPT"; } > "$F"
cd $D/cloud-logs || exit 1
out=$(CODEX_HOME=$HOME/.codex-deepsignal perl -e 'alarm 120; exec @ARGV' codex cloud ${CR_ARGS} exec --env deepsignal --branch "$BR" --attempts 1 "$(cat "$F")" 2>&1); rm -f "$F" error.log
id=$(echo "$out" | grep -oE 'task_e_[0-9a-f]+' | head -1); [ -n "$id" ] || { echo "cloud-review: submit failed: $out" >&2; exit 1; }
echo "cloud-review: submitted $id on $BR" >&2
until (CODEX_HOME=$HOME/.codex-deepsignal codex cloud status $id 2>/dev/null | head -1 | grep -qvE 'PENDING|RUNNING'); do sleep 60; done
diff=$(CODEX_HOME=$HOME/.codex-deepsignal codex cloud diff $id 2>/dev/null); rm -f error.log
others=$(echo "$diff" | grep -E '^\+\+\+ b/' | grep -v "^+++ b/$RF$")
if [ -n "$others" ]; then echo "cloud-review: REJECTED $id: the review changed other files: $others" > "$OUT"; exit 2; fi
echo "$diff" | awk -v rf="$RF" 'index($0, "+++ b/" rf)==1{f=1;next} f && /^@@/{next} f && /^\+/{print substr($0,2)}' > "$OUT"
[ -s "$OUT" ] || { echo "cloud-review: EMPTY review from $id" > "$OUT"; exit 3; }
echo "cloud-review: $id done ($(wc -l < "$OUT" | tr -d ' ') lines)" >&2
