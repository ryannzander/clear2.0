---
name: validate-data
description: Use when a dataset has a card and its methodology spec exists, and it must be checked against what the spec requires before modeling.
---

# /validate-data

## When
The validate step of each phase, or any time a dataset is refreshed. Specs define what "valid" means, so the spec must exist first.

## Inputs
Dataset slug. Its card `knowledge/data/<slug>.md` and the spec `methodology/<part>.md`.

## Steps
0. Run `uv run python scripts/storage.py` first. Checks on raw files need `data/raw` online; if it is OFFLINE, stop and tell the Lead.
1. Read the card, then the spec's data-requirements section (coverage, variables, units, time resolution, period, completeness). No spec or no such section: stop and tell the Lead.
2. Turn each requirement into a check. Write them as a pandera schema in `src/clear/schemas/<slug>.py` (use the helpers in `schemas/common.py`: tz-aware UTC `time_utc`, non-negative concentrations), plus custom checks for what pandera cannot say:
   - duplicates and gaps per station or sensor, missing-hour counts
   - ranges and unit sanity, sentinel values (e.g. -999)
   - time convention applied correctly, DST edges
   - station and period coverage against the spec
3. Add a contract test in `tests/contract/` using a tiny synthetic fixture that passes and one that fails.
4. Run it on the real data: `uv run pytest tests/contract -k <slug>`, then the schema and custom checks on the real file with `uv run python` (driver script in `notebooks/` if needed; scratch only). Parquet or Zarr stage outputs are read from `data/interim|processed`; raw files from `data/raw/`.
5. Write `knowledge/data/<slug>.validation.md`: frontmatter (dataset, date, spec link, result), a table (check | spec source | result | n failing), the issues found, what was corrected and how.
6. Set the card: `validation: validated` (all pass) or `partial` (known, documented gaps); `validation_report: knowledge/data/<slug>.validation.md`.
7. Methodology-affecting issues (spec thresholds unmet, conflicting units, a station set or period that must change, parameter-code choice): do not fix. Hand to the Methodologist for `/adr`.
8. `/review` for the `src/` and `tests/` changes, commit `feat: schema for <slug>`; then the report and card as `data: validate <slug>` (mechanical). Push both.

## Outputs
Schema module, contract test, validation report, updated card, list of ADR candidates.

## Done when
- [ ] Every spec data requirement maps to a check, or is listed as not checkable and why.
- [ ] Report exists and the card links it.
- [ ] Card `validation` matches the report.
- [ ] Each methodology-affecting issue has an `/adr` draft or is in the Lead's open-questions list.
- [ ] Schema code passed `/review`; commits pushed.

## Standards to load
- `docs/standards/data.md` (schemas at stage boundaries, validation).
- `docs/standards/code.md` when writing the schema module and tests.
