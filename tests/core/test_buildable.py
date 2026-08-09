"""Phase 1: Buildable dotted-path dispatch and round-trip."""

from __future__ import annotations

import pytest

from anvil.core.config import (
    AnvilConfigError,
    parse,
    qualname,
    resolve_target,
)
from tests.core._config_toys import Backbone, ResNet, ResNet18
from tests.core._config_toys import ConfigToyTask as ToyTask


def test_qualname_is_dotted() -> None:
    """
    Condition:
    A concrete Buildable class is named.

    Expected:
    qualname returns module.qualname with a dot.
    """
    name = qualname(ResNet)
    assert name.endswith(".ResNet")
    assert "." in name


def test_resolve_target_concrete() -> None:
    """
    Condition:
    resolve_target is given this module's ResNet dotted path.

    Expected:
    The ResNet class is returned.
    """
    assert resolve_target(qualname(ResNet)) is ResNet


def test_resolve_target_rejects_short_name() -> None:
    """
    Condition:
    `_target_` is a short name without dots.

    Expected:
    AnvilConfigError — never a registry lookup.
    """
    with pytest.raises(AnvilConfigError, match="dotted path"):
        resolve_target("resnet18")


def test_resolve_target_rejects_non_buildable() -> None:
    """
    Condition:
    `_target_` points at torch.nn.Linear.

    Expected:
    AnvilConfigError explaining Buildable requirement.
    """
    with pytest.raises(AnvilConfigError, match="Buildable"):
        resolve_target("torch.nn.Linear")


def test_resolve_target_missing_module() -> None:
    """
    Condition:
    `_target_` module does not exist.

    Expected:
    AnvilConfigError wrapping the import failure.
    """
    with pytest.raises(AnvilConfigError, match="could not import"):
        resolve_target("nosuchmod.Thing")


def test_abstract_slot_requires_target() -> None:
    """
    Condition:
    Validating Backbone (abstract) from a dict without `_target_`.

    Expected:
    AnvilConfigError requiring an explicit dotted path.
    """
    with pytest.raises(AnvilConfigError, match="explicit"):
        Backbone.model_validate({"depth": 18})


def test_concrete_omits_target() -> None:
    """
    Condition:
    ResNet18 is validated from a plain field dict without `_target_`.

    Expected:
    Instance is constructed with defaults.
    """
    model = ResNet18.model_validate({})
    assert model.depth == 18


def test_polymorphic_round_trip() -> None:
    """
    Condition:
    ToyTask holds ResNet(depth=101) in a SerializeAsAny[Backbone] slot.

    Expected:
    model_dump embeds dotted `_target_`; parse restores an equal object.
    """
    task = ToyTask(backbone=ResNet(depth=101))
    dumped = task.model_dump()
    assert dumped["backbone"]["_target_"] == qualname(ResNet)
    assert dumped["backbone"]["depth"] == 101
    restored = parse(dumped, ToyTask)
    assert restored == task
    assert type(restored.backbone) is ResNet
    assert restored.backbone.depth == 101


def test_build_is_pure() -> None:
    """
    Condition:
    A concrete ResNet config is built.

    Expected:
    build() returns the runtime product without side config mutation.
    """
    cfg = ResNet(depth=34)
    assert cfg.build() == {"depth": 34}
