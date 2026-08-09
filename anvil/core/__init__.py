"""anvil.core: frozen framework (the anvil)."""

from __future__ import annotations

from anvil.core.api import export, find_batch_size, find_lr, forge, resume, test, validate
from anvil.core.callback import CallbackConfig, PluginConfig
from anvil.core.config import (
    AnvilBuildError,
    AnvilConfigError,
    AnvilContractError,
    AnvilError,
    AnvilShapeError,
    AnvilSmokeError,
    Buildable,
    load_yaml,
    parse,
    qualname,
    resolve_target,
)
from anvil.core.contracts import Batch, Sample, Split, Stage
from anvil.core.data import Data
from anvil.core.experiment import Experiment, GlobalConfig, Trainer
from anvil.core.task import Net, Optimizer, Scheduler, StepOutput, Task, TaskModule

__all__ = [
    "forge",
    "resume",
    "validate",
    "test",
    "export",
    "find_batch_size",
    "find_lr",
    "CallbackConfig",
    "PluginConfig",
    "Buildable",
    "qualname",
    "resolve_target",
    "parse",
    "load_yaml",
    "AnvilError",
    "AnvilConfigError",
    "AnvilContractError",
    "AnvilBuildError",
    "AnvilShapeError",
    "AnvilSmokeError",
    "Batch",
    "Sample",
    "Stage",
    "Split",
    "Data",
    "Experiment",
    "GlobalConfig",
    "Trainer",
    "Net",
    "Optimizer",
    "Scheduler",
    "StepOutput",
    "Task",
    "TaskModule",
]

# Re-exports a function named ``test``; this package is not a pytest suite.
__test__ = False
