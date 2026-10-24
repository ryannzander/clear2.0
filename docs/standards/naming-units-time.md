# Naming, units, time

One vocabulary, units in names, one clock (UTC). Canonical terms: [GLOSSARY.md](../../GLOSSARY.md).
Code layout: [code.md](code.md). Data cards: [writing.md](writing.md#data-card).

## Naming rules

| Thing | Rule | Example |
|---|---|---|
| Python, columns, config keys | `snake_case`, ASCII | `wind_speed_ms` |
| Canonical term | Use the GLOSSARY "Canonical code name". Add the term there first. | `alert_level` |
| Column pattern | `<quantity>[_<qualifier>]_<unit>` | `pm25_ugm3`, `distance_km` |
| Modules | Spec slug, `-` → `_` | `lag-plume` → `lag_plume.py` |
| Knowledge, figure, spec files | lowercase, hyphens | `fig_<slug>.py`, `knowledge/docs/<slug>.md` |
| Booleans | `is_` / `has_` prefix | `is_bad_air_day` |
| Counts | `n_` prefix | `n_stations` |
| Identifiers | `_id` suffix, string dtype | `station_id` |
| Timestamps | `_utc` suffix; the main one is `time_utc` | `start_utc` |
| Abbreviations | Only those in GLOSSARY | `aqhi`, `aod`, `era5` |

- Never `pm2.5`, `PM25`, `temp`, `val`, `data2`. Check the GLOSSARY "Avoid" column.
- Interim tables rename source columns to canonical names. The data card keeps the original
  name in its variables table.

## Unit suffixes

A unit suffix is mandatory on every physical column, variable and config key.

| Suffix | Unit | Notes |
|---|---|---|
| `_ugm3` | µg/m³ | Mass concentration. `pm25_ugm3` |
| `_ppb` | parts per billion | Gas mixing ratio. |
| `_ms` | metres per second | Speed. **Not** milliseconds; milliseconds are never used as a column unit. |
| `_deg` | degrees | Angles, lat/lon (`lat_deg`, `lon_deg`), wind direction. Direction convention goes in the data card. |
| `_km` | kilometres | Distances, domain sizes. |
| `_m` | metres | Heights, small distances. |
| `_h` | hours | Durations, lags (`lag_h`). |
| `_min` | minutes | Sub-hourly durations and sampling intervals. |
| `_pct` | percent, 0-100 | Use `_frac` for 0-1. |
| `_frac` | fraction, 0-1 | |
| `_hpa` | hectopascal | Pressure. |
| `_k` | kelvin | Temperature. Convert to the canonical unit at ingest. |
| `_utc` | UTC timestamp | tz-aware, see below. |

- Dimensionless (indices, counts): no suffix; say so in the docstring or data card.
- One canonical unit per quantity. Convert at ingest and record the conversion in the card.
- New unit: add a row here and in the GLOSSARY before using it.

## Time rules

1. Every timestamp is **tz-aware UTC** (`datetime64[ns, UTC]`) in a column named `time_utc`.
2. **Normalize at ingest.** Raw keeps what the source gave. `interim` and later hold UTC
   only. Conversion happens in `clear.timeutil`, with the source convention passed in
   explicitly, never inferred.
3. The source convention (zone, hour label, DST behaviour) is recorded in the data card
   field `time_convention`. The card is the single record.
4. **Local Toronto time appears only in figures and the dashboard**, converted at the last
   step with `zoneinfo.ZoneInfo("America/Toronto")`.
5. Axis and table labels say the zone: "UTC" or "Toronto local (EST/EDT)". Never unlabelled.
6. Join and resample in UTC only.
7. In text and logs write ISO 8601 with a zone: `2025-06-05T14:00:00Z`.

### Hour labelling

| Label | Timestamp is | `13:00` covers |
|---|---|---|
| Hour-beginning (HB) | Start of the interval | 13:00-14:00 |
| Hour-ending (HE) | End of the interval | 12:00-13:00 |

- **PROVISIONAL:** `time_utc` in hourly tables is hour-beginning. An ADR (`proposed`)
  confirms or changes it in the Phase 1 spec step. Until then, convert HE sources by subtracting 1 h.
- Hourly tables hold on-the-hour stamps only. Test: `time_utc.dt.minute == 0`.
- Instantaneous values, interval means and accumulations are labelled differently by
  sources. The data card states which each variable is.

### DST pitfalls

| Pitfall | Rule |
|---|---|
| Source stamps local clock time with DST | Localize with `ambiguous="raise"`, `nonexistent="raise"`. Resolve cases with a documented source rule. |
| Source stamps local *standard* time all year | Fixed offset, no DST. Do not use `America/Toronto`. Confirm in the card. |
| Spring forward: a local hour does not exist | The gap is real. Do not fabricate the hour. |
| Fall back: a local hour occurs twice | Ambiguous. Needs a source flag or row order. Never guess. |
| Hour `24` / `24:00` labels | Parse as 00:00 of the next day; treat as HE. |
| Daily aggregates | The day boundary comes from the spec. Name the column `date_utc` or `date_toronto`, never bare `date`. |
| `pd.to_datetime` on mixed offsets | Pass `utc=True`; assert the result dtype. |
| Epoch integers | State the unit (s or ms) and anchor to UTC when converting. |
| Resampling in local time | Don't. Resample in UTC, convert for display. |

Edge cases for tests: 2025-03-09 (spring forward) and 2025-11-02 (fall back) in Toronto.
See [code.md](code.md#unit-tiny-synthetic-fixtures).

## Per-source time conventions

Nothing here is asserted. Each cell is filled from the source's documentation when its
data card is written, then copied into the card's `time_convention` field.

| Source | Zone / DST | Hour label | Native interval |
|---|---|---|---|
| NAPS | to verify in data card | to verify in data card | to verify in data card |
| Ontario MECP | to verify in data card | to verify in data card | to verify in data card |
| US EPA AQS (88101, 88502) | to verify in data card | to verify in data card | to verify in data card |
| AirNow | to verify in data card | to verify in data card | to verify in data card |
| PurpleAir | to verify in data card | to verify in data card | to verify in data card |
| ERA5 | to verify in data card | to verify in data card | to verify in data card |
| NOAA HMS smoke | to verify in data card | to verify in data card | to verify in data card |
| FIRMS | to verify in data card | to verify in data card | to verify in data card |
| AOD product | to verify in data card | to verify in data card | to verify in data card |

## Station IDs

**PROVISIONAL.** Format `<source>:<id>`, confirmed in `methodology/stations.md` (Phase 1).

- `<source>` is the lowercase source key from the GLOSSARY code-name column: `naps:<id>`,
  `purpleair:<id>`.
- `<id>` is the provider's identifier as a string, exactly as published (keep leading zeros).
- No spaces. Dtype is `string`, never integer.
- A site that reports to two networks gets two IDs. How they are linked is a spec question.
