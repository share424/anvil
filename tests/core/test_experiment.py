"""Phase 1: Experiment parse from dict / YAML."""

from __future__ import annotations

from pathlib import Path

from anvil.core import Experiment, GlobalConfig, Trainer, load_yaml, parse, qualname
from tests.core._config_toys import ConfigToyTask as ToyTask
from tests.core._config_toys import ResNet


def test_experiment_from_python() -> None:
    """
    Condition:
    Experiment is constructed with a ToyTask in Python.

    Expected:
    Fields round-trip through model_dump / parse.
    """
    exp = Experiment(
        global_=GlobalConfig(project="p", name="n"),
        task=ToyTask(backbone=ResNet(depth=50)),
        trainer=Trainer(max_epochs=2),
    )
    dumped = exp.model_dump(by_alias=True)
    assert dumped["global"]["project"] == "p"
    assert dumped["task"]["_target_"] == qualname(ToyTask)
    restored = parse(dumped, Experiment)
    assert restored.global_.name == "n"
    assert restored.trainer.max_epochs == 2
    assert isinstance(restored.task, ToyTask)
    assert restored.task.backbone.depth == 50


def test_experiment_from_yaml(tmp_path: Path) -> None:
    """
    Condition:
    A YAML file names ToyTask via dotted `_target_`.

    Expected:
    load_yaml + parse yields a typed Experiment.
    """
    path = tmp_path / "exp.yaml"
    path.write_text(
        "\n".join(
            [
                "global:",
                "  project: cifar",
                "  name: toy",
                "task:",
                f"  _target_: {qualname(ToyTask)}",
                "  backbone:",
                f"    _target_: {qualname(ResNet)}",
                "    depth: 18",
                "trainer:",
                "  max_epochs: 1",
                "",
            ]
        )
    )
    raw = load_yaml(path)
    exp = parse(raw, Experiment)
    assert exp.global_.project == "cifar"
    assert isinstance(exp.task, ToyTask)
    assert exp.task.backbone.depth == 18
