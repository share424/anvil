"""anvil.core.runtime.seeding: reproducibility helpers."""

from __future__ import annotations

import lightning as L

__all__ = ["seed_everything"]


def seed_everything(seed: int, *, deterministic: bool = False) -> None:
    """Seed Python, NumPy, and PyTorch via Lightning.

    Args:
        seed: Global seed.
        deterministic: If True, request deterministic algorithms. Defaults to False.
    """
    L.seed_everything(seed, workers=True)
    if deterministic:
        import torch

        torch.use_deterministic_algorithms(True)
