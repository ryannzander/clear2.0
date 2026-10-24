---
id: 0009
title: Old doc-04 station years and count vs the Phase 1 rebuild
status: accepted
date: 2026-10-24
decided_by: Ryan
affects: [methodology/stations.md]
supersedes: null
---

# 0009 — Old doc-04 station years and count vs the Phase 1 rebuild

## Context

The golden check against the old station analysis
([doc 04](../knowledge/docs/seagate-documents-04-toronto-stations-toronto-pm25-station-statistical-analysis.md#2-station-inventory-years-active-and-data-completeness))
fails on 10 of 20 first/last years and on the station count: e.g. NAPS 060435 "2010–2025" vs
2010–2024 rebuilt, MECP 31103 "2000–2020" vs 2003–2019, "10 stations" vs 11 sites. Two causes:
the old pipeline labelled NAPS/ON hours by their end in UTC (prior-stations card), so a file's
last evening fell into the next year; and it merged NAPS stations into ON stations within 1 km,
so MECP codes inherit NAPS years (MECP files hold no data before 2003, mecp card).

## Options

| Option | Pros | Cons |
|---|---|---|
| A. The rebuild stands: years in each source's own calendar, sites by ADR 0008 (500 m); record doc 04's numbers as `reported` | Matches the providers' files; no spill-over years | Old docs' tables no longer match |
| B. Reproduce doc 04: hour-ending UTC years and the 1 km NAPS→ON merge | Old numbers reproduce | Reintroduces an off-by-one-year artefact and hides which network measured what |

## Recommendation

**Option A.** Both differences are artefacts of old conventions, not data differences;
MECP years match the old pipeline's own station table (`prior-stations`, `on_provincial_stations`).

## Decision

Option A, chosen by Ryan 2026-10-24 (interactive question).

## Consequences

- Tests: `tests/golden/expected/stations.yaml` holds the rebuild value, doc 04's `reported`
  value and `adr: 0009` for each difference.
- Specs to update: `methodology/stations.md#completeness` (years-active rule),
  `methodology/stations.md#golden-numbers`
