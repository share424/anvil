"""anvil.core.runtime.shapecheck: meta-device forward before smoke."""

from __future__ import annotations

from pathlib import Path

import torch

from anvil.core.config.errors import AnvilShapeError
from anvil.core.runtime.logging import get_logger
from anvil.core.task import Task, TaskModule

__all__ = ["check_shapes"]

_log = get_logger(__name__)


def check_shapes(task: Task, module: TaskModule, log_path: Path | None = None) -> None:
    """Rebuild-forward on the meta device to catch wiring bugs early.

    Args:
        task: Validated task config (for ``example_input_shape`` / forward).
        module: Built ``TaskModule`` (used for reporting; forward uses a meta copy).
        log_path: Optional ``shapes.txt`` path. Defaults to None.

    Raises:
        AnvilShapeError: If the meta forward fails with a real shape error.
    """
    _ = module
    shape = task.data.example_input_shape
    lines = [f"example_input_shape: {shape}"]
    try:
        with torch.device("meta"):
            net = task.build_net()
            x = torch.empty(shape, device="meta")
            out = task.example_forward(net, x)
        lines.append(f"meta forward ok: output_type={type(out).__name__}")
    except NotImplementedError as exc:
        lines.append(f"meta forward skipped (NotImplementedError): {exc}")
        _log.warning("shape check skipped: %s", exc)
    except Exception as exc:
        lines.append(f"meta forward FAILED: {type(exc).__name__}: {exc}")
        if log_path is not None:
            log_path.write_text("\n".join(lines) + "\n")
        raise AnvilShapeError(
            "meta-device shape check failed",
            path=type(task).__name__,
            value=str(exc),
            hint="check module channel/spatial wiring or example_input_shape",
        ) from exc
    if log_path is not None:
        log_path.write_text("\n".join(lines) + "\n")
