---
id: EXP-NNN
title: <short title>
issue: "#N"               # GitHub issue this experiment answers
spec: methodology/<slug>.md#<anchor>
status: planned           # planned | running | done | abandoned
headline: false           # true only after Ryan has seen the result
mlflow_experiment: EXP-NNN-slug
---

# EXP-NNN — <title>

<!-- Copy this folder to research/experiments/EXP-NNN-slug/. Fill Result and Conclusion from metrics.json. Agents read this file, never mlruns/. -->

## Hypothesis

<!-- One falsifiable sentence. Name the metric and the comparison. -->

## Setup

- **Data versions:** `<dataset-slug>` sha256 `<hash>` (`manifests/inventory.csv`)
- **Config:** `config/<file>.yaml` at commit `<git sha>`
- **Seed(s):** `<filled in when run>`
- **Rerun:** `uv run clear <command> ...`

## Result

<!-- Numbers copied from metrics.json, plus figure links (figures/out/fig_<slug>.png). -->

| Metric | Value | Baseline |
|---|---|---|
| `<metric>` | `<value>` | `<value>` |

## Conclusion

<!-- Did the result support the hypothesis? Two or three lines. Flag anything Ryan must decide as an ADR. -->

## Next

<!-- Follow-up experiments or specs to update, as issue links. -->

- `<next step>`
