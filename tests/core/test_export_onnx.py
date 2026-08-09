"""ONNX export."""

from __future__ import annotations

from pathlib import Path

import pytest

from anvil.core import Experiment, GlobalConfig, Trainer, export, forge
from anvil.core.config.errors import AnvilConfigError
from anvil.core.runtime.export_onnx import parse_input_shape
from tests.core._toys import ToyTask


def test_parse_input_shape() -> None:
    """
    Condition:
    CLI-style and tuple input shapes are parsed.

    Expected:
    Matching int tuples; None stays None; bad strings raise.
    """
    assert parse_input_shape(None) is None
    assert parse_input_shape("1,3,32,32") == (1, 3, 32, 32)
    assert parse_input_shape((2, 4)) == (2, 4)
    with pytest.raises(AnvilConfigError, match="invalid"):
        parse_input_shape("1,x,3")


def test_export_onnx_toy(tmp_path: Path) -> None:
    """
    Condition:
    ToyTask is forged one epoch then exported to ONNX.

    Expected:
    Exit 0 and a non-empty .onnx file; onnxruntime-free load via onnx checker.
    """
    import onnx

    out = tmp_path / "out"
    exp = Experiment(
        global_=GlobalConfig(project="toy", name="onnx", output_dir=str(out), seed=0),
        task=ToyTask(),
        trainer=Trainer(max_epochs=1, accelerator="cpu", devices=1),
    )
    assert forge(exp, raise_on_error=True) == 0
    ckpt = (out / "toy" / "onnx" / "latest" / "checkpoints" / "last.ckpt").resolve()
    onnx_path = tmp_path / "model.onnx"
    assert (
        export(
            exp,
            ckpt,
            onnx_path,
            input_shape=(1, 4),
            raise_on_error=True,
        )
        == 0
    )
    assert onnx_path.is_file()
    assert onnx_path.stat().st_size > 0
    model = onnx.load(str(onnx_path))
    onnx.checker.check_model(model)
