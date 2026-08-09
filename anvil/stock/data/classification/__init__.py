"""anvil.stock.data.classification."""

from anvil.stock.data.classification.cifar import (
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
