"""Classification metrics."""

from __future__ import annotations

from typing import Literal

from torchmetrics.classification import MulticlassAccuracy as MulticlassAccuracyMetric
from torchmetrics.classification import MulticlassF1Score as MulticlassF1ScoreMetric

from anvil.core.config.base import Buildable

__all__ = ["MulticlassAccuracy", "MulticlassF1"]


class MulticlassAccuracy(Buildable[MulticlassAccuracyMetric]):
    """Torchmetrics multiclass accuracy."""

    num_classes: int = 10

    def build(self) -> MulticlassAccuracyMetric:
        """Build the metric."""
        return MulticlassAccuracyMetric(num_classes=self.num_classes)


class MulticlassF1(Buildable[MulticlassF1ScoreMetric]):
    """Torchmetrics multiclass F1."""

    num_classes: int = 10
    average: Literal["micro", "macro", "weighted", "none"] = "macro"

    def build(self) -> MulticlassF1ScoreMetric:
        """Build the metric."""
        return MulticlassF1ScoreMetric(num_classes=self.num_classes, average=self.average)
