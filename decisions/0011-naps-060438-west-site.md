---
id: 0011
title: NAPS 060438 in the Toronto West site
status: proposed
date: 2026-10-24
decided_by: Ryan
affects: [methodology/stations.md]
supersedes: null
---

# 0011 — NAPS 060438 in the Toronto West site

## Context

NAPS 060438 lies ~185 m from NAPS 060430 / MECP 35125 (Toronto West), so ADR 0008 links it
into that site and `merged` averages it with 060430 (same source). EXP-003 shows it reads
+1.47 µg/m³ above 060430 (RMSE 4.39, r 0.82), unlike every other co-located pair
(r ≥ 0.99) — a different instrument or method ([naps card](../knowledge/data/naps-hourly-pm25.md)).

## Options

| Option | Pros | Cons |
|---|---|---|
| A. Keep it in the site but prefer 060430 (drop 060438 hours when 060430 has a value) | Keeps data where 060430 is missing | A per-station rule |
| B. Exclude 060438 from the merged series | Simple; West = 060430/MECP/AirNow | Loses its hours (060430 is ~99% complete anyway) |
| C. Keep averaging (current) | No change | Mixes two instruments; +0.7 µg/m³ shift in hours with both |

## Recommendation

**Option B.** 060430 and MECP 35125 already give the West site ≥ 99% completeness, so 060438 adds a bias but almost no coverage.

## Decision

_Pending._

## Consequences

- Config keys: `config/stations.yaml` (an exclusion list)
- Code: `src/clear/stations/combine.py`
