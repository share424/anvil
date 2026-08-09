"""Phase 6: validate / test CLI and batch checks."""

from __future__ import annotations

from pathlib import Path

import pytest
import torch

from anvil.core import Experiment, GlobalConfig, Trainer, forge, validate
from anvil.core.api import test as anvil_test
from anvil.core.config.errors import AnvilShapeError
from anvil.core.runtime.batchcheck import beartype_available, check_batch
from anvil.stock.data.classification.cifar import ClassificationBatch
from tests.core._toys import ToyTask


def test_validate_and_test_from_checkpoint(tmp_path: Path) -> None:
    """
    Condition:
    ToyTask forges one epoch; validate and test run against last.ckpt.

    Expected:
    Both exit 0.
    """
    out = tmp_path / "out"
    exp = Experiment(
        global_=GlobalConfig(project="toy", name="vt", output_dir=str(out), seed=0),
        task=ToyTask(),
        trainer=Trainer(max_epochs=1, accelerator="cpu", devices=1),
    )
    assert forge(exp, raise_on_error=True) == 0
    ckpt = (out / "toy" / "vt" / "latest" / "checkpoints" / "last.ckpt").resolve()
    assert ckpt.is_file()
    assert validate(exp, ckpt, raise_on_error=True) == 0
    assert anvil_test(exp, ckpt, raise_on_error=True) == 0


def test_validate_missing_ckpt_raises(tmp_path: Path) -> None:
    """
    Condition:
    validate is called with a missing checkpoint path.

    Expected:
    AnvilConfigError (via raise_on_error).
    """
    from anvil.core import AnvilConfigError

    exp = Experiment(
        global_=GlobalConfig(project="toy", name="miss", output_dir=str(tmp_path)),
        task=ToyTask(),
        trainer=Trainer(max_epochs=1, accelerator="cpu", devices=1),
    )
    with pytest.raises(AnvilConfigError, match="checkpoint not found"):
        validate(exp, tmp_path / "nope.ckpt", raise_on_error=True)


@pytest.mark.skipif(not beartype_available(), reason="beartype not installed")
def test_classification_batch_jaxtyping_ok() -> None:
    """
    Condition:
    A well-shaped ClassificationBatch is checked with beartype enabled.

    Expected:
    check_batch returns without error.
    """
    batch = ClassificationBatch(
        images=torch.zeros(2, 3, 32, 32),
        labels=torch.zeros(2, dtype=torch.long),
    )
    check_batch(batch, ClassificationBatch, enabled=True)


@pytest.mark.skipif(not beartype_available(), reason="beartype not installed")
def test_classification_batch_jaxtyping_bad_rank() -> None:
    """
    Condition:
    ClassificationBatch images have the wrong rank.

    Expected:
    AnvilShapeError naming batch.images.
    """
    batch = ClassificationBatch(
        images=torch.zeros(2, 3, 32),  # type: ignore[arg-type]
        labels=torch.zeros(2, dtype=torch.long),
    )
    with pytest.raises(AnvilShapeError, match="batch.images"):
        check_batch(batch, ClassificationBatch, enabled=True)
