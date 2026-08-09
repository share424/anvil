"""anvil.core.api: ``forge``, ``resume``, and ``find_batch_size`` entrypoints."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Literal

import lightning as L
from lightning.pytorch.callbacks import DeviceStatsMonitor, ModelCheckpoint, ModelSummary

from anvil.core.config.base import Buildable
from anvil.core.config.errors import (
    AnvilBuildError,
    AnvilConfigError,
    AnvilShapeError,
    AnvilSmokeError,
)
from anvil.core.config.loader import load_yaml
from anvil.core.config.parse import parse
from anvil.core.experiment import Experiment, GlobalConfig, Trainer
from anvil.core.runtime import smoke as smoke_mod
from anvil.core.runtime.artifacts import (
    RunDirectory,
    append_resumed,
    create_run_directory,
    refresh_latest,
    write_artifacts,
)
from anvil.core.runtime.batchcheck import batch_checking_enabled
from anvil.core.runtime.batchsize import scale_batch_size
from anvil.core.runtime.export_onnx import export_onnx as _export_onnx
from anvil.core.runtime.export_onnx import load_checkpoint_weights, parse_input_shape
from anvil.core.runtime.gpu import GpuUsageLogger, device_stats_enabled
from anvil.core.runtime.live import assert_run_resumable
from anvil.core.runtime.logging import configure_logging, get_logger
from anvil.core.runtime.lr import find_learning_rate
from anvil.core.runtime.project import find_last_checkpoint, resolve_run_directory
from anvil.core.runtime.seeding import seed_everything
from anvil.core.runtime.shapecheck import check_shapes
from anvil.core.task import Task, TaskModule

__all__ = [
    "forge",
    "resume",
    "validate",
    "test",
    "export",
    "find_batch_size",
    "find_lr",
]

# Not a pytest module (re-exports a function named ``test``).
__test__ = False

_log = get_logger(__name__)


def forge(
    config: str | Path | dict[str, Any] | Experiment | Task,
    overrides: list[str] | None = None,
    *,
    dry_run: bool = False,
    no_smoke: bool = False,
    raise_on_error: bool = False,
) -> int:
    """Run an experiment from any supported config source.

    Args:
        config: YAML path, dict, ``Experiment``, or bare ``Task``.
        overrides: CLI-style ``key=value`` overrides. Defaults to None.
        dry_run: If True, stop after smoke. Defaults to False.
        no_smoke: If True, skip the smoke check. Defaults to False.
        raise_on_error: If True, raise instead of returning an exit code.
            Defaults to False.

    Returns:
        Process exit code (0 success, 1 config, 2 shape/smoke, 3 training).
    """
    configure_logging()
    try:
        return _forge(
            config,
            overrides=overrides,
            dry_run=dry_run,
            no_smoke=no_smoke,
        )
    except (AnvilConfigError, AnvilShapeError, AnvilSmokeError) as exc:
        if raise_on_error:
            raise
        code = 2 if isinstance(exc, (AnvilShapeError, AnvilSmokeError)) else 1
        _log.error("%s", exc)
        return code
    except Exception as exc:
        if raise_on_error:
            raise
        _log.error("anvil.forge failed: %s", exc)
        return 3


def resume(
    target: str | Path,
    overrides: list[str] | None = None,
    *,
    no_smoke: bool = True,
    raise_on_error: bool = False,
) -> int:
    """Continue the most recent run of a project, or a specific run directory.

    Args:
        target: Run directory, project dir, or ``project/name``.
        overrides: Optional overrides (recorded; shape-changing ones should fail later).
            Defaults to None.
        no_smoke: Skip smoke by default on resume. Defaults to True.
        raise_on_error: Raise instead of exit codes. Defaults to False.

    Returns:
        Process exit code.
    """
    configure_logging()
    try:
        run_dir = resolve_run_directory(target)
        assert_run_resumable(run_dir)
        ckpt = find_last_checkpoint(run_dir)
        resolved = run_dir / "config.resolved.yaml"
        return _forge(
            resolved,
            overrides=overrides,
            dry_run=False,
            no_smoke=no_smoke,
            resume_ckpt=str(ckpt),
            reuse_run_dir=run_dir,
        )
    except (AnvilConfigError, AnvilShapeError, AnvilSmokeError) as exc:
        if raise_on_error:
            raise
        code = 2 if isinstance(exc, (AnvilShapeError, AnvilSmokeError)) else 1
        _log.error("%s", exc)
        return code
    except Exception as exc:
        if raise_on_error:
            raise
        _log.error("anvil.resume failed: %s", exc)
        return 3


def validate(
    config: str | Path | dict[str, Any] | Experiment | Task,
    ckpt: str | Path,
    overrides: list[str] | None = None,
    *,
    raise_on_error: bool = False,
) -> int:
    """Run Lightning validation from a checkpoint.

    Args:
        config: YAML path, dict, ``Experiment``, or bare ``Task``.
        ckpt: Checkpoint path (``last.ckpt`` / ``*.ckpt``).
        overrides: CLI-style overrides. Defaults to None.
        raise_on_error: Raise instead of exit codes. Defaults to False.

    Returns:
        Process exit code.
    """
    return _evaluate(
        config,
        ckpt,
        overrides=overrides,
        mode="validate",
        raise_on_error=raise_on_error,
    )


def test(
    config: str | Path | dict[str, Any] | Experiment | Task,
    ckpt: str | Path,
    overrides: list[str] | None = None,
    *,
    raise_on_error: bool = False,
) -> int:
    """Run Lightning test from a checkpoint.

    Args:
        config: YAML path, dict, ``Experiment``, or bare ``Task``.
        ckpt: Checkpoint path (``last.ckpt`` / ``*.ckpt``).
        overrides: CLI-style overrides. Defaults to None.
        raise_on_error: Raise instead of exit codes. Defaults to False.

    Returns:
        Process exit code.
    """
    return _evaluate(
        config,
        ckpt,
        overrides=overrides,
        mode="test",
        raise_on_error=raise_on_error,
    )


def _evaluate(
    config: str | Path | dict[str, Any] | Experiment | Task,
    ckpt: str | Path,
    *,
    overrides: list[str] | None,
    mode: Literal["validate", "test"],
    raise_on_error: bool,
) -> int:
    configure_logging()
    try:
        ckpt_path = Path(ckpt)
        if not ckpt_path.is_file():
            raise AnvilConfigError(
                "checkpoint not found",
                path="--ckpt",
                value=str(ckpt_path),
                hint="pass a path to last.ckpt from a completed forge",
            )
        experiment = _to_experiment(config, overrides)
        g = experiment.global_
        run = create_run_directory(g.output_dir, g.project, f"{g.name}-{mode}", None)
        write_artifacts(run, experiment, overrides)
        refresh_latest(run, g.project, f"{g.name}-{mode}", g.output_dir)
        seed_everything(g.seed, deterministic=g.deterministic)
        data = experiment.task.data.build()
        module = experiment.task.build()
        assert isinstance(module, TaskModule)
        module.check_batches = batch_checking_enabled(
            strict_shapes=g.strict_shapes,
            dry_run=False,
        )
        trainer = _build_trainer(experiment.trainer, run)
        if mode == "validate":
            trainer.validate(module, datamodule=data, ckpt_path=str(ckpt_path))
        else:
            trainer.test(module, datamodule=data, ckpt_path=str(ckpt_path))
        return 0
    except (AnvilConfigError, AnvilShapeError, AnvilSmokeError) as exc:
        if raise_on_error:
            raise
        code = 2 if isinstance(exc, (AnvilShapeError, AnvilSmokeError)) else 1
        _log.error("%s", exc)
        return code
    except Exception as exc:
        if raise_on_error:
            raise
        _log.error("anvil.%s failed: %s", mode, exc)
        return 3


def export(
    config: str | Path | dict[str, Any] | Experiment | Task,
    ckpt: str | Path,
    out: str | Path,
    overrides: list[str] | None = None,
    *,
    input_shape: str | tuple[int, ...] | list[int] | None = None,
    opset: int = 17,
    raise_on_error: bool = False,
) -> int:
    """Export the task inference graph to ONNX.

    Loads ``ckpt`` weights into a freshly built ``TaskModule``, then exports
    ``Task.example_forward`` (not loss/metrics) via ``torch.onnx.export``.

    Args:
        config: YAML path, dict, ``Experiment``, or bare ``Task``.
        ckpt: Checkpoint path (``last.ckpt`` / ``*.ckpt``).
        out: Destination ``.onnx`` path.
        overrides: CLI-style overrides. Defaults to None.
        input_shape: Dummy input shape (``1,3,32,32`` or tuple). Defaults to
            ``data.example_input_shape`` with batch size 1.
        opset: ONNX opset. Defaults to 17.
        raise_on_error: Raise instead of exit codes. Defaults to False.

    Returns:
        Process exit code (0 success, 1 config, 2 shape/smoke, 3 export error).
    """
    configure_logging()
    try:
        ckpt_path = Path(ckpt)
        if not ckpt_path.is_file():
            raise AnvilConfigError(
                "checkpoint not found",
                path="--ckpt",
                value=str(ckpt_path),
                hint="pass a path to last.ckpt from a completed forge",
            )
        experiment = _to_experiment(config, overrides)
        g = experiment.global_
        seed_everything(g.seed, deterministic=g.deterministic)
        module = experiment.task.build()
        assert isinstance(module, TaskModule)
        load_checkpoint_weights(module, ckpt_path)
        module.eval()
        shape = parse_input_shape(input_shape)
        written = _export_onnx(
            module,
            out,
            input_shape=shape,
            opset=opset,
        )
        print(f"wrote {written}")
        return 0
    except (AnvilConfigError, AnvilShapeError, AnvilSmokeError, AnvilBuildError) as exc:
        if raise_on_error:
            raise
        code = 2 if isinstance(exc, (AnvilShapeError, AnvilSmokeError)) else 1
        if isinstance(exc, AnvilBuildError):
            code = 3
        _log.error("%s", exc)
        return code
    except Exception as exc:
        if raise_on_error:
            raise
        _log.error("anvil.export failed: %s", exc)
        return 3


def find_batch_size(
    config: str | Path | dict[str, Any] | Experiment | Task,
    overrides: list[str] | None = None,
    *,
    mode: Literal["power", "binsearch"] = "power",
    init_val: int = 2,
    max_trials: int = 25,
    steps_per_trial: int = 3,
    max_val: int = 8192,
    raise_on_error: bool = False,
) -> int:
    """Search for the largest ``task.data.batch_size`` that fits in memory.

    Args:
        config: YAML path, dict, ``Experiment``, or bare ``Task``.
        overrides: CLI-style overrides. Defaults to None.
        mode: ``power`` or ``binsearch``. Defaults to ``power``.
        init_val: Starting batch size. Defaults to 2.
        max_trials: Maximum tuner iterations. Defaults to 25.
        steps_per_trial: Steps per trial. Defaults to 3.
        max_val: Upper bound. Defaults to 8192.
        raise_on_error: Raise instead of returning -1. Defaults to False.

    Returns:
        Suggested batch size, or ``-1`` on failure when not raising.
    """
    configure_logging()
    try:
        experiment = _to_experiment(config, overrides)
        g = experiment.global_
        seed_everything(g.seed, deterministic=g.deterministic)
        data = experiment.task.data.build()
        module = experiment.task.build()
        assert isinstance(module, TaskModule)
        size = scale_batch_size(
            module,
            data,
            accelerator=experiment.trainer.accelerator,
            devices=experiment.trainer.devices,
            precision=experiment.trainer.precision,
            mode=mode,
            init_val=init_val,
            max_trials=max_trials,
            steps_per_trial=steps_per_trial,
            max_val=max_val,
        )
        _log.info("use override: task.data.batch_size=%s", size)
        print(f"task.data.batch_size={size}")
        return size
    except (AnvilConfigError, AnvilShapeError, AnvilSmokeError) as exc:
        if raise_on_error:
            raise
        _log.error("%s", exc)
        return -1
    except Exception as exc:
        if raise_on_error:
            raise
        _log.error("anvil.find_batch_size failed: %s", exc)
        return -1


def find_lr(
    config: str | Path | dict[str, Any] | Experiment | Task,
    overrides: list[str] | None = None,
    *,
    min_lr: float = 1e-8,
    max_lr: float = 1.0,
    num_training_steps: int = 100,
    mode: Literal["exponential", "linear"] = "exponential",
    early_stop_threshold: float | None = 4.0,
    raise_on_error: bool = False,
) -> float:
    """Suggest an initial learning rate via Lightning ``LearningRateFinder``.

    Args:
        config: YAML path, dict, ``Experiment``, or bare ``Task``.
        overrides: CLI-style overrides. Defaults to None.
        min_lr: Sweep start. Defaults to 1e-8.
        max_lr: Sweep end. Defaults to 1.0.
        num_training_steps: Steps in the range test. Defaults to 100.
        mode: ``exponential`` or ``linear``. Defaults to ``exponential``.
        early_stop_threshold: Divergence threshold. Defaults to 4.0.
        raise_on_error: Raise instead of returning ``-1.0``. Defaults to False.

    Returns:
        Suggested learning rate, or ``-1.0`` on failure when not raising.
    """
    configure_logging()
    try:
        experiment = _to_experiment(config, overrides)
        g = experiment.global_
        seed_everything(g.seed, deterministic=g.deterministic)
        data = experiment.task.data.build()
        module = experiment.task.build()
        assert isinstance(module, TaskModule)
        suggested = find_learning_rate(
            module,
            data,
            accelerator=experiment.trainer.accelerator,
            devices=experiment.trainer.devices,
            precision=experiment.trainer.precision,
            min_lr=min_lr,
            max_lr=max_lr,
            num_training_steps=num_training_steps,
            mode=mode,
            early_stop_threshold=early_stop_threshold,
        )
        _log.info("use override: task.optimizer.lr=%s", suggested)
        print(f"task.optimizer.lr={suggested}")
        return suggested
    except (AnvilConfigError, AnvilShapeError, AnvilSmokeError) as exc:
        if raise_on_error:
            raise
        _log.error("%s", exc)
        return -1.0
    except Exception as exc:
        if raise_on_error:
            raise
        _log.error("anvil.find_lr failed: %s", exc)
        return -1.0


def _forge(
    config: str | Path | dict[str, Any] | Experiment | Task,
    *,
    overrides: list[str] | None,
    dry_run: bool,
    no_smoke: bool,
    resume_ckpt: str | None = None,
    reuse_run_dir: Path | None = None,
) -> int:
    original = Path(config) if isinstance(config, (str, Path)) else None
    experiment = _to_experiment(config, overrides)
    g = experiment.global_
    if reuse_run_dir is not None:
        run = RunDirectory(reuse_run_dir, original)
        ckpt_path = Path(resume_ckpt) if resume_ckpt else None
        append_resumed(run, ckpt_path or run.root, global_step=_checkpoint_global_step(ckpt_path))
    else:
        run = create_run_directory(g.output_dir, g.project, g.name, original)
        write_artifacts(run, experiment, overrides)
        refresh_latest(run, g.project, g.name, g.output_dir)
    _log.info("run directory: %s", run.root)
    seed_everything(g.seed, deterministic=g.deterministic)
    data = experiment.task.data.build()
    module = experiment.task.build()
    assert isinstance(module, TaskModule)
    module.check_batches = batch_checking_enabled(
        strict_shapes=g.strict_shapes,
        dry_run=dry_run,
    )
    trainer = _build_trainer(experiment.trainer, run)
    check_shapes(experiment.task, module, log_path=run.shapes_log)
    if no_smoke:
        run.smoke_log.write_text("smoke check skipped (--no-smoke)\n")
    else:
        smoke_mod.check(module, data, log_path=run.smoke_log)
    module.train()
    if dry_run:
        _log.info("dry run: built + checked; not fitting")
        return 0
    trainer.fit(module, datamodule=data, ckpt_path=resume_ckpt)
    return 0


def _to_experiment(
    source: str | Path | dict[str, Any] | Experiment | Task,
    overrides: list[str] | None,
) -> Experiment:
    if isinstance(source, Experiment):
        return source
    if isinstance(source, Task):
        return Experiment(
            global_=GlobalConfig(project="default", name=type(source).__name__),
            task=source,
            trainer=Trainer(max_epochs=1, accelerator="cpu", devices=1),
        )
    if isinstance(source, dict):
        return parse(source, Experiment)
    if isinstance(source, (str, Path)):
        raw = load_yaml(source, overrides=overrides)
        return parse(raw, Experiment)
    raise AnvilConfigError(
        f"unsupported config type {type(source).__name__}",
        hint="pass a path, dict, Experiment, or Task",
    )


def _build_trainer(cfg: Trainer, run: Any) -> L.Trainer:
    kwargs = cfg.model_dump()
    kwargs.pop("_target_", None)
    log_device_stats = bool(kwargs.pop("log_device_stats", True))
    summary_depth = int(kwargs.pop("model_summary_max_depth", 2))
    kwargs.pop("callbacks", None)
    kwargs.pop("plugins", None)
    kwargs = {key: value for key, value in kwargs.items() if value is not None}
    kwargs["default_root_dir"] = str(run.root)
    callbacks = [_build_extension(item) for item in cfg.callback_list()]
    if not _has_checkpoint(callbacks):
        callbacks.append(
            ModelCheckpoint(
                dirpath=str(run.checkpoints),
                save_last=True,
                save_top_k=0,
            )
        )
    if kwargs.get("enable_model_summary", True) and not _has_type(callbacks, ModelSummary):
        callbacks.append(ModelSummary(max_depth=summary_depth))
    if device_stats_enabled(str(cfg.accelerator), flag=log_device_stats):
        if not _has_type(callbacks, DeviceStatsMonitor):
            callbacks.append(DeviceStatsMonitor())
        if not _has_type(callbacks, GpuUsageLogger):
            callbacks.append(GpuUsageLogger(log_path=run.file("gpu.txt")))
    kwargs["callbacks"] = callbacks
    plugins = [_build_extension(item) for item in cfg.plugin_list()]
    if plugins:
        kwargs["plugins"] = plugins if len(plugins) > 1 else plugins[0]
    return L.Trainer(**kwargs)


def _build_extension(value: Any) -> Any:
    if isinstance(value, Buildable):
        return value.build()
    return value


def _has_checkpoint(callbacks: list[Any]) -> bool:
    return any(isinstance(cb, ModelCheckpoint) for cb in callbacks)


def _has_type(callbacks: list[Any], typ: type) -> bool:
    return any(isinstance(cb, typ) for cb in callbacks)


def _checkpoint_global_step(ckpt: Path | None) -> int | None:
    if ckpt is None or not ckpt.is_file():
        return None
    try:
        import torch

        payload = torch.load(ckpt, map_location="cpu", weights_only=False)
    except Exception:  # ponytail: resume bookkeeping must not fail the run
        return None
    if isinstance(payload, dict) and "global_step" in payload:
        return int(payload["global_step"])
    return None
