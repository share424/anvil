"""anvil.core.callback: Buildable bases for Lightning callbacks and plugins."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from lightning.pytorch.callbacks import Callback

from anvil.core.config.base import Buildable

__all__ = ["CallbackConfig", "PluginConfig"]


class CallbackConfig(Buildable[Callback], ABC):
    """Config that builds a Lightning ``Callback``."""

    @abstractmethod
    def build(self) -> Callback:
        """Construct the callback."""


class PluginConfig(Buildable[Any], ABC):
    """Config that builds a Lightning Trainer plugin.

    Covers precision plugins, cluster environments, ``CheckpointIO``, layer-sync,
    and other objects accepted by ``Trainer(plugins=...)``.
    """

    @abstractmethod
    def build(self) -> Any:
        """Construct the plugin."""
