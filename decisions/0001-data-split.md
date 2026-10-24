---
id: 0001
title: Train, validation and test years
status: accepted
date: 2026-10-24
decided_by: Ryan
affects: [methodology/stations.md]
supersedes: null
---

# 0001 — Train, validation and test years

## Context

Every model in CLEAR needs fixed train/validation/test years, and Phase 1 reports
completeness per split. Dad's background note (issue #1) proposes "Training years:
2021-2024 / Validation: 2025 / Testing: 2026". NAPS ends 2024 and MECP 2025
([naps](../knowledge/data/naps-hourly-pm25.md), [mecp](../knowledge/data/mecp-hourly-pm25.md));
AirNow is the only government source for 2026 and our copy ends 2026-10-08
([airnow](../knowledge/data/airnow-hourlyaqobs.md)).

## Options

| Option | Pros | Cons |
|---|---|---|
| A. 2021-24 train / 2025 val / 2026 test (calendar years, UTC) | Matches the brief; 2023 smoke season in train | 2026 test is partial (to Oct 8) and AirNow-only |
| B. Leave open | No commitment yet | Completeness per split cannot be reported |

## Recommendation

**Option A.** It is the brief's split and keeps the 2023 smoke season for training.

## Decision

Option A, chosen by Ryan 2026-10-24 (interactive question).

## Consequences

- Config keys: `config/splits.yaml: splits`
- Code: `src/clear/stations/completeness.py`
- Specs to update: `methodology/stations.md#completeness`
