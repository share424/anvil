"""anvil.core.config.errors: framework exception hierarchy."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from pydantic import ValidationError

__all__ = [
    "AnvilError",
    "AnvilConfigError",
    "AnvilContractError",
    "AnvilBuildError",
    "AnvilShapeError",
    "AnvilSmokeError",
]


class AnvilError(Exception):
    """Base for every framework-raised error."""

    def __init__(
        self,
        message: str,
        *,
        path: str | None = None,
        value: Any = None,
        hint: str | None = None,
    ) -> None:
        """Create an error with an optional config path and hint.

        Args:
            message: Short description of what went wrong.
            path: Dotted config path responsible, if known. Defaults to None.
            value: Offending value, if known. Defaults to None.
            hint: Concrete suggestion for fixing the error. Defaults to None.
        """
        self.path = path
        self.value = value
        self.hint = hint
        super().__init__(_format(message, path, value, hint))


class AnvilConfigError(AnvilError):
    """Parse, unknown field, or unresolvable `_target_`."""

    @classmethod
    def from_pydantic(cls, exc: ValidationError) -> AnvilConfigError:
        """Rewrite a pydantic ValidationError with dotted paths."""
        errors = exc.errors()
        if not errors:
            return cls(str(exc))
        first = errors[0]
        loc = ".".join(str(part) for part in first.get("loc", ()))
        return cls(
            str(first.get("msg", exc)),
            path=loc or None,
            value=first.get("input"),
            hint=_hint_for_pydantic(first),
        )


class AnvilContractError(AnvilError):
    """Wiring or batch-contract mismatch."""


class AnvilBuildError(AnvilError):
    """A ``build()`` call failed."""


class AnvilShapeError(AnvilError):
    """Meta-device shape check failed."""


class AnvilSmokeError(AnvilError):
    """Pre-flight smoke check failed."""


def _format(message: str, path: str | None, value: Any, hint: str | None) -> str:
    lines = [message if path is None else f"{message} at '{path}'"]
    if value is not None:
        lines.append(f"  value: {value!r}")
    if hint:
        lines.append(f"  hint:  {hint}")
    return "\n".join(lines)


def _hint_for_pydantic(error: Mapping[str, Any]) -> str | None:
    err_type = error.get("type")
    if err_type == "extra_forbidden":
        return "remove the unknown field, or check for a typo in the field name"
    if err_type == "missing":
        return "supply the required field"
    return None
