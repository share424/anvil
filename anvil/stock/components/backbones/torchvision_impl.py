"""Torchvision model runtime helpers (no anvil imports)."""

from __future__ import annotations

from collections import OrderedDict
from typing import Any

import torch.nn.functional as F
from torch import Tensor, nn
from torchvision.models import get_model
from torchvision.models.feature_extraction import create_feature_extractor


def build_torchvision_features(
    name: str,
    weights: Any,
    *,
    return_nodes: list[str] | None,
    exclude: list[str],
    pool: bool,
    as_dict: bool,
) -> nn.Module:
    """Build a features-only torchvision module.

    Args:
        name: ``torchvision.models.get_model`` name (e.g. ``\"resnet18\"``).
        weights: Weight enum / string / ``None`` passed to ``get_model``.
        return_nodes: Nodes for ``create_feature_extractor``, or ``None`` to strip heads.
        exclude: Module attribute names replaced with ``Identity`` when not using nodes.
        pool: If True, spatially pool 4D tensors to ``(N, C)``.
        as_dict: If True and multiple ``return_nodes``, return an ``OrderedDict``.

    Returns:
        An ``nn.Module`` producing features.
    """
    model = get_model(name, weights=weights)
    if return_nodes:
        return _FeatureNodes(model, return_nodes, pool=pool, as_dict=as_dict)
    return _StrippedFeatures(model, exclude=exclude, pool=pool)


class _StrippedFeatures(nn.Module):
    """Torchvision model with selected head attributes replaced by Identity."""

    def __init__(self, model: nn.Module, *, exclude: list[str], pool: bool) -> None:
        super().__init__()
        self.pool = pool
        replaced = False
        for attr in exclude:
            if hasattr(model, attr):
                setattr(model, attr, nn.Identity())
                replaced = True
        if not replaced:
            raise ValueError(
                f"none of exclude={exclude!r} found on {type(model).__name__}; "
                "pass return_nodes explicitly (e.g. ['flatten'] or ['avgpool'])"
            )
        self.model = model

    def forward(self, x: Tensor) -> Tensor:
        out = self.model(x)
        if isinstance(out, Tensor):
            return _maybe_pool(out, self.pool)
        raise TypeError(
            f"stripped torchvision model returned {type(out).__name__}; "
            "use return_nodes for multi-output models"
        )


class _FeatureNodes(nn.Module):
    """``create_feature_extractor`` wrapper with ordered node selection."""

    def __init__(
        self,
        model: nn.Module,
        return_nodes: list[str],
        *,
        pool: bool,
        as_dict: bool,
    ) -> None:
        super().__init__()
        if not return_nodes:
            raise ValueError("return_nodes must be non-empty")
        self.nodes = list(return_nodes)
        self.pool = pool
        self.as_dict = as_dict
        node_map = {name: name for name in self.nodes}
        self.extractor = create_feature_extractor(model, return_nodes=node_map)

    def forward(self, x: Tensor) -> Tensor | OrderedDict[str, Tensor]:
        raw = self.extractor(x)
        if self.as_dict:
            return OrderedDict((name, _maybe_pool(raw[name], self.pool)) for name in self.nodes)
        if len(self.nodes) != 1:
            raise RuntimeError(
                "multiple return_nodes require as_dict=True "
                f"(got {self.nodes!r})"
            )
        return _maybe_pool(raw[self.nodes[0]], self.pool)


def _maybe_pool(tensor: Tensor, pool: bool) -> Tensor:
    if pool and tensor.ndim == 4:
        return F.adaptive_avg_pool2d(tensor, 1).flatten(1)
    if pool and tensor.ndim > 2 and tensor.ndim != 4:
        return tensor.flatten(1)
    return tensor
