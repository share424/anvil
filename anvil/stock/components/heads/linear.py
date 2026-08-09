"""Linear classification head."""

from __future__ import annotations

from abc import ABC

from torch import nn

from anvil.core.config.base import Buildable

__all__ = ["Head", "LinearHead"]


class Head(Buildable[nn.Module], ABC):
    """Abstract classification head."""

    in_channels: int
    num_classes: int


class LinearHead(Head):
    """Single linear layer over pooled features."""

    in_channels: int = 512
    num_classes: int = 10

    def build(self) -> nn.Module:
        """Build ``nn.Linear(in_channels, num_classes)``."""
        return nn.Linear(self.in_channels, self.num_classes)
