"""anvil.stock.data."""

from anvil.stock.data.classification import (
    Cifar10,
    ClassificationBatch,
    ClassificationData,
    ClassificationSyntheticData,
    ImageFolder,
)

__all__ = [
    "ClassificationBatch",
    "ClassificationData",
    "Cifar10",
    "ImageFolder",
    "ClassificationSyntheticData",
]
