"""anvil.core.runtime.batchsize: Lightning ``BatchSizeFinder`` wrapper."""

from __future__ import annotations

from typing import Any, Literal

import lightning as L
from lightning.pytorch.callbacks import BatchSizeFinder

from anvil.core.runtime.logging import get_logger

__all__ = ["FindBatchSize", "scale_batch_size"]

_log = get_logger(__name__)


class FindBatchSize(BatchSizeFinder):
    """``BatchSizeFinder`` that stops the trainer after the search (find-only runs)."""

    def __init__(self, *args: Any, stop_after: bool = True, **kwargs: Any) -> None:
        """Create the finder.

        Args:
            *args: Forwarded to ``BatchSizeFinder``.
            stop_after: If True, set ``trainer.should_stop`` after scaling so a
                find-only ``fit`` does not continue training. Defaults to True.
            **kwargs: Forwarded to ``BatchSizeFinder``.
        """
        super().__init__(*args, **kwargs)
        self.stop_after = stop_after

    def on_fit_start(self, trainer: L.Trainer, pl_module: L.LightningModule) -> None:
        """Run the search, then optionally halt the fit loop."""
        super().on_fit_start(trainer, pl_module)
        if self.stop_after:
            trainer.should_stop = True


def scale_batch_size(
    module: L.LightningModule,
    datamodule: L.LightningDataModule,
    *,
    accelerator: str = "auto",
    devices: Any = "auto",
    precision: Any = "32-true",
    mode: Literal["power", "binsearch"] = "power",
    init_val: int = 2,
    max_trials: int = 25,
    steps_per_trial: int = 3,
    max_val: int = 8192,
    batch_arg_name: str = "batch_size",
    margin: float = 0.05,
) -> int:
    """Find the largest batch size that fits via Lightning ``BatchSizeFinder``.

    Runs a find-only ``fit``: the callback searches on ``fit`` start, then stops
    so no full training epoch runs. Mutates ``datamodule.<batch_arg_name>``.

    Args:
        module: Built task module.
        datamodule: Built datamodule with a mutable ``batch_size``.
        accelerator: Trainer accelerator. Defaults to ``auto``.
        devices: Trainer devices. Defaults to ``auto``.
        precision: Trainer precision. Defaults to ``32-true``.
        mode: ``power`` or ``binsearch``. Defaults to ``power``.
        init_val: Starting batch size. Defaults to 2.
        max_trials: Maximum search iterations. Defaults to 25.
        steps_per_trial: Train steps per trial. Defaults to 3.
        max_val: Upper bound on batch size. Defaults to 8192.
        batch_arg_name: Attribute to mutate. Defaults to ``batch_size``.
        margin: Safety margin for ``binsearch``. Defaults to 0.05.

    Returns:
        Suggested batch size.
    """
    finder = FindBatchSize(
        mode=mode,
        steps_per_trial=steps_per_trial,
        init_val=init_val,
        max_trials=max_trials,
        batch_arg_name=batch_arg_name,
        margin=margin,
        max_val=max_val,
        stop_after=True,
    )
    trainer = L.Trainer(
        accelerator=accelerator,
        devices=devices,
        precision=precision,
        callbacks=[finder],
        max_epochs=1,
        limit_train_batches=0,
        limit_val_batches=0,
        logger=False,
        enable_checkpointing=False,
        enable_model_summary=False,
    )
    trainer.fit(module, datamodule=datamodule)
    size = int(getattr(datamodule, batch_arg_name))
    _log.info("suggested %s=%s", batch_arg_name, size)
    return size
