"""anvil.core.runtime.lr: Lightning ``LearningRateFinder`` wrapper."""

from __future__ import annotations

from typing import Any, Literal

import lightning as L
from lightning.pytorch.callbacks import LearningRateFinder

from anvil.core.runtime.logging import get_logger

__all__ = ["FindLearningRate", "find_learning_rate"]

_log = get_logger(__name__)


class FindLearningRate(LearningRateFinder):
    """``LearningRateFinder`` that stops after the range test (find-only runs)."""

    def __init__(self, *args: Any, stop_after: bool = True, **kwargs: Any) -> None:
        """Create the finder.

        Args:
            *args: Forwarded to ``LearningRateFinder``.
            stop_after: Halt fit after the search. Defaults to True.
            **kwargs: Forwarded to ``LearningRateFinder``.
        """
        super().__init__(*args, **kwargs)
        self.stop_after = stop_after

    def on_fit_start(self, trainer: L.Trainer, pl_module: L.LightningModule) -> None:
        """Run the LR range test, then optionally stop."""
        super().on_fit_start(trainer, pl_module)
        if self.stop_after:
            trainer.should_stop = True


def find_learning_rate(
    module: L.LightningModule,
    datamodule: L.LightningDataModule,
    *,
    accelerator: str = "auto",
    devices: Any = "auto",
    precision: Any = "32-true",
    min_lr: float = 1e-8,
    max_lr: float = 1.0,
    num_training_steps: int = 100,
    mode: Literal["exponential", "linear"] = "exponential",
    early_stop_threshold: float | None = 4.0,
    update_attr: bool = True,
    attr_name: str = "lr",
) -> float:
    """Suggest an initial LR via Lightning ``LearningRateFinder``.

    Lightning looks for ``lr`` / ``learning_rate`` on the module. Anvil copies
    ``task.optimizer.lr`` onto ``module.lr`` before the sweep.

    Args:
        module: Built task module.
        datamodule: Built datamodule.
        accelerator: Trainer accelerator. Defaults to ``auto``.
        devices: Trainer devices. Defaults to ``auto``.
        precision: Trainer precision. Defaults to ``32-true``.
        min_lr: Sweep start. Defaults to 1e-8.
        max_lr: Sweep end. Defaults to 1.0.
        num_training_steps: Steps in the range test. Defaults to 100.
        mode: ``exponential`` or ``linear``. Defaults to ``exponential``.
        early_stop_threshold: Divergence threshold. Defaults to 4.0.
        update_attr: Write the suggestion onto ``module.<attr_name>``. Defaults to True.
        attr_name: Module attribute for the LR. Defaults to ``lr``.

    Returns:
        Suggested learning rate.
    """
    _sync_module_lr(module, attr_name=attr_name)
    finder = FindLearningRate(
        min_lr=min_lr,
        max_lr=max_lr,
        num_training_steps=num_training_steps,
        mode=mode,
        early_stop_threshold=early_stop_threshold,
        update_attr=update_attr,
        attr_name=attr_name,
        stop_after=True,
    )
    trainer = L.Trainer(
        accelerator=accelerator,
        devices=devices,
        precision=precision,
        callbacks=[finder],
        max_epochs=100,
        limit_val_batches=0,
        logger=False,
        enable_checkpointing=False,
        enable_model_summary=False,
    )
    trainer.fit(module, datamodule=datamodule)
    result = finder.optimal_lr
    if result is None:
        raise RuntimeError("LearningRateFinder did not produce a result")
    suggested = result.suggestion()
    if suggested is None:
        # Short / early-stopped sweeps may not satisfy the default skip window.
        suggested = result.suggestion(skip_begin=0, skip_end=0)
    if suggested is None:
        raise RuntimeError("LearningRateFinder.suggestion() returned None")
    suggested_f = float(suggested)
    _log.info("suggested lr=%s", suggested_f)
    return suggested_f


def _sync_module_lr(module: L.LightningModule, *, attr_name: str) -> None:
    """Expose optimizer LR on the LightningModule for Lightning's finder."""
    if hasattr(module, attr_name):
        return
    task = getattr(module, "task", None)
    optimizer = getattr(task, "optimizer", None) if task is not None else None
    lr = getattr(optimizer, "lr", None) if optimizer is not None else None
    setattr(module, attr_name, float(lr) if lr is not None else 0.1)
