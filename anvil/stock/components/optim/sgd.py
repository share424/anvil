"""Optimizer and scheduler configs."""

from __future__ import annotations

from typing import Any

import torch
from torch.optim import Optimizer as TorchOptimizer
from torch.optim.lr_scheduler import CosineAnnealingLR

from anvil.core.task import Optimizer, Scheduler

__all__ = ["SGD", "CosineAnnealing"]


class SGD(Optimizer):
    """Stochastic gradient descent."""

    lr: float = 0.1
    momentum: float = 0.9
    weight_decay: float = 5.0e-4

    def build_with_params(self, params: Any) -> TorchOptimizer:
        """Build ``torch.optim.SGD``."""
        return torch.optim.SGD(
            params,
            lr=self.lr,
            momentum=self.momentum,
            weight_decay=self.weight_decay,
        )


class CosineAnnealing(Scheduler):
    """Cosine annealing over epochs."""

    t_max: int = 100
    eta_min: float = 0.0

    def build_with_optimizer(self, optimizer: TorchOptimizer) -> CosineAnnealingLR:
        """Build ``CosineAnnealingLR``."""
        return CosineAnnealingLR(optimizer, T_max=self.t_max, eta_min=self.eta_min)
