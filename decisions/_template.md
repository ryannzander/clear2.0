---
id: NNNN                  # next free number, see decisions/INDEX.md
title: <short question, imperative or noun phrase>
status: proposed          # proposed | accepted | rejected | superseded
date: YYYY-MM-DD          # date proposed; update when decided
decided_by: Ryan
affects: []               # methodology/<slug>.md paths this changes
supersedes: null          # NNNN of the ADR this replaces, or null
---

# NNNN — <title>

<!-- Copy to decisions/NNNN-slug.md. Agents fill everything except Decision. Ryan decides. Max 200 lines. -->

## Context

<!-- Why a decision is needed. Quote each conflicting source with its mirror path. Three to six lines. -->

## Options

<!-- At least two. Include "do nothing" if it is real. -->

| Option | Pros | Cons |
|---|---|---|
| A. `<option>` | `<pro>` | `<con>` |
| B. `<option>` | `<pro>` | `<con>` |

## Recommendation

<!-- The agent's pick, one option, with the reason in two or three lines. Ryan may overrule. -->

**Option `<A|B>`.** `<reason>`

## Decision

<!-- Leave empty until Ryan answers. Then: chosen option, date, any change to the recommendation, and set status in the frontmatter. -->

_Pending._

## Consequences

<!-- What must change once accepted. One line each. -->

- Config keys: `config/<file>.yaml: <key>`
- Code: `src/clear/<module>.py`
- Tests: `tests/<unit|contract|golden>/<file>`
- Specs to update: `methodology/<slug>.md#<anchor>`
