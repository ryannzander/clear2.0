---
name: review
description: Use before committing changes to gated paths (research code and specs, plus tooling, tests, hooks, CI and pre-commit; list = GATED in scripts/check_review.py). Independent review of the staged diff by the reviewer subagent (Opus 5.5, fresh context), then record the pass, commit and push.
---

# /review

## When
Anything staged under a gated path: `src/ config/ methodology/ decisions/ research/experiments/ figures/src/ scripts/ tests/ .claude/hooks/ .claude/skills/review/ .github/workflows/`, or the files `.claude/agents/reviewer.md .claude/settings.json .pre-commit-config.yaml .gitignore .ignore pyproject.toml uv.lock` (source of truth: `GATED` in `scripts/check_review.py`). Renames count as delete + add. Maps, mirrors, any `INDEX.md`, STATUS, log and docs skip review.

## Inputs
The staged diff. Run from the Lead (or the specialist that staged it).

## Steps
1. `git diff --cached --stat`. No gated paths: skip review and commit.
   Gated: first let the fixers settle so the reviewed diff is the committed diff:
   `uv run pre-commit run` → if it changed files, `git add` them and run it again until clean.
   (The `check-review` hook fails at this point; that is expected.)
2. Gather context: `git diff --cached`; linked specs (follow `Method:` lines); linked ADRs; the checklist in `docs/system/04-review-and-commit.md`.
3. Review, round 1: delegate to the `reviewer` subagent (Agent tool, `subagent_type: reviewer`, Opus 5.5). The prompt is self-contained: repo purpose (wildfire-smoke early warning for Toronto), what the change is meant to do (one line), the paths of the linked specs/ADRs, and "review the staged diff against the checklist; read-only; reply in your return contract". Do not pass the author's reasoning or self-assessment.
4. Fix findings (the author, not the reviewer). Re-stage. Re-review.
   - Each new round is a NEW `reviewer` delegation. Its prompt repeats the original brief, the prior findings, and what was changed for each.
   - Maximum 2 fix rounds (3 reviews in all). If it still fails, stop and escalate to Ryan through the Lead with the open findings.
5. On pass, with the final diff staged (any later change to staging voids the record):
   `uv run python scripts/check_review.py record --verdict pass --reviewer "claude/opus-5.5" --round N`
   `N` is the round that passed. Add `--notes "..."` for non-blocking findings.
6. Commit with a conventional message and **no AI attribution** (no `Co-Authored-By`, no "Generated with"). Then `git push`. The pre-commit hook runs `check_review.py check`.
7. Big changes: put the written review in `research/reviews/<topic>.md` and commit it in a separate follow-up commit (ungated, so no review). Staging it into the reviewed commit after step 5 would change the diff hash and void the record.

## Outputs
`.review/last.json` (gitignored), a pushed commit, optional note in `research/reviews/`.

## Done when
- [ ] Verdict is `pass` on the exact staged diff that was committed.
- [ ] `check_review.py record` ran after the last staging change.
- [ ] Commit has no AI attribution; pushed to `main`.
- [ ] Or: two fix rounds failed and the open findings were handed to the Lead for Ryan.

## Standards to load
- `docs/system/04-review-and-commit.md` (checklist, gate).
- `docs/standards/git.md` (commit messages, pre-commit).
