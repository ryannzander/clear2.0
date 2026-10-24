---
id: 0005
title: Hour label of time_utc
status: accepted
date: 2026-10-24
decided_by: Ryan
affects: [methodology/stations.md]
supersedes: null
---

# 0005 — Hour label of time_utc

## Context

Sources label hours differently: NAPS hour-ending local standard time (documented), MECP
hour-ending EST (observed match with NAPS, not documented), AirNow hour-beginning UTC
(documented) ([naps](../knowledge/data/naps-hourly-pm25.md),
[mecp](../knowledge/data/mecp-hourly-pm25.md), [airnow](../knowledge/data/airnow-hourlyaqobs.md)).
`time_utc` needs one label ([naming-units-time.md](../docs/standards/naming-units-time.md#hour-labelling)).

## Options

| Option | Pros | Cons |
|---|---|---|
| A. Hour-beginning | Matches AirNow and the existing code | NAPS/MECP shift back 1 h on read |
| B. Hour-ending | Matches NAPS/MECP | AirNow shifts forward 1 h; code changes |

## Recommendation

**Option A.** Fewer changes, and AirNow (the only 2026 source) is native hour-beginning.

## Decision

Option A, chosen by Ryan 2026-10-24 (interactive question). MECP's hour-ending label stays an observed fact; the build
re-checks it by comparing co-located MECP and NAPS series at lag 0.

## Consequences

- Code: `src/clear/timeutil.py` (PROVISIONAL note removed)
- Docs: `docs/standards/naming-units-time.md#hour-labelling`
