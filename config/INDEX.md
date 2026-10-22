# config/ — every methodological constant

YAML files loaded by `clear.config` into pydantic models. No magic numbers in code: each
constant lives here with a comment linking its spec section (`methodology/<slug>.md#<anchor>`)
or ADR. Changing a value here is a gated change (needs `/review`).

Line format: `- [file.yaml](file.yaml) — what it holds · spec it serves · status`.

Each file appears when a spec in Phase 2 names constants, and is listed here with the
spec it serves.

- [grid.yaml](grid.yaml) — study domain centre + half-width (map extents) · `methodology/grid.md` (not yet written) · PROVISIONAL
