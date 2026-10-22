# research/ — experiments, literature, log, reviews

Line format: `- [name](path) — what it is · status · key fact`.

## Experiments

One folder per experiment: `experiments/EXP-NNN-slug/` with `README.md` and `metrics.json`.
Scaffold from the template with `/experiment`. Agents read the README, never `mlruns/`.

- [_template/README.md](experiments/_template/README.md) — experiment README template · template · copy, don't edit
- [_template/metrics.json](experiments/_template/metrics.json) — metrics skeleton · template · copy, don't edit

No experiments yet. The first appear in Phase 4. Line format for experiments:
`- [EXP-NNN-slug](experiments/EXP-NNN-slug/README.md) — hypothesis · planned|running|done|abandoned · headline result`.

## Literature

- [literature/INDEX.md](literature/INDEX.md) — Scout's cited notes, one file per topic · empty · see that file

## Log

Append-only daily log, one file per day: `log/YYYY-MM-DD.md`. Newest first below.

- [log/2026-10-20.md](log/2026-10-20.md) — R&D system designed, Phase 0 scaffold built · done · next is Phase 1 on 2026-10-21

## Reviews

`reviews/` holds optional written review notes for big changes, committed.
The pass/fail record of the latest review is `.review/last.json` (gitignored).

No review notes yet.
