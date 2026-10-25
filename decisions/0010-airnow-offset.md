---
id: 0010
title: AirNow offset against NAPS and MECP
status: accepted
date: 2026-10-24
decided_by: Ryan
affects: [methodology/stations.md]
supersedes: null
---

# 0010 — AirNow offset against NAPS and MECP

## Context

EXP-003 (`research/experiments/EXP-003-station-overlap-ab/metrics.json`, `agreement`) shows
AirNow 0.3–0.5 µg/m³ above NAPS/MECP at East, West and North since 2023-07 (r ≈ 0.99),
none at Downtown John St. AirNow is preliminary ([airnow card](../knowledge/data/airnow-hourlyaqobs.md))
and the only 2026 source, so merged series step at the 2025→2026 hand-over (test split).

## Options

| Option | Pros | Cons |
|---|---|---|
| A. Leave as published; note it | No new constant | Test split biased +0.3–0.5 µg/m³ at 3 sites |
| B. Subtract a per-site offset fitted on 2023-07–2025 overlap | Continuous series | A fitted constant; preliminary data may be revised |
| C. Use AirNow only where no NAPS/MECP exists (already the merged rule) and flag 2026 | No adjustment | Bias stays in 2026 |

## Recommendation

**Option A.** The offset is small next to smoke-event levels; revisit when the target series is specified.

## Decision

Option A, chosen by Ryan 2026-10-24: AirNow stays as published; the offset is noted in
the spec, EXP-003 and the AirNow validation reports. Revisit when the target series is specified.

## Consequences

- None in code or config (option A).
- Specs to update: `methodology/stations.md#open-questions` (closed, points here)
