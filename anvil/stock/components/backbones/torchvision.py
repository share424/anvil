"""Torchvision backbone adapter (pretrained-capable)."""

from __future__ import annotations

from typing import Any

from pydantic import ConfigDict, Field, field_validator, model_validator
from torch import nn

from anvil.core.config.errors import AnvilConfigError
from anvil.stock.components.backbones import torchvision_impl
from anvil.stock.components.backbones.resnet import Backbone

__all__ = ["TorchvisionFeatures"]


class TorchvisionFeatures(Backbone):
    r"""Features from a ``torchvision.models.get_model`` network.

    This is the stock exception for reusing torchvision (including pretrained
    ``weights``) instead of reimplementing ImageNet backbones. CIFAR-oriented
    ``ResNet18`` remains for small-input training from scratch.

    Layer selection — choose one:

    * ``return_nodes``: keep only these graph nodes via
      ``create_feature_extractor`` (e.g. ``['flatten']`` skips ``fc``;
      ``['layer2', 'layer3', 'layer4']`` for multi-scale).
    * otherwise: replace ``exclude`` attributes with ``Identity`` (default
      strips ``fc`` / ``classifier`` / ``head`` / ``heads``).

    For classification, use a single node (or stripped head) so ``forward``
    returns one tensor. Set ``as_dict=True`` when multiple ``return_nodes``
    should be returned as an ``OrderedDict`` (detection-style).
    """

    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
        populate_by_name=True,
        serialize_by_alias=True,
    )

    name: str
    out_channels_: list[int] = Field(alias="out_channels")
    weights: str | None = None
    return_nodes: list[str] | None = None
    exclude: list[str] = Field(default_factory=lambda: ["fc", "classifier", "head", "heads"])
    pool: bool = True
    as_dict: bool = False

    @property
    def out_channels(self) -> list[int]:
        """Channel counts declared on the config (wiring contract)."""
        return list(self.out_channels_)

    @field_validator("out_channels_")
    @classmethod
    def _non_empty_channels(cls, value: list[int]) -> list[int]:
        if not value:
            raise AnvilConfigError(
                "out_channels must be non-empty",
                path="out_channels",
                hint="e.g. out_channels=[512] for ResNet-18 flatten features",
            )
        return value

    @field_validator("return_nodes")
    @classmethod
    def _non_empty_nodes(cls, value: list[str] | None) -> list[str] | None:
        if value is not None and len(value) == 0:
            raise AnvilConfigError(
                "return_nodes must be non-empty when set",
                path="return_nodes",
                hint="omit return_nodes to strip exclude heads, or list node names",
            )
        return value

    @model_validator(mode="after")
    def _check_output_contract(self) -> TorchvisionFeatures:
        channels = self.out_channels_
        if self.return_nodes is not None:
            if self.as_dict:
                if len(channels) != len(self.return_nodes):
                    raise AnvilConfigError(
                        "out_channels length must match return_nodes",
                        path="out_channels",
                        value=channels,
                        hint=f"return_nodes has {len(self.return_nodes)} entries",
                    )
            elif len(self.return_nodes) > 1:
                raise AnvilConfigError(
                    "multiple return_nodes require as_dict=True",
                    path="return_nodes",
                    value=self.return_nodes,
                    hint="set as_dict=True, or pass a single node for a tensor output",
                )
            elif len(channels) != 1:
                raise AnvilConfigError(
                    "single-tensor output expects out_channels of length 1",
                    path="out_channels",
                    value=channels,
                )
        elif len(channels) != 1:
            raise AnvilConfigError(
                "stripped-head mode expects out_channels of length 1",
                path="out_channels",
                value=channels,
                hint="or set return_nodes for multi-level features",
            )
        return self

    def build(self) -> nn.Module:
        """Build the torchvision features module."""
        return torchvision_impl.build_torchvision_features(
            self.name,
            self._resolve_weights(),
            return_nodes=self.return_nodes,
            exclude=list(self.exclude),
            pool=self.pool,
            as_dict=self.as_dict,
        )

    def _resolve_weights(self) -> Any:
        if self.weights is None:
            return None
        key = self.weights.strip()
        if key.upper() == "DEFAULT":
            return "DEFAULT"
        try:
            from torchvision.models import get_model_weights

            enum_cls = get_model_weights(self.name)
            if key in enum_cls.__members__:
                return enum_cls[key]
        except Exception:  # ponytail: fall through to raw string for get_model
            pass
        return key
