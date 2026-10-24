---
id: 0002
title: What Toronto means
status: accepted
date: 2026-10-24
decided_by: Ryan
affects: [methodology/stations.md, methodology/grid.md]
supersedes: null
---

# 0002 — What Toronto means

## Context

Issues #1 and #2 say "in Toronto" without a definition. The old docs used boxes and radii
around Toronto ([grid approach](../knowledge/docs/seagate-documents-15-the-grid-approach-the-grid-approach.md)).
The City of Toronto publishes its boundary as one WGS 84 polygon
([boundary card](../knowledge/data/toronto-city-boundary.md)).

## Options

| Option | Pros | Cons |
|---|---|---|
| A. City of Toronto boundary polygon | Official, reproducible, 641.7 km² | Leaves out nearby GTA monitors (Mississauga) |
| B. A box or radius around City Hall | Simple | Arbitrary edge; not what 'in Toronto' means |

## Recommendation

**Option A.** An official polygon is reproducible and matches the plain meaning of the question.

## Decision

Option A, decided by Ryan 2026-10-24 (Phase 1 planning).

## Consequences

- Code: `src/clear/geo.py`, `src/clear/grid/cells.py`
- Data: `data/raw/City of Toronto boundary/toronto-boundary-wgs84.zip`
