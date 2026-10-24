# config/ — every methodological constant

YAML files loaded by `clear.config` into pydantic models. No magic numbers in code: each
constant lives here with a comment linking its spec section (`methodology/<slug>.md#<anchor>`)
or ADR. Changing a value here is a gated change (needs `/review`).

Line format: `- [file.yaml](file.yaml) — what it holds · spec it serves · status`.

Each file appears when a spec names constants, and is listed here with the spec it serves.

- [grid.yaml](grid.yaml) — `toronto_grid` (0.1° cells, Toronto-cell rule; ADR 0006) + study `domain` (map extents) · `methodology/grid.md` · domain PROVISIONAL (Phase 2)
- [stations.yaml](stations.yaml) — sources (folders, clock, sentinels), QC, priority, overlap mode, crosswalk, completeness · `methodology/stations.md` · ADRs 0003–0005, 0007, 0008
- [splits.yaml](splits.yaml) — train 2021–24 / val 2025 / test 2026 · `methodology/stations.md` · ADR 0001
