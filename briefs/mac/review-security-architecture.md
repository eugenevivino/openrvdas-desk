# Brief: Astra ultra review of docs/SECURITY-ARCHITECTURE.md (read-only)

- Lane: MacBook, `KALON_ALLOW_ASTRA=1 nice -n 10 ~/bin/ds-codex -m gpt-6.2-astra` with reasoning `ultra`, RAM-gated per shared-machine rules.
- Read-only. Output one report file: `review/security-architecture-astra.md` in the desk scratch dir. No edits to the doc.
- Inputs: desk `docs/SECURITY-ARCHITECTURE.md`; context `research/2026-11-18-mcp-reference-architecture.md`, `docs/mcp-design.md`, `briefs/p2/115-roles.md`, `briefs/cloud/p2-ai-triage.md`; fork `server/cached_data_server.py`, `utils/install_openrvdas.sh` (nginx template).

## Questions (answer each: AGREE / CHANGE (what) / CANNOT TELL (what evidence is missing))
1. Threat model: any missing threat with real ship likelihood? Is T1 (CDS publish) correctly ranked top?
2. Is Django + allauth the right single identity store vs FastAPI JWT or a separate IdP, given offline and FIPS constraints?
3. Vault (section 7): is the envelope design sound (nonce handling, AAD, KEK protectors, no PCR binding default, escrow)? Any failure mode that loses secrets at sea?
4. Crypto profile (section 6): any non-approved algorithm left in? Is TOTP HMAC-SHA1 acceptable under FIPS 140-3? ECDSA P-384 vs Ed25519 choice?
5. Audit chain (section 8.2): can an admin with root defeat it undetected? What does the design honestly guarantee against root?
6. Compliance table (section 11): flag each mapping you believe is wrong. Do not invent STIG rule IDs; say CANNOT TELL where the source text is needed.
7. MVP cut (section 12): is it achievable by 2026-11-25 and is anything missing that would make the console less secure than upstream today?
8. Effectiveness: anything here that would get routed around by techs at 03:00 or blank the bridge display?

Verdict line at top: SHIP AS IS / SHIP WITH CHANGES (list) / REWORK (why).
