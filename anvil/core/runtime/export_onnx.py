"""anvil.core.runtime.export_onnx: export a TaskModule inference graph to ONNX."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import torch
from torch import Tensor, nn

from anvil.core.config.errors import AnvilBuildError, AnvilConfigError
from anvil.core.runtime.logging import get_logger
from anvil.core.task import TaskModule

__all__ = ["export_onnx", "parse_input_shape", "InferenceWrapper"]

_log = get_logger(__name__)


class InferenceWrapper(nn.Module):
    """Thin ``nn.Module`` that exposes ``Task.example_forward`` for ONNX export.

    Lightning bookkeeping stays off the export graph.
    """

    def __init__(self, module: TaskModule) -> None:
        """Bind architecture slots from a built ``TaskModule``.

        Args:
            module: Built task module (weights already loaded).
        """
        super().__init__()
        self._task = module.task
        self._net = module.net
        for name, child in module.net.items():
            self.add_module(name, child)

    def forward(self, x: Tensor) -> Any:
        """Run the task inference graph on ``x``."""
        return self._task.example_forward(self._net, x)


def parse_input_shape(value: str | tuple[int, ...] | list[int] | None) -> tuple[int, ...] | None:
    """Parse a CLI ``1,3,32,32`` string (or pass through a tuple/list).

    Args:
        value: Comma-separated ints, sequence, or None.

    Returns:
        Shape tuple, or None when ``value`` is None.
    """
    if value is None:
        return None
    if isinstance(value, (tuple, list)):
        return tuple(int(v) for v in value)
    parts = [p.strip() for p in str(value).split(",") if p.strip()]
    if not parts:
        raise AnvilConfigError(
            "empty --input-shape",
            path="--input-shape",
            hint="e.g. --input-shape 1,3,32,32",
        )
    try:
        return tuple(int(p) for p in parts)
    except ValueError as exc:
        raise AnvilConfigError(
            "invalid --input-shape",
            path="--input-shape",
            value=value,
            hint="use comma-separated integers, e.g. 1,3,32,32",
        ) from exc


def export_onnx(
    module: TaskModule,
    out: str | Path,
    *,
    input_shape: tuple[int, ...] | None = None,
    opset: int = 17,
    input_name: str = "input",
    output_name: str = "output",
) -> Path:
    """Export ``module`` inference to an ONNX file.

    Args:
        module: Built ``TaskModule`` with weights loaded.
        out: Destination ``.onnx`` path.
        input_shape: Dummy input shape. Defaults to ``data.example_input_shape``
            with batch size forced to 1.
        opset: ONNX opset version. Defaults to 17.
        input_name: ONNX input tensor name. Defaults to ``input``.
        output_name: ONNX output tensor name. Defaults to ``output``.

    Returns:
        Absolute path written.

    Raises:
        AnvilConfigError: Missing optional ONNX deps or bad shape.
        AnvilBuildError: Export failed.
    """
    _require_onnx_deps()
    out_path = Path(out).expanduser().resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    shape = input_shape or _default_export_shape(module.task.data.example_input_shape)
    if not shape:
        raise AnvilConfigError(
            "cannot determine export input shape",
            path="task.data.example_input_shape",
            hint="pass --input-shape 1,3,H,W",
        )
    dummy = torch.randn(*shape)
    wrapper = InferenceWrapper(module).eval()
    _log.info("exporting ONNX to %s (shape=%s, opset=%s)", out_path, shape, opset)
    try:
        result = torch.onnx.export(
            wrapper,
            (dummy,),
            f=str(out_path),
            dynamo=True,
            input_names=[input_name],
            output_names=[output_name],
            opset_version=opset,
            external_data=False,
        )
        if result is not None and hasattr(result, "save") and not out_path.is_file():
            result.save(str(out_path))
    except Exception as exc:
        raise AnvilBuildError(
            "ONNX export failed",
            path="export",
            value=str(exc),
            hint="check example_forward / --input-shape; install anvil[export]",
        ) from exc
    if not out_path.is_file():
        raise AnvilBuildError(
            "ONNX export produced no file",
            path="export",
            value=str(out_path),
        )
    _log.info("wrote %s (%s bytes)", out_path, out_path.stat().st_size)
    return out_path


def _default_export_shape(example: tuple[int, ...]) -> tuple[int, ...]:
    if not example:
        return example
    return (1, *example[1:])


def _require_onnx_deps() -> None:
    missing: list[str] = []
    try:
        import onnx  # noqa: F401
    except ImportError:
        missing.append("onnx")
    try:
        import onnxscript  # noqa: F401
    except ImportError:
        missing.append("onnxscript")
    if missing:
        raise AnvilConfigError(
            "ONNX export requires optional dependencies",
            path="export",
            value=", ".join(missing),
            hint="pip install 'anvil[export]' (or 'anvil[all]')",
        )


def load_checkpoint_weights(module: TaskModule, ckpt: str | Path) -> None:
    """Load Lightning checkpoint weights into ``module``.

    Args:
        module: Built task module.
        ckpt: Path to a ``.ckpt`` file.
    """
    path = Path(ckpt)
    payload = torch.load(path, map_location="cpu", weights_only=False)
    if not isinstance(payload, dict) or "state_dict" not in payload:
        raise AnvilConfigError(
            "checkpoint missing state_dict",
            path="--ckpt",
            value=str(path),
        )
    state = payload["state_dict"]
    incompatible = module.load_state_dict(state, strict=False)
    if incompatible.missing_keys:
        _log.warning("missing keys when loading ckpt: %s", incompatible.missing_keys[:8])
    if incompatible.unexpected_keys:
        _log.warning("unexpected keys when loading ckpt: %s", incompatible.unexpected_keys[:8])
