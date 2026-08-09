"""Phase: ``anvil init`` scaffolds a config YAML."""

from __future__ import annotations

from pathlib import Path

import pytest

from anvil.blueprints import ResNet18Classification
from anvil.core import AnvilConfigError, load_yaml, parse
from anvil.core.cli import main
from anvil.core.experiment import Experiment
from anvil.core.init import init_project


def test_init_skeleton_without_blueprint(tmp_path: Path) -> None:
    """
    Condition:
    init_project is called on an empty directory with no blueprint.

    Expected:
    config.yaml exists and names ResNet18Classification as a starting _target_.
    """
    out = init_project(tmp_path / "demo")
    assert out == tmp_path / "demo" / "config.yaml"
    text = out.read_text()
    assert "anvil.blueprints.ResNet18Classification" in text
    assert "global:" in text
    assert "trainer:" in text


def test_init_from_blueprint_dumps_defaults(tmp_path: Path) -> None:
    """
    Condition:
    init_project uses --blueprint ResNet18Classification.

    Expected:
    YAML parses to an Experiment whose task is that blueprint.
    """
    out = init_project(
        tmp_path / "bp",
        blueprint="anvil.blueprints.ResNet18Classification",
    )
    raw = load_yaml(out)
    exp = parse(raw, Experiment)
    assert isinstance(exp.task, ResNet18Classification)
    assert exp.global_.name == "ResNet18Classification"


def test_init_refuses_overwrite_unless_force(tmp_path: Path) -> None:
    """
    Condition:
    config.yaml already exists and force is False.

    Expected:
    AnvilConfigError; force=True overwrites.
    """
    init_project(tmp_path)
    with pytest.raises(AnvilConfigError, match="already exists"):
        init_project(tmp_path)
    out = init_project(tmp_path, force=True)
    assert out.is_file()


def test_init_cli_blueprint_alias(tmp_path: Path) -> None:
    """
    Condition:
    CLI is invoked with ``anvil init DIR --blueprints PATH``.

    Expected:
    Exit 0 and config.yaml is written.
    """
    dest = tmp_path / "cli_bp"
    code = main(
        [
            "init",
            str(dest),
            "--blueprints",
            "anvil.blueprints.ResNet18Classification",
        ]
    )
    assert code == 0
    assert (dest / "config.yaml").is_file()


def test_init_cli_skeleton(tmp_path: Path) -> None:
    """
    Condition:
    CLI is invoked as ``anvil init DIR`` with no blueprint.

    Expected:
    Exit 0 and skeleton config.yaml is written.
    """
    dest = tmp_path / "cli_skel"
    assert main(["init", str(dest)]) == 0
    assert (dest / "config.yaml").is_file()
