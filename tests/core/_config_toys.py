"""Shared toy Buildables for Phase 1 config tests."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from pydantic import Field, SerializeAsAny

from anvil.core.config import Buildable


class Backbone(Buildable[Any], ABC):
    """Abstract backbone slot for polymorphic-parse tests."""

    @property
    @abstractmethod
    def out_channels(self) -> list[int]:
        """Return output channel list."""
        raise NotImplementedError


class ResNet(Backbone):
    """Concrete backbone config used in round-trip tests."""

    depth: int = 50

    @property
    def out_channels(self) -> list[int]:
        """Return ResNet feature channels for ``depth``."""
        return [256, 512, 1024, 2048] if self.depth >= 50 else [64, 128, 256, 512]

    def build(self) -> dict[str, int]:
        """Return a stub product (not an nn.Module)."""
        return {"depth": self.depth}


class ResNet18(ResNet):
    """Pinned ResNet-18 config."""

    depth: int = 18


class ConfigToyTask(Buildable[str]):
    """Buildable task-shaped config for Experiment parse tests."""

    backbone: SerializeAsAny[Backbone] = Field(default_factory=ResNet18)

    def build(self) -> str:
        """Build a string marker from the backbone product."""
        built = self.backbone.build()
        return f"task-{built['depth']}"
