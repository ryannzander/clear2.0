# Code standard

Applies to `src/clear/`, `scripts/`, `figures/src/`, `tests/`. Hard rules: [AGENTS.md](../../AGENTS.md).
Names and units: [naming-units-time.md](naming-units-time.md). Toolchain: `uv` (Python 3.12),
`ruff`, `pyright` (strict on `src/`), `pytest`.

## Package layout

| Path | Holds |
|---|---|
| `src/clear/<part>.py` | One module per methodology part. `<part>` = spec slug with `-` → `_` (`methodology/alert-levels.md` → `alert_levels.py`). Past 400 lines it becomes a subpackage `<part>/`. |
| `src/clear/cli.py` | typer app `clear`; mounts `clear.viz.cli:app` as `clear figures`. |
| `src/clear/config.py` | Loads `config/<name>.yaml` into pydantic models. |
| `src/clear/schemas/` | pandera schemas; shared checks in `common.py`. |
| `src/clear/timeutil.py` | Source timestamps → tz-aware UTC. |
| `src/clear/viz/` | Tokens, style, figure helpers ([figures.md](figures.md)). |
| `src/clear/ingest/` | Fetch modules, one per source (`/ingest`, `.claude/skills/ingest/SKILL.md`). |

- No spec, no module: create a part module only after `methodology/<part>.md` exists.
  Infrastructure (`config`, `schemas`, `timeutil`, `viz`, `cli`, `ingest`) is exempt.
- Parts import `config`, `schemas`, `timeutil`. `src/` never imports `figures/`,
  `notebooks/` or `scripts/`.
- Public names go in `__all__`. New module → add one line to `src/clear/INDEX.md`.
- CLI (typer): every runnable step is `uv run clear <group> <command>`, except fetch modules,
  which run as `uv run python -m clear.ingest.<source>` (ingest skill, step 3). A command is
  thin: parse args, call a function, print one result line. Inputs are arguments, no hidden
  globals, non-zero exit on failure.

## Notebooks

Scratch only: `notebooks/*.py` (jupytext percent). Never commit `.ipynb`; never import one.
Code used twice, or feeding a number anyone cites, is promoted to `src/clear/` with a test.

## Typing

pyright strict on `src/`: annotate every signature, no bare `Any`, no blanket `# type: ignore`.
A narrow `# pyright: ignore[rule]` needs a why-comment. Validate at the boundary (pandera,
pydantic), then trust the types inside.

## Docstrings (NumPy style)

Every public function has: summary, `Method:` line (the spec section that defines the
behaviour; infra code links its standard instead), Parameters with **units and shapes**,
Returns, Raises.

```python
def hourly_mean(readings: pd.DataFrame, *, min_valid_frac: float) -> pd.DataFrame:
    """Aggregate sub-hourly readings to one value per station-hour.

    Method: methodology/<part>.md#<section>

    Parameters
    ----------
    readings : pandas.DataFrame
        ``station_id`` (str), ``time_utc`` (datetime64[ns, UTC]), ``pm25_ugm3``
        (float, µg/m³, NaN = missing). Shape ``(n_readings, 3)``.
    min_valid_frac : float
        Minimum share of non-missing readings per hour, 0-1. From ``config/<part>.yaml``.

    Returns
    -------
    pandas.DataFrame
        ``station_id``, ``time_utc`` (hour start), ``pm25_ugm3``.
        Shape ``(n_station_hours, 3)``. Short hours are NaN, not dropped.

    Raises
    ------
    ValueError
        If ``time_utc`` is naive or not UTC.
    """
```

Examples are illustrative: no CLEAR decision, helper names show intent; `src/clear/` wins.

## Comments say why

- Code says what; a comment says why: the constraint, the source quirk, the spec rule.
  Good: `# Sort first: the rolling window assumes increasing time; input order is not guaranteed`.
  Bad: `# sort by time`. Link evidence: `# see knowledge/data/<card>.md`.
- No commented-out code. A TODO carries an issue number: `# TODO(#123): ...`.

## Size limits (soft)

Functions ≤ 40 lines, modules ≤ 400. Over the limit: split, or the reviewer asks why.
One job per function; pure logic inside, file and network I/O at the edges.

## Config: no magic numbers

Every methodological constant lives in `config/<name>.yaml` with a comment linking its spec
section or ADR. Code reads it through `clear.config` into a typed model.

```yaml
# config/<part>.yaml
# Spec: methodology/<part>.md#<section> · ADR: decisions/NNNN-<slug>.md
min_valid_frac: 0.75   # PLACEHOLDER for illustration, not a CLEAR decision
```

```python
from pydantic import BaseModel, ConfigDict, Field
from clear.config import load_config   # helper name: check src/clear/config.py

class PartConfig(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    min_valid_frac: float = Field(ge=0, le=1)

cfg = load_config("<part>", PartConfig)
hourly = hourly_mean(readings, min_valid_frac=cfg.min_valid_frac)
```

- Magic: thresholds, windows, lags, grid sizes, split dates, seeds, hyperparameters.
  Not magic: `0`, `1`, named unit conversions.
- A value the spec lacks is an open question (ADR `proposed`), not a guess in code.

## Error handling: fail loud at boundaries

- Validate where data enters: file read, API response, CLI args, config load, stage handoff.
- Raise specific exceptions naming the file, column and offending value. No bare `except:`.
- No silent repair: no `errors="coerce"` or `fillna` unless a spec rule says so and the
  count of changed values is logged or asserted. Missing stays NaN. No default-to-zero or
  last-value fallbacks; a missing config key is an error.
- `logging` for diagnostics; `print` only for CLI output.

## Tests

| Folder | Proves | Data |
|---|---|---|
| `unit/` | One function does the right thing on edge cases | Tiny synthetic frames built in code |
| `contract/` | Table shapes match the pandera schema at each stage | Synthetic frames, plus real tables when present |
| `golden/` | Code reproduces numbers reported in old docs | Real data; skipped when `data/` is absent (CI) |

### Unit: tiny synthetic fixtures

Cover at least: Toronto DST spring-forward (2025-03-09) and fall-back (2025-11-02), a missing
hour, a multi-hour sensor dropout, duplicate timestamps, an all-NaN station, HE vs HB off-by-one.

```python
def test_fall_back_hour_is_ambiguous_not_guessed():
    # 01:30 occurs twice on 2025-11-02 in Toronto; guessing would shift the series by 1 h
    local = pd.Series(pd.to_datetime(["2025-11-02 01:30"]))
    with pytest.raises(ValueError, match="ambiguous"):
        to_utc(local, tz="America/Toronto")   # clear.timeutil; signature illustrative
```

### Contract: pandera

One schema per stage boundary in `src/clear/schemas/`, built from `schemas/common.py`
helpers. Test one good frame and one bad frame per rule.

```python
schema = pa.DataFrameSchema(
    {"station_id": pa.Column(str),
     "time_utc": pa.Column(pd.DatetimeTZDtype(tz="UTC")),
     "pm25_ugm3": pa.Column(float, pa.Check.ge(0), nullable=True)},
    unique=["station_id", "time_utc"], strict=True,
)

def test_negative_concentration_is_rejected():
    bad = make_frame(pm25_ugm3=[-1.0])
    with pytest.raises(pa.errors.SchemaError):
        schema.validate(bad)
```

### Golden: reproduce old numbers

- One entry per number reported in an old doc, in `tests/golden/expected/<part>.yaml`.
  Set `tol` once, from how the old doc rounded it.
- Mismatch: never loosen `tol` or edit `value`. Write an ADR (`proposed`) with both numbers
  and the cause; Ryan decides. Once accepted, update `value` and set `adr:`.

```yaml
- id: <slug>
  value: <number as reported>
  tol: <absolute tolerance>
  source: knowledge/docs/<mirror>.md      # section or table
  adr: null
```

```python
@pytest.mark.parametrize("want", load_golden("<part>"), ids=lambda w: w.id)
def test_reproduces_reported_number(want, processed_dir):
    if not processed_dir.exists():
        pytest.skip("data/ not present")
    assert compute(want.id, processed_dir) == pytest.approx(want.value, abs=want.tol)
```

## Readability checklist (Reviewer applies)

1. Names come from [GLOSSARY.md](../../GLOSSARY.md), snake_case, units in the name. No `df2`, `tmp`, `x` outside a 3-line scope.
2. Every timestamp is tz-aware UTC in `time_utc`. No naive datetimes. Local time appears only in `viz`.
3. No magic numbers. Each constant is in `config/*.yaml` with a spec or ADR link.
4. Each public function has a docstring with units, shapes, `Raises`, and a `Method:` line that points at a section that exists.
5. Full annotations; pyright strict passes; every `ignore` has a reason.
6. Functions ≤ 40 lines, modules ≤ 400, one job each, no nesting deeper than 3, inputs not mutated, I/O at the edges.
7. Comments explain why. No commented-out code, no TODO without an issue number.
8. Boundaries validate through a pandera schema. No bare `except`, no silent coerce or fill; messages name the bad value.
9. New behaviour has a unit test with an edge-case fixture; new schema has a contract test; a ported number has a golden entry.
10. No code copied from a notebook; no duplicate of a helper in `timeutil` or `schemas.common`.
11. The code makes no methodology choice the spec lacks. Gaps are open questions or ADRs.
12. The diff does one thing, and `INDEX.md` lists any new module.
