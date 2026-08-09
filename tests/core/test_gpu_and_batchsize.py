"""GPU logging and batch-size search (BatchSizeFinder)."""

from __future__ import annotations

from pathlib import Path
from typing import Any, cast

import pytest
from lightning.pytorch.callbacks import DeviceStatsMonitor
from lightning.pytorch.core.datamodule import LightningDataModule

from anvil.core import Experiment, GlobalConfig, Trainer, find_batch_size, forge
from anvil.core.api import _build_trainer
from anvil.core.runtime.artifacts import RunDirectory
from anvil.core.runtime.gpu import GpuUsageLogger, device_stats_enabled
from tests.core._toys import ToyTask


def test_device_stats_enabled_respects_cpu_and_flag() -> None:
    """
    Condition:
    device_stats_enabled is queried for cpu / gpu / disabled flag.

    Expected:
    CPU and flag=False disable; gpu/auto enable when the flag is True.
    """
    assert device_stats_enabled("cpu", flag=True) is False
    assert device_stats_enabled("gpu", flag=False) is False
    assert device_stats_enabled("gpu", flag=True) is True
    assert device_stats_enabled("auto", flag=True) is True


def test_build_trainer_attaches_gpu_callbacks(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Condition:
    device_stats_enabled reports True while building a CPU trainer (CI-safe).

    Expected:
    DeviceStatsMonitor and GpuUsageLogger are present; gpu.txt path is set.
    """
    monkeypatch.setattr("anvil.core.api.device_stats_enabled", lambda *args, **kwargs: True)
    run = RunDirectory(tmp_path / "run")
    (tmp_path / "run").mkdir()
    (tmp_path / "run" / "checkpoints").mkdir()
    trainer = cast(
        Any,
        _build_trainer(
            Trainer(max_epochs=1, accelerator="cpu", devices=1, log_device_stats=True),
            run,
        ),
    )
    types = {type(cb) for cb in trainer.callbacks}
    assert DeviceStatsMonitor in types
    assert GpuUsageLogger in types
    gpu_cb = next(cb for cb in trainer.callbacks if isinstance(cb, GpuUsageLogger))
    assert gpu_cb.log_path == run.file("gpu.txt")


def test_datamodule_batch_size_is_mutable() -> None:
    """
    Condition:
    ToyTask data is built into a datamodule.

    Expected:
    batch_size can be mutated for BatchSizeFinder.
    """
    data = cast(Any, ToyTask().data.build())
    assert isinstance(data, LightningDataModule)
    assert data.batch_size == ToyTask().data.batch_size
    data.batch_size = 7
    assert data.batch_size == 7
    loader = data.train_dataloader()
    assert loader.batch_size == 7


def test_find_batch_size_toy_cpu() -> None:
    """
    Condition:
    find_batch_size runs on ToyTask with a tiny trial budget on CPU
    (BatchSizeFinder callback).

    Expected:
    A positive batch size is returned.
    """
    exp = Experiment(
        global_=GlobalConfig(project="tune", name="bs", output_dir="outputs"),
        task=ToyTask(),
        trainer=Trainer(max_epochs=1, accelerator="cpu", devices=1),
    )
    size = find_batch_size(
        exp,
        mode="power",
        init_val=2,
        max_trials=2,
        steps_per_trial=1,
        max_val=16,
        raise_on_error=True,
    )
    assert size >= 2


def test_forge_cpu_skips_gpu_callbacks(tmp_path: Path) -> None:
    """
    Condition:
    Toy forge on CPU with log_device_stats default.

    Expected:
    Exit 0 and no gpu.txt (CUDA logging not attached on cpu accelerator).
    """
    exp = Experiment(
        global_=GlobalConfig(project="gpu", name="cpu", output_dir=str(tmp_path / "out")),
        task=ToyTask(),
        trainer=Trainer(max_epochs=1, accelerator="cpu", devices=1, log_device_stats=True),
    )
    assert forge(exp, dry_run=True, raise_on_error=True) == 0
    run = (tmp_path / "out" / "gpu" / "cpu" / "latest").resolve()
    assert not (run / "gpu.txt").exists()
