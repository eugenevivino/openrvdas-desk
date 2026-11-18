# DeepSignal adoption strategy for operational vessel use

Source: Eugene's Deep Research report, 2026-11-18. NOTE: the copy that reached the desk
was truncated mid-table (it stops in the vessel software landscape table at OpenVDM).
Everything below is only what was visible. Re-send the full text to complete this note.
Claims are the report's, not independently verified here (inferred until checked).

## Answer
Do not pitch DeepSignal as a large block merged into OpenRVDAS. Make it an independently
versioned, MIT-compatible observability and QC layer with thin OpenRVDAS adapters.
Order: deterministic QC and health first, dashboards second, AI optional, local,
explainable, and unable to control acquisition.

## Why (report's evidence)
- OpenRVDAS v2.7.0 docs say it is not an analysis package; QC, gridding and analysis
  happen downstream, and it is deliberately not turnkey.
- Wholesale merge gives maintainers a permanent support burden and asks operators to
  trust unproven software in the acquisition path.

## Milestones (measured as operator deployments, not merged lines)
1. One Scripps vessel runs DeepSignal read-only in shadow for a full cruise or equivalent,
   raw data preserved independently, removable with no change to acquisition.
2. Replication on a vessel run by a different institution.
3. An operator other than the author installs, diagnoses, upgrades and recovers it from docs alone.
First ship candidates: R/V Roger Revelle or R/V Sally Ride (needs Scripps marine technical
leadership agreement). R2R shows OpenRVDAS output from both, incl. a 2024 Revelle
distribution with MetAcq and Seapath streams.

## Publication and funding (dates per the report, unverified)
- First paper: operational validation in JTECH after the first serious sea trial.
- JOSS later: needs six months public development, tagged release, tests, docs,
  contribution process, research use, maintenance evidence.
- Funding order: in-kind pilot; NSF PESOSE Track 1 (deadline 2027-03-02, up to $300k) only
  if a public product with an emerging community exists; NSF Oceanographic Instrumentation
  (target 2027-01-11) via Tech Services; NOAA IOOS Ocean Technology Transition later.

## Adoption rule
Do not ask operators to believe DeepSignal improves operations. Instrument the trial so the data proves it.

## Landscape (visible rows)
OpenRVDAS (Nuyina, Revelle, Sally Ride), CORIOLIX (Sikuliaq, Point Sur, Pelican, Savannah,
Revelle, Okeanos Explorer; interoperability target), SCS (NOAA lineage, do not claim gone),
MetAcq (good first QC target, SAMOS validates met), Seapath (a source to monitor, not a
competitor), UHDAS (coexist), OpenVDM (data management; row cut off).

## Conflict with current decisions
Conflicts with D-ARCH3 (contrib code drop). Recorded as open decision D-ADOPT1. No change of course.
