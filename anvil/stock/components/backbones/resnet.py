"""ResNet backbone configs."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Literal

from torch import nn

from anvil.core.config.base import Buildable
from anvil.stock.components.backbones import resnet_impl

__all__ = ["Backbone", "ResNet", "ResNet18"]


class Backbone(Buildable[nn.Module], ABC):
    """Abstract backbone slot for classification / detection."""

    @property
    @abstractmethod
    def out_channels(self) -> list[int]:
        """Channel counts of emitted feature levels (classification: one vector)."""


class ResNet(Backbone):
    """CIFAR-friendly ResNet backbone (features only)."""

    depth: Literal[18] = 18
    in_channels: int = 3

    @property
    def out_channels(self) -> list[int]:
        """Return the final feature width."""
        return [512]

    def build(self) -> nn.Module:
        """Build the ResNet implementation."""
        return resnet_impl.ResNet(depth=int(self.depth), in_channels=self.in_channels)


class ResNet18(ResNet):
    """Pinned ResNet-18 backbone."""

    depth: Literal[18] = 18
