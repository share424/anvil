"""Stock classification tests."""

from __future__ import annotations

from pathlib import Path

import pytest

from anvil.core import (
    AnvilContractError,
    Experiment,
    GlobalConfig,
    Trainer,
    forge,
    load_yaml,
    parse,
)
from anvil.stock import SimpleClassificationTask
from anvil.stock.components import LinearHead, ResNet18
from anvil.stock.data import ClassificationSyntheticData


@pytest.fixture
def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def test_num_classes_mismatch_fails_at_parse() -> None:
    """
    Condition:
    Head num_classes disagrees with data.num_classes.

    Expected:
    AnvilContractError at construction time.
    """
    with pytest.raises(AnvilContractError, match="num_classes"):
        SimpleClassificationTask(
            head=LinearHead(num_classes=3),
            data=ClassificationSyntheticData(num_classes=10),
        )


def test_forge_synthetic_one_epoch(tmp_path: Path) -> None:
    """
    Condition:
    SimpleClassificationTask with ClassificationSyntheticData data forges one CPU epoch.

    Expected:
    Exit 0 and last.ckpt exists.
    """
    task = SimpleClassificationTask(
        backbone=ResNet18(),
        head=LinearHead(num_classes=10),
        data=ClassificationSyntheticData(train_size=32, val_size=16, batch_size=8),
    )
    exp = Experiment(
        global_=GlobalConfig(
            project="stock", name="synth", output_dir=str(tmp_path / "out"), seed=0
        ),
        task=task,
        trainer=Trainer(max_epochs=1, accelerator="cpu", devices=1),
    )
    assert forge(exp, raise_on_error=True) == 0
    run = (tmp_path / "out" / "stock" / "synth" / "latest").resolve()
    assert (run / "checkpoints" / "last.ckpt").is_file()


def test_yaml_synthetic_dry_run(repo_root: Path, tmp_path: Path) -> None:
    """
    Condition:
    configs/resnet18_synthetic.yaml is loaded and dry-run forged.

    Expected:
    Exit code 0.
    """
    cfg = repo_root / "configs" / "resnet18_synthetic.yaml"
    code = forge(
        cfg,
        overrides=[f"global.output_dir={tmp_path / 'out'}"],
        dry_run=True,
        raise_on_error=True,
    )
    assert code == 0


def test_yaml_cifar_parses(repo_root: Path) -> None:
    """
    Condition:
    configs/resnet18_cifar10.yaml is loaded and parsed.

    Expected:
    Experiment with SimpleClassificationTask.
    """
    raw = load_yaml(repo_root / "configs" / "resnet18_cifar10.yaml")
    exp = parse(raw, Experiment)
    assert isinstance(exp.task, SimpleClassificationTask)
    assert exp.task.head.num_classes == 10
    assert exp.task.scheduler is not None
    assert exp.task.scheduler.t_max == 100


def test_yaml_cifar_dry_run(repo_root: Path, tmp_path: Path) -> None:
    """
    Condition:
    Shipped configs/resnet18_cifar10.yaml is dry-run forged (may download CIFAR-10).

    Expected:
    Exit code 0.
    """
    cfg = repo_root / "configs" / "resnet18_cifar10.yaml"
    code = forge(
        cfg,
        overrides=[
            f"global.output_dir={tmp_path / 'out'}",
            "trainer.accelerator=cpu",
            "trainer.devices=1",
            "task.data.batch_size=8",
            "task.data.num_workers=0",
        ],
        dry_run=True,
        raise_on_error=True,
    )
    assert code == 0
