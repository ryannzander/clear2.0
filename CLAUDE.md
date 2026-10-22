@AGENTS.md

## Claude-specific

- **Delegate by role.** The Lead calls specialists with the Agent tool using the names in
  `.claude/agents/` (`librarian`, `data-steward`, `methodologist`, `experimenter`,
  `figure-maker`, `scout`, `reviewer`). Each agent file pins its model.
- **Ask Ryan with the interactive question tool**, recommended option first. Batch related
  questions; don't drip them one at a time.
- **Skills** live in `.claude/skills/<name>/SKILL.md`. Each points to the standard or
  template it needs — load that file, not the whole `docs/` tree.
- **Hooks** (`.claude/hooks/`, wired in `.claude/settings.json`):
  - block writes/moves/deletes in `archive/`, `data/raw/`, `data/prior/` and the legacy
    folders (also when the path is given via the link target, e.g. `E:\CLEAR 2.0\RAW Data\...`,
    and via redirects, `cd`/`pushd`/`Set-Location` into them, `git clean -x/-X`,
    `git stash --all`, and recursive deletes/moves of a folder above them: `rm -rf data`);
  - guard `inbox/` too: agents may add new files and edit `inbox/_plan.yaml`; no
    Glob/Grep sweeps, deletes or overwrites there (`intake.py` does the moving);
  - block Glob/Grep sweeps over those folders, and any recursive Glob whose base folder (the
    `path` plus the pattern's leading folders) is above or inside one (repo root, `data/`,
    `E:/`; Glob ignores `.gitignore`) — scope it: `src/**/*.py`, not `**/*.py`;
    `data/processed/**/*.parquet`, not `data/**/*.parquet`;
  - exempt a command only when it really runs `python scripts/intake.py` or
    `scripts/inventory.py`, not when it merely mentions them;
  - block agents from `git commit --no-verify`/`-n` and `CLEAR_SKIP_REVIEW` (Ryan only);
  - block Read on a binary that has a mirror, and reply with the mirror path;
  - run `ruff format` + `ruff check --fix` after every `.py` edit.
- **Reviewer.** `/review` delegates to the `reviewer` subagent (Opus 5.5) in a fresh
  context — pass it the diff, spec links and checklist, never your own reasoning.
- **Bulk work** (e.g. mirroring dozens of docs) fans out to parallel `librarian` agents in
  batches; each returns a one-line summary per file, never the file contents.
- **Memory.** Durable facts about the project belong in the repo (STATUS.md, specs, ADRs),
  not in Claude memory, so other agents can see them too.
