"""TaskModule registers architecture slots as top-level children."""

from __future__ import annotations

from anvil.core.task import TaskModule
from tests.core._toys import ToyTask


def test_task_module_summary_lists_slot_names() -> None:
    """
    Condition:
    ToyTask builds a TaskModule.

    Expected:
    Named children include the architecture slot (model), not a nested Net.
    """
    module = ToyTask().build()
    assert isinstance(module, TaskModule)
    child_names = {name for name, _ in module.named_children()}
    assert "model" in child_names
    assert "net" not in child_names
    assert module.net.model is module.model
