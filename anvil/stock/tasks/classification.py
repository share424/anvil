"""Simple image classification task."""

from __future__ import annotations

from typing import Any, ClassVar

from pydantic import Field, SerializeAsAny, model_validator
from torch import Tensor, nn
from torch.nn import functional as F

from anvil.core.config.errors import AnvilContractError
from anvil.core.contracts import Batch, Stage
from anvil.core.runtime.live import is_live_module
from anvil.core.runtime.logging import get_logger
from anvil.core.task import Net, StepOutput, Task
from anvil.stock.components.backbones.resnet import Backbone, ResNet18
from anvil.stock.components.heads.linear import Head, LinearHead
from anvil.stock.components.optim.sgd import SGD, CosineAnnealing
from anvil.stock.data.classification.cifar import (
    Cifar10,
    ClassificationBatch,
    ClassificationData,
)
from anvil.stock.metrics.classification import MulticlassAccuracy, MulticlassF1

__all__ = ["SimpleClassificationTask"]

_log = get_logger(__name__)


def _default_metrics() -> dict[str, Any]:
    return {
        "acc": MulticlassAccuracy(num_classes=10),
        "f1": MulticlassF1(num_classes=10),
    }


def _unpack(batch: Any) -> tuple[Tensor, Tensor]:
    if isinstance(batch, ClassificationBatch):
        return batch.images, batch.labels
    if isinstance(batch, (tuple, list)) and len(batch) == 2:
        return batch[0], batch[1]
    if isinstance(batch, dict):
        return batch["input"], batch["target"]
    raise TypeError(f"cannot unpack classification batch of type {type(batch).__name__}")


class SimpleClassificationTask(Task):
    """Single-tower image classification (backbone → head).

    Architecture slots accept a stock config or a live ``nn.Module`` escape hatch.
    Live modules mark the run non-reproducible and refuse ``resume``.
    """

    batch_type: ClassVar[type[Batch]] = ClassificationBatch

    backbone: SerializeAsAny[Backbone] | nn.Module = Field(default_factory=ResNet18)
    head: SerializeAsAny[Head] | nn.Module = Field(default_factory=LinearHead)
    data: SerializeAsAny[ClassificationData] = Field(default_factory=Cifar10)
    optimizer: SGD = Field(default_factory=SGD)
    scheduler: CosineAnnealing | None = Field(default_factory=lambda: CosineAnnealing(t_max=100))
    metrics: dict[str, Any] = Field(default_factory=_default_metrics)

    @model_validator(mode="after")
    def _check_wiring(self) -> SimpleClassificationTask:
        """Align head channels / classes with backbone and data when both are configs."""
        skipped: list[str] = []
        if is_live_module(self.backbone) or is_live_module(self.head):
            skipped.append("task.head.in_channels vs backbone.out_channels")
        else:
            assert isinstance(self.backbone, Backbone)
            assert isinstance(self.head, Head)
            expected_in = self.backbone.out_channels[-1]
            if self.head.in_channels != expected_in:
                raise AnvilContractError(
                    "incompatible head.in_channels",
                    path="task.head.in_channels",
                    value=self.head.in_channels,
                    hint=f"backbone emits {expected_in} channels",
                )
        if is_live_module(self.head):
            skipped.append("task.head.num_classes vs data.num_classes")
        else:
            assert isinstance(self.head, Head)
            if self.head.num_classes != self.data.num_classes:
                raise AnvilContractError(
                    "incompatible num_classes",
                    path="task.head.num_classes",
                    value=self.head.num_classes,
                    hint=f"data.num_classes is {self.data.num_classes}",
                )
        if skipped:
            _log.warning(
                "skipped wiring checks for live module slot(s): %s",
                ", ".join(skipped),
            )
        return self

    def example_forward(self, net: Net, x: Tensor) -> Tensor:
        """Backbone → head."""
        return net.head(net.backbone(x))

    def step(self, net: Net, batch: Any, stage: Stage) -> StepOutput:
        """Cross-entropy on logits."""
        _ = stage
        images, labels = _unpack(batch)
        logits = net.head(net.backbone(images))
        loss = F.cross_entropy(logits, labels)
        return StepOutput(loss=loss, preds=logits, targets=labels)
