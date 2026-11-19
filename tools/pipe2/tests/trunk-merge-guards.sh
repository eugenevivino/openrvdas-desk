#!/bin/bash
# The shared pre-push hook refuses a unit push that merges trunk history and allows landing a unit on trunk.
set -u; D=/private/tmp/deepsignal; T=$(mktemp -d $D/hooktest.XXXX); cd $T
git init -q --bare origin.git && git clone -q origin.git w 2>/dev/null && cd w && git config core.hooksPath $D/hooks && git config user.email t@t && git config user.name t
git commit -q --allow-empty -m base && git push -q origin HEAD:refs/heads/main && git checkout -q -b deepsignal/unit && git commit -q --allow-empty -m u1 && git push -q origin deepsignal/unit
git checkout -q main && git commit -q --allow-empty -m m2 && git push -q origin main && git checkout -q deepsignal/unit && git merge -q --no-ff -m "merge main into unit" main
if git push -q origin deepsignal/unit 2>/dev/null; then echo "FAIL a trunk merge into a unit was pushed"; exit 1; else echo "PASS trunk merge into a unit refused"; fi
git checkout -q main && git merge -q --no-ff -m land deepsignal/unit~1 && git push -q origin main && echo "PASS landing a unit on trunk allowed" || { echo "FAIL landing refused"; exit 1; }
