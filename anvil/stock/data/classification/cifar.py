"""Classification data contract and readers."""

from __future__ import annotations

from abc import ABC
from dataclasses import dataclass
from pathlib import Path
from typing import Any, ClassVar

from jaxtyping import Float, Int
from pydantic import Field
from torch import Tensor
from torch.utils.data import Dataset
from torchvision import transforms
from torchvision.datasets import CIFAR10 as TorchCIFAR10
from torchvision.datasets import FakeData
from torchvision.datasets import ImageFolder as TorchImageFolder

from anvil.core.contracts import Batch, Split
from anvil.core.data import Data

__all__ = [
    "ClassificationBatch",
    "ClassificationData",
    "Cifar10",
    "ImageFolder",
    "ClassificationSyntheticData",
]


@dataclass(frozen=True)
class ClassificationBatch(Batch):
    """One collated classification batch.

    Attributes:
        images: Stacked images ``(batch, channels, height, width)``.
        labels: Class indices ``(batch,)``.
    """

    images: Float[Tensor, "batch channels height width"]
    labels: Int[Tensor, "batch"]


class ClassificationData(Data, ABC):
    """Base for classification readers yielding ``(image, label)``."""

    batch_type: ClassVar[type[Batch]] = ClassificationBatch
    num_classes: int = 10
    example_input_shape: tuple[int, ...] = (2, 3, 32, 32)

    def collate_fn(self, samples: list[Any]) -> ClassificationBatch:
        """Stack ``(image, label)`` samples into a ``ClassificationBatch``."""
        from torch.utils.data import default_collate

        images, labels = default_collate(samples)
        return ClassificationBatch(images=images, labels=labels)


class Cifar10(ClassificationData):
    """CIFAR-10 via torchvision."""

    root: str = "/tmp/anvil-cifar10"
    download: bool = True
    batch_size: int = 128
    num_workers: int = 2
    num_classes: int = 10

    def build_dataset(self, split: Split) -> Dataset[Any]:
        """Build the CIFAR-10 train or test split."""
        train = split is Split.TRAIN
        transform = _train_transform() if train else _eval_transform()
        return TorchCIFAR10(
            root=self.root,
            train=train,
            download=self.download,
            transform=transform,
        )


class ImageFolder(ClassificationData):
    """Folder-name labels via ``torchvision.datasets.ImageFolder``.

    Expects ``root/train/<class>/...`` and ``root/val/<class>/...``.
    """

    root: Path
    num_classes: int
    image_size: int = 32
    batch_size: int = 32
    num_workers: int = 2

    def build_dataset(self, split: Split) -> Dataset[Any]:
        """Build one split from ``root/{train,val}``."""
        split_dir = Path(self.root) / ("train" if split is Split.TRAIN else "val")
        transform = (
            _train_transform(self.image_size)
            if split is Split.TRAIN
            else _eval_transform(self.image_size)
        )
        return TorchImageFolder(str(split_dir), transform=transform)


class ClassificationSyntheticData(ClassificationData):
    """Classification ``FakeData`` reader for demos and CI (no download)."""

    train_size: int = 64
    val_size: int = 32
    image_size: int = 32
    num_classes: int = 10
    batch_size: int = 8
    num_workers: int = 0
    example_input_shape: tuple[int, ...] = Field(default=(2, 3, 32, 32))

    def build_dataset(self, split: Split) -> Dataset[Any]:
        """Build FakeData for train or val."""
        size = self.train_size if split is Split.TRAIN else self.val_size
        return FakeData(
            size=size,
            image_size=(3, self.image_size, self.image_size),
            num_classes=self.num_classes,
            transform=_eval_transform(self.image_size),
        )


def _train_transform(size: int = 32) -> transforms.Compose:
    if size == 32:
        return transforms.Compose(
            [
                transforms.RandomCrop(32, padding=4),
                transforms.RandomHorizontalFlip(),
                transforms.ToTensor(),
            ]
        )
    return transforms.Compose(
        [
            transforms.Resize(size),
            transforms.RandomHorizontalFlip(),
            transforms.ToTensor(),
        ]
    )


def _eval_transform(size: int = 32) -> transforms.Compose:
    ops: list[Any] = []
    if size != 32:
        ops.append(transforms.Resize(size))
    ops.append(transforms.ToTensor())
    return transforms.Compose(ops)
