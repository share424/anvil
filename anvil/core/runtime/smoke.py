"""anvil.core.runtime.smoke: one-batch pre-flight check."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import torch
from torch import Tensor

from anvil.core.config.errors import AnvilSmokeError
from anvil.core.contracts import Stage
from anvil.core.runtime.batchcheck import check_batch
from anvil.core.runtime.logging import get_logger
from anvil.core.task import TaskModule

__all__ = ["check"]

_log = get_logger(__name__)


def check(
    module: TaskModule,
    datamodule: Any,
    *,
    log_path: Path | None = None,
) -> None:
    """Run one train batch (with backward) and one val batch.

    Args:
        module: Built task module.
        datamodule: Lightning datamodule with train/val loaders.
        log_path: Optional ``smoke.txt`` path. Defaults to None.

    Raises:
        AnvilSmokeError: If loss is non-finite or no gradients flow.
    """
    lines: list[str] = []
    train_loader = datamodule.train_dataloader()
    batch = next(iter(train_loader))
    lines.append(_describe_batch("train", batch))
    check_batch(batch, module.task.batch_type, enabled=module.check_batches)
    module.train()
    output = module.task.step(module.net, batch, Stage.TRAIN)
    _assert_finite_scalar(output.loss, "train")
    output.loss.backward()
    _assert_some_grad(module, lines)
    module.zero_grad(set_to_none=True)
    val_loader = datamodule.val_dataloader()
    val_batch = next(iter(val_loader))
    lines.append(_describe_batch("val", val_batch))
    check_batch(val_batch, module.task.batch_type, enabled=module.check_batches)
    module.eval()
    with torch.no_grad():
        val_out = module.task.step(module.net, val_batch, Stage.VAL)
    _assert_finite_scalar(val_out.loss, "val")
    lines.append("smoke check passed")
    report = "\n".join(lines) + "\n"
    if log_path is not None:
        log_path.write_text(report)
    _log.info("smoke check passed")


def _describe_batch(name: str, batch: Any) -> str:
    from dataclasses import fields, is_dataclass

    if is_dataclass(batch) and not isinstance(batch, type):
        parts = [_tensor_summary(f"{name}.{f.name}", getattr(batch, f.name)) for f in fields(batch)]
        return "; ".join(parts)
    if isinstance(batch, (tuple, list)):
        parts = [_tensor_summary(f"{name}[{i}]", item) for i, item in enumerate(batch)]
        return "; ".join(parts)
    if isinstance(batch, dict):
        parts = [_tensor_summary(f"{name}.{k}", v) for k, v in batch.items()]
        return "; ".join(parts)
    return _tensor_summary(name, batch)


def _tensor_summary(label: str, value: Any) -> str:
    if isinstance(value, Tensor):
        return f"{label}: shape={tuple(value.shape)} dtype={value.dtype}"
    return f"{label}: type={type(value).__name__}"


def _assert_finite_scalar(loss: Tensor, stage: str) -> None:
    if loss.ndim != 0:
        raise AnvilSmokeError(f"{stage} loss must be scalar", value=tuple(loss.shape))
    if not torch.isfinite(loss).item():
        raise AnvilSmokeError(f"{stage} loss is not finite", value=loss.detach())


def _assert_some_grad(module: TaskModule, lines: list[str]) -> None:
    with_grad = 0
    none_modules: list[str] = []
    for name, param in module.named_parameters():
        if param.grad is not None:
            with_grad += 1
        else:
            none_modules.append(name)
    if with_grad == 0:
        raise AnvilSmokeError(
            "no parameter received a gradient",
            hint="check that the loss connects to the Net",
        )
    if none_modules:
        preview = ", ".join(none_modules[:5])
        lines.append(f"warning: {len(none_modules)} params had None grad (e.g. {preview})")
