---
name: method-check
description: Use when code in src/clear/ should be checked against its methodology spec, before review of a pipeline module or after a spec changes. Reports gaps; edits nothing.
---

# /method-check

## When
After the Experimenter writes or changes a module, after a spec or ADR changes, or before build sign-off of a part.

## Inputs
Module name (e.g. `clear.<part>`) and its spec `methodology/<part>.md`.

## Steps
1. Read the spec: its decisions, formulas, definitions, constants, open questions. Note accepted ADRs it links.
2. Find the module through `src/clear/INDEX.md`. List its public functions and classes (Grep for `^def |^class ` in that module).
3. For each public function: read its NumPy docstring `Method:` line.
   - Missing `Method:` line: undocumented.
   - Link does not resolve to a spec heading: broken.
   - Behavior differs from the spec section (formula, window, units, inclusion rules): mismatch. Quote spec and code lines.
4. Constants: Grep the module for numeric literals and thresholds. Each must come from `config/<name>.yaml` via `clear.config`, and the YAML key must carry a comment linking the spec section or ADR. Literals in code: magic numbers.
5. Spec to code: walk each decision in the spec and find where the code implements it. None found: unimplemented.
6. Naming and time: units in names, `time_utc` tz-aware UTC, names from `GLOSSARY.md`. Report violations.
7. ADR state: any dependency on a `proposed` ADR or an unresolved open question is flagged.
8. Report in the reply as a table: `# | kind | code (path:line) | spec section | note`. Kinds: unimplemented, undocumented, mismatch, magic-number, broken-link, naming, blocked-by-proposed-ADR. Add counts per kind.

## Outputs
A findings table in the reply. No files change; no commit.

## Done when
- [ ] Every public function was checked for a `Method:` link.
- [ ] Every numeric constant was traced to `config/` or flagged.
- [ ] Every spec decision was mapped to code or flagged unimplemented.
- [ ] Findings are tagged for the right owner: spec issues to the Methodologist (`/adr`), code issues to the Experimenter.
- [ ] Nothing was edited.

## Standards to load
- `docs/standards/code.md` (docstring, config and typing rules).
- `docs/standards/naming-units-time.md` for the naming and time checks.
