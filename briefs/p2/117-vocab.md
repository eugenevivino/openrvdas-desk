# Brief: p2-vocab (Standard vocabularies (CF, SeaVoX, R2R, ICES, UN/LOCODE))

- Decision: D-PARITY1, IDEAS #117 (Eugene approved building #104-#124, 2026-11-18)
- Risk tier: low
- Module: exactly one. Branch `deepsignal/p2-vocab` from `3b4b76e`
- Lane: `cloud` (Sol medium, fixed)
- Fresh session, under 40 turns
- Upstream home: openrvdas_contrib tree, fork only for now
- Value (techs/science/shore): 2/4/4
- Depends on: none; #104 erddap, #52 registry and #120 cruise metadata read its files later

## Goal
Field names, instruments, events, ships and ports can be tagged with the standard terms archives expect,
checked by a tool, without anyone memorizing code lists.

## Background facts (do not re-derive)
- Base is the contrib `master` tree at `3b4b76e`: it carries a 2024 core tree (old Transform base class,
  no BaseModule). Copy the import-compatibility approach of
  `git show origin/deepsignal/vector-wind:contrib/deepsignal/logger/transforms/vector_wind_average_transform.py`
  so the module also works on current core. If that branch is unreadable, write plain absolute imports
  and say so.
- Create empty `__init__.py` files only where missing, byte-identical to the wind branch (empty), so
  parallel branches merge cleanly.
- OpenRVDAS loads classes from a config with `class:` plus `module:` (for example
  `module: contrib.deepsignal.<module>.<file>`). Records may arrive as a DASRecord, a dict with
  `timestamp` and `fields`, a list of either, or None; handle all, pass None through.
- File ownership is disjoint across phase 2 tasks: you own ONLY the paths under Scope.
- No network in this task. Do NOT type code lists from memory: codes you cannot read from a file in this
  repository must not appear. Real lists are imported from files a person downloads (see Design).

## Design (lead decisions; flag disagreement in the report)
Package `contrib/deepsignal/vocab/`:
- One local store format, `vocab/<scheme>.json`: `{"scheme": "cf_standard_names", "version": "...",
  "source": "...", "imported": "<UTC>", "terms": {"<id>": {"label": ..., "units": ..., "definition": ...}}}`.
- Importers (offline, from files the person downloads):
  - `import_cf <cf-standard-name-table.xml>` (the CF standard name table XML: `entry id`, `canonical_units`,
    `description`).
  - `import_nvs <file.rdf|.ttl|.json>` for NERC Vocabulary Server collections (L22 instruments, L35
    manufacturers, EL1 and EL2 event terms, C17 ICES ship codes) in SKOS RDF/XML: `skos:Concept`,
    `skos:prefLabel`, `skos:notation`, `dc:identifier`. Parse with `xml.etree.ElementTree` only.
  - `import_csv <file.csv> --scheme <name> --id-col --label-col` for R2R device types and UN/LOCODE.
- Seed: ship tiny fixture files under the test folder only, written by hand to look like the real
  formats; the package ships NO term lists.
- `lookup(scheme, id)`, `search(scheme, text)`, `check_tags(yaml)`: a tag file maps local names to terms,
  `{TSG_Temp: {cf: sea_water_temperature, units: degree_C}}`; findings: unknown term, units not
  equal to the CF canonical units and not in a small built-in compatible set (degree_C vs K is allowed and
  noted; any other mismatch is an error), scheme not imported (warning: "import it with ...").
- CLI: `python -m contrib.deepsignal.vocab import_cf <xml>`, `... check <tags.yaml>`, `... search cf temp`.

## Failing test first
`contrib/deepsignal/test/vocab/test_vocab.py` with fixture files: each importer reads its fixture; lookup
and search; check findings (unknown, unit mismatch, compatible units, scheme missing); XML with an entity
expansion attempt is refused (use `defusedxml` only if already installed; otherwise reject DOCTYPE).

## Module contract
Docs `contrib/deepsignal/docs/vocab.md`: where to download each list (name the publisher, no invented
URLs), how to import, how to tag. Depends on no other module.

## Acceptance (exact commands, from repo root, Linux, no browser)
```
python3.12 -m unittest discover -s contrib/deepsignal/test/vocab -t . -v
```
```
python3.12 -m flake8 --config .flake8 contrib/deepsignal/vocab contrib/deepsignal/test/vocab
```

## Scope
Create or change only: `contrib/deepsignal/vocab/**`, `contrib/deepsignal/test/vocab/**`, `contrib/deepsignal/docs/vocab.md`, `contrib/deepsignal/configs/vocab_*.yaml`, and empty `__init__.py` files where missing. Everything else is read-only.

## Usability (anything a tech sees or edits)
Answer each line of desk `docs/USABILITY.md` in the report, or N/A with a reason. Every config error is one
plain-English line naming the setting, what it saw, what it expected, and a good example.

## Trust boundaries and data integrity
Config and input files are hand-edited and untrusted: `yaml.safe_load` only, no `eval`. Never change or
drop an incoming value; only add fields or write new files. Missing or stale inputs are shown as such,
never guessed.

## Non-goals and banned
No core changes. No new dependency. No network. No refactors, renames or formatting outside Scope. No
loosened, skipped or deleted tests, no swallowed errors, no sleeps for test ordering.

## Stop rule
No code change needed: stop and report. Two fix rounds still red: stop and report.

## Result (builder fills in)
- Head sha:
- RED receipt:
- Acceptance tails:
- Open questions:
