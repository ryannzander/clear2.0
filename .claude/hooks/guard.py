"""PreToolUse guard: keep originals immutable and agents out of the binary piles.

Enforces AGENTS.md hard rules 1-3 and 9. It stops accidents; it is not a sandbox
(known limits: docs/system/01-context-layer.md, "Guard limits").

- Write/Edit/MultiEdit/NotebookEdit into a protected folder or .git/ -> blocked.
- Glob/Grep inside a protected folder or inbox/, or a recursive Glob that starts at or
  above one (repo root, data/, a folder above the repo or a data drive) -> blocked; use
  knowledge/, the INDEX files, manifests/inventory-summary.csv or Grep
  manifests/inventory.csv.
- data/raw and data/prior are usually junctions to other drives (scripts/storage.py).
  Paths given via the link target (E:/..., D:/...) map back to the repo folder and get
  the same protection.
- Read of an original that has a text mirror (per knowledge/_sources.json) -> blocked,
  with the mirror path in the message. Reading .md files is never blocked.
- Bash/PowerShell, also inside ``cmd /c``, ``powershell -c``, ``bash -c``, ``$(...)``:
  writes into a protected folder (also extract/download/fix-in-place tools), cd into one,
  deleting/moving a path that is or holds one (``data``, ``data/*/*``, the repo, ``..``, a
  data drive, a backup folder named in .env), robocopy /MIR /PURGE /MOV near them, or a
  non-ignore-aware recursive sweep (``find .``, ``ls -R data``, ``grep -r x .``) -> blocked.
  A segment that runs ``[uv run] python scripts/intake.py|inventory.py`` is exempt.
  ``cd`` carries over to later segments of the same command.
- Blocked outright: ``git clean -x/-X`` and ``git stash --all`` (they remove gitignored
  originals); and Ryan's manual bypasses of the commit guards: ``git commit
  --no-verify``, ``CLEAR_SKIP_REVIEW``, pre-commit's ``SKIP=``, ``core.hooksPath``,
  ``pre-commit uninstall``, writes into ``.git/hooks``.
- inbox/: no sweeps, deletes or overwrites; agents may add files and edit _plan.yaml.
- Relative paths resolve against the payload ``cwd`` (the shell's working folder).

One stdlib-only file by design: it runs standalone under the system Python (>= 3.10),
before any project environment exists. Reads the hook JSON from stdin. Exit 2 + stderr =
block; exit 0 = allow. An internal error allows the call (exit 0, traceback on stderr) so
a bug here never wedges a session.
"""

from __future__ import annotations

import json
import os
import re
import shlex
import sys
import traceback
from pathlib import Path
from typing import Any

PROTECTED_DIRS: tuple[str, ...] = (
    "archive",
    "data/raw",
    "data/prior",
    "CLEAR 2.0 (misc docs)",
    "RAW Data",
)
EXEMPT_SCRIPTS: tuple[str, ...] = ("scripts/intake.py", "scripts/inventory.py")
SOURCES_JSON = "knowledge/_sources.json"
# inbox/ holds files waiting for intake: no sweeps, no deletes, no overwrites. Agents may
# add new files and edit these two.
INBOX = "inbox"
INBOX_WRITABLE: frozenset[str] = frozenset({"inbox/_plan.yaml", "inbox/readme.md"})
WILDCARD_CHARS = "*?[{"

# Recursive listers that ignore .gitignore/.ignore (rg and fd honour them, so are allowed).
SWEEP_VERBS: frozenset[str] = frozenset({"find", "tree"})
IGNORE_AWARE_VERBS: frozenset[str] = frozenset({"rg", "fd", "fdfind"})
LIST_VERBS: frozenset[str] = frozenset({"ls", "dir", "gci", "get-childitem"})
GREP_VERBS: frozenset[str] = frozenset({"grep", "egrep", "fgrep", "select-string", "sls"})
DELETE_VERBS: frozenset[str] = frozenset(
    {"rm", "rmdir", "unlink", "shred", "del", "erase", "rd", "remove-item", "ri"}
)
MOVE_VERBS: frozenset[str] = frozenset(
    {"mv", "move", "move-item", "mi", "ren", "rename", "rename-item", "rni"}
)
MUTATE_VERBS: frozenset[str] = (
    DELETE_VERBS
    | MOVE_VERBS
    | frozenset(
        {
            "clear-content",
            "clc",
            "set-content",
            "sc",
            "add-content",
            "ac",
            "out-file",
            "new-item",
            "ni",
            "touch",
            "mkdir",
            "md",
            "truncate",
            "ln",
            "chmod",
            "chown",
            "tee",
            # extract, convert or download in place: every path operand may be written
            "unzip",
            "7z",
            "tar",
            "gzip",
            "gunzip",
            "bunzip2",
            "xz",
            "unxz",
            "expand-archive",
            "dos2unix",
            "unix2dos",
            "curl",
            "wget",
            "invoke-webrequest",
            "iwr",
            "invoke-restmethod",
            "irm",
        }
    )
)
COPY_VERBS: frozenset[str] = frozenset(
    {"cp", "copy", "copy-item", "cpi", "robocopy", "xcopy", "rsync"}
)
# cmd-style verbs take /X switches; elsewhere /e is a Git Bash drive root, not a switch.
CMD_STYLE_VERBS: frozenset[str] = frozenset(
    {
        "cmd",
        "robocopy",
        "xcopy",
        "dir",
        "del",
        "erase",
        "rd",
        "rmdir",
        "copy",
        "move",
        "ren",
        "tree",
    }
)
# Which shell parses the text: bash has backslash escapes (`RAW\ Data`, `\"`); PowerShell
# and cmd do not, so there every backslash is a path separator (`data\raw\`).
BASH, POWERSHELL, CMD = "bash", "powershell", "cmd"
WRAPPER_SHELLS: dict[str, tuple[str, tuple[str, ...]]] = {
    "cmd": (CMD, ("/c", "/k")),
    "powershell": (POWERSHELL, ("-c", "-command")),
    "pwsh": (POWERSHELL, ("-c", "-command")),
    "bash": (BASH, ("-c", "-lc")),
    "sh": (BASH, ("-c", "-lc")),
    "zsh": (BASH, ("-c", "-lc")),
}
GIT_COMMIT_VALUE_OPTIONS: frozenset[str] = frozenset(
    {"-m", "-F", "-C", "-c", "-t", "--message", "--file", "--author", "--date", "--template"}
)
SWITCH_RE = re.compile(r"^/[A-Za-z?]+(:\S*)?$")
ROBOCOPY_DELETING: frozenset[str] = frozenset({"/mir", "/purge", "/mov", "/move"})
RG_NO_IGNORE: frozenset[str] = frozenset(
    {"-u", "-uu", "-uuu", "--no-ignore", "--no-ignore-dot", "--no-ignore-vcs", "--unrestricted"}
)
INPLACE_VERBS: frozenset[str] = frozenset({"sed", "perl"})
CD_VERBS: frozenset[str] = frozenset(
    {"cd", "chdir", "pushd", "set-location", "sl", "push-location"}
)
PYTHON_VERBS: frozenset[str] = frozenset({"python", "python3", "py"})
# git options that take a value before the subcommand: `git -C <dir> clean -fdx`.
GIT_VALUE_OPTIONS: frozenset[str] = frozenset(
    {"-C", "-c", "--git-dir", "--work-tree", "--namespace", "--config-env"}
)
WILDCARD_TARGETS: frozenset[str] = frozenset({"*", ".", "./", "./*", "/*", ".\\*", ".\\"})
SKIP_PREFIX_TOKENS: frozenset[str] = frozenset(
    {"sudo", "command", "&", ".", "exec", "nohup", "time", "env"}
)

# Segment separators outside quotes: || && ; | newline, and a lone & (bash background, cmd
# separator) but not the & in 2>&1, &> or >&.
SEPARATOR_RE = re.compile(r"\|\||&&|;|\||\n|(?<![>&])&(?![>&])")
SUBSTITUTION_RE = re.compile(r"\$\(([^()]*)\)|`([^`]*)`")
REDIRECT_RE = re.compile(r">{1,2}\s*(?:\"([^\"]*)\"|'([^']*)'|([^\s\"'|;&]+))")
REDIRECT_TOKEN_RE = re.compile(r"^\d*>>?(?!&)(.*)$")
BACKUP_ENV_PREFIX = "CLEAR_BACKUP_"
BYPASSES: tuple[tuple[re.Pattern[str], str], ...] = (
    (
        re.compile(
            r"(?i)CLEAR_SKIP_REVIEW\s*=|Env:CLEAR_SKIP_REVIEW\b"
            r"|SetEnvironmentVariable\(\s*['\"]CLEAR_SKIP_REVIEW"
        ),
        "CLEAR_SKIP_REVIEW is Ryan's manual bypass of the review gate. Agents run /review.",
    ),
    (
        re.compile(r"(?i)(?:^|[\s;(])(?:export\s+|set\s+|\$env:)?SKIP\s*=|Env:SKIP\b"),
        "pre-commit's SKIP= turns commit hooks (and the review gate) off. Ryan only.",
    ),
    (re.compile(r"(?i)core\.hooksPath"), "Changing core.hooksPath turns the commit guards off."),
    (
        re.compile(r"(?i)pre-commit\s+uninstall"),
        "pre-commit uninstall turns the commit guards off.",
    ),
)


class BlockedError(Exception):
    """Raised with the message to show the agent."""


# ------------------------------------------------------------------------ paths


def project_root(payload: dict[str, Any]) -> Path:
    return Path(os.environ.get("CLAUDE_PROJECT_DIR") or payload.get("cwd") or os.getcwd())


def absolute(raw: str, cwd: Path) -> Path:
    """Return any path form (relative to ``cwd``, ~, /c/... Git Bash style) as absolute."""
    text = os.path.expanduser(raw.strip().strip("\"'")).replace("\\", "/")
    drive = re.match(r"^/([a-zA-Z])(?:/(.*))?$", text)  # /e and /e/x are Git Bash drives
    if drive and os.name == "nt":
        text = f"{drive.group(1)}:/{drive.group(2) or ''}"
    path = Path(text)
    return path if path.is_absolute() else cwd / text


def to_repo_rel(raw: str, root: Path, cwd: Path | None = None) -> str | None:
    """Normalize any path form to repo-relative POSIX; None if outside the repo.

    Relative paths resolve against ``cwd`` (the shell's working folder), default the root.
    """
    if not raw.strip().strip("\"'"):
        return ""
    path = absolute(raw, cwd or root)
    real = os.path.realpath(path)  # resolves the existing part; a new file's name is kept
    for target, folder in link_targets(root):
        inside = _relative(real, target)
        if inside is not None:
            return folder if inside == "" else f"{folder}/{inside}"
    return _relative(path, root)


def _relative(path: Path | str, base: Path | str) -> str | None:
    """Return ``path`` relative to ``base`` as POSIX ("" for base itself); None if outside."""
    try:
        rel = os.path.normpath(os.path.relpath(path, base)).replace("\\", "/")
    except ValueError:  # different drive on Windows
        return None
    if rel == ".":
        return ""
    return None if rel.startswith("../") or rel == ".." else rel


def link_targets(root: Path) -> list[tuple[str, str]]:
    """(real target, repo folder) for each protected folder that is a link elsewhere."""
    pairs: list[tuple[str, str]] = []
    for folder in PROTECTED_DIRS:
        real = os.path.realpath(root / folder)
        expected = os.path.join(os.path.realpath(root), *folder.split("/"))
        if os.path.normcase(real) != os.path.normcase(expected):
            pairs.append((real, folder))
    return pairs


def is_protected(rel: str | None) -> bool:
    if not rel:
        return False
    low = rel.lower()
    return any(low == d.lower() or low.startswith(d.lower() + "/") for d in PROTECTED_DIRS)


def contains_protected(rel: str) -> bool:
    """Return True if folder ``rel`` ("" = repo root) has a protected folder below it."""
    low = rel.lower().strip("/")
    return any(not low or d.lower().startswith(low + "/") for d in PROTECTED_DIRS)


def in_inbox(rel: str | None) -> bool:
    low = (rel or "").lower()
    return low == INBOX or low.startswith(INBOX + "/")


def in_git_dir(rel: str | None) -> bool:
    """Return True for .git/hooks and .git/config: they decide whether the guards run."""
    low = (rel or "").lower()
    return low in (".git", ".git/config", ".git/hooks") or low.startswith(".git/hooks/")


def waiting_inbox_file(rel: str | None, root: Path) -> bool:
    """Return True for an existing inbox file (not folder) other than the plan/README."""
    low = (rel or "").lower()
    return in_inbox(rel) and low not in INBOX_WRITABLE and (root / str(rel)).is_file()


def backup_dirs(root: Path) -> list[str]:
    """Return the backup folders named by ``CLEAR_BACKUP_*`` keys in the repo-root .env."""
    env = root / ".env"
    if not env.is_file():
        return []
    dirs: list[str] = []
    for line in env.read_text(encoding="utf-8-sig", errors="replace").splitlines():
        key, _, value = line.strip().partition("=")
        if key.strip().startswith(BACKUP_ENV_PREFIX) and value.strip():
            dirs.append(value.strip().strip("\"'"))
    return dirs


def holds_originals(raw: str, root: Path, cwd: Path) -> bool:
    """Return True if deleting/moving ``raw`` would touch originals, backups or inbox files.

    That is: a protected path, a folder above one (``data``, the repo root, ``..``), an
    inbox file other than the plan, or, outside the repo, a folder at or above the repo,
    a link target (a data drive) or a backup folder, or anything inside a backup folder.
    """
    rel = to_repo_rel(raw or ".", root, cwd)
    if rel is not None:
        if in_inbox(rel):
            return rel.lower() not in INBOX_WRITABLE
        return is_protected(rel) or contains_protected(rel)
    path = absolute(raw, cwd)
    backups = backup_dirs(root)
    above = [str(root), *(target for target, _ in link_targets(root)), *backups]
    inside_backup = any(_relative(path, b) is not None for b in backups)
    return inside_backup or any(_relative(t, path) is not None for t in above)


def wildcard_prefix(path: str) -> tuple[str, bool]:
    """Split a glob/wildcard path into (literal leading folders, wildcard in a folder?).

    ``data/*/*`` -> ("data", True); ``data/interim/*.parquet`` -> ("data/interim", False).
    """
    segments = path.replace("\\", "/").split("/")
    first = next((i for i, s in enumerate(segments) if any(c in s for c in WILDCARD_CHARS)), None)
    if first is None:
        return path, False
    return "/".join(segments[:first]), first < len(segments) - 1


def has_wildcard(text: str) -> bool:
    return any(c in text for c in WILDCARD_CHARS)


def mentions_protected(segment: str, root: Path, shell: str = BASH) -> bool:
    """Return True if the text names a protected folder as a path (not a sub-folder name)."""
    text = segment.replace("\\ ", " ") if shell == BASH else segment  # bash `RAW\ Data`
    text = " " + text.replace("\\", "/").lower()
    root_text = str(root).replace("\\", "/").lower().rstrip("/") + "/"
    text = text.replace(root_text, " ")
    if re.match(r"^[a-z]:/", root_text):  # Git Bash spelling: /c/users/...
        text = text.replace(f"/{root_text[0]}/{root_text[3:]}", " ")
    text = re.sub(r"(?<=[\s\"'=(])\./", "", text)
    for d in PROTECTED_DIRS:
        if re.search(r"[\s\"'=(]" + re.escape(d.lower()) + r"(?:$|[/\s\"')])", text):
            return True
    return any(target.replace("\\", "/").lower() in text for target, _ in link_targets(root))


def load_mirrors(root: Path) -> dict[str, str]:
    path = root / SOURCES_JSON
    if not path.is_file():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    return {k.lower(): str(v.get("mirror", "")) for k, v in data.items() if isinstance(v, dict)}


# ------------------------------------------------------------------------ tools


def guard_write(tool_input: dict[str, Any], root: Path, cwd: Path) -> None:
    raw = str(tool_input.get("file_path") or tool_input.get("notebook_path") or "")
    rel = to_repo_rel(raw, root, cwd)
    if is_protected(rel):
        raise BlockedError(
            f"{rel} is inside a read-only originals folder (AGENTS.md rule 1). Originals "
            "change only via scripts/intake.py (/map-refresh) or /ingest."
        )
    if in_git_dir(rel):
        raise BlockedError(f"{rel}: .git/ (hooks, config) controls the commit guards. Ryan only.")
    if waiting_inbox_file(rel, root):
        raise BlockedError(
            f"{rel} is waiting for intake: don't change it. Only scripts/intake.py moves inbox "
            "files; agents may add new files and edit inbox/_plan.yaml."
        )


def guard_read(tool_input: dict[str, Any], root: Path, cwd: Path) -> None:
    rel = to_repo_rel(str(tool_input.get("file_path") or ""), root, cwd)
    if not rel or rel.lower().endswith(".md"):
        return
    mirror = load_mirrors(root).get(rel.lower())
    if mirror:
        raise BlockedError(
            f"{rel} has a text mirror. Read {mirror} instead (AGENTS.md rule 3) — "
            "it is cheaper and is what the specs cite."
        )


def guard_glob(tool_input: dict[str, Any], root: Path, cwd: Path) -> None:
    raw = str(tool_input.get("path") or "")
    pattern = str(tool_input.get("pattern") or "").replace("\\", "/")
    base = absolute(raw, cwd) if raw.strip() else cwd
    prefix, _ = wildcard_prefix(pattern)
    start = absolute(prefix, base) if prefix else base  # where the walk really begins
    start_rel = to_repo_rel(str(start), root)
    if is_protected(start_rel) or in_inbox(start_rel):
        raise BlockedError(_sweep_message())
    # Claude Code's Glob ignores .gitignore/.ignore, so a recursive glob that starts at or
    # above a protected folder (repo root, data/, a parent folder) walks into the originals.
    if "**" in pattern and holds_originals(str(start), root, cwd):
        raise BlockedError(
            f"A recursive glob from {start_rel or start}/ walks into the originals. Scope "
            "`path` (or the pattern's first folders) to a working folder, e.g. src/, docs/, "
            "data/processed/; for originals read manifests/inventory-summary.csv, then "
            "knowledge/ or Grep manifests/inventory.csv."
        )


def guard_grep(tool_input: dict[str, Any], root: Path, cwd: Path) -> None:
    rel = to_repo_rel(str(tool_input.get("path") or "."), root, cwd)
    glob = str(tool_input.get("glob") or "").replace("\\", "/").lower()
    glob = glob[2:] if glob.startswith("./") else glob
    glob_hits = any(glob == d.lower() or glob.startswith(d.lower() + "/") for d in PROTECTED_DIRS)
    inbox_sweep = in_inbox(rel) and (rel or "").lower() not in INBOX_WRITABLE
    if is_protected(rel) or inbox_sweep or glob_hits:
        raise BlockedError(_sweep_message())


def _sweep_message() -> str:
    return (
        "Searching inside archive/, data/raw/, data/prior/, inbox/ or the legacy folders is "
        "blocked (AGENTS.md rule 2). Use knowledge/ (mirrors + data cards), the INDEX.md files, "
        "manifests/inventory-summary.csv (one row per dataset folder), or Grep "
        "manifests/inventory.csv."
    )


# ------------------------------------------------------------------------ shell


def _tokens(segment: str) -> list[str]:
    try:
        return shlex.split(segment, posix=True)
    except ValueError:
        return segment.split()


def _verb_and_args(tokens: list[str]) -> tuple[str, list[str]]:
    idx = 0
    while idx < len(tokens) and (
        tokens[idx] in SKIP_PREFIX_TOKENS or re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", tokens[idx])
    ):
        idx += 1
    if idx >= len(tokens):
        return "", []
    verb = tokens[idx].replace("\\", "/").rsplit("/", 1)[-1].lower()
    verb = verb[:-4] if verb.endswith(".exe") else verb
    return verb, tokens[idx + 1 :]


def _non_flags(args: list[str], verb: str = "") -> list[str]:
    """Return the operands: not -flags, not /switches for cmd-style verbs.

    A PowerShell ``-Path:data`` colon parameter yields its value as an operand.
    """
    cmd_style = verb in CMD_STYLE_VERBS
    operands: list[str] = []
    for a in args:
        colon = re.match(r"^-[A-Za-z]+:(.+)$", a)
        if colon:
            operands.append(colon.group(1))
        elif a and not a.startswith("-") and not (cmd_style and SWITCH_RE.match(a)):
            operands.append(a)
    return operands


def _is_recursive_flag(verb: str, arg: str, shell: str) -> bool:
    low = arg.lower()
    if low.startswith(("-rec", "-depth")) or low in ("--recursive", "/s"):
        return True
    if re.fullmatch(r"-[A-Za-z]{1,4}", arg) is None:
        return False
    letters = arg[1:]
    if verb == "ls" and shell == BASH:  # GNU ls: -R recursive, -r reverse
        return "R" in letters
    return "r" in letters.lower()  # rm -rf, grep -r, PowerShell -r(ecurse)


def _is_recursive_listing(verb: str, args: list[str], shell: str) -> bool:
    if verb in SWEEP_VERBS:
        return True
    if verb in LIST_VERBS or verb in GREP_VERBS:
        return any(_is_recursive_flag(verb, a, shell) for a in args)
    if verb == "rg":  # rg honours .ignore unless told not to
        return any(a.lower() in RG_NO_IGNORE for a in args)
    return False


def _git_danger(verb: str, args: list[str]) -> str | None:
    if verb != "git":
        return None
    i = 0  # skip global options: `git -C <dir> -c k=v clean -fdx`
    while i < len(args) and args[i].startswith("-"):
        i += 2 if args[i] in GIT_VALUE_OPTIONS else 1
    if i >= len(args):
        return None
    sub, flags = args[i], args[i + 1 :]
    short = [f for f in flags if f.startswith("-") and not f.startswith("--")]
    if sub == "clean" and any("x" in f or "X" in f for f in short):
        return "`git clean -x/-X` deletes gitignored files — that includes every original."
    if sub == "stash" and any(f in ("-a", "--all") for f in flags):
        return "`git stash --all` moves gitignored files — that includes every original."
    if sub == "commit" and _skips_hooks(flags):
        return "`git commit --no-verify` skips the guards and the review gate; Ryan only."
    return None


def _skips_hooks(commit_args: list[str]) -> bool:
    """Return True for ``git commit --no-verify`` / ``-n`` (option values are skipped)."""
    i = 0
    while i < len(commit_args):
        arg = commit_args[i]
        if arg in GIT_COMMIT_VALUE_OPTIONS:  # -m "- add x" is a message, not a flag
            i += 2
            continue
        if arg == "--no-verify" or (re.fullmatch(r"-[A-Za-z]+", arg) and "n" in arg[1:]):
            return True
        i += 1
    return False


def _wrapped_command(verb: str, args: list[str]) -> tuple[str, str] | None:
    """Return (inner command, its shell) for ``cmd /c``, ``powershell -c``, ``bash -c``."""
    if verb not in WRAPPER_SHELLS:
        return None
    shell, flags = WRAPPER_SHELLS[verb]
    i = next((k for k, a in enumerate(args) if a.lower() in flags), None)
    if i is None:
        return None
    rest = args[i + 1 :]
    return (rest[0] if len(rest) == 1 else shlex.join(rest)), shell


def _runs_exempt_script(verb: str, args: list[str]) -> bool:
    """Return True only for ``[uv run] python scripts/intake.py|inventory.py ...`` itself."""
    if verb == "uv" and args[:1] == ["run"]:
        rest = args[1:]
        while rest and rest[0].startswith("-"):
            rest = rest[1:]
        verb, args = _verb_and_args(rest)
    if verb not in PYTHON_VERBS:
        return False
    script = next((a for a in args if not a.startswith("-")), "")
    return script.replace("\\", "/").lower().endswith(EXEMPT_SCRIPTS)


def _redirect_targets(segment: str, tokens: list[str]) -> list[str]:
    """Redirect targets from the tokens (quotes, escaped spaces) and the raw text (x>f)."""
    targets: list[str] = []
    for i, tok in enumerate(tokens):
        m = REDIRECT_TOKEN_RE.match(tok)
        target = (m.group(1) or (tokens[i + 1] if i + 1 < len(tokens) else "")) if m else ""
        if target and not target.startswith("&"):
            targets.append(target)
    unquoted = re.sub(r"\"[^\"]*\"|'[^']*'", " ", segment)  # `-m 'a > archive/x'` is text
    targets += [next(g for g in gs if g) for gs in REDIRECT_RE.findall(unquoted) if any(gs)]
    return targets


def _changes_dir(paths: list[str], root: Path, cwd: Path) -> Path:
    """Check a cd and return the new working folder for later segments."""
    if any(is_protected(to_repo_rel(p, root, cwd)) for p in paths):
        raise BlockedError(
            "Don't cd into an originals folder: work from the repo root and read knowledge/."
        )
    return absolute(paths[0], cwd) if paths and paths[0] != "-" else cwd


def _check_delete_or_move(verb: str, args: list[str], root: Path, cwd: Path, shell: str) -> None:
    if verb not in DELETE_VERBS | MOVE_VERBS:
        return
    if verb in DELETE_VERBS and any(a in WILDCARD_TARGETS for a in args):
        raise BlockedError("A wildcard delete could hit the originals. Name the files explicitly.")
    recursive = any(_is_recursive_flag(verb, a, shell) for a in args)
    for path in _non_flags(args, verb):
        if has_wildcard(path):  # judged by its literal leading folders: data/*/* -> data
            prefix, in_folder = wildcard_prefix(path)
            risky = in_folder or recursive or verb in MOVE_VERBS or prefix not in ("", ".")
            hit = risky and holds_originals(prefix or ".", root, cwd)
        else:
            hit = holds_originals(path, root, cwd)
        if hit:
            raise BlockedError(
                "This would delete or move originals, inbox files, or a folder that holds them "
                "(data/, the repo, a data drive). Name the exact files; originals change only "
                "via scripts/intake.py (/map-refresh) or /ingest."
            )


def _scanned_paths(verb: str, args: list[str]) -> list[str]:
    """Return the folders a listing/search command walks (default: the working folder)."""
    if verb == "find":  # paths come before the expression (-name, !, ...)
        scan = []
        for a in args:
            if a.startswith(("-", "(", "!")):
                break
            scan.append(a)
    elif verb in GREP_VERBS or verb == "rg":  # first operand is the pattern
        scan = _non_flags(args, verb)[1:]
    else:  # ls/dir/gci/tree/fd: skip PowerShell option values (-Filter *.py)
        scan, skip = [], False
        for a in args:
            if skip:
                skip = False
            elif a.lower() in ("-filter", "-include", "-exclude", "-depth"):
                skip = True
            elif a in _non_flags([a], verb):
                scan.append(a)
    return scan or ["."]


def _check_sweep(verb: str, args: list[str], root: Path, cwd: Path, shell: str) -> None:
    scan = _scanned_paths(verb, args)
    if _is_recursive_listing(verb, args, shell):
        hit = any(holds_originals(wildcard_prefix(p)[0] or ".", root, cwd) for p in scan)
    elif verb in IGNORE_AWARE_VERBS:  # they skip ignored folders unless one is named
        hit = any(is_protected(to_repo_rel(p, root, cwd)) for p in scan)
    else:
        hit = False
    if hit:
        raise BlockedError(_sweep_message())


def _copy_targets(verb: str, args: list[str], root: Path, cwd: Path) -> list[str]:
    """Return what a copy writes: its destination (robocopy/xcopy: 2nd operand, else last)."""
    paths = _non_flags(args, verb)
    flags = {a.lower() for a in args}
    deleting = flags & ROBOCOPY_DELETING if verb in ("robocopy", "xcopy") else set()
    if verb == "rsync":
        deleting = {a for a in flags if a.startswith("--delete") or a == "--remove-source-files"}
    ends = paths[:2] if verb in ("robocopy", "xcopy") else paths[:1] + paths[-1:]
    if deleting and any(holds_originals(p, root, cwd) for p in ends):
        raise BlockedError(
            "robocopy /MIR, /PURGE, /MOV(E) and rsync --delete remove files: never point them "
            "at originals or a backup. Copy only missing files: /E /XC /XN /XO (/backup-check)."
        )
    if verb not in ("robocopy", "xcopy"):
        return paths[-1:]
    return paths[:2] if flags & {"/mov", "/move"} else paths[1:2]


def _into_folder(verb: str, args: list[str], root: Path, cwd: Path) -> list[str | None]:
    """For cp/mv into an existing folder, the files it would create: <folder>/<source name>."""
    paths = _non_flags(args, verb)
    if verb not in COPY_VERBS | MOVE_VERBS or len(paths) < 2:
        return []
    folder = to_repo_rel(paths[-1], root, cwd)
    if folder is None or not (root / folder).is_dir():
        return []
    names = [p.replace("\\", "/").rstrip("/").rsplit("/", 1)[-1] for p in paths[:-1]]
    return [f"{folder}/{name}" if folder else name for name in names]


def _check_writes(
    segment: str,
    tokens: list[str],
    verb: str,
    args: list[str],
    ctx: tuple[Path, Path, str],
) -> None:
    root, cwd, shell = ctx
    paths = _non_flags(args, verb)
    written = [to_repo_rel(t, root, cwd) for t in _redirect_targets(segment, tokens)]
    written += _into_folder(verb, args, root, cwd)
    if verb in COPY_VERBS:
        written += [to_repo_rel(d, root, cwd) for d in _copy_targets(verb, args, root, cwd)]
    inplace = verb in INPLACE_VERBS and any(
        a == "--in-place" or (a.startswith("-") and not a.startswith("--") and "i" in a[1:])
        for a in args
    )
    inplace = inplace or (verb == "ruff" and ("--fix" in args or args[:1] == ["format"]))
    mutates = verb in MUTATE_VERBS or inplace
    if mutates:
        written += [to_repo_rel(p, root, cwd) for p in paths]
    # Name check too: unquoted names with spaces (RAW Data/x) split into several tokens.
    named = mutates and mentions_protected(segment, root, shell)
    if named or any(is_protected(rel) for rel in written):
        raise BlockedError(
            "This command would change a read-only originals folder (AGENTS.md rule 1). "
            "Use scripts/intake.py (/map-refresh) or /ingest."
        )
    if any(in_git_dir(rel) for rel in written):
        raise BlockedError(".git/ (hooks, config) controls the commit guards. Ryan only.")
    if any(waiting_inbox_file(rel, root) for rel in written):
        raise BlockedError(
            "This would overwrite a file waiting in inbox/. Only scripts/intake.py moves inbox "
            "files; add new files or edit inbox/_plan.yaml instead."
        )


def check_segment(segment: str, root: Path, cwd: Path, shell: str) -> Path:
    """Check one simple command; return the working folder for the next segment."""
    for pattern, message in BYPASSES:
        if pattern.search(segment):
            raise BlockedError(message)
    # Backslashes become slashes (posix shlex would eat them). Only in bash is a backslash
    # before a space an escape (`RAW\ Data` -> one token); in PowerShell/cmd `data\raw\ x`
    # is a folder path followed by another argument.
    if shell == BASH:
        tokens = _tokens(re.sub(r"\\(?! )", "/", segment))
    else:
        tokens = _tokens(segment.replace("\\", "/"))
    verb, args = _verb_and_args(tokens)
    wrapped = _wrapped_command(verb, args)
    if wrapped is not None:
        check_command(wrapped[0], root, cwd, wrapped[1])
        return cwd
    if _runs_exempt_script(verb, args):
        return cwd
    if danger := _git_danger(verb, args):
        raise BlockedError(danger)
    if verb in CD_VERBS:
        return _changes_dir(_non_flags(args, verb), root, cwd)
    _check_delete_or_move(verb, args, root, cwd, shell)
    _check_sweep(verb, args, root, cwd, shell)
    _check_writes(segment, tokens, verb, args, (root, cwd, shell))
    return cwd


def split_commands(command: str, shell: str = BASH) -> list[str]:
    """Split a command line on separators outside quotes (``a | 'x|y'`` -> 2 parts).

    Only bash escapes a quote with a backslash; in PowerShell/cmd a quoted path that ends
    in a backslash still ends at its closing quote.
    """
    parts: list[str] = []
    start, quote, i = 0, "", 0
    while i < len(command):
        c = command[i]
        if quote:
            escaped = shell == BASH and quote == '"' and c == "\\"
            i += 2 if escaped else 1
            quote = "" if (c == quote and not escaped) else quote
        elif c in "\"'":
            quote, i = c, i + 1
        elif m := SEPARATOR_RE.match(command, i):
            parts.append(command[start:i])
            start = i = m.end()
        else:
            i += 1
    parts.append(command[start:])
    return parts


def check_command(command: str, root: Path, cwd: Path, shell: str) -> None:
    for groups in SUBSTITUTION_RE.findall(command):  # $(...) and `...` run too
        check_command(next((g for g in groups if g), ""), root, cwd, shell)
    for segment in split_commands(command, shell):
        segment = segment.strip().lstrip("(").rstrip(")").strip()  # (subshell)
        if segment:
            cwd = check_segment(segment, root, cwd, shell)


def guard_bash(tool_input: dict[str, Any], root: Path, cwd: Path) -> None:
    check_command(str(tool_input.get("command") or ""), root, cwd, BASH)


def guard_powershell(tool_input: dict[str, Any], root: Path, cwd: Path) -> None:
    check_command(str(tool_input.get("command") or ""), root, cwd, POWERSHELL)


HANDLERS = {
    "Write": guard_write,
    "Edit": guard_write,
    "MultiEdit": guard_write,
    "NotebookEdit": guard_write,
    "Read": guard_read,
    "Glob": guard_glob,
    "Grep": guard_grep,
    "Bash": guard_bash,
    "PowerShell": guard_powershell,
}


def main() -> int:
    if hasattr(sys.stderr, "reconfigure"):  # the system Python may default to cp1252
        sys.stderr.reconfigure(encoding="utf-8")  # type: ignore[union-attr]
    try:
        # Bytes + utf-8-sig: the system Python may default to cp1252, and PowerShell pipes
        # prepend a BOM.
        payload = json.loads(sys.stdin.buffer.read().decode("utf-8-sig") or "{}")
        handler = HANDLERS.get(str(payload.get("tool_name", "")))
        if handler is None:
            return 0
        root = project_root(payload)
        cwd = Path(str(payload.get("cwd") or root))  # the shell's folder; relative paths
        handler(payload.get("tool_input") or {}, root, cwd)
    except BlockedError as blocked:
        print(f"BLOCKED by .claude/hooks/guard.py: {blocked}", file=sys.stderr)
        return 2
    except Exception:  # noqa: BLE001 — a guard bug must never wedge the session
        print("guard.py internal error (call allowed):", file=sys.stderr)
        traceback.print_exc()
        return 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
