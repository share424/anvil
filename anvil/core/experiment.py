"""anvil.core.experiment: top-level experiment config."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field, SerializeAsAny, field_validator, model_validator

from anvil.core.callback import CallbackConfig, PluginConfig
from anvil.core.config.base import Buildable, resolve_target
from anvil.core.config.errors import AnvilConfigError

__all__ = ["GlobalConfig", "Trainer", "Experiment"]


class GlobalConfig(BaseModel):
    """Experiment identity and reproducibility knobs (YAML key: ``global``)."""

    model_config = ConfigDict(extra="forbid")

    project: str
    name: str
    seed: int = 42
    deterministic: bool = False
    output_dir: str = "outputs"
    tags: list[str] = Field(default_factory=list)
    notes: str | None = None
    strict_shapes: bool = False


class Trainer(Buildable[Any]):
    """Lightning ``Trainer`` config.

    Common knobs are declared explicitly. Extra keys are still allowed and forwarded
    to Lightning for less-common Trainer flags.

    ``callbacks`` / ``plugins`` mirror Lightning's shape
    (``T | list[T] | None``), but hold **configs** (``CallbackConfig`` /
    ``PluginConfig``), not live Lightning objects — same rule as architecture
    slots. Live objects remain the loud escape hatch only.
    """

    model_config = ConfigDict(extra="allow", validate_assignment=True)

    # loop
    max_epochs: int | None = 100
    max_steps: int = -1
    min_epochs: int | None = None
    min_steps: int | None = None
    max_time: Any = None

    # hardware / precision
    accelerator: str = "auto"
    devices: Any = "auto"
    num_nodes: int = 1
    precision: str = "32-true"
    strategy: str = "auto"
    sync_batchnorm: bool = False

    # optimization helpers
    accumulate_grad_batches: int = 1
    gradient_clip_val: float | None = None
    gradient_clip_algorithm: str | None = None

    # data / val cadence
    check_val_every_n_epoch: int | None = 1
    val_check_interval: float | int | None = None
    limit_train_batches: float | int | None = None
    limit_val_batches: float | int | None = None
    limit_test_batches: float | int | None = None
    overfit_batches: float | int = 0

    # logging / UI
    log_every_n_steps: int = 50
    enable_checkpointing: bool = True
    enable_progress_bar: bool = True
    enable_model_summary: bool = True
    model_summary_max_depth: int = 2
    log_device_stats: bool = True
    detect_anomaly: bool = False
    deterministic: bool | str | None = None
    profiler: str | None = None
    barebones: bool = False

    # extensions — Lightning-shaped unions, config-typed (built in ``_build_trainer``)
    callbacks: list[SerializeAsAny[CallbackConfig]] | SerializeAsAny[CallbackConfig] | None = None
    plugins: list[SerializeAsAny[PluginConfig]] | SerializeAsAny[PluginConfig] | None = None
    logger: Any = True

    @model_validator(mode="before")
    @classmethod
    def _coerce_extensions(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data
        out = dict(data)
        if "callbacks" in out:
            out["callbacks"] = _normalize_extension_list(
                out["callbacks"],
                path="trainer.callbacks",
                coerce=_coerce_callback,
            )
        if "plugins" in out:
            out["plugins"] = _normalize_extension_list(
                out["plugins"],
                path="trainer.plugins",
                coerce=_coerce_plugin,
            )
        return out

    def callback_list(self) -> list[CallbackConfig]:
        """Return callbacks as a list (empty if unset)."""
        return _as_list(self.callbacks)

    def plugin_list(self) -> list[PluginConfig]:
        """Return plugins as a list (empty if unset)."""
        return _as_list(self.plugins)

    def build(self) -> Any:
        """Construct a ``lightning.Trainer`` (prefer ``anvil.core.api`` wiring)."""
        import lightning as L

        kwargs = self.model_dump()
        for key in (
            "_target_",
            "log_device_stats",
            "model_summary_max_depth",
            "callbacks",
            "plugins",
        ):
            kwargs.pop(key, None)
        return L.Trainer(**kwargs)


class Experiment(BaseModel):
    """Top-level experiment: global / task / trainer.

    ``task`` accepts a ``Buildable`` or a mapping with dotted-path ``_target_``.
    """

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    global_: GlobalConfig = Field(alias="global")
    task: Any
    trainer: Trainer = Field(default_factory=Trainer)

    @field_validator("task", mode="before")
    @classmethod
    def _coerce_task(cls, value: Any) -> Any:
        if isinstance(value, Buildable):
            return value
        if isinstance(value, dict) and "_target_" in value:
            return _buildable_from_mapping(value)
        if isinstance(value, dict):
            raise AnvilConfigError(
                "task mapping requires `_target_`",
                path="task",
                value=value,
                hint="set `_target_` to a concrete Buildable dotted path",
            )
        raise AnvilConfigError(
            "task must be a Buildable or a mapping with `_target_`",
            path="task",
            value=type(value).__name__,
        )


def _buildable_from_mapping(value: dict[str, Any]) -> Buildable[Any]:
    payload = dict(value)
    target_path = payload.pop("_target_")
    if not isinstance(target_path, str):
        raise AnvilConfigError(
            "`_target_` must be a string dotted path",
            path="_target_",
            value=target_path,
        )
    target = resolve_target(target_path)
    return target.model_validate(payload)


def _normalize_extension_list(
    value: Any,
    *,
    path: str,
    coerce: Any,
) -> list[Any] | None:
    if value is None:
        return None
    if isinstance(value, list):
        return [coerce(item) for item in value]
    return [coerce(value)]


def _coerce_callback(value: Any) -> CallbackConfig:
    if isinstance(value, CallbackConfig):
        return value
    if isinstance(value, dict) and "_target_" in value:
        built = _buildable_from_mapping(value)
        if not isinstance(built, CallbackConfig):
            raise AnvilConfigError(
                "`_target_` must name a CallbackConfig",
                path="trainer.callbacks",
                value=type(built).__name__,
            )
        return built
    raise AnvilConfigError(
        "callback must be a CallbackConfig or mapping with `_target_`",
        path="trainer.callbacks",
        value=type(value).__name__,
        hint=(
            "e.g. {_target_: anvil.stock.callbacks.EarlyStopping, monitor: val/loss, patience: 10} "
            "(not a live lightning.Callback — use CallbackConfig)"
        ),
    )


def _coerce_plugin(value: Any) -> PluginConfig:
    if isinstance(value, PluginConfig):
        return value
    if isinstance(value, dict) and "_target_" in value:
        built = _buildable_from_mapping(value)
        if not isinstance(built, PluginConfig):
            raise AnvilConfigError(
                "`_target_` must name a PluginConfig",
                path="trainer.plugins",
                value=type(built).__name__,
            )
        return built
    raise AnvilConfigError(
        "plugin must be a PluginConfig or mapping with `_target_`",
        path="trainer.plugins",
        value=type(value).__name__,
        hint="subclass PluginConfig and set `_target_` to its dotted path",
    )


def _as_list[T](value: list[T] | T | None) -> list[T]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]
