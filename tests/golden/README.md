# Golden tests

Golden tests check that the rebuilt pipeline reproduces numbers already reported in
Ryan's earlier analyses, e.g. bad-air-day counts per year, event clusters 2018–2025,
station completeness. They turn the old docs into a validation harness.

Filled in Phase 2, when each spec lists the numbers its sources report.

## Rules

- One test file per methodology part: `tests/golden/test_<spec-slug>.py`.
- Each expected value cites where it came from: the mirror path and section, e.g.
  `knowledge/docs/05-toronto-bad-air-days/toronto-high-pm25-days-2000-2025.md#by-year`.
- Expected values live in the test (they are facts about old documents, not config).
- Golden tests need `data/processed/`, which is local-only. Mark them
  `@pytest.mark.golden` and skip cleanly when the data is absent, so CI stays green.
- **A mismatch is never "fixed" by editing the expected value.** Open an ADR
  (`/adr`): which number is right, the old doc or the new pipeline, and why. Ryan decides.

## Template

```python
import pytest

pytestmark = pytest.mark.golden


def test_bad_air_days_2023_match_old_report(processed_data):
    # Source: knowledge/docs/<folder>/<doc>.md#<section> — "<quoted number>"
    expected = ...  # <filled in Phase 2>
    assert compute_bad_air_days(processed_data, year=2023) == expected
```
