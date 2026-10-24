---
id: 0008
title: Linking stations across networks into sites
status: accepted
date: 2026-10-24
decided_by: Ryan
affects: [methodology/stations.md]
supersedes: null
---

# 0008 — Linking stations across networks into sites

## Context

IDs do not map 1:1 across networks: AirNow `000060424` "Toronto Downtown" carries NAPS ID
060424, but its values match MECP 31103 = NAPS 060433
([airnow card](../knowledge/data/airnow-hourlyaqobs.md)). Co-located pairs found in the
catalogue step lie within ~250 m; the downtown move (Bay/Wellesley to 55 John St.) is ~1.9 km. The old pipeline merged NAPS
into ON stations within 1 km ([doc 04](../knowledge/docs/seagate-documents-04-toronto-stations-toronto-pm25-station-statistical-analysis.md)),
which also joined NAPS 060439 (732 m from 060433).

## Options

| Option | Pros | Cons |
|---|---|---|
| A. Link stations within 500 m (single linkage) into one `site_id` | Coordinates are the one key all networks share; catches the AirNow anomaly | Two distinct monitors < 500 m apart would merge |
| B. Link by published IDs | No threshold | Fails on the known anomaly |

## Recommendation

**Option A.** Distance is the only key all three networks share.

## Decision

Option A, chosen by Ryan 2026-10-24 (interactive question).

## Consequences

- Config keys: `config/stations.yaml: crosswalk_max_distance_m`
- Code: `src/clear/stations/registry.py`
