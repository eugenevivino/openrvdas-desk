#!/bin/bash
# Lead push guard (D-PIPE1 rule 9, incident 2026-11-18 22:43Z): flake8 on contrib/deepsignal must be clean before a
# manual push from a fork checkout. Usage: lead-push.sh <repo> <refspec>
set -u
R=$1; SPEC=$2; PY=/private/tmp/deepsignal/console-core/venv/bin/python
if [ -d "$R/contrib/deepsignal" ]; then
  out=$(cd "$R" && $PY -m flake8 --config .flake8 contrib/deepsignal 2>&1) || { echo "lead-push: flake8 not clean, not pushed:"; echo "$out" | head -5; exit 1; }
fi
# D-PIPE2 rule 9: never merge trunk into a unit branch
src=${SPEC%%:*}; dst=${SPEC#*:}; [ "$dst" = "$SPEC" ] && dst="refs/heads/$SPEC"
/private/tmp/deepsignal/trunk-merge-check.sh "$R" "$(git -C "$R" rev-parse "$src")" "$dst" || exit 1
git -C "$R" push -q origin "$SPEC"
