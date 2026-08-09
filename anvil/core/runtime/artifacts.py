"""anvil.core.runtime.artifacts: run directories and reproducibility files."""

from __future__ import annotations

import datetime
import platform
import shutil
import subprocess
import sys
from pathlib import Path

from omegaconf import OmegaConf
from pydantic import BaseModel

from anvil.core.runtime.logging import get_logger

__all__ = [
    "RunDirectory",
    "create_run_directory",
    "refresh_latest",
    "write_artifacts",
    "append_resumed",
]
_log = get_logger(__name__)


class RunDirectory:
    """Resolved run directory paths.

    Attributes:
        root: Timestamped run directory.
        checkpoints: Checkpoint subdirectory.
        logs: Log subdirectory.
        smoke_log: Path to ``smoke.txt``.
        shapes_log: Path to ``shapes.txt``.
        original_config_path: Entrypoint YAML path, if any.
    """

    def __init__(self, root: Path, original_config_path: Path | None = None) -> None:
        """Create a run directory handle.

        Args:
            root: Timestamped run root.
            original_config_path: Optional YAML entrypoint path. Defaults to None.
        """
        self.root = root
        self.original_config_path = original_config_path
        self.checkpoints = root / "checkpoints"
        self.logs = root / "logs"
        self.smoke_log = root / "smoke.txt"
        self.shapes_log = root / "shapes.txt"

    def file(self, name: str) -> Path:
        """Return a path under the run root.

        Args:
            name: File name.

        Returns:
            Absolute path under ``root``.
        """
        return self.root / name


def create_run_directory(
    output_dir: str | Path,
    project: str,
    name: str,
    original_path: Path | None = None,
) -> RunDirectory:
    """Create ``{output_dir}/{project}/{name}/{timestamp}/`` with subdirs.

    Args:
        output_dir: Root output directory.
        project: Project name.
        name: Experiment name.
        original_path: Optional entrypoint YAML. Defaults to None.

    Returns:
        A ``RunDirectory`` for the new run.
    """
    base = Path(output_dir) / project / name
    base.mkdir(parents=True, exist_ok=True)
    stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    root = _unique_dir(base, stamp)
    root.mkdir(parents=True, exist_ok=False)
    (root / "checkpoints").mkdir()
    (root / "logs").mkdir()
    (root / "smoke.txt").touch()
    (root / "shapes.txt").touch()
    return RunDirectory(root, original_path)


def refresh_latest(run: RunDirectory, project: str, name: str, output_dir: str | Path) -> None:
    """Point ``{output_dir}/{project}/{name}/latest`` at this run.

    Args:
        run: Current run directory.
        project: Project name.
        name: Experiment name.
        output_dir: Root output directory.
    """
    link = Path(output_dir) / project / name / "latest"
    if link.is_symlink() or link.exists():
        link.unlink()
    link.symlink_to(run.root.resolve(), target_is_directory=True)


def write_artifacts(
    run: RunDirectory,
    experiment: BaseModel,
    overrides: list[str] | None = None,
) -> None:
    """Write reproducibility files before ``build()``.

    Args:
        run: Run directory.
        experiment: Validated experiment config.
        overrides: CLI overrides. Defaults to None.
    """
    _write_original(run)
    _write_resolved(run, experiment)
    run.file("overrides.txt").write_text("\n".join(overrides or []) + ("\n" if overrides else ""))
    run.file("git.txt").write_text(_capture_git())
    run.file("env.txt").write_text(_capture_env())


def append_resumed(run: RunDirectory, checkpoint: Path, *, global_step: int | None = None) -> None:
    """Append a resume record to ``resumed.txt``.

    Args:
        run: Run directory being continued.
        checkpoint: Checkpoint path used for resume.
        global_step: Optional step recorded from the checkpoint. Defaults to None.
    """
    stamp = datetime.datetime.now().isoformat(timespec="seconds")
    step_part = f" global_step={global_step}" if global_step is not None else ""
    line = f"{stamp} ckpt={checkpoint}{step_part}\n"
    path = run.file("resumed.txt")
    with path.open("a", encoding="utf-8") as handle:
        handle.write(line)


def _unique_dir(base: Path, stamp: str) -> Path:
    candidate = base / stamp
    if not candidate.exists():
        return candidate
    index = 1
    while True:
        alt = base / f"{stamp}_{index}"
        if not alt.exists():
            return alt
        index += 1


def _write_original(run: RunDirectory) -> None:
    target = run.file("config.original.yaml")
    src = run.original_config_path
    if src is None or not src.exists():
        target.write_text("# (config supplied in-memory; no entrypoint file)\n")
        return
    shutil.copyfile(src, target)


def _write_resolved(run: RunDirectory, experiment: BaseModel) -> None:
    from anvil.core.experiment import Experiment
    from anvil.core.runtime.live import (
        NON_REPRODUCIBLE_HEADER,
        dump_experiment,
        find_live_module_paths,
    )
    from anvil.core.runtime.logging import get_logger

    if not isinstance(experiment, Experiment):
        dumped = experiment.model_dump(by_alias=True, mode="json")
        run.file("config.resolved.yaml").write_text(OmegaConf.to_yaml(dumped))
        return

    live_paths = find_live_module_paths(experiment.task)
    dumped = dump_experiment(experiment)
    body = OmegaConf.to_yaml(dumped)
    if live_paths:
        listed = ", ".join(live_paths)
        header = f"{NON_REPRODUCIBLE_HEADER}\n# affected: {listed}\n"
        run.file("NON_REPRODUCIBLE").write_text(f"live modules at: {listed}\n")
        get_logger(__name__).warning(
            "run marked non-reproducible (live nn.Module at %s); resume will be refused",
            listed,
        )
        run.file("config.resolved.yaml").write_text(header + body)
    else:
        run.file("config.resolved.yaml").write_text(body)


def _capture_git() -> str:
    if shutil.which("git") is None:
        return "not a git repository (git binary not found on PATH)\n"
    try:
        return _git_fields()
    except Exception as exc:  # ponytail: never fail the run over git capture
        return f"git capture failed: {type(exc).__name__}: {exc}\n"


def _git_fields() -> str:
    parts = [
        "=== sha ===",
        _git_out(["rev-parse", "HEAD"]),
        "\n=== branch ===",
        _git_out(["rev-parse", "--abbrev-ref", "HEAD"]),
        "\n=== dirty ===",
        _git_out(["status", "--porcelain"]),
        "\n=== diff (tracked files) ===",
        _git_out(["diff", "HEAD"]),
    ]
    return "\n".join(parts) + "\n"


def _git_out(args: list[str]) -> str:
    result = subprocess.run(["git", *args], capture_output=True, text=True, check=True)
    return result.stdout


def _capture_env() -> str:
    parts = [
        "=== python ===",
        sys.version,
        "\n=== platform ===",
        platform.platform(),
        "\n=== packages ===",
        _package_freeze(),
        "\n=== torch / cuda ===",
        _torch_cuda_info(),
        "\n=== nvidia-smi ===",
        _nvidia_smi(),
    ]
    return "\n".join(parts) + "\n"


def _package_freeze() -> str:
    """Return an installed-package freeze (uv-first; pip is often absent)."""
    uv = shutil.which("uv")
    if uv is not None:
        text = _run_capture([uv, "pip", "freeze"])
        if text.strip():
            return text
    text = _run_capture([sys.executable, "-m", "pip", "freeze"])
    if text.strip():
        return text
    meta = _metadata_freeze()
    if meta.strip():
        return meta
    return (
        "(could not list packages: no uv pip freeze, pip module, "
        "or importlib.metadata distributions)\n"
    )


def _run_capture(cmd: list[str]) -> str:
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False,
            timeout=60,
        )
    except Exception as exc:  # ponytail: env capture must not fail the run
        return f"({' '.join(cmd)} failed: {type(exc).__name__}: {exc})\n"
    if result.returncode != 0 and not result.stdout.strip():
        err = (result.stderr or "").strip() or f"exit {result.returncode}"
        return f"({' '.join(cmd)} failed: {err})\n"
    return result.stdout


def _metadata_freeze() -> str:
    try:
        from importlib import metadata
    except ImportError:
        return ""
    lines: list[str] = []
    for dist in sorted(metadata.distributions(), key=lambda d: (d.metadata["Name"] or "").lower()):
        name = dist.metadata["Name"]
        version = dist.version
        if name and version:
            lines.append(f"{name}=={version}")
    return "\n".join(lines) + ("\n" if lines else "")


def _torch_cuda_info() -> str:
    try:
        import torch
    except Exception as exc:  # ponytail: torch may be unavailable at capture time
        return f"(torch import failed: {type(exc).__name__}: {exc})\n"
    lines = [
        f"torch={torch.__version__}",
        f"cuda_available={torch.cuda.is_available()}",
        f"torch.version.cuda={torch.version.cuda}",
        f"cudnn_enabled={torch.backends.cudnn.enabled}",
        f"device_count={torch.cuda.device_count()}",
    ]
    if torch.cuda.is_available():
        for index in range(torch.cuda.device_count()):
            props = torch.cuda.get_device_properties(index)
            lines.append(
                f"gpu[{index}]={torch.cuda.get_device_name(index)} "
                f"total_memory_gb={props.total_memory / (1024**3):.2f}"
            )
    return "\n".join(lines) + "\n"


def _nvidia_smi() -> str:
    if shutil.which("nvidia-smi") is None:
        return "(nvidia-smi not found on PATH)\n"
    text = _run_capture(
        [
            "nvidia-smi",
            "--query-gpu=index,name,driver_version,memory.total,memory.used",
            "--format=csv",
        ]
    )
    return text if text.strip() else "(nvidia-smi produced no output)\n"
