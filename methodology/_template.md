---
part: <slug>              # = src/clear/<slug>.py = methodology/<slug>.md
status: draft             # draft | review | accepted
owner: methodologist
sources: []               # knowledge/docs/... mirror paths this spec distills
decisions: []             # decisions/NNNN-slug.md paths
updated: YYYY-MM-DD
---

# <Part title>

<!-- Copy this file to methodology/<slug>.md. Keep every section, even if empty. Max 200 lines. -->

## Purpose

<!-- One short paragraph: what this part produces and why the next part needs it. -->

## Inputs

<!-- One row per input. Time convention = source convention (e.g. local standard time, hour-ending); ingest normalizes to UTC. -->

| Name | Source dataset / data card | Units | Time convention |
|---|---|---|---|
| `<name>` | `knowledge/data/<dataset-slug>.md` | `<unit>` | `<filled in Phase 2>` |

## Outputs

<!-- One row per output table or grid. Schema = the pandera schema in src/clear/schemas/. -->

| Name | Schema | Units |
|---|---|---|
| `<name>` | `<schema name or column list>` | `<unit>` |

## Method

<!-- Numbered steps, imperative. Each heading carries a stable {#anchor}; code links methodology/<slug>.md#<anchor>. Never rename an anchor once code links to it. -->

### 1. <Step name> {#step-1-anchor}

<!-- What happens, in which order, with which constants (name them, don't give values here). -->

### 2. <Step name> {#step-2-anchor}

## Constants

<!-- Every number the method uses. Value lives in config/, not in code. Justification = source mirror or ADR. -->

| Name | Value | Config key | Justification / ADR |
|---|---|---|---|
| `<name>` | `<filled in Phase 2>` | `config/<file>.yaml: <key>` | `<mirror path or decisions/NNNN-slug.md>` |

## Decisions

<!-- Link ADRs only, one line each: markdown link to the ADR file in decisions/, then what it decided. Never restate the decision here. -->

- None yet.

## Open questions

<!-- Numbered. Tag `→ ADR?` when Ryan must decide. State the conflict between sources; do not resolve it silently. -->

1. `<question>` → ADR?

## Validation criteria

<!-- What data and results must satisfy. Testable, with thresholds from Constants. Feeds /validate-data and golden tests. -->

- `<criterion>`

## Golden numbers

<!-- Numbers reported in old docs that the rebuilt pipeline must reproduce. A mismatch needs an ADR. -->

| Number | Value (from old doc) | Source mirror path | Test name |
|---|---|---|---|
| `<what the number is>` | `<value>` | `knowledge/docs/<slug>.md` | `tests/golden/test_<name>.py::<test>` |

## Sources

<!-- Mirrors (evidence) first, then literature notes. Each cited claim above points back here. -->

- `knowledge/docs/<slug>.md` — `<what it contributes>`
- `research/literature/<topic>.md` — `<what it contributes>`
