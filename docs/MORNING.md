# Morning queue for Eugene (newest first)

- Linux gate (D-GATE1): r5 review HOLD again (5 new P1s), so the verdict gate is dropped. A small ADVISORY workflow (raw pytest and flake8 output, no GREEN/RED) is on branch gate/linux-advisory once built; it needs a merge to desk main before any dispatch works. Approve that merge, or say stop spending on the Linux gate.

- D-SEC1 adopt the security architecture and its MVP cut (docs/SECURITY-ARCHITECTURE.md section 12). Security code merges wait for you.
- D-SEC2 login layer: recommended Django accounts plus allauth MFA (this closes the #115 login item).
- D-SEC3 rename the #115 role "public" to "authenticated viewer".
- D-SEC4 vault core (host-key) moves into the Nov 25 pilot for TOTP seeds, Django secret and TLS keys; AI stays off until the vault is in and the ship opts in explicitly.
- D-SEC6: Nov 25 is a Wednesday (not Tuesday). It is a supervised pilot beside the existing bridge display; ship cutover only after the four release checks in docs/SECURITY-ARCHITECTURE.md section 12 pass.
- D-SEC5 reference FIPS platform: RHEL 9.

- SECURITY (critical): upstream CachedDataServer binds all interfaces on 8766 and accepts unauthenticated publish, including via nginx /cds-ws. The console install must bind it to localhost and expose a read-only websocket only; closing publish is part of the security architecture block (#189-#198, trust zones plus CDS write lockdown). Do not expose the console beyond the ship LAN until that lands.


- #188 AI watch assistant: pick the API provider and put the key in the ship environment (never in git). A lead check against the real API runs outside the sandbox. Defaults: $2/day, $30/month caps; you can change them.

- CRITICAL security package, offline first: signed audit (#32), local identity, trust zones (#115, #151, #155). Needs your review before anything is enabled.
- #164 CalibrationTransform must NOT be enabled on any live config until you approve.

- #137 eez-mode (critical: controls logging): lead check with a real Marine Regions file and a recorded track. EEZ data never committed until the Marine Regions license is verified.
- FYI no action: live checks of #131 against OpenVDM 2.17 sample data and #133 against a Sealog demo server come after merge.

- #121 device-pack: approve downloading the public manufacturer manuals named in briefs/mac/p2-device-pack.md (for example the MetSpecs PDF at calcofi.org) into /private/tmp/deepsignal/p2-device-pack/manuals/. Reply yes in the project thread. Until then #121 is held; everything else runs.

- #130 instrument-init: after merge, needs a real-hardware check with a tech present (it writes to instruments). Not run before then.

- #115 roles: pick the login layer (Django accounts, FastAPI JWT, or a reverse proxy). The role engine is built without login; #105 REST binds to localhost until you choose.
- #120 cruise metadata: do you have access to MFP or MOMS exports? v1 ships without that import.
- NCEI KAOU archive blocks robots: a person must download a real SAMOS file by hand if you want byte-exact tests (optional).

Rewritten as items are answered. Each line: what, why it needs you, what is already done around it.

- Mini login: you said the Mini is signed in, but the check on the Mini shows no `~/.codex-deepsignal` (only Kalon's
  `~/.codex`). The sign-in probably landed on the MacBook. On the Mini run:
  `mkdir -p ~/.codex-deepsignal && CODEX_HOME=$HOME/.codex-deepsignal /opt/homebrew/bin/codex login`
  then `resume/mini-finish.sh` runs from the MacBook. Meanwhile the #78 `ultra` review runs on the MacBook (no loss, only slower).
- Downloads for #121 device-pack and #139 kongsberg-tap: the Mac lane needs Eugene's own yes to download the public manufacturer manuals and format documents named in briefs/mac/p2-device-pack.md and briefs/mac/p2-kongsberg-tap.md into /private/tmp/deepsignal/<module>/manuals/ (manifest with URL, size, SHA-256; never committed). Reply "yes, download the #121 and #139 documents" in the project thread; one yes unlocks both.
- QARTOD (D-QARTOD3 outcome): the final Astra ultra re-review of fix round 3 is BLOCK at deepsignal/qartod-flags 1660680 on stock CSV inputs (a record is still lost, and a flat-line failure can become an overall pass); flat-line performance now passes. The branch is left unmerged; no further rounds. Eugene decides: accept with these as known issues, re-brief, or drop. Review: /private/tmp/deepsignal/qartod-fix3-review/answer.md (MacBook).
- Sonar estimators #170-#174 (Mac, Astra high) are HELD: all five briefs pin numpy==2.2.6 and scipy==1.15.3, which no DeepSignal Python on the MacBook has (weighted-depth built but 19 of 22 tests error on import, so it was not pushed). Approve creating an isolated venv /private/tmp/deepsignal/venv-sci (Homebrew python3.12; pip install numpy==2.2.6 scipy==1.15.3 from PyPI) and the five builds resume. Reply yes in the project thread.
- websockets: contrib master's 2024 CDS breaks on websockets 14+ (harness uses a fixture-side shim for now). Clean answer: a websockets<14 pin or a CDS fix, proposed upstream only with your approval (D-UPSTREAM0).
