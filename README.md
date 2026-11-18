# openrvdas-desk

The team desk for Eugene's OpenRVDAS work: how the agents are organized, what
they have decided, what they are building next, and the gate every change must
pass. The code lives in the fork `eugenevivino/openrvdas`. This repo never
ships upstream, so upstream pull requests stay clean.

Start with `AGENTS.md`, then `docs/OPERATING-SYSTEM.md`.

| Path | What it is | Size budget |
|---|---|---|
| `AGENTS.md` | The contract every agent reads first (Claude and Codex) | 200 lines |
| `CLAUDE.md` | Import shim for Claude Code | 10 lines |
| `docs/OPERATING-SYSTEM.md` | Architecture of the team: machines, roles, flow, gates, approvals | 400 lines |
| `docs/RULES.md` | Numbered standing rules from Eugene. Newest wins | 120 lines |
| `docs/DECISIONS.md` | Decision log, one entry per decision, IDs `D-<AREA><n>` | append only |
| `docs/ROADMAP.md` | Ranked work, phases, bold bets | 200 lines |
| `docs/CODEX.md` | How we use Codex: codex-run, model tiers, context hygiene, caps | 190 lines |
| `docs/BUILDERS.md` | Claude manages, Codex builds: split, models, local and cloud paths | 120 lines |
| `docs/USABILITY.md` | Usability checklist every module and screen passes (rule 26) | 80 lines |
| `docs/IDEAS.md` | Master list of every idea: status, phase, source | one row per idea |
| `docs/STATE.md` | Where things stand now. Rewritten, never appended | 60 lines |
| `docs/WORKLOG.md` | One line per finished item | append only |
| `docs/INCIDENTS.md` | One entry per break, stall, or rule change | append only |
| `briefs/` | Work units for builders (`TEMPLATE.md`) | one file per unit |
| `handoffs/` | Lead briefs between sessions (`LEAD_BRIEF_TEMPLATE.md`) | one file per handoff |
| `research/` | Research desk outputs, dated | one file per question |
| `gate/` | The test gate that runs on the Mac Mini | code plus locking test |
| `mini/SETUP.md` | One-time Mini setup runbook | |

Size budgets are rules, not hopes. A file over budget gets split or summarized
in the same change that pushed it over. The Kalon desk taught this lesson:
state files that only grow (300 KB and up) stop being read.
