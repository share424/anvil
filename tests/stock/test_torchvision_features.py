"""TorchvisionFeatures backbone adapter."""

from __future__ import annotations

from collections import OrderedDict
from pathlib import Path

import pytest
import torch
from torch import nn

from anvil.core import AnvilConfigError, Experiment, GlobalConfig, Trainer, forge
from anvil.stock import ClassificationSyntheticData, LinearHead, SimpleClassificationTask
from anvil.stock.components import TorchvisionFeatures


def test_strip_head_resnet18_forward() -> None:
    """
    Condition:
    TorchvisionFeatures strips fc and builds resnet18 without weights.

    Expected:
    Forward returns (N, 512) and out_channels wiring matches LinearHead.
    """
    cfg = TorchvisionFeatures(name="resnet18", out_channels=[512], weights=None)
    module = cfg.build()
    assert isinstance(module, nn.Module)
    y = module(torch.randn(2, 3, 224, 224))
    assert tuple(y.shape) == (2, 512)
    task = SimpleClassificationTask(
        backbone=cfg,
        head=LinearHead(in_channels=512, num_classes=10),
        data=ClassificationSyntheticData(image_size=224, train_size=8, val_size=4, batch_size=2),
    )
    assert task.backbone.out_channels == [512]


def test_return_nodes_skips_fc() -> None:
    """
    Condition:
    return_nodes=['flatten'] selects features before fc.

    Expected:
    Output shape (N, 512).
    """
    cfg = TorchvisionFeatures(
        name="resnet18",
        out_channels=[512],
        return_nodes=["flatten"],
        weights=None,
    )
    y = cfg.build()(torch.randn(2, 3, 224, 224))
    assert tuple(y.shape) == (2, 512)


def test_multi_nodes_require_as_dict() -> None:
    """
    Condition:
    Multiple return_nodes are set without as_dict.

    Expected:
    AnvilConfigError at construction.
    """
    with pytest.raises(AnvilConfigError, match="as_dict"):
        TorchvisionFeatures(
            name="resnet18",
            out_channels=[128, 256, 512],
            return_nodes=["layer2", "layer3", "layer4"],
            weights=None,
        )


def test_multi_nodes_as_dict() -> None:
    """
    Condition:
    return_nodes with as_dict=True.

    Expected:
    Forward returns OrderedDict of pooled tensors with matching channels.
    """
    cfg = TorchvisionFeatures(
        name="resnet18",
        out_channels=[128, 256, 512],
        return_nodes=["layer2", "layer3", "layer4"],
        as_dict=True,
        weights=None,
    )
    out = cfg.build()(torch.randn(1, 3, 224, 224))
    assert isinstance(out, OrderedDict)
    assert list(out) == ["layer2", "layer3", "layer4"]
    assert out["layer2"].shape[1] == 128
    assert out["layer4"].shape[1] == 512


def test_forge_torchvision_backbone(tmp_path: Path) -> None:
    """
    Condition:
    Classification task with TorchvisionFeatures forges one CPU epoch.

    Expected:
    Exit 0.
    """
    task = SimpleClassificationTask(
        backbone=TorchvisionFeatures(name="resnet18", out_channels=[512], weights=None),
        head=LinearHead(in_channels=512, num_classes=10),
        data=ClassificationSyntheticData(
            image_size=64,
            train_size=16,
            val_size=8,
            batch_size=4,
            example_input_shape=(2, 3, 64, 64),
        ),
    )
    exp = Experiment(
        global_=GlobalConfig(
            project="tv", name="features", output_dir=str(tmp_path / "out"), seed=0
        ),
        task=task,
        trainer=Trainer(max_epochs=1, accelerator="cpu", devices=1),
    )
    assert forge(exp, raise_on_error=True) == 0
