# Brief: console `install` (one-command install and self-test page)

- Decision: D-CONSOLE1, MVP #1 item d ("stable integration into OpenRVDAS"). Risk tier: medium (edits nginx config on a ship server). Module id: `self-test`

## Goal
A tech installs the console on a ship server with one command, then opens one page that proves it is connected.

## Build
- `contrib/deepsignal/console/install/install.sh` (bash, POSIX tools only):
  - Flags: `--openrvdas-root` (default `/opt/openrvdas`), `--nginx-conf` (auto-detected: `/etc/nginx/sites-enabled/openrvdas.conf` on Ubuntu, `/etc/nginx/conf.d/openrvdas.conf` on RHEL; if neither exists, stop and say which paths were checked), `--dry-run`, `--uninstall`.
  - Inserts this block once, between `# BEGIN deepsignal-console` and `# END deepsignal-console` markers, inside the existing `server {` block. It is idempotent: a second run changes nothing.
    ```
    location /console/ {
        alias <openrvdas-root>/contrib/deepsignal/console/dist/;
        try_files $uri $uri/ /console/index.html;
    }
    ```
  - Makes a timestamped backup first, runs `nginx -t`, and restores the backup automatically if the test fails. Reloads with `systemctl reload nginx` (or prints the command with `--no-reload`).
  - Prints what it did in plain English and the URL to open.
  - Never touches any other part of the config.
  - `--uninstall` removes only the marked block.
  - Needs root for the real run; with `--dry-run` it prints the diff only.
- Route `self-test`, titled "Self-test", order 95. It shows:
  - Pass/fail rows (word + shape): connected to the cache (URL), number of fields, number of loggers in `status:logger_status`, cruise mode, newest record age, and whether the page files loaded (with any problems).
  - Night palette check: shows the current tokens.
  - A "Copy report" button that copies plain text (falls back to selecting the text).
- D-SETUP1 (desk DECISIONS): first light in 10 minutes or less with 3 or fewer actions. The docs show exactly 3: run install.sh, open http://<server>/console/, read the self-test page. Time a cold run of the script (it must finish in under 2 minutes on a normal ship server) and report it.
- Docs `docs/install.md`: Turn it on in 5 minutes, how to see it working, how to turn it off, and what it does NOT do (it does not change OpenRVDAS, loggers or supervisord).

## Tests first
- `contrib/deepsignal/test/console/test_install.py` (pytest, no root): runs `install.sh` against temp copies of an Ubuntu-style and a RHEL-style nginx conf, with a stub `nginx` on PATH that passes or fails. It covers:
  - Insertion inside `server {`.
  - Idempotence.
  - Backup and restore when `nginx -t` fails.
  - `--dry-run` writes nothing.
  - `--uninstall`.
  - A missing conf gives the plain message.
- `selfTest.test.tsx`: rows for connected and disconnected, zero loggers, a page problem, and copy text.

## Scope
`contrib/deepsignal/console/install/**`, `contrib/deepsignal/console/src/modules/self-test/**`, `contrib/deepsignal/console/docs/install.md`, `contrib/deepsignal/test/console/test_install.py`.

## Extra acceptance (from repo root)
```
python3 -m pytest contrib/deepsignal/test/console/test_install.py -v && flake8 contrib/deepsignal/test/console/test_install.py && bash -n contrib/deepsignal/console/install/install.sh
```

## Rules every console task follows

Read these files in the repository first: `contrib/deepsignal/console/CONTRACT.md`, `contrib/deepsignal/console/src/contract/index.ts`, `contrib/deepsignal/console/DESIGN.md` (the "Rulebook v2 additions" section wins over v1 where they differ). The contract is fixed: never edit `src/contract/**` or `CONTRACT.md`. If the contract blocks you, stop and say exactly what you need.

Ownership: you own ONLY the paths listed under Scope. Everything else is read-only, in particular `src/registry.ts`, `src/App.tsx`, `src/main.tsx`, `src/cds.ts`, `src/store.ts`, `src/lighting*.ts`, `src/pages.ts`, `src/index.css`, `index.html`, `package.json`, `package-lock.json`, `vite.config.ts`, `tsconfig*.json`, `.oxlintrc.json`, `DESIGN.md`, `README.md`, `public/**`, `dist/**`, `demo_cache.py`, `contrib/deepsignal/configs/**`, other modules' folders, and `contrib/deepsignal/test/console/test_console_live.py`. No new dependency of any kind.

Your module is `src/modules/<id>/index.ts` default-exporting a `ConsoleModule` (types in the contract). Core discovers it by glob; do not register it anywhere. If core's registry is not on your branch yet, that is expected: your tests import your module directly.

Tests: Vitest on jsdom, beside your code (`src/modules/<id>/*.test.ts(x)`). Build a minimal fake `ConsoleContext` inside your own folder (for example `src/modules/<id>/testkit.ts`) from `src/contract/fake-feed.json`, with a fake clock you step. Cover every behavior named in this brief. Use only `ctx.clock.now()` for time.

Screens: word + shape for every state, color third; tokens only (`--bg --panel --panel2 --line --fg --muted --accent --ok --check --stale --down --chart --grid` and fonts `--f-number --f-body --f-mono`), never literal colors; canvas/SVG read tokens at draw time and redraw on `ctx.lighting.subscribe`; Night must never paint a light surface (empty, loading and error states included); plain English, units always shown; touch targets at least 44 px; bridge sizes: primary value 48 px, labels at least 18 px, metadata at least 16 px; render all data as text (no `innerHTML`, no `dangerouslySetInnerHTML`, no `eval`).

Browser checks: Chromium does not run in this sandbox. If the brief asks for a browser test, write it as `contrib/deepsignal/test/console/test_<id>_browser.py`, mark it `@pytest.mark.lead_run`, make it skip with reason "browser test, run by lead outside the sandbox" when Playwright is not importable, and list it in your report.

`dist/` is rebuilt once at integration. Prove the build works, then restore it before committing.

Banned: loosening, skipping or deleting existing tests; swallowed errors; sleeps or timers for test ordering; refactors, renames or formatting outside your scope.

Docs: write `contrib/deepsignal/console/docs/<id>.md` for a ship tech: what it does in one sentence, how to turn it on or configure it (copy-paste example), how to see it working, what it does NOT do.

## Acceptance (run from `contrib/deepsignal/console`, paste the tails)
```
npx oxlint && npx tsc -b --noEmit
```
```
npx vitest run
```
```
npm run build && git checkout -- dist && git clean -fdq dist
```
