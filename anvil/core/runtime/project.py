"""anvil.core.runtime.project: locate runs for ``resume``."""

from __future__ import annotations

from pathlib import Path

from anvil.core.config.errors import AnvilConfigError

__all__ = ["resolve_run_directory", "find_last_checkpoint"]


def resolve_run_directory(target: str | Path, *, output_dir: str | Path = "outputs") -> Path:
    """Resolve a resume target to a run directory containing ``config.resolved.yaml``.

    Resolution order:
      1. Path to a run directory
      2. Project directory with a ``latest`` symlink
      3. ``project/name`` under ``output_dir``
      4. Bare name matching exactly one project under ``output_dir``

    Args:
        target: Run path, project path, or ``project/name``.
        output_dir: Default outputs root. Defaults to ``outputs``.

    Returns:
        Absolute path to the run directory.

    Raises:
        AnvilConfigError: If the target cannot be resolved uniquely.
    """
    path = Path(target)
    if path.is_dir() and (path / "config.resolved.yaml").exists():
        return path.resolve()
    if path.is_dir() and (path / "latest").exists():
        return _follow_latest(path)
    slash = str(target).replace("\\", "/")
    if "/" in slash:
        project, _, name = slash.partition("/")
        return _follow_latest(Path(output_dir) / project / name)
    return _unique_project_name(slash, Path(output_dir))


def find_last_checkpoint(run_dir: Path) -> Path:
    """Return ``checkpoints/last.ckpt`` under ``run_dir``.

    Args:
        run_dir: Run directory.

    Returns:
        Path to ``last.ckpt``.

    Raises:
        AnvilConfigError: If the checkpoint is missing.
    """
    ckpt = run_dir / "checkpoints" / "last.ckpt"
    if not ckpt.is_file():
        raise AnvilConfigError(
            "resume checkpoint not found",
            path=str(ckpt),
            hint="forge at least one epoch with checkpointing enabled (save_last)",
        )
    return ckpt


def _follow_latest(project_dir: Path) -> Path:
    latest = project_dir / "latest"
    if not latest.exists():
        raise AnvilConfigError(
            "no latest run symlink",
            path=str(project_dir),
            hint="forge once to create outputs/.../latest",
        )
    resolved = latest.resolve()
    if not (resolved / "config.resolved.yaml").exists():
        raise AnvilConfigError(
            "latest does not point at a valid run directory",
            path=str(resolved),
        )
    return resolved


def _unique_project_name(name: str, output_dir: Path) -> Path:
    matches = [p for p in output_dir.glob(f"*/{name}") if p.is_dir()]
    if len(matches) == 1:
        return _follow_latest(matches[0])
    if not matches:
        raise AnvilConfigError(
            f"no project named {name!r} under {output_dir}",
            hint="pass project/name or a run directory path",
        )
    listed = ", ".join(str(m) for m in matches)
    raise AnvilConfigError(
        f"ambiguous experiment name {name!r}",
        value=listed,
        hint="pass an explicit project/name",
    )
