"""anvil.core.config.base: ``Buildable`` — validated config that builds a runtime object."""

from __future__ import annotations

import inspect
from abc import ABC, abstractmethod
from importlib import import_module
from typing import Any

from pydantic import BaseModel, ConfigDict, model_serializer, model_validator

from anvil.core.config.errors import AnvilConfigError

__all__ = ["Buildable", "qualname", "resolve_target"]


class Buildable[T](BaseModel, ABC):
    """A validated config node that constructs a runtime object.

    Subclasses declare ordinary pydantic fields and implement ``build``. YAML
    ``_target_`` is always a fully-qualified dotted path to a concrete
    ``Buildable`` subclass — never a short name, never a runtime class.
    """

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    @abstractmethod
    def build(self) -> T:
        """Construct the runtime object this config describes."""

    @model_serializer(mode="wrap")
    def _serialize_with_target(self, handler: Any) -> dict[str, Any]:
        return {"_target_": qualname(type(self)), **handler(self)}

    @model_validator(mode="wrap")
    @classmethod
    def _dispatch_target(cls, data: Any, handler: Any, info: Any = None) -> Any:
        _ = info
        if not isinstance(data, dict):
            return handler(data)
        if "_target_" not in data:
            return _validate_without_target(cls, data, handler)
        return _validate_with_target(cls, data, handler)


def qualname(cls: type) -> str:
    """Return ``module.qualname`` for a class."""
    return f"{cls.__module__}.{cls.__qualname__}"


def resolve_target(path: str) -> type[Buildable[Any]]:
    """Import ``path`` and assert it is a concrete ``Buildable`` subclass."""
    if "." not in path:
        raise AnvilConfigError(
            "`_target_` must be a fully-qualified dotted path",
            path="_target_",
            value=path,
            hint=(
                "use e.g. anvil.stock.components.backbones.ResNet18 — short names are not supported"
            ),
        )
    module_path, _, name = path.rpartition(".")
    try:
        module = import_module(module_path)
    except ModuleNotFoundError as exc:
        raise AnvilConfigError(
            "could not import module for `_target_`",
            path="_target_",
            value=path,
            hint=str(exc),
        ) from exc
    try:
        obj = getattr(module, name)
    except AttributeError as exc:
        raise AnvilConfigError(
            f"module has no attribute {name!r}",
            path="_target_",
            value=path,
            hint=f"check the class name on {module_path}",
        ) from exc
    return _assert_concrete_buildable(obj, path)


def _assert_concrete_buildable(obj: Any, path: str) -> type[Buildable[Any]]:
    if not isinstance(obj, type) or not issubclass(obj, Buildable):
        raise AnvilConfigError(
            "`_target_` must name a Buildable config class (not a runtime class)",
            path="_target_",
            value=path,
            hint="in v2, `_target_` points at the pydantic config that builds the object",
        )
    if inspect.isabstract(obj):
        raise AnvilConfigError(
            "`_target_` must name a concrete Buildable subclass",
            path="_target_",
            value=path,
            hint="point at a non-abstract config class",
        )
    return obj


def _validate_without_target(cls: type[Buildable[Any]], data: dict[str, Any], handler: Any) -> Any:
    if inspect.isabstract(cls):
        raise AnvilConfigError(
            "abstract config slot requires an explicit `_target_`",
            path=qualname(cls),
            value=data,
            hint=(f"set `_target_` to a concrete subclass dotted path (annotating {cls.__name__})"),
        )
    return handler(data)


def _validate_with_target(cls: type[Buildable[Any]], data: dict[str, Any], handler: Any) -> Any:
    payload = dict(data)
    target_path = payload.pop("_target_")
    if not isinstance(target_path, str):
        raise AnvilConfigError(
            "`_target_` must be a string dotted path",
            path="_target_",
            value=target_path,
        )
    target = resolve_target(target_path)
    if target is cls:
        return handler(payload)
    return target.model_validate(payload)
