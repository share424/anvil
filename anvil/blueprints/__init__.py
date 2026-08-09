"""anvil.blueprints: ready-to-forge experiment recipes.

Requires stock. Install: ``pip install 'anvil[blueprints]'`` (or ``[all]``).
"""

from __future__ import annotations

from anvil.blueprints._deps import require_stock

require_stock()

from anvil.blueprints.classification import ResNet18Classification

__all__ = ["ResNet18Classification"]
