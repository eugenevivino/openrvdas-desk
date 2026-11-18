# Brief: deepsignal-app-ia (full app page inventory, IA and first-draft mockups)

- Asked by Eugene 2026-11-18 08:34Z: "Get Astra to start working on some first-draft mockups of various pages. To list what pages we'll even need for this full app. How it should be organized. Use principles from impeccable.style."
- Lane: mac, `~/bin/ds-codex -m gpt-6.2-astra`, effort high, workspace-write, fresh session, under 40 turns. Scratch `/private/tmp/deepsignal/app-ia/` only.
- Output branch: `deepsignal/app-ia` on the fork, created from `deepsignal/console-contract`. Docs and static HTML only, under `contrib/deepsignal/design/app-ia/`. No code in `contrib/deepsignal/console/`.

## Inputs (the lead places these in the scratch dir; Codex has no network)
- `impeccable/`: the Impeccable skill text already installed for the console (4.8.0), plus a saved text copy of https://impeccable.style/ fetched by the lead. Read it first and apply its principles. Where it conflicts with DESIGN.md, DESIGN.md wins.
- `DESIGN.md`: the console rulebook v1, v2 and v3 visual gate. `CONTRACT.md`: the plugin contract.
- `mockup.html`: the current console mockup. Reuse its look: tokens, type, three lighting modes, one-click Night with red as the default.
- `IDEAS.md`, `ROADMAP.md`, `TARGET-PARITY.md` and `DECISIONS.md` from desk main.
- `USER-JOURNEYS.md`, if it exists by then.

## Step 1: `IA.md` (information architecture)
1. A complete page inventory for the full DeepSignal app. For each page give: id, name, who uses it (bridge, tech, science, shore, admin), the one job it does, the main content, its data source (cache field, ServerAPI, module), the IDEAS numbers it serves, and its status (MVP built, briefed, or new).
2. It must cover at least these areas:
   - The console MVP pages: Bridge, Science, Health, Self-test, auto pages and Map.
   - Instruments and loggers: list, detail, add, swap, calibrate, and the instrument history log.
   - QARTOD quality: test config, flags review, corrections approve and roll back, and the drift report.
   - Link health and serial device servers (#156 and #157).
   - Ship systems and seismic (#138 to #160).
   - EEZ and clearance (#137).
   - The scoreboard (designer and preview).
   - The MCP and AI assistant, including the API key setting.
   - The setup wizard and first light (D-SETUP1: 10 minutes or less, 3 actions or fewer).
   - Config and instrument profiles.
   - The OpenVDM, Sealog and Grafana integrations.
   - Admin and security: users, roles, API keys, audit log.
   - The protected-species view.
   - Alerts history, the event log, the shore view, and settings.
3. Organization:
   - Top-level navigation of 5 to 7 groups, named the way crews talk.
   - A sitemap tree.
   - Persona start pages.
   - How a user moves between groups.
   - The global chrome: alert banner, connection pill, Night, search or command palette.
   - Where read-only monitoring ends and actions that change things begin. Changes ask once, say what will change, and can be undone.
4. The top 10 tech journeys as page paths. For example: add an instrument, recover a dead sensor, calibrate, first light, a link drop, and a disk filling up. Mark any step that has no page as GAP.
5. Keep it under 400 lines, as tables and a tree. No essay.

## Step 2: first-draft mockups (static HTML, no external assets)
- 8 to 10 key pages, one self-contained HTML file each, built in the same style as `mockup.html`. Every page has the Day, Dusk, Night red and Night neutral switch and one-click Night, uses only design tokens, and shows realistic sample data marked as sample.
- Priorities:
  - App home or navigation shell.
  - Instruments list and instrument detail with calibration history.
  - Add-instrument wizard step.
  - Setup wizard first light.
  - QARTOD flags review.
  - Link health and serial device servers.
  - Alerts history.
  - Scoreboard designer.
  - AI assistant panel with the key-not-set state.
  - Admin roles.
- `index.html` links every mockup and the IA.
- Apply the V1 to V3 visual gate yourself (tokens, type scale, 4 px spacing) and note any exception.

## Report (under 40 lines)
Files written, the page count by group, the 5 biggest open questions for Eugene, and anything uncertain, with verified claims kept separate from inferred ones.
