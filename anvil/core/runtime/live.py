"""anvil.core.runtime.live: live ``nn.Module`` escape hatch helpers."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel
from torch import nn

from anvil.core.config.base import Buildable, qualname
from anvil.core.config.errors import AnvilConfigError
from anvil.core.experiment import Experiment
from anvil.core.task import _NON_MODULE_FIELDS, Task

__all__ = [
    "LIVE_MARKER_PREFIX",
    "NON_REPRODUCIBLE_HEADER",
    "assert_run_resumable",
    "dump_experiment",
    "find_live_module_paths",
    "is_live_module",
    "live_object_marker",
]

LIVE_MARKER_PREFIX = "<live object:"
NON_REPRODUCIBLE_HEADER = "# NON-REPRODUCIBLE: live module escape hatch"


def is_live_module(value: Any) -> bool:
    """Return True if ``value`` is a live ``nn.Module`` (not a Buildable config)."""
    return isinstance(value, nn.Module)


def live_object_marker(module: nn.Module) -> str:
    """Return the placeholder string written into ``config.resolved.yaml``."""
    return f"{LIVE_MARKER_PREFIX} {type(module).__name__}>"


def find_live_module_paths(task: Task) -> list[str]:
    """Return dotted ``task.<field>`` paths holding live modules."""
    paths: list[str] = []
    for name in type(task).model_fields:
        if name in _NON_MODULE_FIELDS:
            continue
        if is_live_module(getattr(task, name)):
            paths.append(f"task.{name}")
    return paths


def dump_experiment(experiment: Experiment) -> dict[str, Any]:
    """Dump an experiment to a plain dict, replacing live modules with markers.

    Args:
        experiment: Validated experiment.

    Returns:
        JSON-friendly mapping suitable for YAML (``global`` / ``task`` / ``trainer``).
    """
    return {
        "global": experiment.global_.model_dump(mode="json"),
        "task": _dump_task(experiment.task),
        "trainer": experiment.trainer.model_dump(mode="json"),
    }


def assert_run_resumable(run_dir: Any) -> None:
    """Refuse resume when the run used the live-module escape hatch.

    Args:
        run_dir: Run directory path.

    Raises:
        AnvilConfigError: If the run is marked non-reproducible.
    """
    from pathlib import Path

    root = Path(run_dir)
    marker = root / "NON_REPRODUCIBLE"
    resolved = root / "config.resolved.yaml"
    text = resolved.read_text() if resolved.is_file() else ""
    if marker.is_file() or NON_REPRODUCIBLE_HEADER in text or LIVE_MARKER_PREFIX in text:
        raise AnvilConfigError(
            "cannot resume a non-reproducible run",
            path=str(root),
            hint=(
                "this run used a live nn.Module escape hatch; "
                "re-forge from a fully serializable config"
            ),
        )


def _dump_task(task: Task) -> dict[str, Any]:
    dumped: dict[str, Any] = {"_target_": qualname(type(task))}
    for name in type(task).model_fields:
        dumped[name] = _dump_value(getattr(task, name))
    return dumped


def _dump_value(value: Any) -> Any:
    if is_live_module(value):
        return live_object_marker(value)
    if isinstance(value, Task):
        return _dump_task(value)
    if isinstance(value, Buildable):
        return value.model_dump(mode="python")
    if isinstance(value, BaseModel):
        return value.model_dump(mode="python")
    if isinstance(value, dict):
        return {key: _dump_value(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_dump_value(item) for item in value]
    return value
