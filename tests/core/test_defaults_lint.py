"""Phase 2: no bare Buildable field defaults in anvil package sources."""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[2] / "anvil"


def _py_files() -> list[Path]:
    return sorted(p for p in _ROOT.rglob("*.py") if "__pycache__" not in p.parts)


@pytest.mark.parametrize("path", _py_files(), ids=lambda p: str(p.relative_to(_ROOT)))
def test_no_bare_buildable_defaults(path: Path) -> None:
    """
    Condition:
    Each anvil source file is parsed for AnnAssign / default field values.

    Expected:
    No ``Field(default=SomeBuildable(...))`` or bare ``= SomeBuildable(`` on class bodies
    that look like pydantic defaults — use default_factory instead.
    """
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    offenders = _find_bare_defaults(tree)
    assert offenders == [], f"{path}: bare Buildable defaults {offenders}"


def _find_bare_defaults(tree: ast.AST) -> list[str]:
    found: list[str] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        if _is_name(node.func, "Field") and _has_default_kw(node):
            found.append(f"Field(default=...) at line {node.lineno}")
    return found


def _is_name(node: ast.AST, name: str) -> bool:
    return isinstance(node, ast.Name) and node.id == name


def _has_default_kw(call: ast.Call) -> bool:
    for keyword in call.keywords:
        if keyword.arg == "default" and isinstance(keyword.value, ast.Call):
            return True
    return False
