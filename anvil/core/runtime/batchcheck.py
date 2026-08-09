"""anvil.core.runtime.batchcheck: optional jaxtyping checks via beartype."""

from __future__ import annotations

import os
import typing
from dataclasses import fields, is_dataclass
from typing import Any, get_type_hints

from anvil.core.config.errors import AnvilShapeError
from anvil.core.contracts import Batch
from anvil.core.runtime.logging import get_logger

__all__ = ["batch_checking_enabled", "check_batch", "beartype_available"]

_log = get_logger(__name__)
_warned_missing = False


def beartype_available() -> bool:
    """Return whether the optional ``beartype`` extra is importable."""
    try:
        import beartype  # noqa: F401
    except ImportError:
        return False
    return True


def batch_checking_enabled(*, strict_shapes: bool = False, dry_run: bool = False) -> bool:
    """Return whether batch jaxtyping checks should run.

    Enabled when ``global.strict_shapes`` is set, under ``--dry-run``, when
    ``ANVIL_STRICT_SHAPES=1``, or when pytest is running (``PYTEST_CURRENT_TEST``).
    """
    if strict_shapes or dry_run:
        return True
    if os.environ.get("ANVIL_STRICT_SHAPES", "").strip() in {"1", "true", "True"}:
        return True
    if os.environ.get("PYTEST_CURRENT_TEST"):
        return True
    return False


def check_batch(batch: Any, expected_type: type[Batch], *, enabled: bool) -> None:
    """Typecheck a batch instance when checking is enabled and beartype is installed.

    Args:
        batch: Runtime batch (dataclass instance preferred).
        expected_type: Task's declared ``batch_type``.
        enabled: Whether checking is active for this run.

    Raises:
        AnvilShapeError: If the batch fails jaxtyping/beartype checks.
    """
    if not enabled:
        return
    if not isinstance(batch, expected_type):
        # Tuple/list collate remains allowed for core toys without Batch dataclasses.
        if not is_dataclass(batch) or not isinstance(batch, Batch):
            return
        raise AnvilShapeError(
            "batch type mismatch",
            path="batch",
            value=type(batch).__name__,
            hint=f"expected {expected_type.__name__}",
        )
    if not beartype_available():
        global _warned_missing
        if not _warned_missing:
            _log.warning(
                "batch shape checks requested but beartype is not installed; "
                "pip install 'anvil[all]' to enable jaxtyping checks"
            )
            _warned_missing = True
        return
    _jaxtype_check_dataclass(batch)


def _jaxtype_check_dataclass(batch: Any) -> None:
    from beartype.door import die_if_unbearable

    hints = get_type_hints(type(batch), include_extras=True)
    for field in fields(batch):
        if field.name not in hints:
            continue
        annotation = hints[field.name]
        if annotation is Any or typing.get_origin(annotation) is typing.ClassVar:
            continue
        value = getattr(batch, field.name)
        try:
            die_if_unbearable(value, annotation)
        except Exception as exc:
            raise AnvilShapeError(
                "batch field failed jaxtyping check",
                path=f"batch.{field.name}",
                value=type(value).__name__,
                hint=str(exc),
            ) from exc
