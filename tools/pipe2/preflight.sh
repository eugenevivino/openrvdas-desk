#!/bin/bash
# D-PIPE2 preflight: check a brief's declared needs in about 2 minutes, before any claim or slot is taken.
# Usage: preflight.sh <brief-or-prompt.md> [repo-dir]    exit 0 = ready, 2 = no needs block, 3 = a need is not met.
# The brief starts with a front-matter block:
#   ---
#   needs:
#     network: no            (yes means github.com must answer within 10 s)
#     tools: python3.12, git (each must be on PATH)
#     disk_gb: 2             (free GB on the data volume after the 5 GB storage floor)
#     ram_gb: 3              (available RAM in GB)
#     required_files: contrib/deepsignal/security/cds_gateway.py   (relative to the repo dir, or absolute)
#   ---
set -u
B=$1; REPO=${2:-.}
[ "$(head -1 "$B")" = "---" ] || { echo "preflight: no needs block at the top of $B (D-PIPE2)"; exit 2; }
blk=$(awk 'NR==1{next} /^---$/{exit} {print}' "$B")
echo "$blk" | grep -q '^needs:' || { echo "preflight: front matter has no needs: key (D-PIPE2)"; exit 2; }
val() { echo "$blk" | sed -nE "s/^[[:space:]]+$1:[[:space:]]*(.*)$/\1/p" | head -1 | sed -E 's/[[:space:]]*#.*$//; s/^\[//; s/\]$//'; }
fail=""
for t in $(val tools | tr ',' ' '); do command -v "$t" > /dev/null 2>&1 || fail="$fail; tool $t missing"; done
dg=$(val disk_gb); if [ -n "$dg" ]; then free=$(df -g /System/Volumes/Data | awk 'NR==2{print $4}'); [ $((free-5)) -ge "${dg%.*}" ] || fail="$fail; disk ${free} GB free leaves less than ${dg} GB above the 5 GB floor"; fi
rg=$(val ram_gb); if [ -n "$rg" ]; then
  pg=$(vm_stat | awk '/page size of/{print $8}'); av=$(vm_stat | awk -v p="${pg:-16384}" '/Pages (free|inactive|speculative)/{gsub(/\./,"",$NF); s+=$NF} END{printf "%d", s*p/1073741824}')
  [ "$av" -ge "${rg%.*}" ] || fail="$fail; RAM ${av} GB available, need ${rg}"; fi
for f in $(val required_files | tr ',' ' '); do case "$f" in /*) p=$f;; *) p=$REPO/$f;; esac; [ -e "$p" ] || fail="$fail; required file $f missing"; done
case "$(val network)" in yes|true) perl -e 'alarm 10; exec @ARGV' curl -sI https://github.com > /dev/null 2>&1 || fail="$fail; network needed but github.com did not answer";; esac
[ -z "$fail" ] && { echo "preflight: ready"; exit 0; }
echo "preflight: NOT READY${fail}"; exit 3
