# CLEAR 2.0

CLEAR 2.0 is a wildfire-smoke early-warning research system for Toronto. It forecasts
PM2.5 and AQHI-aligned alert levels from ground monitors (NAPS, Ontario, EPA), low-cost
sensors (PurpleAir), satellite fire and smoke products, and ERA5 wind. This repo is the
R&D workspace: methodology, data handling, code, experiments and figures.

## Status

Phase 1 (stations + grid). Each phase builds one stage of the forecasting system:
catalogue → spec → validate → build → answer. Current state: [STATUS.md](STATUS.md).

## Layout

See [AGENTS.md](AGENTS.md) for the repo map, rules, roles and standards.

## Quickstart

Needs [uv](https://docs.astral.sh/uv/) (Python 3.12).

```
uv sync --all-groups
uv run pre-commit install
uv run clear --help
```

## Raw data is not in this repo

Raw datasets and original documents are gitignored. They are large and licences vary by
provider. `data/raw` and `data/prior` are links to other drives (`uv run python scripts/storage.py`).
The repo keeps provenance (`data/sources.yaml`) and per-folder file counts
(`manifests/inventory-summary.csv`) so every dataset can be traced and re-fetched. The
per-file hashes (`manifests/inventory.csv`) stay local.
