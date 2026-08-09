"""anvil.core.data: ``Data`` config base and split datamodule assembly."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, ClassVar

import lightning as L
from pydantic import Field
from torch.utils.data import DataLoader, Dataset

from anvil.core.config.base import Buildable
from anvil.core.contracts import Batch, Split

__all__ = ["Data"]


class Data(Buildable[L.LightningDataModule], ABC):
    """Config for a Lightning datamodule owned by a task family.

    Subclasses implement ``build_dataset``; ``build`` wraps train/val (and optional
    test) splits into a shared datamodule.
    """

    batch_type: ClassVar[type[Batch]]

    batch_size: int = 32
    eval_batch_size: int | None = None
    num_workers: int = 0
    pin_memory: bool = False
    example_input_shape: tuple[int, ...] = Field(default=(2, 3, 8, 8))

    @abstractmethod
    def build_dataset(self, split: Split) -> Dataset[Any]:
        """Construct the reader for one split."""

    def collate_fn(self, samples: list[Any]) -> Any:
        """Collate samples into a batch (override to return a ``Batch`` dataclass)."""
        from torch.utils.data import default_collate

        return default_collate(samples)

    def build(self) -> L.LightningDataModule:
        """Wrap ``build_dataset`` for each split into a datamodule."""
        return _SplitDataModule(self)


class _SplitDataModule(L.LightningDataModule):
    """Framework-internal datamodule built from a ``Data`` config.

    Exposes a mutable ``batch_size`` attribute so Lightning's ``BatchSizeFinder``
    can search without rebuilding the config object.
    """

    def __init__(self, config: Data) -> None:
        super().__init__()
        self._config = config
        self.batch_size = config.batch_size
        self._train = config.build_dataset(Split.TRAIN)
        self._val = config.build_dataset(Split.VAL)
        self._test = config.build_dataset(Split.TEST)

    def train_dataloader(self) -> DataLoader[Any]:
        return self._loader(self._train, self.batch_size, shuffle=True)

    def val_dataloader(self) -> DataLoader[Any]:
        size = self._config.eval_batch_size or self.batch_size
        return self._loader(self._val, size, shuffle=False)

    def test_dataloader(self) -> DataLoader[Any]:
        size = self._config.eval_batch_size or self.batch_size
        return self._loader(self._test, size, shuffle=False)

    def _loader(self, dataset: Dataset[Any], batch_size: int, *, shuffle: bool) -> DataLoader[Any]:
        return DataLoader(
            dataset,
            batch_size=batch_size,
            shuffle=shuffle,
            num_workers=self._config.num_workers,
            pin_memory=self._config.pin_memory,
            collate_fn=self._config.collate_fn,
        )
