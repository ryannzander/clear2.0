# decisions/ — ADRs, one file per decision

Every methodology conflict or change to a target, threshold, split or metric becomes an
ADR here. Agents draft with `/adr` (status `proposed`); only Ryan accepts or rejects.
Files are `NNNN-slug.md`, written from [_template.md](_template.md).

Line format: `- [NNNN-slug](NNNN-slug.md) — the question · status · the answer in one phrase`.

**Next number: 0012.**

- [0001-data-split](0001-data-split.md) — train, validation and test years · accepted · 2021-24 / 2025 / 2026
- [0002-toronto-city-boundary](0002-toronto-city-boundary.md) — what Toronto means · accepted · the City of Toronto boundary polygon
- [0003-station-overlap-ab](0003-station-overlap-ab.md) — same site in several networks · accepted · build merged and separate, A/B in EXP-003
- [0004-completeness-75pct](0004-completeness-75pct.md) — how missing data is measured · accepted · % hours present + 75% flag
- [0005-time-utc-hour-beginning](0005-time-utc-hour-beginning.md) — hour label of time_utc · accepted · hour-beginning
- [0006-grid-0p1-toronto-cells](0006-grid-0p1-toronto-cells.md) — 0.1° grid alignment and Toronto cells · accepted · edges on 0.1° multiples, any overlap
- [0007-station-value-qc](0007-station-value-qc.md) — which hourly values count as missing · accepted · sentinels + negatives; repeats averaged
- [0008-site-crosswalk-500m](0008-site-crosswalk-500m.md) — linking stations across networks · accepted · within 500 m = one site
- [0009-golden-station-years](0009-golden-station-years.md) — old doc-04 station years vs rebuild · accepted · rebuild stands; doc values kept as `reported`
- [0010-airnow-offset](0010-airnow-offset.md) — AirNow 0.3–0.5 µg/m³ above NAPS/MECP at 3 sites · proposed · recommend: leave as published
- [0011-naps-060438-west-site](0011-naps-060438-west-site.md) — NAPS 060438 averaged into Toronto West · proposed · recommend: exclude from merged
