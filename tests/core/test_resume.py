"""Phase 2: resume reuses the same run directory."""

from __future__ import annotations

from pathlib import Path

from anvil.core import Experiment, GlobalConfig, Trainer, forge, resume
from tests.core._toys import ToyTask


def test_resume_reuses_run_dir(tmp_path: Path) -> None:
    """
    Condition:
    Forge 1 epoch, then resume the same project/name.

    Expected:
    Still a single run directory under the project; last.ckpt still present.
    """
    out = tmp_path / "out"
    exp = Experiment(
        global_=GlobalConfig(project="toy", name="resume", output_dir=str(out), seed=0),
        task=ToyTask(),
        trainer=Trainer(max_epochs=1, accelerator="cpu", devices=1),
    )
    assert forge(exp, raise_on_error=True) == 0
    project = out / "toy" / "resume"
    runs_before = [p for p in project.iterdir() if p.is_dir() and p.name != "latest"]
    assert len(runs_before) == 1
    assert resume(f"{out}/toy/resume", raise_on_error=True) == 0
    runs_after = [p for p in project.iterdir() if p.is_dir() and p.name != "latest"]
    assert len(runs_after) == 1
    assert (runs_after[0] / "checkpoints" / "last.ckpt").is_file()
