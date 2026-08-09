"""anvil: config-driven DL experiments.

Core is always available. Stock and blueprints are optional layers
(``pip install 'anvil[stock]'`` / ``'anvil[blueprints]'`` / ``'anvil[all]'``).
"""

from __future__ import annotations

from anvil.core.api import export, find_batch_size, find_lr, forge, resume, test, validate

__all__ = [
    "__version__",
    "forge",
    "resume",
    "validate",
    "test",
    "export",
    "find_batch_size",
    "find_lr",
]

__version__ = "0.1.0"

# Re-exports a function named ``test``; this package is not a pytest suite.
__test__ = False
