---
id: 0003
title: Same site in several networks
status: accepted
date: 2026-10-24
decided_by: Ryan
affects: [methodology/stations.md]
supersedes: null
---

# 0003 — Same site in several networks

## Context

One physical monitor can report to NAPS, MECP and AirNow under different IDs (NAPS 060430 =
MECP 35125 = AirNow 124000060430; [mecp card](../knowledge/data/mecp-hourly-pm25.md)).
Counting them as separate stations inflates coverage; merging them hides source disagreement.

## Options

| Option | Pros | Cons |
|---|---|---|
| A. Build both `merged` and `separate`, compare in EXP-003; keep a config switch | Evidence decides; later models can repeat the test | Two code paths |
| B. Always merge | One series per site | Loses per-source detail |
| C. Always keep separate | Simple | Double-counts sites |

## Recommendation

**Option A.** Ryan asked for an A/B test. `merged` = one series per site, best source per hour by
priority NAPS > MECP > AirNow (validated networks first, preliminary AirNow last), keeping
a `source` column.

## Decision

Option A, decided by Ryan 2026-10-24 (Phase 1 planning).

## Consequences

- Config keys: `config/stations.yaml: overlap_mode`, `source_priority`
- Code: `src/clear/stations/combine.py`
- Experiment: `research/experiments/EXP-003-station-overlap-ab/`
