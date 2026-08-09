"""Shared toy Task / Data / modules for Phase 2 forge tests."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, ClassVar

import torch
from pydantic import Field
from torch import Tensor, nn
from torch.utils.data import Dataset

from anvil.core import (
    Batch,
    Buildable,
    Data,
    Net,
    Optimizer,
    Split,
    Stage,
    StepOutput,
    Task,
)


@dataclass(frozen=True)
class ToyBatch(Batch):
    """Marker batch type for synthetic loaders."""


class ToyLinear(Buildable[nn.Module]):
    """Linear layer config for tests."""

    in_features: int = 4
    out_features: int = 3

    def build(self) -> nn.Module:
        """Build an ``nn.Linear``."""
        return nn.Linear(self.in_features, self.out_features)


class ToySGD(Optimizer):
    """SGD optimizer config for tests."""

    lr: float = 0.1

    def build_with_params(self, params: Any) -> torch.optim.Optimizer:
        """Build SGD for ``params``."""
        return torch.optim.SGD(params, lr=self.lr)


class ToyDataset(Dataset[tuple[Tensor, Tensor]]):
    """Synthetic (x, y) pairs."""

    def __init__(self, size: int, in_features: int = 4, num_classes: int = 3) -> None:
        """Create a fixed-length random dataset.

        Args:
            size: Number of samples.
            in_features: Feature width. Defaults to 4.
            num_classes: Label range. Defaults to 3.
        """
        self.size = size
        self.in_features = in_features
        self.num_classes = num_classes

    def __len__(self) -> int:
        """Return dataset length."""
        return self.size

    def __getitem__(self, index: int) -> tuple[Tensor, Tensor]:
        """Return one synthetic sample."""
        _ = index
        x = torch.randn(self.in_features)
        y = torch.randint(0, self.num_classes, ())
        return x, y


class ToyData(Data):
    """Synthetic data for core forge tests."""

    batch_type: ClassVar[type[Batch]] = ToyBatch
    train_size: int = 16
    val_size: int = 8
    in_features: int = 4
    num_classes: int = 3
    batch_size: int = 4
    num_workers: int = 0
    example_input_shape: tuple[int, ...] = (2, 4)

    def build_dataset(self, split: Split) -> Dataset[Any]:
        """Build train or val synthetic data."""
        size = self.train_size if split is Split.TRAIN else self.val_size
        return ToyDataset(size, self.in_features, self.num_classes)


class ToyTask(Task):
    """Single Linear module classification toy."""

    batch_type: ClassVar[type[Batch]] = ToyBatch
    model: ToyLinear = Field(default_factory=ToyLinear)
    data: ToyData = Field(default_factory=ToyData)
    optimizer: ToySGD = Field(default_factory=ToySGD)

    def example_forward(self, net: Net, x: Tensor) -> Tensor:
        """Forward through ``net.model``."""
        return net.model(x)

    def step(self, net: Net, batch: Any, stage: Stage) -> StepOutput:
        """Cross-entropy on a (x, y) batch."""
        _ = stage
        x, y = batch
        logits = net.model(x)
        loss = nn.functional.cross_entropy(logits, y)
        return StepOutput(loss=loss, preds=logits, targets=y)
