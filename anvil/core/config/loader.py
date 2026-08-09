"""anvil.core.config.loader: YAML → plain dict (extends, overrides, interpolation)."""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path
from typing import Any, cast

from omegaconf import DictConfig, ListConfig, OmegaConf

from anvil.core.config.errors import AnvilConfigError

__all__ = ["load_yaml", "register_resolvers"]

_RESOLVERS_REGISTERED = False


def register_resolvers() -> None:
    """Register custom OmegaConf resolvers once (idempotent)."""
    global _RESOLVERS_REGISTERED
    if _RESOLVERS_REGISTERED:
        return
    OmegaConf.register_new_resolver("now", _resolve_now, replace=True)
    OmegaConf.register_new_resolver("env", _resolve_env, replace=True)
    _RESOLVERS_REGISTERED = True


def load_yaml(
    path: str | Path,
    overrides: list[str] | None = None,
    *,
    config_root: str | Path | None = None,
) -> dict[str, Any]:
    """Load a YAML entrypoint to a plain dict.

    Resolution order: ``extends`` chain (depth-first, later wins), entrypoint
    file, CLI dotlist overrides, then interpolation. Returns a plain Python
    dict — no ``DictConfig`` leaves this boundary.
    """
    register_resolvers()
    entry = Path(path).resolve()
    if not entry.is_file():
        raise AnvilConfigError(f"config file not found: {entry}")
    root = Path(config_root).resolve() if config_root is not None else _find_config_root(entry)
    cfg = _load_with_extends(entry, root, chain=[str(entry)])
    if overrides:
        cfg = OmegaConf.merge(cfg, OmegaConf.from_dotlist(overrides))
    if not isinstance(cfg, DictConfig):
        raise AnvilConfigError("config root must be a mapping after merge")
    container = OmegaConf.to_container(cfg, resolve=True)
    if not isinstance(container, dict):
        raise AnvilConfigError("resolved config must be a mapping")
    return cast(dict[str, Any], container)


def _load_with_extends(file_path: Path, config_root: Path, chain: list[str]) -> DictConfig:
    raw = OmegaConf.load(file_path)
    if not isinstance(raw, DictConfig):
        raise AnvilConfigError(
            f"config file root must be a mapping: {file_path}",
            value=type(raw).__name__,
        )
    extends = raw.pop("extends", None)
    if extends is None:
        return raw
    if isinstance(extends, str):
        entries = [extends]
    elif isinstance(extends, (list, tuple, ListConfig)):
        entries = [str(item) for item in cast(Sequence[Any], extends)]
    else:
        raise AnvilConfigError(
            "'extends' must be a string or list of paths",
            path="extends",
            value=extends,
        )
    merged: DictConfig = OmegaConf.create({})
    for entry in entries:
        base = _resolve_extends(entry, config_root, chain)
        merged = cast(DictConfig, OmegaConf.merge(merged, base))
    return cast(DictConfig, OmegaConf.merge(merged, raw))


def _resolve_extends(entry: str, config_root: Path, chain: list[str]) -> DictConfig:
    base_path = (config_root / entry).resolve()
    if not base_path.suffix:
        base_path = base_path.with_suffix(".yaml")
    key = str(base_path)
    if key in chain:
        cycle = " -> ".join([*chain, key])
        raise AnvilConfigError(
            "cycle detected in extends chain",
            path="extends",
            value=entry,
            hint=cycle,
        )
    if not base_path.is_file():
        raise AnvilConfigError(
            f"extends target not found: {base_path}",
            path="extends",
            value=entry,
        )
    return _load_with_extends(base_path, config_root, chain=[*chain, key])


def _find_config_root(entrypoint: Path) -> Path:
    for parent in (entrypoint.parent, *entrypoint.parents):
        if parent.name == "configs":
            return parent
    return entrypoint.parent


def _resolve_now(pattern: str = "%Y%m%d_%H%M%S") -> str:
    from datetime import datetime

    return datetime.now().strftime(pattern)


def _resolve_env(name: str, default: str | None = None) -> str:
    import os

    value = os.environ.get(name, default)
    if value is None:
        raise AnvilConfigError(
            f"environment variable {name!r} is unset and no default was given",
            path=f"env:{name}",
        )
    return value
