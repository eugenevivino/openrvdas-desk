# ProjectArchitect (PA3) review, 2026-11-18

Read-only. Repo Druthulu/ProjectArchitect, commit edcc2b0 (2026-11-16), version
3.32.19, cloned shallow and read, installer not run. Verified = read in the files.

## What it is (verified)
A Claude Code add-on (hooks, subagents, a plugin, a statusline, a local sqlite
ledger) that runs work as a plan: phases with a machine-checkable milestone,
plan approval by the human, one fresh "expert" per task, "retriever" helpers
that read long material and return short answers, and a plain-English recap at
phase close. Its own bench claims average context per request of 47k to 69k
tokens against 459k to 547k for one long vanilla session. Those figures are the
author's, not ours; inferred, not verified here.

## Good parts we took (D-PA1, rules 19 to 22)
1. Retrievers: `agents/retriever-digest.md` and `retriever-code.md`. Haiku-class,
   read, grep, glob, write only, answer under a line cap, `NOT FOUND` when out of
   scope, stop by the 20th tool call, optional report file.
2. Milestones a machine can check: `templates/GENERATION_PLAN.template.md`
   (`milestone:` per phase, "a command can go with it").
3. Ledger of cost per request, shown live in a statusline (`pa_ledger.py`,
   `pa_statusline.py`).
4. Plain-English recap at each phase close (`templates/PhaseEnd.template.md`).

## Security read (what we did not take, verified)
- `install.sh` runs `sudo apt-get install -y python3` if no Python 3.12, clones
  the repo into `~/.claude/pa3-src`, runs `pa_install.py --root`, which edits
  `~/.claude/settings.json` (backs it up) to add global hooks and a statusline.
- `pa/usage_api.py` reads `~/.claude/.credentials.json` and sends its OAuth bearer
  token to `https://api.anthropic.com/api/oauth/usage` (an undocumented endpoint
  with the `oauth-2025-04-20` beta header) to show plan usage. The token goes to
  Anthropic only, but it is a use of the login that Claude Code did not ask for.
- Optional external coders send prompts and code to OpenRouter on a new key.
- No sign of exfiltration to other hosts in the files I grepped. Not a full
  audit: the 38 MB of hooks, tests and plugin code were not read line by line.
Verdict: do not install; copy the ideas as rules and scripts of our own.
