"""Soft dependency checks for ``anvil.blueprints``."""

from __future__ import annotations

import importlib

__all__ = ["require_stock"]


def require_stock() -> None:
    """Ensure ``anvil.stock`` is importable.

    Raises:
        ImportError: If stock is missing, with an install hint for ``anvil[blueprints]``.
    """
    try:
        importlib.import_module("anvil.stock")
    except ImportError as exc:
        raise ImportError(
            "anvil.blueprints requires anvil.stock — install with: "
            "pip install 'anvil[blueprints]' (or 'anvil[stock]')"
        ) from exc
