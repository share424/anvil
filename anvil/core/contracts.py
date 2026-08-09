"""anvil.core.contracts: framework-owned sample/batch markers and stage enums.

Task-family details (e.g. box formats) live in ``anvil.stock``, not here.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

__all__ = ["Batch", "Sample", "Stage", "Split"]


class Stage(StrEnum):
    """Training stage label passed to ``Task.step``."""

    TRAIN = "train"
    VAL = "val"
    TEST = "test"
    PREDICT = "predict"


class Split(StrEnum):
    """Dataset split name."""

    TRAIN = "train"
    VAL = "val"
    TEST = "test"
    PREDICT = "predict"


@dataclass(frozen=True)
class Sample:
    """Marker base for a single dataset sample."""


@dataclass(frozen=True)
class Batch:
    """Marker base for a collated batch."""
