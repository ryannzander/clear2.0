---
name: experiment
description: Use when a GitHub experiment issue is ready to run. Scaffolds EXP-NNN-slug from the template, runs it through the clear CLI, records metrics and a README, reviews, commits and comments on the issue.
---

# /experiment

## When
An issue from the experiment template exists with a hypothesis, a linked spec and a config.

## Inputs
Issue number `N`.

## Steps
1. Read the issue: `gh issue view N`. Note hypothesis, spec link, data, config, success criteria.
2. Check preconditions: the spec exists and its linked ADRs are `accepted`; input datasets have cards with `validation: validated` or `partial`. If not, stop and report to the Lead.
3. Number: read `research/INDEX.md`; take the next `NNN`. Scaffold: `cp -r research/experiments/_template research/experiments/EXP-NNN-slug`.
4. Config: write `research/experiments/EXP-NNN-slug/config.yaml` for run parameters only. Methodological constants stay in `config/*.yaml` with spec/ADR comments. No magic numbers in code.
5. Code: pipeline changes go in `src/clear/` to `docs/standards/code.md` (docstrings with `Method:`, pyright strict, tests). Run `uv run ruff check`, `uv run pyright`, `uv run pytest`.
6. Run: `uv run clear <command> --config research/experiments/EXP-NNN-slug/config.yaml` (command from the issue/spec). Log to MLflow if installed (`mlruns/`, gitignored); skip if the `ml` group is absent.
7. Record:
   - `metrics.json`: final numbers only, with units and the data period.
   - `README.md`: hypothesis, issue, spec, config, result, conclusion. The conclusion says what the data supports and nothing beyond it.
   - Golden check: if a number reproduces one from an old doc and differs, stop; that needs an ADR.
   - `headline` stays false until Ryan has seen the result.
8. Add the line to `research/INDEX.md`.
9. Stage; run `/review` (`research/experiments/`, `src/` and `config/` are gated). Fix findings.
10. Commit `exp: EXP-NNN <slug>` and push. No AI attribution.
11. Comment on the issue with 3 lines (result, conclusion, README path): `gh issue comment N --body "<3 lines>"`.

## Outputs
`research/experiments/EXP-NNN-slug/` (README.md, metrics.json, config.yaml); code and tests in `src/clear/`; INDEX line; issue comment.

## Done when
- [ ] README has all six fields, with real numbers matching `metrics.json`.
- [ ] Run is reproducible from config plus the commit hash noted in the README.
- [ ] Ruff, pyright and pytest are clean.
- [ ] `/review` passed on the staged diff; pushed.
- [ ] Issue comment posted.
- [ ] Anything headline-worthy is flagged to the Lead for Ryan.

## Standards to load
- `docs/standards/code.md`.
- `research/experiments/_template/README.md` (field list).
