"""Every public function and class in src/clear has a ``Method:`` line that resolves.

Rule: docs/standards/code.md#docstrings-numpy-style (checklist item 4: the ``Method:``
line points at a section that exists).
"""

import ast
import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
PACKAGE = REPO / "src" / "clear"
METHOD_RE = re.compile(r"^\s*Method:\s*(\S+?)#(\S+)\s*$", re.MULTILINE)


def github_anchor(heading: str) -> str:
    # GitHub heading slug: lowercase, drop punctuation (keep word chars, '-', ' '), ' ' -> '-'.
    return re.sub(r"[^\w\- ]", "", heading.strip().lower()).replace(" ", "-")


def anchors(markdown: Path) -> set[str]:
    text = markdown.read_text(encoding="utf-8")
    return {github_anchor(h) for h in re.findall(r"^#{1,6} (.+)$", text, flags=re.MULTILINE)}


def public_symbols() -> list[tuple[str, str | None]]:
    found: list[tuple[str, str | None]] = []
    for module in sorted(PACKAGE.rglob("*.py")):
        tree = ast.parse(module.read_text(encoding="utf-8"))
        for node in tree.body:
            is_def = isinstance(node, ast.FunctionDef | ast.ClassDef)
            if is_def and not node.name.startswith("_"):
                rel = module.relative_to(REPO).as_posix()
                found.append((f"{rel}::{node.name}", ast.get_docstring(node)))
    return found


@pytest.mark.parametrize(
    ("symbol", "docstring"), [pytest.param(s, d, id=s) for s, d in public_symbols()]
)
def test_public_symbol_has_resolvable_method_line(symbol: str, docstring: str | None):
    assert docstring, f"{symbol}: missing docstring"
    match = METHOD_RE.search(docstring)
    assert match, f"{symbol}: no 'Method: <path>#<anchor>' line"
    target, anchor = REPO / match.group(1), match.group(2)
    assert target.is_file(), f"{symbol}: {match.group(1)} does not exist"
    assert anchor in anchors(target), f"{symbol}: no heading #{anchor} in {match.group(1)}"
