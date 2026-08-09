"""Phase 2: forge / seed / artifacts on core-only toys."""

from __future__ import annotations

from pathlib import Path

import pytest
import torch
from torch import nn

from anvil.core import Experiment, GlobalConfig, Trainer, forge
from anvil.core.runtime.seeding import seed_everything
from tests.core._toys import ToyLinear, ToyTask


def test_forge_dry_run_writes_artifacts(tmp_path: Path) -> None:
    """
    Condition:
    ToyTask is forged with dry_run under a temp output_dir.

    Expected:
    Exit 0; run dir has resolved config, shapes.txt, smoke.txt, latest symlink.
    """
    exp = Experiment(
        global_=GlobalConfig(project="toy", name="dry", output_dir=str(tmp_path / "out")),
        task=ToyTask(),
        trainer=Trainer(max_epochs=1, accelerator="cpu", devices=1),
    )
    code = forge(exp, dry_run=True, raise_on_error=True)
    assert code == 0
    latest = tmp_path / "out" / "toy" / "dry" / "latest"
    assert latest.exists()
    run = latest.resolve()
    assert (run / "config.resolved.yaml").is_file()
    assert (run / "shapes.txt").is_file()
    assert "smoke check passed" in (run / "smoke.txt").read_text()
    assert (run / "git.txt").is_file()
    assert (run / "env.txt").is_file()


def test_forge_one_epoch(tmp_path: Path) -> None:
    """
    Condition:
    ToyTask forges one real epoch on CPU.

    Expected:
    Exit 0 and last.ckpt exists under checkpoints/.
    """
    exp = Experiment(
        global_=GlobalConfig(project="toy", name="fit", output_dir=str(tmp_path / "out"), seed=0),
        task=ToyTask(),
        trainer=Trainer(max_epochs=1, accelerator="cpu", devices=1, enable_checkpointing=True),
    )
    code = forge(exp, raise_on_error=True)
    assert code == 0
    run = (tmp_path / "out" / "toy" / "fit" / "latest").resolve()
    assert (run / "checkpoints" / "last.ckpt").is_file()


def test_seed_obedience() -> None:
    """
    Condition:
    ToyLinear.build() is called under two different seeds and twice under one seed.

    Expected:
    Different seeds differ; same seed matches (seed before build).
    """
    seed_everything(1)
    m1 = ToyLinear().build()
    assert isinstance(m1, nn.Linear)
    w1 = m1.weight.detach().clone()
    seed_everything(2)
    m2 = ToyLinear().build()
    assert isinstance(m2, nn.Linear)
    w2 = m2.weight.detach().clone()
    seed_everything(1)
    m1b = ToyLinear().build()
    assert isinstance(m1b, nn.Linear)
    w1b = m1b.weight.detach().clone()
    assert not torch.equal(w1, w2)
    assert torch.equal(w1, w1b)


def test_forge_accepts_bare_task(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Condition:
    forge is called with a bare ToyTask (no Experiment wrapper).

    Expected:
    Defaults wrap it and dry_run succeeds.
    """
    monkeypatch.chdir(tmp_path)
    code = forge(ToyTask(), dry_run=True, raise_on_error=True)
    assert code == 0
