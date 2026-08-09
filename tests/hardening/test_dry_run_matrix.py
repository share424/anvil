"""Phase 6: --dry-run matrix over shipped configs and blueprints."""

from __future__ import annotations

from pathlib import Path

import pytest

from anvil.core import Experiment, GlobalConfig, Trainer, forge
from anvil.core.config.loader import load_yaml
from anvil.stock import ClassificationSyntheticData

_ROOT = Path(__file__).resolve().parents[2]
_CONFIGS = sorted((_ROOT / "configs").glob("*.yaml"))


@pytest.mark.parametrize("config_path", _CONFIGS, ids=lambda p: p.name)
def test_dry_run_shipped_config(config_path: Path, tmp_path: Path) -> None:
    """
    Condition:
    Each top-level YAML under configs/ is forged with --dry-run.

    Expected:
    Exit 0. CIFAR entrypoints swap data to synthetic (no download) while keeping
    the rest of the resolved config.
    """
    overrides = [
        f"global.output_dir={tmp_path / 'out'}",
        "trainer.max_epochs=1",
        "trainer.accelerator=cpu",
        "trainer.devices=1",
        "task.data.batch_size=4",
        "task.data.num_workers=0",
    ]
    raw = load_yaml(config_path, overrides=overrides)
    if "cifar" in config_path.name:
        raw["task"]["data"] = {
            "_target_": "anvil.stock.data.classification.cifar.ClassificationSyntheticData",
            "train_size": 16,
            "val_size": 8,
            "batch_size": 4,
            "num_workers": 0,
            "num_classes": 10,
        }
    assert forge(raw, dry_run=True, raise_on_error=True) == 0


def test_dry_run_shipped_blueprints(tmp_path: Path) -> None:
    """
    Condition:
    Every public blueprint is forged dry-run with synthetic data.

    Expected:
    Exit 0 for each.
    """
    from anvil import blueprints

    for name in blueprints.__all__:
        cls = getattr(blueprints, name)
        task = cls(data=ClassificationSyntheticData(train_size=16, val_size=8, batch_size=4))
        exp = Experiment(
            global_=GlobalConfig(
                project="ci",
                name=name.lower(),
                output_dir=str(tmp_path / "out"),
                seed=0,
            ),
            task=task,
            trainer=Trainer(max_epochs=1, accelerator="cpu", devices=1),
        )
        assert forge(exp, dry_run=True, raise_on_error=True) == 0
