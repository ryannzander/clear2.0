---
name: adr
description: Use when sources conflict, a new methodology choice appears, or a target, threshold, split or metric must change. Drafts a decision record for Ryan and records his answer.
---

# /adr

## When
Any methodology decision. Ryan decides all ADRs. Never resolve a conflict silently.

## Inputs
The question, the conflicting sources or options, the spec section it blocks.

## Steps
1. Next number: read `decisions/INDEX.md`; take the highest `NNNN` plus one. Slug is lowercase-hyphen.
2. `cp decisions/_template.md decisions/NNNN-slug.md`. Set `status: proposed` and today's date.
3. Fill in:
   - Context: the question and why it matters, with mirror citations (`knowledge/docs/<path>.md#heading`).
   - Options: each with trade-offs, effect on the pipeline and on results, cost to reverse.
   - Recommendation: one option, with reasons. Mark the evidence behind it.
4. Link the ADR from the spec's open question. Add a line to `decisions/INDEX.md`: `- [NNNN-slug](NNNN-slug.md) — question · proposed · recommended option`.
5. Ask Ryan with the interactive question tool, recommended option first. Batch related ADRs into one ask. Only the Lead talks to Ryan; a subagent returns the draft path and the question to the Lead.
6. On the answer: record the chosen option, Ryan's reason if given, and the date. Set `status: accepted` (or `rejected`, with what happens instead).
7. Update the spec: replace the open question with the decision and a link to the ADR. Update the INDEX line status.
8. Run `uv run python scripts/check_maps.py --ci` (checks ADR links and size budgets; no originals or mirrors changed, so the full check is not needed).
9. `/review` (gated), commit `docs(decisions): NNNN <slug>`, push. A `proposed` draft may be committed before Ryan answers; say so in the message.

## Outputs
`decisions/NNNN-slug.md`, updated `decisions/INDEX.md` and linked spec.

## Done when
- [ ] Options have trade-offs; a recommendation is stated.
- [ ] Ryan answered; his choice and the date are recorded.
- [ ] Status is `accepted` or `rejected`, not `proposed` (unless still waiting; then it is on the Lead's open list).
- [ ] The spec links the ADR and no longer lists the question as open.
- [ ] `check_maps.py --ci` passes; `/review` passed; pushed.

## Standards to load
- `decisions/_template.md`.
- `docs/standards/writing.md` for citation and INDEX line format.
