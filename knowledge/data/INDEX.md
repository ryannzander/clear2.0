# knowledge/data/ — data cards for every `data/raw` and `data/prior` dataset

One card per dataset: `<dataset-slug>.md`. Cards hold provider, variables, units, time
coverage, time convention, spatial coverage, rows and validation status. Agents read the
card, never the raw file. Validation reports sit beside the card as `<dataset-slug>.validation.md`.
Prior-output cards have `source: data/prior/<folder>`.

Line format: `- [dataset-slug](dataset-slug.md) — what it is · validation: unvalidated|partial|validated · time and space coverage`.

No data cards yet. They appear after the first `/map-refresh` (Phase 1, from 2026-10-21).
Provenance of each dataset: [data/sources.yaml](../../data/sources.yaml). Pipeline outputs: [data/INDEX.md](../../data/INDEX.md).
