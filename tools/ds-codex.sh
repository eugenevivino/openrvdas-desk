#!/bin/bash
# ds-codex: DeepSignal-only Codex launcher (D-SEP, Eugene 2026-11-18: DeepSignal and Kalon/l2audio are fully separate).
# Never calls or edits ~/bin/codex-run and never touches ~/.codex. Usage, from a folder under /private/tmp/deepsignal/:
#   ds-codex [--dry-run] [--sub-agents] [--wait-ram[=SECONDS]] -m <gpt-6.2-sol|gpt-6.2-astra|gpt-6-luna> [-c model_reasoning_effort=<level>] [codex exec args...] [-]
# Exit codes: 2 bad usage, 3 Astra without KALON_ALLOW_ASTRA=1, 4 full-access/bypass/write-widening refused,
#             6 model not allowed, 7 no -m, 8 connector guard refused, 9 cwd outside scratch, 10 another DeepSignal job holds the lock,
#             11 RAM gate: free RAM under 4 GB or swap used over 3.8 GB (defaults; DS_MIN_FREE_MB / DS_MAX_SWAP_MB /
#                DS_REQUIRE_PRESSURE1=1 override per machine), with --wait-ram: still so at the deadline.
set -u
DS_HOME="$HOME/.codex-deepsignal"
SCRATCH="/private/tmp/deepsignal"
LOCK="$SCRATCH/.ds-codex.lock"
CX="${DS_CODEX_BIN:-/opt/homebrew/bin/codex}"

# (a) Isolate the environment: our own Codex home, no Kalon or codex-run variables (KALON_ALLOW_ASTRA is the only opt-in honored).
astra_ok="${KALON_ALLOW_ASTRA:-0}"
for v in $(compgen -e); do case "$v" in KALON_*|CODEX_RUN_*|CODEX_HOME) unset "$v";; esac; done
export CODEX_HOME="$DS_HOME"
LOG="$DS_HOME/launch-log.txt"

die() { echo "ds-codex: REFUSED: $2" >&2; exit "$1"; }

# Parse our own flag and the model; copy everything else through.
dry=0; subs=0; waitram=0; model=""; effort="default"; prev=""; args=(); cds=()
for a in "$@"; do
  if [ "$a" = "--dry-run" ]; then dry=1; prev="$a"; continue; fi
  if [ "$a" = "--sub-agents" ]; then subs=1; prev="$a"; continue; fi
  if [ "$a" = "--wait-ram" ]; then waitram=3600; prev="$a"; continue; fi
  case "$a" in --wait-ram=*) waitram="${a#--wait-ram=}"; [[ "$waitram" =~ ^[0-9]+$ ]] || die 2 "--wait-ram=SECONDS needs a number"; prev="$a"; continue;; esac
  case "$prev" in
    -m|--model) model="$a";;
    -C|--cd) cds+=("$a");;
    -c|--config)
      case "$a" in
        model=*) die 7 "set the model with -m, not -c model=";;
        model_reasoning_effort=*) effort="${a#model_reasoning_effort=}"; effort="${effort//\"/}";;
      esac;;
  esac
  case "$a" in --model=*) model="${a#--model=}";; --cd=*) cds+=("${a#--cd=}");; esac
  args+=("$a"); prev="$a"
done

# (b) Model: explicit, allow-listed, Astra only with the opt-in.
[ -n "$model" ] || die 7 "rule 2: name the model with -m (gpt-6.2-sol, gpt-6.2-astra or gpt-6-luna)"
case "$model" in gpt-6.2-sol|gpt-6.2-astra|gpt-6-luna) ;; *) die 6 "model '$model' is not allowed (gpt-6.2-sol, gpt-6.2-astra, gpt-6-luna)";; esac
if [[ "$model" == *astra* && "$astra_ok" != 1 ]]; then die 3 "$model needs KALON_ALLOW_ASTRA=1 for this one approved job"; fi

# (c) Working folder must resolve under the DeepSignal scratch root, including any -C/--cd.
in_scratch() { local r; r=$(cd "$1" 2>/dev/null && pwd -P) || return 1; case "$r/" in "$SCRATCH"/*) return 0;; esac; return 1; }
in_scratch "$PWD" || die 9 "cwd $(pwd -P) is not under $SCRATCH/"
for d in "${cds[@]+"${cds[@]}"}"; do in_scratch "$d" || die 9 "-C $d is not under $SCRATCH/"; done

# (e) Safety: no full access, no bypass, no widening of writable paths, no profiles, no connectors.
# Multi-agent switches are off too: on 2026-11-18 a gpt-6.2-sol job spawned a gpt-6.2-astra xhigh sub-agent (bypassing the Astra opt-in).
GUARD_FEATURES=(apps plugins remote_plugin plugin_sharing enable_mcp_apps codex_apps_mcp_2026_07_28 browser_use browser_use_external browser_use_full_cdp_access computer_use in_app_browser multi_agent multi_agent_v2 multi_agent_v2_dynamic_tools multi_agent_mode enable_fanout runtime_agent_instances)
check_cfg() {
  local v="$1" k f g; k="${v%%=*}"; k="${k// /}"
  case "$k" in
    mcp_servers*|apps|apps.*|profile|profiles*|features|agents|agents.*|model_catalog_json) die 8 "config key '$k' is not allowed (ds-codex sets it)";;
    sandbox_workspace_write*|sandbox_mode|approval_policy) die 4 "config key '$k' is set by ds-codex, not the caller";;
  esac
  if [[ "$k" == features.* ]]; then
    f="${k#features.}"
    for g in "${GUARD_FEATURES[@]}"; do [ "$f" = "$g" ] && [[ "${v#*=}" != *false* ]] && die 8 "re-enabling $g is not allowed"; done
  fi
}
sandbox="workspace-write"; prev=""
for a in "${args[@]+"${args[@]}"}"; do
  case "$prev" in
    -c|--config) check_cfg "$a";;
    --enable) for g in "${GUARD_FEATURES[@]}"; do [ "$a" = "$g" ] && die 8 "--enable $g"; done;;
    -s|--sandbox) case "$a" in workspace-write|read-only) sandbox="$a";; *) die 4 "sandbox '$a' is not allowed";; esac;;
  esac
  case "$a" in
    --config=*) check_cfg "${a#--config=}";;
    -c?*) check_cfg "${a#-c}";;
    --enable=*) for g in "${GUARD_FEATURES[@]}"; do [ "${a#--enable=}" = "$g" ] && die 8 "--enable=$g"; done;;
    --sandbox=*) case "${a#--sandbox=}" in workspace-write|read-only) sandbox="${a#--sandbox=}";; *) die 4 "sandbox '${a#--sandbox=}' is not allowed";; esac;;
    -p|--profile|--profile=*|-p?*) die 8 "profiles are not allowed ($a)";;
    --add-dir|--add-dir=*) die 4 "--add-dir is not allowed";;
    --dangerously-bypass-approvals-and-sandbox|--dangerously-bypass-hook-trust|--full-auto|*danger-full-access*) die 4 "full-access or bypass flag $a";;
  esac
  prev="$a"
done

# (e) Connector guard, fail closed (logic copied from Kalon's codex-run, run against our own home).
feats=$("$CX" features list 2>/dev/null | awk '{print $1}')
for need in apps plugins; do printf '%s\n' "$feats" | grep -qx "$need" || die 8 "the installed CLI has no '$need' switch, so the connector guard cannot be applied"; done
dis=(); for f in "${GUARD_FEATURES[@]}"; do
  [ "$subs" = 1 ] && [ "$f" = multi_agent ] && continue   # --sub-agents re-enables only the v1 switch; v2 and the rest stay off
  printf '%s\n' "$feats" | grep -qx "$f" && dis+=(--disable "$f")
done

# --sub-agents (opt-in, default OFF; Eugene 2026-11-18): spawn_agent takes its own model and reasoning_effort and the
# [agents] defaults do not bind it, so the pin is a per-job model catalog (model_catalog_json): only the parent's model and
# the cheaper gpt-6-luna, each limited to efforts no higher than the parent's. Astra is in it only when the parent is Astra
# (which already needs KALON_ALLOW_ASTRA=1). Depth 1, at most 2 sub-agents at once, 15 min per sub-agent job.
# A sub-agent never counts as the independent review. After the job, every sub-agent session is audited and logged.
subcfg=()
if [ "$subs" = 1 ]; then
  CATDIR="$SCRATCH/.ds-codex-catalogs"; mkdir -p "$CATDIR"; CAT="$CATDIR/$(date -u +%Y%m%dT%H%M%SZ)-$$.json"
  cap=$(python3 -I - "$DS_HOME/models_cache.json" "$CAT" "$model" "$effort" <<'PY'
import json, sys
src, out, parent, eff = sys.argv[1:5]
order = ["minimal", "low", "medium", "high", "xhigh", "max", "ultra"]
ms = {m["slug"]: m for m in json.load(open(src))["models"]}
if parent not in ms: sys.exit("parent model not in the CLI model cache")
if eff == "default": eff = ms[parent].get("default_reasoning_level") or "medium"
if eff not in order: sys.exit("unknown effort " + eff)
keep = []
for slug in dict.fromkeys([parent, "gpt-6-luna"]):
    if slug not in ms: continue
    m = dict(ms[slug])
    m["supported_reasoning_levels"] = [l for l in m["supported_reasoning_levels"] if order.index(l["effort"]) <= order.index(eff)]
    if not m["supported_reasoning_levels"]: continue
    if m.get("default_reasoning_level") not in [l["effort"] for l in m["supported_reasoning_levels"]]:
        m["default_reasoning_level"] = m["supported_reasoning_levels"][-1]["effort"]
    keep.append(m)
json.dump({"models": keep}, open(out, "w"))
print(eff)
PY
  ) || die 8 "could not build the sub-agent model catalog (fail closed)"
  subcfg=(-c "model_catalog_json=\"$CAT\"" -c "agents.max_depth=1" -c "agents.max_concurrent_threads_per_session=2"
          -c "agents.default_subagent_model=\"$model\"" -c "agents.default_subagent_reasoning_effort=\"$cap\"" -c "agents.job_max_runtime_seconds=900")
fi
mcp_names() { "$CX" "$@" mcp list --json 2>/dev/null | python3 -I -c 'import sys,json; print("\n".join(s["name"] for s in json.load(sys.stdin) if s.get("enabled")))'; }
servers=$(mcp_names "${dis[@]}") || die 8 "MCP server list unreadable (fail closed)"
off=(); while IFS= read -r n; do [ -n "$n" ] && off+=(-c "mcp_servers.$n.enabled=false"); done <<< "$servers"
still=$(mcp_names "${dis[@]}" "${off[@]+"${off[@]}"}") || die 8 "MCP server list unreadable after overrides (fail closed)"
[ -z "$still" ] || die 8 "MCP servers still enabled after overrides: $still"

sb=(); [[ " ${args[*]+"${args[*]}"} " == *" -s "* || " ${args[*]+"${args[*]}"} " == *" --sandbox "* || " ${args[*]+"${args[*]}"} " == *"--sandbox="* ]] || sb=(--sandbox workspace-write)
cmd=("$CX" exec "${dis[@]}" "${off[@]+"${off[@]}"}" "${subcfg[@]+"${subcfg[@]}"}" -c 'approval_policy="never"' -c 'sandbox_workspace_write.writable_roots=[]' "${sb[@]+"${sb[@]}"}" "${args[@]+"${args[@]}"}")

# (i) RAM gate (shared-machine rule from Kalon, 2026-11-18): refuse unless free RAM >= 4 GB and swap used <= 3.8 GB.
# Available RAM (lead, 2026-11-18) = free + speculative + purgeable + file-backed pages, capped at physical RAM minus
# wired minus compressor-occupied pages (inactive is NOT added: file-backed already holds the inactive file cache and
# inactive anonymous pages are not freely reclaimable). Swap used from vm.swapusage. Every component is printed.
# Floors can be lowered per machine by the caller (the Mini's launch gate sets DS_MIN_FREE_MB=2048 DS_MAX_SWAP_MB=2457
# ); kernel pressure level 1 (normal) is required by default (DS_REQUIRE_PRESSURE1=1). Values must be plain integers.
RAM_MIN_FREE_MB=${DS_MIN_FREE_MB:-4096}; SWAP_MAX_USED_MB=${DS_MAX_SWAP_MB:-3891}; REQ_P1=${DS_REQUIRE_PRESSURE1:-1}
[[ "$RAM_MIN_FREE_MB" =~ ^[0-9]+$ && "$SWAP_MAX_USED_MB" =~ ^[0-9]+$ ]] || die 2 "DS_MIN_FREE_MB and DS_MAX_SWAP_MB must be integers"
ram_state() {
  local pg free_mb swap_mb
  pg=$(sysctl -n hw.pagesize)
  local comp; comp=$(vm_stat | awk -v pg="$pg" -v mem="$(sysctl -n hw.memsize)" '
    {v=$NF; gsub(/\./,"",v)}
    /^Pages free:/ {f=v} /^Pages speculative:/ {sp=v} /^Pages purgeable:/ {pu=v} /^File-backed pages:/ {fb=v}
    /^Pages wired down:/ {w=v} /^Pages occupied by compressor:/ {c=v}
    END {mb=pg/1048576; sum=(f+sp+pu+fb)*mb; cap=mem/1048576-(w+c)*mb; tot=(sum<cap)?sum:cap
         printf "%d free=%d speculative=%d purgeable=%d file_backed=%d sum=%d cap(RAM-wired-compressed)=%d", tot, f*mb, sp*mb, pu*mb, fb*mb, sum, cap}')
  free_mb=${comp%% *}
  swap_mb=$(sysctl -n vm.swapusage | sed -E 's/.*used = ([0-9.]+)M.*/\1/'); swap_mb=${swap_mb%.*}
  RAM_MSG="available_MB=$free_mb (min $RAM_MIN_FREE_MB) [MB: ${comp#* }] swap_used_MB=$swap_mb (max $SWAP_MAX_USED_MB) pressure_level=$(sysctl -n kern.memorystatus_vm_pressure_level)"
  [ "$free_mb" -ge "$RAM_MIN_FREE_MB" ] && [ "$swap_mb" -le "$SWAP_MAX_USED_MB" ] || return 1
  [ "$REQ_P1" != 1 ] || [ "$(sysctl -n kern.memorystatus_vm_pressure_level)" = 1 ]
}
if [ "$dry" = 1 ]; then ram_state && echo "ds-codex: RAM gate OK: $RAM_MSG" >&2 || echo "ds-codex: RAM gate would REFUSE (11): $RAM_MSG" >&2
elif ! ram_state; then
  [ "$waitram" -gt 0 ] || die 11 "RAM gate: $RAM_MSG (use --wait-ram[=SECONDS] to wait)"
  ram_deadline=$(( $(date +%s) + waitram )); echo "ds-codex: waiting for RAM (up to ${waitram}s): $RAM_MSG" >&2
  until ram_state; do [ "$(date +%s)" -ge "$ram_deadline" ] && die 11 "RAM gate still closed after ${waitram}s: $RAM_MSG"; sleep 30; done
  echo "ds-codex: RAM gate open: $RAM_MSG" >&2
fi

# (d) One DeepSignal job at a time: lock dir holding the owner PID; a lock whose PID is gone is stale and removed.
lock_held() { [ -d "$LOCK" ] || return 1; local p; p=$(cat "$LOCK/pid" 2>/dev/null); [ -n "$p" ] && kill -0 "$p" 2>/dev/null && { echo "$p"; return 0; }; return 1; }
if holder=$(lock_held); then die 10 "another DeepSignal Codex job holds $LOCK (pid $holder)"; fi
[ -d "$LOCK" ] && { echo "ds-codex: removing stale lock (pid $(cat "$LOCK/pid" 2>/dev/null || echo none) is gone)" >&2; rm -rf "$LOCK"; }

# (g) Dry run: print the exact command and stop (the lock is checked but not taken).
if [ "$dry" = 1 ]; then printf 'CODEX_HOME=%q' "$CODEX_HOME"; printf ' %q' "${cmd[@]}"; printf '\n'; exit 0; fi

mkdir "$LOCK" 2>/dev/null || die 10 "another DeepSignal Codex job took $LOCK just now"
echo $$ > "$LOCK/pid"
child=""
cleanup() { rm -rf "$LOCK"; rm -f "$SCRATCH/.ds-codex-start-$$"; }
on_signal() { [ -n "$child" ] && kill -TERM "$child" 2>/dev/null; wait "$child" 2>/dev/null; rc=$((128 + $1)); log_line "$rc"; cleanup; exit "$rc"; }
START_MARK="$SCRATCH/.ds-codex-start-$$"; : > "$START_MARK"
# Post-job audit: every session file written since launch that came from a sub-agent spawn, with the models and efforts it ran.
audit_subagents() {
  find "$DS_HOME/sessions" -name '*.jsonl' -newer "$START_MARK" 2>/dev/null | python3 -I -c '
import json, sys, collections
out = []
for f in sys.stdin.read().split():
    meta = {}; seen = collections.Counter()
    for l in open(f, errors="replace"):
        try: d = json.loads(l)
        except ValueError: continue
        p = d.get("payload", {})
        if d.get("type") == "session_meta" and not meta: meta = p
        elif d.get("type") == "turn_context": seen[(p.get("model"), p.get("effort"))] += 1
    if isinstance(meta.get("source"), dict) and "subagent" in meta["source"]:
        out.append(",".join("%s/%s" % k for k in seen) or "unknown")
print(";".join(out) or "none")'
}
log_line() {
  local sa; sa=$(audit_subagents)
  printf '%s\tmodel=%s\teffort=%s\tsandbox=%s\tsub_agents=%s\tsub_agent_models=%s\tcwd=%s\texit=%s\n' "$(date -u +%FT%TZ)" "$model" "$effort" "$sandbox" "$([ "$subs" = 1 ] && echo on || echo off)" "$sa" "$(pwd -P)" "$1" >> "$LOG"
  case "$sa" in none) ;; *) for x in ${sa//;/ }; do for y in ${x//,/ }; do
    case "${y%%/*}" in "$model"|gpt-6-luna) [ "$subs" = 1 ] || echo "ds-codex: WARNING: sub-agent ran ($y) although --sub-agents was off" >&2;;
      *) echo "ds-codex: WARNING: sub-agent ran on ${y%%/*}, not the parent model $model or gpt-6-luna" >&2;; esac; done; done;; esac
}
trap 'on_signal 14' ALRM; trap 'on_signal 15' TERM; trap 'on_signal 2' INT; trap 'on_signal 1' HUP

# (h) Run codex exec as a child (not exec) so the exit code is logged (f) and the lock is released.
# The explicit <&0 keeps our stdin (the piped prompt): without it bash gives a background job /dev/null.
"${cmd[@]}" <&0 &
child=$!
wait "$child"; rc=$?
log_line "$rc"; cleanup
exit "$rc"
