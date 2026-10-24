---
id: 0007
title: Which hourly values count as missing
status: accepted
date: 2026-10-24
decided_by: Ryan
affects: [methodology/stations.md]
supersedes: null
---

# 0007 — Which hourly values count as missing

## Context

Missing codes differ: NAPS `-999`; MECP `9999` (documented) and `-999` (not documented);
AirNow none, but rare `-9999`/`-4996`. All three hold other negatives. MECP has 1,102
duplicate station-dates; NAPS can report several method codes per station-date, and the old
code averaged them ([naps](../knowledge/data/naps-hourly-pm25.md),
[mecp](../knowledge/data/mecp-hourly-pm25.md), [airnow](../knowledge/data/airnow-hourlyaqobs.md)).

## Options

| Option | Pros | Cons |
|---|---|---|
| A. Sentinels and every negative value = missing; several values for one station-hour (MECP duplicates, NAPS method codes) are averaged | Simple, conservative, matches the old code | Drops small valid negatives near zero |
| B. As A, but keep negatives down to -5 µg/m³ | Near-zero noise stays unbiased | Negative concentrations in the target |

## Recommendation

**Option A.** Conservative and simple; near-zero negatives do not matter for smoke events.

## Decision

Option A, chosen by Ryan 2026-10-24 (interactive question).

## Consequences

- Config keys: `config/stations.yaml: sources.*.sentinels`, `negative_is_missing`
- Code: `src/clear/stations/qc.py` (readers keep raw values)
