#!/bin/bash
# mac-build.sh <slug> <model> <effort>   (brief at /private/tmp/deepsignal/p2-<slug>/brief.md, clone in .../repo)
# Builds one Mac-lane module with ds-codex (behind the lock and RAM gate), then runs the brief's acceptance
# commands itself, then commits and pushes deepsignal/p2-<slug> ONLY if every command passed. Logs to mac-builds.log.
set -u
s=$1; model=$2; effort=$3; rerun=0; [ "${4:-}" = "--rerun-skipped" ] && rerun=1
# D-PIPE2: --rerun-skipped reruns only the failed or skipped acceptance commands recorded in the job receipt
# (no new Codex job), then commits and pushes if all now pass.
D=/private/tmp/deepsignal; W=${MB_DIR:-$D/p2-$s}; R=${MB_REPO:-$W/repo}; BR=${MB_BRANCH:-deepsignal/p2-$s}; LOG=$D/mac-builds.log
[ -e "$W/.skip" ] && [ "${MB_FORCE:-0}" != 1 ] && { echo "$(date -u +%TZ) $s: SKIPPED (already run out of order; marker $W/.skip)" >> $LOG; exit 0; }
PY=$D/console-core/venv/bin/python; [ -x "$PY" ] || PY=/opt/homebrew/bin/python3.12
n_acc=$(awk '/^## Acceptance/{f=1;next} /^## /{f=0} f && /^(python3\.12|python3|flake8|node|npm|npx) /' "$W/brief.md" | wc -l | tr -d ' ')
if [ "$n_acc" = 0 ]; then echo "$(date -u +%TZ) $s: NOT LAUNCHED (brief has 0 acceptance commands under a line-start ## Acceptance heading)" >> "$LOG"; exit 1; fi   # D-PIPE1 rule 9 guard
{ cat "$W/brief.md"; cat <<'EOF'

## Instructions for this job (from the lead)
- Do not spawn sub-agents. Work only inside the brief's Scope. Write the failing tests first, run them and show RED, then
  implement until the brief's acceptance commands pass. Use /opt/homebrew/bin/python3.12 (PYTHONDONTWRITEBYTECODE=1).
  flake8 7.5.0 is at /private/tmp/deepsignal/console-core/venv/bin/python -m flake8. For node work, node_modules is
  already installed in contrib/deepsignal/console.
- Edit files only: no git commit, push or other git writes; no network; no installs.
- Report under 40 lines: files changed, test names, RED then GREEN tails, design points you disagree with,
  VERIFIED separate from INFERRED. No em dashes.
EOF
} > "$W/prompt.md"
rundir=$(grep -m1 '^## Acceptance' "$W/brief.md" | sed -nE 's/.*from `?(contrib\/[A-Za-z0-9_.\/-]+)`?.*/\1/p'); wd="$R/${rundir:-.}"
if [ -f "$wd/package.json" ] && [ ! -d "$wd/node_modules" ]; then (cd "$wd" && npm ci --no-audit --no-fund > "$W/npm-ci.log" 2>&1) || { echo "$(date -u +%TZ) $s: npm ci FAILED" >> "$LOG"; exit 1; }; fi
# D-PIPE2 pinned HEAD: the job is bound to the branch head it was cloned at; it refuses to run (or push) if the
# remote branch head has moved.
PIN=$(git -C "$R" rev-parse HEAD); RCPT=$D/receipts/job-$s.tsv; mkdir -p $D/receipts
remote_head() { git ls-remote https://github.com/eugenevivino/openrvdas "refs/heads/$BR" | cut -f1; }
if [ "$rerun" = 0 ]; then
  rh=$(remote_head); [ -z "$rh" ] || [ "$rh" = "$PIN" ] || { echo "$(date -u +%TZ) $s: NOT LAUNCHED (pinned head ${PIN:0:7} but $BR is now ${rh:0:7}; re-cut the job, D-PIPE2)" >> "$LOG"; exit 1; }
echo "$(date -u +%TZ) $s: START $model $effort (pinned ${PIN:0:7})" >> "$LOG"
env_astra=(); [[ "$model" == *astra* ]] && env_astra=(env KALON_ALLOW_ASTRA=1)
${env_astra[@]+"${env_astra[@]}"} "$D/ds-launch-when-ok.sh" "$R" "$W/prompt.md" "$W/run.log" 14400 -- -m "$model" -c "model_reasoning_effort=$effort" --output-last-message "$W/answer.md" - >> "$LOG" 2>&1
else echo "$(date -u +%TZ) $s: RERUN of failed or skipped acceptance from $RCPT" >> "$LOG"; fi
cmds=$(awk '/^## Acceptance/{f=1;next} /^## /{f=0} f && /^(python3\.12|python3|flake8|node|npm|npx) /' "$W/brief.md")
export PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/private/tmp/deepsignal/shims${PYTHONPATH:+:$PYTHONPATH}; ok=0; tot=0
prev=""; [ "$rerun" = 1 ] && [ -f "$RCPT" ] && prev=$(cat "$RCPT"); : > "$RCPT.new"
while IFS= read -r c; do
  [ -z "$c" ] && continue; tot=$((tot+1))
  if [ "$rerun" = 1 ] && printf '%s\n' "$prev" | awk -F'\t' -v c="$c" '$1=="passed" && $3==c{f=1} END{exit !f}'; then
    ok=$((ok+1)); printf 'passed\t0\t%s\n' "$c" >> "$RCPT.new"; echo "    [kept passed] $c" >> "$LOG"; continue; fi
  cc=${c/#python3.12 /$PY }; cc=${cc/#python3 /$PY }; cc=${cc/#flake8 /$PY -m flake8 }; cc=${cc/ -m pytest / -m pytest -p no:cacheprovider }
  cdir="$wd"; case "$c" in python*|flake8*) cdir="${R:-$A/repo}";; esac
    out=$(cd "$cdir" && perl -e 'alarm 900; exec @ARGV' bash -c "$cc" 2>&1); rc=$?; [ $rc = 0 ] && ok=$((ok+1))
  printf '%s\t%s\t%s\n' "$([ $rc = 0 ] && echo passed || echo failed)" "$rc" "$c" >> "$RCPT.new"
  echo "    [$rc] $c :: $(echo "$out" | grep -E 'Ran [0-9]+|passed|failed|OK|FAILED|Error|Tests ' | tail -2 | tr '\n' ' ' | cut -c1-160)" >> "$LOG"
done <<< "$cmds"
mv "$RCPT.new" "$RCPT"
changed=$(git -C "$R" status --porcelain -uall | grep -vE 'node_modules/|/dist/|__pycache__' | awk '{print $2}')
rh=$(remote_head); if [ -n "$rh" ] && [ "$rh" != "$PIN" ]; then echo "$(date -u +%TZ) $s: NOT PUSHED (pinned head ${PIN:0:7} but $BR moved to ${rh:0:7} during the job; re-cut onto the tip, D-PIPE2)" >> "$LOG"; exit 1; fi
if [ "$tot" -gt 0 ] && [ "$ok" = "$tot" ] && [ -n "$changed" ]; then
  for p in $changed; do git -C "$R" add -- "$p"; done
  git -C "$R" commit -q -m "DeepSignal: $s (Mac build, $model $effort)

Built by Codex via ds-codex on the MacBook from desk brief $(basename "$W")/brief.md. Lead acceptance:
all $tot acceptance commands rc 0. Needs the fresh read-only review.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" && git -C "$R" push -q origin "HEAD:refs/heads/$BR" \
  && echo "$(date -u +%TZ) $s: PUSHED $(git -C "$R" rev-parse --short HEAD) ($ok/$tot acceptance)" >> "$LOG"
else
  echo "$(date -u +%TZ) $s: NOT PUSHED ($ok/$tot acceptance rc 0; changed files: $(echo "$changed" | wc -l | tr -d ' ')); lead decides" >> "$LOG"
fi
