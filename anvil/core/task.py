"""anvil.core.task: ``Task`` config, ``Net``, and internal ``TaskModule``."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field, fields, is_dataclass, replace
from typing import Any, ClassVar

import lightning as L
import torch
from pydantic import ConfigDict, Field, SerializeAsAny, model_validator
from torch import Tensor, nn
from torch.optim import Optimizer as TorchOptimizer
from torchmetrics import Metric

from anvil.core.config.base import Buildable, resolve_target
from anvil.core.config.errors import AnvilConfigError, AnvilContractError, AnvilShapeError
from anvil.core.contracts import Batch, Stage
from anvil.core.data import Data

__all__ = ["StepOutput", "Net", "Optimizer", "Scheduler", "Task", "TaskModule"]

_NON_MODULE_FIELDS = frozenset(
    {
        "data",
        "optimizer",
        "scheduler",
        "metrics",
        "criterion",
        "param_groups",
        "ema",
    }
)


@dataclass
class StepOutput:
    """Return value of ``Task.step``.

    Attributes:
        loss: Scalar loss tensor.
        preds: Predictions for metrics / logging.
        targets: Ground-truth targets for metrics.
        log_dict: Extra scalars to log this step.
    """

    loss: Tensor
    preds: Any = None
    targets: Any = None
    log_dict: dict[str, Tensor] = field(default_factory=dict)


class Net:
    """Built modules, addressed by the task field name that configured them.

    ``Net`` is intentionally *not* an ``nn.Module``. Modules are registered as
    direct children of ``TaskModule`` so Lightning's model summary shows
    ``backbone`` / ``head`` (etc.) instead of a single opaque ``Net`` row.
    """

    def __init__(self, modules: dict[str, nn.Module]) -> None:
        """Store modules for attribute / mapping access.

        Args:
            modules: Mapping of slot name to built ``nn.Module``.
        """
        object.__setattr__(self, "_modules", dict(modules))
        for name, module in modules.items():
            object.__setattr__(self, name, module)

    def __getitem__(self, name: str) -> nn.Module:
        """Return a module by slot name."""
        return self._modules[name]

    def __contains__(self, name: object) -> bool:
        """Return whether ``name`` is a registered slot."""
        return name in self._modules

    def __iter__(self) -> Any:
        """Iterate slot names."""
        return iter(self._modules)

    def __len__(self) -> int:
        """Return the number of modules."""
        return len(self._modules)

    def keys(self) -> Any:
        """Return slot names."""
        return self._modules.keys()

    def values(self) -> Any:
        """Return modules."""
        return self._modules.values()

    def items(self) -> Any:
        """Return ``(name, module)`` pairs."""
        return self._modules.items()

    def __getattr__(self, name: str) -> Any:
        """Attribute access for slot names (and raise like a missing attr)."""
        modules = object.__getattribute__(self, "_modules")
        if name in modules:
            return modules[name]
        raise AttributeError(name)


class Optimizer(Buildable[Any], ABC):
    """Config for a torch optimizer.

    ``build()`` is not used for construction — call ``build_with_params`` once
    parameter groups exist (inside ``TaskModule.configure_optimizers``).
    """

    def build(self) -> Any:
        """Refuse no-arg build; optimizers need parameters."""
        raise AnvilConfigError(
            "Optimizer.build() requires parameters",
            hint="TaskModule calls build_with_params(params) after the Net exists",
        )

    @abstractmethod
    def build_with_params(self, params: Any) -> TorchOptimizer:
        """Construct the optimizer for ``params``."""


class Scheduler(Buildable[Any], ABC):
    """Config for a learning-rate scheduler."""

    def build(self) -> Any:
        """Refuse no-arg build; schedulers need an optimizer."""
        raise AnvilConfigError(
            "Scheduler.build() requires an optimizer",
            hint="TaskModule calls build_with_optimizer(opt) in configure_optimizers",
        )

    @abstractmethod
    def build_with_optimizer(self, optimizer: TorchOptimizer) -> Any:
        """Construct the scheduler for ``optimizer``."""


class Task(Buildable["TaskModule"], ABC):
    """Pydantic task config: architecture slots, data contract, and ``step`` logic."""

    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
        arbitrary_types_allowed=True,
    )

    batch_type: ClassVar[type[Batch]]
    data: SerializeAsAny[Data]
    optimizer: SerializeAsAny[Optimizer] | None = None
    scheduler: SerializeAsAny[Scheduler] | None = None
    metrics: dict[str, Buildable[Any]] = Field(default_factory=dict)

    @abstractmethod
    def step(self, net: Net, batch: Any, stage: Stage) -> StepOutput:
        """Compute loss and predictions for one batch."""

    def example_forward(self, net: Net, x: Tensor) -> Any:
        """Run a shape-check forward. Override for multi-slot nets.

        Args:
            net: Built modules.
            x: Example input tensor (often on the meta device).

        Returns:
            Model output (unused except for shape errors).
        """
        if len(net) == 1:
            return next(iter(net.values()))(x)
        raise AnvilShapeError(
            "multi-module Net requires Task.example_forward override",
            path=type(self).__name__,
            hint="implement example_forward to wire backbone → head (etc.)",
        )

    def build_net(self) -> Net:
        """Build every module-producing field into a ``Net``."""
        modules: dict[str, nn.Module] = {}
        for name in type(self).model_fields:
            if name in _NON_MODULE_FIELDS:
                continue
            value = getattr(self, name)
            module = _as_module(name, value)
            if module is not None:
                modules[name] = module
        if not modules:
            raise AnvilConfigError(
                "task built an empty Net",
                path=type(self).__name__,
                hint="declare at least one Buildable field that builds an nn.Module",
            )
        return Net(modules)

    def build(self) -> TaskModule:
        """Construct the Lightning module for this task."""
        return TaskModule(task=self, net=self.build_net())

    @model_validator(mode="before")
    @classmethod
    def _coerce_metrics(cls, data: Any) -> Any:
        """Rehydrate ``metrics`` entries that arrived as ``{_target_: ...}`` dicts."""
        if not isinstance(data, dict):
            return data
        metrics = data.get("metrics")
        if not isinstance(metrics, dict):
            return data
        coerced = {name: _coerce_buildable(value) for name, value in metrics.items()}
        return {**data, "metrics": coerced}

    @model_validator(mode="after")
    def _check_batch_contract(self) -> Task:
        data_batch = self.data.batch_type
        if not issubclass(data_batch, self.batch_type):
            raise AnvilContractError(
                "incompatible batch contract",
                path="task.data",
                value=type(self.data).__name__,
                hint=(
                    f"{type(self.data).__name__} produces {data_batch.__name__}, "
                    f"but {type(self).__name__} consumes {self.batch_type.__name__}"
                ),
            )
        return self


class TaskModule(L.LightningModule):
    """Framework-internal LightningModule — users subclass ``Task``, not this."""

    def __init__(self, task: Task, net: Net) -> None:
        """Attach a validated task config and its built ``Net``.

        Args:
            task: Validated task config (kept for ``step`` / dumps).
            net: Built architecture modules.
        """
        super().__init__()
        self.task = task
        self.net = net
        for name, module in net.items():
            self.add_module(name, module)
        self.metrics = nn.ModuleDict(
            {name: metric.build() for name, metric in task.metrics.items()}
        )
        self.check_batches = False
        self.save_hyperparameters(ignore=["task", "net"])

    def forward(self, x: Tensor) -> Any:
        """Delegate to ``task.example_forward``."""
        return self.task.example_forward(self.net, x)

    def transfer_batch_to_device(self, batch: Any, device: torch.device, dataloader_idx: int = 0) -> Any:
        """Move a batch to ``device``, reconstructing frozen dataclasses.

        Lightning's default mover mutates dataclass fields in place and rejects
        ``frozen=True`` batches.
        """
        _ = dataloader_idx
        return _move_batch(batch, device)

    def training_step(self, batch: Any, batch_idx: int) -> Tensor:
        """Run the train stage."""
        _ = batch_idx
        return _run_step(self, batch, Stage.TRAIN)

    def validation_step(self, batch: Any, batch_idx: int) -> Tensor:
        """Run the val stage."""
        _ = batch_idx
        return _run_step(self, batch, Stage.VAL)

    def test_step(self, batch: Any, batch_idx: int) -> Tensor:
        """Run the test stage."""
        _ = batch_idx
        return _run_step(self, batch, Stage.TEST)

    def on_validation_epoch_end(self) -> None:
        """Log and reset validation metrics."""
        _log_metrics(self, Stage.VAL)

    def on_test_epoch_end(self) -> None:
        """Log and reset test metrics."""
        _log_metrics(self, Stage.TEST)

    def configure_optimizers(self) -> Any:
        """Build the optimizer (and optional scheduler) from the task config."""
        params = self.parameters()
        if self.task.optimizer is None:
            from torch.optim import Adam

            opt: TorchOptimizer = Adam(params)
        else:
            opt = self.task.optimizer.build_with_params(params)
        if self.task.scheduler is None:
            return opt
        scheduler = self.task.scheduler.build_with_optimizer(opt)
        return {"optimizer": opt, "lr_scheduler": {"scheduler": scheduler, "interval": "epoch"}}


def _as_module(name: str, value: Any) -> nn.Module | None:
    if isinstance(value, nn.Module):
        return _for_current_factory_device(value)
    if isinstance(value, Buildable):
        built = value.build()
        if isinstance(built, nn.Module):
            return built
        return None
    if value is None:
        return None
    raise AnvilConfigError(
        f"task field {name!r} is not a Buildable or nn.Module",
        path=name,
        value=type(value).__name__,
    )


def _for_current_factory_device(module: nn.Module) -> nn.Module:
    """Return ``module``, or an empty meta clone when the tensor factory is meta.

    Live modules must not be mutated: ``to_empty`` would otherwise move the user's
    escape-hatch weights onto ``meta`` and break the subsequent smoke check.
    """
    if torch.empty(0).device.type != "meta":
        return module
    import copy

    return copy.deepcopy(module).to_empty(device="meta")


def _coerce_buildable(value: Any) -> Any:
    if isinstance(value, Buildable):
        return value
    if isinstance(value, dict) and "_target_" in value:
        payload = dict(value)
        target_path = payload.pop("_target_")
        if not isinstance(target_path, str):
            raise AnvilConfigError(
                "`_target_` must be a string dotted path",
                path="metrics._target_",
                value=target_path,
            )
        target = resolve_target(target_path)
        return target.model_validate(payload)
    return value


def _move_batch(batch: Any, device: torch.device) -> Any:
    if isinstance(batch, Tensor):
        return batch.to(device)
    if isinstance(batch, (list, tuple)):
        moved = [_move_batch(item, device) for item in batch]
        return type(batch)(moved)
    if isinstance(batch, dict):
        return {key: _move_batch(value, device) for key, value in batch.items()}
    if is_dataclass(batch) and not isinstance(batch, type):
        updates = {f.name: _move_batch(getattr(batch, f.name), device) for f in fields(batch)}
        return replace(batch, **updates)
    return batch


def _run_step(module: TaskModule, batch: Any, stage: Stage) -> Tensor:
    from anvil.core.runtime.batchcheck import check_batch

    check_batch(batch, module.task.batch_type, enabled=module.check_batches)
    output = module.task.step(module.net, batch, stage)
    module.log(f"{stage.value}/loss", output.loss, prog_bar=True, on_step=True, on_epoch=True)
    for key, value in output.log_dict.items():
        module.log(f"{stage.value}/{key}", value, on_step=True, on_epoch=False)
    _update_metrics(module, output, stage)
    return output.loss


def _update_metrics(module: TaskModule, output: StepOutput, stage: Stage) -> None:
    if stage is Stage.TRAIN or not module.metrics:
        return
    if output.preds is None or output.targets is None:
        return
    for metric in module.metrics.values():
        if isinstance(metric, Metric):
            metric.update(output.preds, output.targets)


def _log_metrics(module: TaskModule, stage: Stage) -> None:
    for name, metric in module.metrics.items():
        if not isinstance(metric, Metric):
            continue
        module.log(f"{stage.value}/{name}", _metric_value(metric), prog_bar=True, on_epoch=True)
        metric.reset()


def _metric_value(metric: Metric) -> Any:
    """Call ``metric.compute()`` without confusing the type checker."""
    m: Any = metric
    return m.compute()
