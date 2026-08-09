"""anvil.core.runtime.logging: process-wide logger setup."""

from __future__ import annotations

import logging

__all__ = ["configure_logging", "get_logger"]

_CONFIGURED = False


def configure_logging(level: int = logging.INFO) -> None:
    """Configure the root ``anvil`` logger once.

    Args:
        level: Logging level. Defaults to ``logging.INFO``.
    """
    global _CONFIGURED
    if _CONFIGURED:
        return
    logger = logging.getLogger("anvil")
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s"))
        logger.addHandler(handler)
    logger.setLevel(level)
    logger.propagate = False
    _CONFIGURED = True


def get_logger(name: str) -> logging.Logger:
    """Return a child logger under ``anvil``.

    Args:
        name: Logger name (usually ``__name__``).

    Returns:
        A ``logging.Logger`` instance.
    """
    configure_logging()
    if name.startswith("anvil."):
        return logging.getLogger(name)
    return logging.getLogger(f"anvil.{name}")
