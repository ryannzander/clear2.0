# research/ — experiments, literature, log, reviews

Line format: `- [name](path) — what it is · status · key fact`.

## Experiments

One folder per experiment: `experiments/EXP-NNN-slug/` with `README.md` and `metrics.json`.
Scaffold from the template with `/experiment`. Agents read the README, never `mlruns/`.

- [_template/README.md](experiments/_template/README.md) — experiment README template · template · copy, don't edit
- [_template/metrics.json](experiments/_template/metrics.json) — metrics skeleton · template · copy, don't edit

- [EXP-001-toronto-gov-stations](experiments/EXP-001-toronto-gov-stations/README.md) — Toronto government stations, years active, missing data (#1) · done · 24 stations = 11 sites; 4 sites complete in every split
- [EXP-002-toronto-grid-0p1](experiments/EXP-002-toronto-grid-0p1/README.md) — one government station per 0.1° Toronto cell? (#2) · done · no: 12 of 17 cells have no active site
- [EXP-003-station-overlap-ab](experiments/EXP-003-station-overlap-ab/README.md) — merged vs separate series (#1) · done · partly supported: merged ≥ best station everywhere; 060438 and AirNow offset not interchangeable

## Literature

- [literature/INDEX.md](literature/INDEX.md) — Scout's cited notes, one file per topic · empty · see that file

## Log

Append-only daily log, one file per day: `log/YYYY-MM-DD.md`. Newest first below.

- [log/2026-10-24.md](log/2026-10-24.md) — Phase 1 built: catalogue, specs, ADRs 0001–0009, stations + grid, EXP-001–003 · done · next is Phase 2 (domain)
- [log/2026-10-22.md](log/2026-10-22.md) — raw copy to E: finished, first full inventory · done · 255,640 originals hashed
- [log/2026-10-20.md](log/2026-10-20.md) — R&D system designed, Phase 0 scaffold built · done · next is Phase 1 on 2026-10-21

## Reviews

`reviews/` holds optional written review notes for big changes, committed.
The pass/fail record of the latest review is `.review/last.json` (gitignored).

No review notes yet.
