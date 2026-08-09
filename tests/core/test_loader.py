"""Phase 1: YAML loader — extends, overrides, cycles."""

from __future__ import annotations

from pathlib import Path

import pytest

from anvil.core.config import AnvilConfigError, load_yaml


@pytest.fixture()
def configs_dir(tmp_path: Path) -> Path:
    root = tmp_path / "configs"
    base = root / "_base_"
    base.mkdir(parents=True)
    (base / "trainer.yaml").write_text("trainer:\n  max_epochs: 10\n  accelerator: cpu\n")
    (root / "child.yaml").write_text(
        "extends:\n  - _base_/trainer.yaml\nglobal:\n  project: demo\n  name: run\n"
        "trainer:\n  max_epochs: 50\n"
    )
    return root


def test_extends_merge_later_wins(configs_dir: Path) -> None:
    """
    Condition:
    child.yaml extends a base trainer and overrides max_epochs.

    Expected:
    Merged dict has max_epochs=50 and keeps accelerator from the base.
    """
    cfg = load_yaml(configs_dir / "child.yaml", config_root=configs_dir)
    assert cfg["trainer"]["max_epochs"] == 50
    assert cfg["trainer"]["accelerator"] == "cpu"
    assert cfg["global"]["project"] == "demo"


def test_cli_overrides_win(configs_dir: Path) -> None:
    """
    Condition:
    Dotlist override sets trainer.max_epochs after extends merge.

    Expected:
    Override value is present in the resolved dict.
    """
    cfg = load_yaml(
        configs_dir / "child.yaml",
        overrides=["trainer.max_epochs=3"],
        config_root=configs_dir,
    )
    assert cfg["trainer"]["max_epochs"] == 3


def test_extends_cycle_reports_chain(tmp_path: Path) -> None:
    """
    Condition:
    Two YAML files extend each other.

    Expected:
    AnvilConfigError whose hint contains the include chain.
    """
    root = tmp_path / "configs"
    root.mkdir()
    (root / "a.yaml").write_text("extends:\n  - b.yaml\nx: 1\n")
    (root / "b.yaml").write_text("extends:\n  - a.yaml\ny: 2\n")
    with pytest.raises(AnvilConfigError, match="cycle") as exc_info:
        load_yaml(root / "a.yaml", config_root=root)
    assert "a.yaml" in (exc_info.value.hint or "")
    assert "b.yaml" in (exc_info.value.hint or "")


def test_missing_file(tmp_path: Path) -> None:
    """
    Condition:
    load_yaml is pointed at a nonexistent path.

    Expected:
    AnvilConfigError.
    """
    with pytest.raises(AnvilConfigError, match="not found"):
        load_yaml(tmp_path / "nope.yaml")
