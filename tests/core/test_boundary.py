"""Boundary: core must not import stock or blueprints."""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[2] / "anvil"
_CORE = _ROOT / "core"
_FORBIDDEN_FROM_CORE = ("anvil.stock", "anvil.blueprints")
_FORBIDDEN_FROM_STOCK = ("anvil.blueprints",)


def _imports_in(tree: ast.AST) -> list[str]:
    found: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            found.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            found.append(node.module)
    return found


def _py_files(root: Path) -> list[Path]:
    return sorted(p for p in root.rglob("*.py") if "__pycache__" not in p.parts)


@pytest.mark.parametrize("path", _py_files(_CORE), ids=lambda p: str(p.relative_to(_ROOT)))
def test_core_does_not_import_stock_or_blueprints(path: Path) -> None:
    """
    Condition:
    Every Python file under anvil.core is parsed.

    Expected:
    No import targets anvil.stock or anvil.blueprints.
    """
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    bad = [name for name in _imports_in(tree) if name.startswith(_FORBIDDEN_FROM_CORE)]
    assert bad == [], f"{path}: forbidden imports {bad}"


@pytest.mark.parametrize(
    "path",
    _py_files(_ROOT / "stock"),
    ids=lambda p: str(p.relative_to(_ROOT)),
)
def test_stock_does_not_import_blueprints(path: Path) -> None:
    """
    Condition:
    Every Python file under anvil.stock is parsed.

    Expected:
    No import targets anvil.blueprints.
    """
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    bad = [name for name in _imports_in(tree) if name.startswith(_FORBIDDEN_FROM_STOCK)]
    assert bad == [], f"{path}: forbidden imports {bad}"
