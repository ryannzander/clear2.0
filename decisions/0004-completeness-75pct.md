---
id: 0004
title: How missing data is measured
status: accepted
date: 2026-10-24
decided_by: Ryan
affects: [methodology/stations.md]
supersedes: null
---

# 0004 — How missing data is measured

## Context

Issue #1 asks for "missing data" per station. The old completeness docs report percentages
of hours present ([completeness](../knowledge/docs/seagate-documents-23-data-completeness-clear2-data-completeness-continental.md)).
A threshold is needed to call a station-period usable.

## Options

| Option | Pros | Cons |
|---|---|---|
| A. % of hours present + a 75% completeness flag | Common air-quality practice; easy to read | 75% is a convention, not derived |
| B. % of hours only | No threshold to defend | No usable/unusable call |

## Recommendation

**Option A.** Report the fraction and flag station-periods below 75%.

## Decision

Option A, decided by Ryan 2026-10-24 (Phase 1 planning).

## Consequences

- Config keys: `config/stations.yaml: completeness_min_frac`
- Code: `src/clear/stations/completeness.py`
