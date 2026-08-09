"""Trainer callbacks and find-lr."""

from __future__ import annotations

from pathlib import Path
from typing import Any, cast

from lightning.pytorch.callbacks import EarlyStopping as LitEarlyStopping
from lightning.pytorch.callbacks import ModelSummary as LitModelSummary

from anvil.core import Experiment, GlobalConfig, Trainer, find_lr, parse
from anvil.core.api import _build_trainer
from anvil.core.runtime.artifacts import RunDirectory
from anvil.stock.callbacks import EarlyStopping, LearningRateMonitor, ModelSummary, WeightAveraging
from tests.core._toys import ToyTask


def test_trainer_parses_callback_buildables() -> None:
    """
    Condition:
    Trainer YAML-like dict lists stock callbacks with dotted _target_.

    Expected:
    Callbacks coerce to Buildable configs and build to Lightning callbacks.
    """
    raw = {
        "max_epochs": 1,
        "accelerator": "cpu",
        "devices": 1,
        "callbacks": [
            {
                "_target_": "anvil.stock.callbacks.EarlyStopping",
                "monitor": "val/loss",
                "patience": 2,
            },
            {"_target_": "anvil.stock.callbacks.LearningRateMonitor"},
            {"_target_": "anvil.stock.callbacks.WeightAveraging"},
        ],
    }
    cfg = Trainer.model_validate(raw)
    callbacks = cfg.callback_list()
    assert isinstance(callbacks[0], EarlyStopping)
    assert isinstance(callbacks[1], LearningRateMonitor)
    assert isinstance(callbacks[2], WeightAveraging)
    assert isinstance(callbacks[0].build(), LitEarlyStopping)


def test_trainer_accepts_single_callback() -> None:
    """
    Condition:
    Trainer is given one callback config (Lightning-shaped singular form).

    Expected:
    It normalizes to a one-element list via callback_list().
    """
    cfg = Trainer(
        max_epochs=1,
        accelerator="cpu",
        devices=1,
        callbacks=EarlyStopping(monitor="val/loss", patience=3),
    )
    assert len(cfg.callback_list()) == 1
    assert cfg.callback_list()[0].patience == 3


def test_build_trainer_attaches_model_summary_and_user_callbacks(tmp_path: Path) -> None:
    """
    Condition:
    Trainer enables model summary depth 3 and an EarlyStopping callback.

    Expected:
    Built Lightning trainer includes ModelSummary(max_depth=3) and EarlyStopping.
    """
    run = RunDirectory(tmp_path / "run")
    (tmp_path / "run").mkdir()
    (tmp_path / "run" / "checkpoints").mkdir()
    cfg = Trainer(
        max_epochs=1,
        accelerator="cpu",
        devices=1,
        model_summary_max_depth=3,
        callbacks=[EarlyStopping(monitor="val/loss", patience=1)],
        log_device_stats=False,
    )
    trainer = cast(Any, _build_trainer(cfg, run))
    types = {type(cb) for cb in trainer.callbacks}
    assert LitEarlyStopping in types
    assert LitModelSummary in types
    summary = next(cb for cb in trainer.callbacks if isinstance(cb, LitModelSummary))
    assert summary._max_depth == 3  # noqa: SLF001 — Lightning stores depth privately


def test_find_lr_toy_cpu() -> None:
    """
    Condition:
    find_lr runs a short LearningRateFinder sweep on ToyTask (CPU).

    Expected:
    A positive learning rate is returned.
    """
    exp = Experiment(
        global_=GlobalConfig(project="tune", name="lr", output_dir="outputs"),
        task=ToyTask(),
        trainer=Trainer(max_epochs=1, accelerator="cpu", devices=1),
    )
    suggested = find_lr(
        exp,
        min_lr=1e-4,
        max_lr=1.0,
        num_training_steps=20,
        early_stop_threshold=None,
        raise_on_error=True,
    )
    assert suggested > 0


def test_model_summary_config_builds() -> None:
    """
    Condition:
    ModelSummary stock config is built.

    Expected:
    Lightning ModelSummary with the requested depth.
    """
    cb = ModelSummary(max_depth=4).build()
    assert isinstance(cb, LitModelSummary)
    assert cb._max_depth == 4  # noqa: SLF001


def test_experiment_round_trips_callbacks() -> None:
    """
    Condition:
    Experiment with EarlyStopping is dumped and re-parsed.

    Expected:
    Callback survives as EarlyStopping Buildable.
    """
    exp = Experiment(
        global_=GlobalConfig(project="p", name="n"),
        task=ToyTask(),
        trainer=Trainer(
            max_epochs=1,
            accelerator="cpu",
            devices=1,
            callbacks=[EarlyStopping(monitor="val/loss", patience=5)],
        ),
    )
    dumped = exp.model_dump(by_alias=True)
    restored = parse(dumped, Experiment)
    callbacks = restored.trainer.callback_list()
    assert isinstance(callbacks[0], EarlyStopping)
    assert callbacks[0].patience == 5


def test_trainer_parses_plugin_buildable() -> None:
    """
    Condition:
    Trainer YAML includes a PluginConfig subclass via _target_.

    Expected:
    Plugin coerces and builds to the live plugin object.
    """
    from anvil.core.callback import PluginConfig

    class _ToyPlugin(PluginConfig):
        name: str = "toy"

        def build(self) -> object:
            return {"plugin": self.name}

    # Register path for resolve_target by attaching to a real module attribute
    import anvil.core.callback as cb_mod

    cb_mod._ToyPlugin = _ToyPlugin
    try:
        cfg = Trainer.model_validate(
            {
                "accelerator": "cpu",
                "devices": 1,
                "plugins": {"_target_": "anvil.core.callback._ToyPlugin", "name": "x"},
            }
        )
        plugins = cfg.plugin_list()
        assert isinstance(plugins[0], _ToyPlugin)
        assert plugins[0].build() == {"plugin": "x"}
    finally:
        delattr(cb_mod, "_ToyPlugin")
