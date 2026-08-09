"""anvil.core.runtime.gpu: GPU memory logging during training."""

from __future__ import annotations

from pathlib import Path
from typing import TextIO

import lightning as L
import torch
from lightning.pytorch.callbacks import Callback

from anvil.core.runtime.logging import get_logger

__all__ = ["GpuUsageLogger", "device_stats_enabled"]

_log = get_logger(__name__)


def device_stats_enabled(accelerator: str, *, flag: bool) -> bool:
    """Return whether device-stat callbacks should be attached.

    Args:
        accelerator: Trainer accelerator setting.
        flag: User ``log_device_stats`` flag.

    Returns:
        True when logging should be enabled.
    """
    if not flag:
        return False
    if accelerator in {"cpu", "tpu"}:
        return False
    return torch.cuda.is_available() or accelerator in {"gpu", "cuda", "auto"}


class GpuUsageLogger(Callback):
    """Log CUDA memory to the logger / terminal and optionally ``gpu.txt``."""

    def __init__(self, log_path: Path | None = None) -> None:
        """Create the callback.

        Args:
            log_path: Optional run-dir ``gpu.txt`` path. Defaults to None.
        """
        super().__init__()
        self.log_path = log_path
        self._file: TextIO | None = None

    def setup(self, trainer: L.Trainer, pl_module: L.LightningModule, stage: str) -> None:
        """Open the gpu log file once at fit start."""
        _ = trainer, pl_module, stage
        if self.log_path is None or not torch.cuda.is_available():
            return
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        self._file = self.log_path.open("a", encoding="utf-8")
        self._file.write(_snapshot_header())
        self._file.flush()

    def teardown(self, trainer: L.Trainer, pl_module: L.LightningModule, stage: str) -> None:
        """Close the gpu log file."""
        _ = trainer, pl_module, stage
        if self._file is not None:
            self._file.write(_snapshot_lines(prefix="teardown"))
            self._file.close()
            self._file = None

    def on_train_epoch_end(self, trainer: L.Trainer, pl_module: L.LightningModule) -> None:
        """Emit per-epoch GPU memory stats."""
        if not torch.cuda.is_available():
            return
        line = _snapshot_lines(prefix=f"epoch={trainer.current_epoch}")
        _log.info("%s", line.strip())
        if self._file is not None:
            self._file.write(line)
            self._file.flush()
        for index in range(torch.cuda.device_count()):
            allocated = torch.cuda.memory_allocated(index) / (1024**3)
            reserved = torch.cuda.memory_reserved(index) / (1024**3)
            peak = torch.cuda.max_memory_allocated(index) / (1024**3)
            pl_module.log(f"gpu/{index}/allocated_gb", allocated, prog_bar=False, on_epoch=True)
            pl_module.log(f"gpu/{index}/reserved_gb", reserved, prog_bar=False, on_epoch=True)
            pl_module.log(f"gpu/{index}/peak_allocated_gb", peak, prog_bar=False, on_epoch=True)


def _snapshot_header() -> str:
    return "=== gpu memory (GiB) ===\n" + _snapshot_lines(prefix="start")


def _snapshot_lines(*, prefix: str) -> str:
    if not torch.cuda.is_available():
        return f"{prefix}: cuda unavailable\n"
    parts: list[str] = []
    for index in range(torch.cuda.device_count()):
        name = torch.cuda.get_device_name(index)
        allocated = torch.cuda.memory_allocated(index) / (1024**3)
        reserved = torch.cuda.memory_reserved(index) / (1024**3)
        peak = torch.cuda.max_memory_allocated(index) / (1024**3)
        parts.append(
            f"{prefix} gpu[{index}]={name} "
            f"allocated={allocated:.3f} reserved={reserved:.3f} peak_allocated={peak:.3f}"
        )
    return "\n".join(parts) + "\n"
