"""anvil.core.config.parse: plain dict → validated pydantic model."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ValidationError

from anvil.core.config.errors import AnvilConfigError

__all__ = ["parse"]


def parse[M: BaseModel](data: dict[str, Any], model_type: type[M]) -> M:
    """Validate ``data`` as ``model_type``, rewriting pydantic errors."""
    try:
        return model_type.model_validate(data)
    except ValidationError as exc:
        raise AnvilConfigError.from_pydantic(exc) from exc
    except AnvilConfigError:
        raise
    except Exception as exc:
        raise AnvilConfigError(str(exc)) from exc
