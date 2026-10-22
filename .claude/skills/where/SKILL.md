---
name: where
description: Use when asked "where is X", "what do we know about X", or "which file covers X". Answers from the maps only (AGENTS.md, INDEX.md files), never by searching folders.
---

# /where

## When
A location or "what do we know" question about docs, data, specs, decisions, code, config, experiments or figures.

## Inputs
The question, as asked.

## Steps
1. Pick the map from the `AGENTS.md` repo map. Common picks:
   - docs and evidence: `knowledge/INDEX.md`
   - datasets: `knowledge/data/INDEX.md`
   - pipeline data on disk: `data/INDEX.md`
   - methodology: `methodology/INDEX.md`; decisions: `decisions/INDEX.md`
   - experiments and literature: `research/INDEX.md`, `research/literature/INDEX.md`
   - code and config: `src/clear/INDEX.md`, `config/INDEX.md`
   - figures: `figures/INDEX.md`
2. Read that INDEX file. Find the line(s) that match.
3. Read the target file only if the INDEX line does not answer the question. Read mirrors and data cards, never binaries.
4. Originals ("does file X exist", "how many files in dataset Y"): read `manifests/inventory-summary.csv` first (one row per dataset folder), then Grep `manifests/inventory.csv` for specific files. If still unclear, one Grep over the `INDEX.md` files (not over protected folders).
5. Stop at 3 reads in total.
6. Answer with paths first, then one or two lines of substance.
7. If nothing is mapped, say so plainly and suggest `/map-refresh` (a new file may sit in `inbox/` or an INDEX may be stale).

## Outputs
A short answer:
- path(s), as links, one per line
- what each is, status, and the key fact from its INDEX line
- gaps: what is not mapped

## Done when
- [ ] Every claim has a path.
- [ ] At most 3 reads.
- [ ] No Glob or Grep ran inside `archive/`, `data/raw/`, `data/prior/`, `CLEAR 2.0 (misc docs)/` or `RAW Data/`.
- [ ] Absence reported as absence, with `/map-refresh` suggested.

## Standards to load
- `docs/standards/writing.md` only if you must interpret an INDEX line format or a frontmatter field.
