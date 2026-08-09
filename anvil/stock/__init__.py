"""anvil.stock: batteries-included material (components, data, tasks, metrics, callbacks).

Install marker: ``pip install 'anvil[stock]'``.
"""

from __future__ import annotations

from anvil.stock.callbacks import (
    EarlyStopping,
    LearningRateMonitor,
    ModelPruning,
    ModelSummary,
    StochasticWeightAveraging,
    WeightAveraging,
)
from anvil.stock.components import SGD, CosineAnnealing, LinearHead, ResNet18, TorchvisionFeatures
from anvil.stock.data import Cifar10, ClassificationSyntheticData, ImageFolder
from anvil.stock.tasks import SimpleClassificationTask

__all__ = [
    "ResNet18",
    "TorchvisionFeatures",
    "LinearHead",
    "SGD",
    "CosineAnnealing",
    "Cifar10",
    "ImageFolder",
    "ClassificationSyntheticData",
    "SimpleClassificationTask",
    "EarlyStopping",
    "LearningRateMonitor",
    "ModelSummary",
    "ModelPruning",
    "WeightAveraging",
    "StochasticWeightAveraging",
]
