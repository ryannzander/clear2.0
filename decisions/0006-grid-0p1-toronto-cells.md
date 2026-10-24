---
id: 0006
title: 0.1 degree grid alignment and Toronto cells
status: accepted
date: 2026-10-24
decided_by: Ryan
affects: [methodology/grid.md]
supersedes: null
---

# 0006 — 0.1 degree grid alignment and Toronto cells

## Context

Issue #2 asks for 0.1° cells "in Toronto". Both old grids put cell edges on round-degree
multiples ([0.5° tables](../knowledge/data/legacy-grid-approach-tables.md),
[CSG-1](../knowledge/data/clear-standard-grid-csg1.md)). The City polygon cuts many cells
partly, and some cells hold no government station.

## Options

| Option | Pros | Cons |
|---|---|---|
| A. Edges on 0.1° multiples; a cell is Toronto if it overlaps the City at all; report % inside | Nests in both old grids; no part of the City is lost | Edge cells may be mostly outside |
| B. Centre inside the City | Fewer, more central cells | Parts of the City fall in no cell |
| C. At least 50% inside | Balanced | Parts of the City fall in no cell |

## Recommendation

**Option A.** Every part of the City lands in a counted cell; `city_frac` lets later phases weight
edge cells. Empty cells are reported, not filled: the one-station-per-cell rule of issue #2
is checked, not assumed.

## Decision

Option A, chosen by Ryan 2026-10-24 (interactive question).

## Consequences

- Config keys: `config/grid.yaml: toronto_grid`
- Code: `src/clear/grid/cells.py`, `src/clear/grid/assign.py`
