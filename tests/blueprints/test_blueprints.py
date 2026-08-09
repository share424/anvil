"""Phase 4: blueprints, resolved-config reforge, live escape hatch."""

from __future__ import annotations

from pathlib import Path

import pytest
import torch
from torch import nn

from anvil.blueprints import ResNet18Classification
from anvil.blueprints._deps import require_stock
from anvil.core import AnvilConfigError, Experiment, GlobalConfig, Trainer, forge, resume
from anvil.stock import ClassificationSyntheticData, LinearHead
from anvil.stock.components.backbones.resnet_impl import ResNet as ResNetImpl


def test_require_stock_ok() -> None:
    """
    Condition:
    Stock is installed in this editable tree.

    Expected:
    require_stock returns without error.
    """
    require_stock()


def test_require_stock_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Condition:
    Importing anvil.stock raises ImportError.

    Expected:
    require_stock raises ImportError naming anvil[blueprints].
    """
    import importlib

    real_import_module = importlib.import_module

    def _fail(name: str, package: str | None = None) -> object:
        if name == "anvil.stock":
            raise ImportError("simulated missing stock")
        return real_import_module(name, package)

    monkeypatch.setattr("anvil.blueprints._deps.importlib.import_module", _fail)
    with pytest.raises(ImportError, match=r"anvil\[blueprints\]"):
        require_stock()


def test_forge_blueprint_synthetic(tmp_path: Path) -> None:
    """
    Condition:
    ResNet18Classification is forged with ClassificationSyntheticData data for one epoch.

    Expected:
    Exit 0 and last.ckpt exists.
    """
    task = ResNet18Classification(
        data=ClassificationSyntheticData(train_size=32, val_size=16, batch_size=8)
    )
    exp = Experiment(
        global_=GlobalConfig(
            project="bp",
            name="resnet18",
            output_dir=str(tmp_path / "out"),
            seed=0,
        ),
        task=task,
        trainer=Trainer(max_epochs=1, accelerator="cpu", devices=1),
    )
    assert forge(exp, raise_on_error=True) == 0
    run = (tmp_path / "out" / "bp" / "resnet18" / "latest").resolve()
    assert (run / "checkpoints" / "last.ckpt").is_file()


def test_forge_bare_blueprint_task(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Condition:
    anvil.forge(ResNet18Classification(...)) is called with a bare Task.

    Expected:
    Exit 0 (Experiment wrap defaults).
    """
    monkeypatch.chdir(tmp_path)
    task = ResNet18Classification(
        data=ClassificationSyntheticData(train_size=16, val_size=8, batch_size=4)
    )
    assert forge(task, raise_on_error=True) == 0


def test_resolved_yaml_is_forge_entrypoint(tmp_path: Path) -> None:
    """
    Condition:
    A run writes config.resolved.yaml; that file is forged again with dry_run.

    Expected:
    Second forge exits 0.
    """
    task = ResNet18Classification(
        data=ClassificationSyntheticData(train_size=16, val_size=8, batch_size=4)
    )
    exp = Experiment(
        global_=GlobalConfig(project="bp", name="resolved", output_dir=str(tmp_path / "out")),
        task=task,
        trainer=Trainer(max_epochs=1, accelerator="cpu", devices=1),
    )
    assert forge(exp, dry_run=True, raise_on_error=True) == 0
    resolved = (tmp_path / "out" / "bp" / "resolved" / "latest" / "config.resolved.yaml").resolve()
    assert forge(resolved, dry_run=True, raise_on_error=True) == 0


def test_resume_continues_global_step(tmp_path: Path) -> None:
    """
    Condition:
    Forge 1 epoch, then resume with max_epochs=2.

    Expected:
    Same run dir; resumed.txt written; checkpoint global_step increases.
    """
    out = tmp_path / "out"
    task = ResNet18Classification(
        data=ClassificationSyntheticData(train_size=16, val_size=8, batch_size=4)
    )
    exp = Experiment(
        global_=GlobalConfig(project="bp", name="resume", output_dir=str(out), seed=0),
        task=task,
        trainer=Trainer(max_epochs=1, accelerator="cpu", devices=1),
    )
    assert forge(exp, raise_on_error=True) == 0
    run = (out / "bp" / "resume" / "latest").resolve()
    ckpt = run / "checkpoints" / "last.ckpt"
    step_before = int(torch.load(ckpt, map_location="cpu", weights_only=False)["global_step"])
    assert (
        resume(str(out / "bp" / "resume"), overrides=["trainer.max_epochs=2"], raise_on_error=True)
        == 0
    )
    assert (run / "resumed.txt").is_file()
    step_after = int(torch.load(ckpt, map_location="cpu", weights_only=False)["global_step"])
    assert step_after > step_before


def test_live_module_marks_non_reproducible_and_blocks_resume(tmp_path: Path) -> None:
    """
    Condition:
    Task uses a live backbone module; forge dry-run; then resume is attempted.

    Expected:
    NON_REPRODUCIBLE marker and live placeholder in resolved YAML; resume raises.
    """
    live_backbone = ResNetImpl(depth=18)
    task = ResNet18Classification(
        backbone=live_backbone,
        head=LinearHead(in_channels=512, num_classes=10),
        data=ClassificationSyntheticData(train_size=16, val_size=8, batch_size=4),
    )
    exp = Experiment(
        global_=GlobalConfig(project="bp", name="live", output_dir=str(tmp_path / "out")),
        task=task,
        trainer=Trainer(max_epochs=1, accelerator="cpu", devices=1),
    )
    assert forge(exp, dry_run=True, raise_on_error=True) == 0
    run = (tmp_path / "out" / "bp" / "live" / "latest").resolve()
    assert (run / "NON_REPRODUCIBLE").is_file()
    text = (run / "config.resolved.yaml").read_text()
    assert "NON-REPRODUCIBLE" in text
    assert "<live object: ResNet>" in text
    ckpt_dir = run / "checkpoints"
    ckpt_dir.mkdir(exist_ok=True)
    torch.save({"global_step": 0, "state_dict": {}}, ckpt_dir / "last.ckpt")
    with pytest.raises(AnvilConfigError, match="non-reproducible"):
        resume(str(tmp_path / "out" / "bp" / "live"), raise_on_error=True)


def test_live_backbone_skips_channel_wiring() -> None:
    """
    Condition:
    Live backbone with a config head that would mismatch channels if checked.

    Expected:
    Construction succeeds (wiring check skipped for live backbone).
    """
    task = ResNet18Classification(
        backbone=nn.Identity(),
        head=LinearHead(in_channels=512, num_classes=10),
        data=ClassificationSyntheticData(num_classes=10),
    )
    assert isinstance(task.backbone, nn.Module)
