"""Notebook-style forge using a blueprint and synthetic data (no download)."""

from __future__ import annotations

import anvil
from anvil.blueprints import ResNet18Classification
from anvil.stock import ClassificationSyntheticData

if __name__ == "__main__":
    anvil.forge(
        ResNet18Classification(
            data=ClassificationSyntheticData(train_size=32, val_size=16, batch_size=8),
        ),
        raise_on_error=True,
    )
