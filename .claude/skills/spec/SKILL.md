---
name: spec
description: Use when a methodology part needs its canonical spec, or an existing spec must be updated from new evidence. Distills mirrors into methodology/<part>.md from the fixed template.
---

# /spec

## When
The spec step of each phase, or when new mirrors, literature notes or ADR outcomes change a part. Specs come before validation and code.

## Inputs
Part slug (matches the future `src/clear/<part>` module name), the requesting issue if any.

## Steps
1. Read `STATUS.md`, `methodology/INDEX.md` (does the spec exist?), `GLOSSARY.md`, `decisions/INDEX.md`.
2. Gather evidence from maps only: `knowledge/INDEX.md` to the mirrors in `knowledge/docs/`; `research/literature/INDEX.md` for cited notes. Read mirrors, never originals. Ask the Lead for a Scout run if outside evidence is missing.
3. New spec: `cp methodology/_template.md methodology/<part>.md`. Existing spec: edit in place.
4. Fill every template section. Each claim cites its mirror: `knowledge/docs/<path>.md#heading`. Use glossary names and units-in-names. Where evidence is missing, write `<unknown>` and list it as an open question; never invent CLEAR facts.
5. Conflicts (sources disagree on a number, definition, target, threshold, split or metric; or a choice has no source): do not pick. Write an open question in the spec with both citations, then run `/adr` for each. Link the `decisions/NNNN-slug.md` file from the spec.
6. List the constants the spec needs, with the config file and key they will live in (`config/<name>.yaml`). Do not create config here.
7. Update `methodology/INDEX.md` (`- [part](part.md) — what it covers · status · key fact`) and the part's row in `STATUS.md`.
8. Check links and size budgets: `uv run python scripts/check_maps.py --ci` (no originals or mirrors changed, so the full check is not needed).
9. Stage, run `/review` (`methodology/` and `decisions/` are gated). Fix findings.
10. Commit `docs(methodology): spec <part>` and push. No AI attribution.

## Outputs
`methodology/<part>.md`, ADR drafts (`status: proposed`) in `decisions/`, updated INDEX files and STATUS row.

## Done when
- [ ] Every template section is filled or marked `<unknown>`.
- [ ] Every claim has a mirror citation.
- [ ] Every conflict is an open question with an ADR link, none resolved silently.
- [ ] Config constants are listed with target file and key.
- [ ] `check_maps.py --ci` passes; `/review` passed; pushed.
- [ ] The Lead has the list of ADRs awaiting Ryan.

## Standards to load
- `methodology/_template.md` (section list).
- `docs/standards/writing.md` (citation and INDEX line format).
