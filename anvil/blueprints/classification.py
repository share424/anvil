"""Classification blueprints."""

from __future__ import annotations

from pydantic import Field, SerializeAsAny
from torch import nn

from anvil.stock.components.backbones.resnet import Backbone, ResNet18
from anvil.stock.components.heads.linear import Head, LinearHead
from anvil.stock.components.optim.sgd import SGD, CosineAnnealing
from anvil.stock.data.classification.cifar import Cifar10, ClassificationData
from anvil.stock.tasks.classification import SimpleClassificationTask

__all__ = ["ResNet18Classification"]


class ResNet18Classification(SimpleClassificationTask):
    """ResNet-18 classifier with CIFAR-10 defaults (ready to forge)."""

    backbone: SerializeAsAny[Backbone] | nn.Module = Field(default_factory=ResNet18)
    head: SerializeAsAny[Head] | nn.Module = Field(
        default_factory=lambda: LinearHead(in_channels=512, num_classes=10)
    )
    data: SerializeAsAny[ClassificationData] = Field(default_factory=Cifar10)
    optimizer: SGD = Field(default_factory=lambda: SGD(lr=0.1, momentum=0.9, weight_decay=5.0e-4))
    scheduler: CosineAnnealing | None = Field(default_factory=lambda: CosineAnnealing(t_max=100))
