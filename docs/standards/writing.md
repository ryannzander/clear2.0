# Writing standard

Formats for everything agents write as text: mirrors, data cards, INDEX files, glossary,
STATUS, log. Specs and ADRs use their templates (`methodology/_template.md`,
`decisions/_template.md`). Size budgets are enforced by `scripts/check_maps.py`.

## Mirror

A mirror is a text copy of an original doc. Agents read mirrors, never the binary.

- One `.md` mirror per logical doc, in `knowledge/docs/`, with a slugified path (lowercase,
  hyphens): `Methods Draft v2.docx` → `methods-draft-v2.md`.
- The same doc in several formats gets one mirror. Prefer docx over pdf; list the rest in
  `aliases`.
- Older versions: `status: superseded`, no mirror unless they hold unique content.
- Converter: `markitdown`; fall back to `pandoc`; `manual` if neither works.

```yaml
---
source: archive/<original path>          # exact original path
aliases: [archive/<same doc>.pdf]        # other formats/copies of the same doc
sha256: <hash of source at conversion>
converted: 2026-10-21                    # date
converter: markitdown                    # markitdown | pandoc | manual
status: current                          # current | superseded
kind: mirror                             # mirror | data-card
---
```

- Body = the converted text. **Light cleanup only**: fix broken tables, drop repeated page
  headers/footers, normalize heading levels, keep list structure.
- **Never paraphrase, summarize, correct or reorder.** Numbers, typos and odd wording stay.
  The mirror is evidence; interpretation goes in the spec.
- Images: not extracted. PNGs get one line in `INDEX.md`. Extract an embedded image only when
  a spec cites it.
- A mirror's `sha256` must equal its source's. The full `check_maps.py` (not `--ci`) fails on a stale mirror.
  Re-convert, do not edit.

## Data card

One card per dataset (xlsx, csv, parquet, nc, grib, json...) in
`knowledge/data/<dataset-slug>.md`. Frontmatter = the mirror fields (`kind: data-card`,
`source: data/raw/<path>`) plus the fields below. A dataset split across many files (e.g. one
per day or station) gets ONE card whose `source` is the dataset folder — it maps every file
below it; omit `sha256` (per-file hashes live in the local `manifests/inventory.csv`).
Cards for prior outputs (old pipeline results) use `source: data/prior/<folder>` and
`validation: unvalidated`, and the body names the legacy script that made them
(`archive/legacy-code/...`) or `<verify>`.

```yaml
dataset: <dataset-slug>
provider: <organisation>
variables: [<canonical name>, ...]
units: {<canonical name>: <unit>, ...}
time_coverage: <start>/<end>            # ISO 8601 UTC
time_convention: <zone; hour-ending|hour-beginning|instantaneous; DST behaviour>
spatial_coverage: <region / bbox / station count>
rows: <integer>
validation: unvalidated                 # unvalidated | partial | validated
validation_report: null                 # knowledge/data/<dataset-slug>.validation.md
```

Body sections, in this order:

```markdown
## What it is
Two sentences: provider, product, level, what one row is.

## Columns / variables
| Original name | Canonical name | Type | Unit | Meaning / notes |
|---|---|---|---|---|

## Coverage
Time range, spatial range, station or tile count, known gaps by year.

## Time convention
Zone, hour label, DST behaviour, and the evidence (doc section or observed check).
See naming-units-time.md.

## Known issues
- Missing codes, flags, duplicates, unit surprises, one bullet each.

## Validation
Status, link to the validation report, date.
```

- Write `<verify>` for any fact not yet confirmed. Never guess.
- Fields are facts about the file, not methodology choices. Choices go in the spec.
- Validation status values and report: [data.md](data.md#validation-reports).

## INDEX.md

One per mapped folder. At most 100 lines. One line per file or sub-folder:

```
- [name](path) — what it is · status · key fact
```

Example (illustrative, not a real entry):

```
- [methods-draft-v2](docs/methods-draft-v2.md) — draft methods write-up · current · tables 1-4 list the stations used
- [site-photo.png](../archive/site-photo.png) — photo of a monitor installation · media · no text content
```

| Rule | Detail |
|---|---|
| Header | A title and at most two lines saying what the folder is |
| Order | Alphabetical, or grouped under `##` headings |
| `status` | Controlled words per folder (`current`, `superseded`, `unvalidated`, `proposed`, `media`) |
| `key fact` | The one thing a reader needs to decide whether to open it |
| Overflow | Past 100 lines, split by sub-folder and link child INDEXes from the parent |
| Competition and pitch material | One line per folder; agents go there only when asked |

## Glossary entry

[GLOSSARY.md](../../GLOSSARY.md) is one table: `Term | Canonical code name | Definition | Units | Avoid`.

- One row per term. Code name in backticks, snake_case. Units use the suffix table in
  [naming-units-time.md](naming-units-time.md); `—` if dimensionless.
- Definition: one sentence. Established external terms get a plain definition; CLEAR-specific
  terms point to their spec: `<defined in methodology/<slug>.md — Phase 2>`.
- Avoid: the aliases agents must not use in code or docs.
- When a spec is written, replace the pointer with the spec's one-sentence definition.
- Unsure of a fact: `<verify>`.

## STATUS.md

At most 60 lines. Rewritten at the end of every session; read at the start.

| Section | Content |
|---|---|
| Header | Phase, next phase, updated date |
| Per-part status | Table: part (spec slug), stage (mapped → spec'd → validated → built) |
| Blockers | Bullets; empty if none |
| Next 3 actions | Numbered, imperative, each doable in one session |
| Open questions for Ryan | Bullets; link the ADR when one exists |

## Research log

`research/log/YYYY-MM-DD.md`. Append-only: add bullets, never rewrite earlier ones.

```markdown
# 2026-10-21
- Decision: ADR 0003 proposed (alert-level source conflict); waiting on Ryan.
- Outcome: 14 docs mirrored; 3 data cards `unvalidated`.
- Next: draft `target-pm25` spec.
```

Tags: `Decision`, `Outcome`, `Next`, `Blocked`. One line each, with a link when there is one.

## Size budgets

| File | Max lines |
|---|---|
| `AGENTS.md` | 150 |
| Any `INDEX.md` | 100 |
| `STATUS.md` | 60 |
| Any file in `docs/` | 200 |
| `GLOSSARY.md` | 150 |

Over budget: split by topic and link. Mirrors and data cards have no limit.

## Prose style

Ryan skims.

- Tables and bullets over paragraphs. Short, concrete, imperative sentences.
- Lead with the answer or the action. Put numbers, paths and commands in backticks.
- No filler or hype words ("comprehensive", "robust", "seamless"). No restating the brief.
- Link instead of repeating. [AGENTS.md](../../AGENTS.md) is the single source for hard rules;
  each standard is the single source for its topic.
- Never invent facts about CLEAR's methodology or data. Use `<filled in Phase 2>` or
  `<verify>`.
- One idea per bullet. A table cell is a phrase, not a paragraph.
- Dates are ISO (`2026-10-21`). Times carry a zone.
