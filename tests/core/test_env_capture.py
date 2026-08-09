"""env.txt capture: packages + GPU info."""

from __future__ import annotations

from anvil.core.runtime.artifacts import _capture_env, _package_freeze, _torch_cuda_info


def test_package_freeze_is_non_empty() -> None:
    """
    Condition:
    The current environment has anvil dependencies installed (uv/editable).

    Expected:
    Package freeze lists at least one distribution (not an empty string).
    """
    text = _package_freeze()
    assert text.strip()
    assert "==" in text or "failed" not in text.lower()


def test_capture_env_includes_torch_and_packages() -> None:
    """
    Condition:
    _capture_env runs in this project venv.

    Expected:
    Sections for packages and torch/cuda are present and non-empty.
    """
    text = _capture_env()
    assert "=== packages ===" in text
    assert "=== torch / cuda ===" in text
    assert "=== nvidia-smi ===" in text
    assert "torch=" in text
    freeze = text.split("=== packages ===", 1)[1].split("===", 1)[0]
    assert freeze.strip()


def test_torch_cuda_info_reports_availability() -> None:
    """
    Condition:
    Torch is installed.

    Expected:
    Info string mentions cuda_available.
    """
    text = _torch_cuda_info()
    assert "cuda_available=" in text
    assert "torch=" in text
