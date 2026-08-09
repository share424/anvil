"""Stock Lightning callback configs."""

from __future__ import annotations

from typing import Any, Literal

from lightning.pytorch.callbacks import (
    EarlyStopping as LitEarlyStopping,
)
from lightning.pytorch.callbacks import (
    LearningRateMonitor as LitLearningRateMonitor,
)
from lightning.pytorch.callbacks import (
    ModelPruning as LitModelPruning,
)
from lightning.pytorch.callbacks import (
    ModelSummary as LitModelSummary,
)
from lightning.pytorch.callbacks import (
    StochasticWeightAveraging as LitStochasticWeightAveraging,
)
from lightning.pytorch.callbacks import (
    WeightAveraging as LitWeightAveraging,
)
from pydantic import Field

from anvil.core.callback import CallbackConfig

__all__ = [
    "EarlyStopping",
    "LearningRateMonitor",
    "ModelSummary",
    "ModelPruning",
    "WeightAveraging",
    "StochasticWeightAveraging",
]


class EarlyStopping(CallbackConfig):
    """Stop when a monitored metric stops improving."""

    monitor: str = "val/loss"
    min_delta: float = 0.0
    patience: int = 3
    verbose: bool = False
    mode: Literal["min", "max"] = "min"
    strict: bool = True
    check_finite: bool = True
    stopping_threshold: float | None = None
    divergence_threshold: float | None = None
    check_on_train_epoch_end: bool | None = None

    def build(self) -> LitEarlyStopping:
        """Build Lightning ``EarlyStopping``."""
        return LitEarlyStopping(
            monitor=self.monitor,
            min_delta=self.min_delta,
            patience=self.patience,
            verbose=self.verbose,
            mode=self.mode,
            strict=self.strict,
            check_finite=self.check_finite,
            stopping_threshold=self.stopping_threshold,
            divergence_threshold=self.divergence_threshold,
            check_on_train_epoch_end=self.check_on_train_epoch_end,
        )


class LearningRateMonitor(CallbackConfig):
    """Log learning rates for all schedulers."""

    logging_interval: Literal["step", "epoch"] | None = None
    log_momentum: bool = False
    log_weight_decay: bool = False

    def build(self) -> LitLearningRateMonitor:
        """Build Lightning ``LearningRateMonitor``."""
        return LitLearningRateMonitor(
            logging_interval=self.logging_interval,
            log_momentum=self.log_momentum,
            log_weight_decay=self.log_weight_decay,
        )


class ModelSummary(CallbackConfig):
    """Layer summary depth (prefer over the default depth-1 summary)."""

    max_depth: int = 2

    def build(self) -> LitModelSummary:
        """Build Lightning ``ModelSummary``."""
        return LitModelSummary(max_depth=self.max_depth)


class ModelPruning(CallbackConfig):
    r"""Structured / unstructured pruning during training.

    Prefer ``parameter_names`` (e.g. ``['weight']``) from YAML — live module
    tuples are not serializable.
    """

    pruning_fn: str = "l1_unstructured"
    parameter_names: list[str] = Field(default_factory=lambda: ["weight"])
    use_global_unstructured: bool = True
    amount: float = 0.5
    apply_pruning: bool = True
    make_pruning_permanent: bool = True
    use_lottery_ticket_hypothesis: bool = True
    resample_parameters: bool = False
    pruning_dim: int | None = None
    pruning_norm: int | None = None
    verbose: int = 0
    prune_on_train_epoch_end: bool = True

    def build(self) -> LitModelPruning:
        """Build Lightning ``ModelPruning``."""
        return LitModelPruning(
            pruning_fn=self.pruning_fn,
            parameter_names=self.parameter_names,
            use_global_unstructured=self.use_global_unstructured,
            amount=self.amount,
            apply_pruning=self.apply_pruning,
            make_pruning_permanent=self.make_pruning_permanent,
            use_lottery_ticket_hypothesis=self.use_lottery_ticket_hypothesis,
            resample_parameters=self.resample_parameters,
            pruning_dim=self.pruning_dim,
            pruning_norm=self.pruning_norm,
            verbose=self.verbose,
            prune_on_train_epoch_end=self.prune_on_train_epoch_end,
        )


class WeightAveraging(CallbackConfig):
    """EMA / equal-weight parameter averaging (Lightning ``WeightAveraging``)."""

    device: str | None = None
    use_buffers: bool = True

    def build(self) -> LitWeightAveraging:
        """Build Lightning ``WeightAveraging``."""
        return LitWeightAveraging(device=self.device, use_buffers=self.use_buffers)


class StochasticWeightAveraging(CallbackConfig):
    """Classic SWA schedule with LR annealing."""

    swa_lrs: float | list[float] = 1e-2
    swa_epoch_start: float | int = 0.8
    annealing_epochs: int = 10
    annealing_strategy: Literal["cos", "linear"] = "cos"
    device: str | None = "cpu"

    def build(self) -> LitStochasticWeightAveraging:
        """Build Lightning ``StochasticWeightAveraging``."""
        kwargs: dict[str, Any] = {
            "swa_lrs": self.swa_lrs,
            "swa_epoch_start": self.swa_epoch_start,
            "annealing_epochs": self.annealing_epochs,
            "annealing_strategy": self.annealing_strategy,
        }
        if self.device is not None:
            kwargs["device"] = self.device
        return LitStochasticWeightAveraging(**kwargs)
