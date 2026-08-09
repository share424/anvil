"""anvil.core.cli: forge / resume / validate / test / export / init / find-*.

argparse only.
"""

from __future__ import annotations

import argparse
from collections.abc import Sequence

from anvil.core.api import export, find_batch_size, find_lr, forge, resume, test, validate
from anvil.core.config.errors import AnvilConfigError
from anvil.core.init import init_project

__all__ = ["main"]


def main(argv: Sequence[str] | None = None) -> int:
    """Parse CLI args and dispatch subcommands.

    Args:
        argv: Argument list (defaults to ``sys.argv[1:]``). Defaults to None.

    Returns:
        Process exit code.
    """
    parser = _build_parser()
    args, dotlist = parser.parse_known_args(argv)
    overrides = _normalize_dotlist(dotlist)
    if args.command == "forge":
        return forge(
            args.config,
            overrides=overrides,
            dry_run=args.dry_run,
            no_smoke=args.no_smoke,
        )
    if args.command == "resume":
        return resume(args.target, overrides=overrides, no_smoke=not args.smoke)
    if args.command == "validate":
        return validate(args.config, args.ckpt, overrides=overrides)
    if args.command == "test":
        return test(args.config, args.ckpt, overrides=overrides)
    if args.command == "export":
        return export(
            args.config,
            args.ckpt,
            args.out,
            overrides=overrides,
            input_shape=args.input_shape,
            opset=args.opset,
        )
    if args.command == "init":
        return _run_init(args)
    if args.command == "find-batch-size":
        size = find_batch_size(
            args.config,
            overrides=overrides,
            mode=args.mode,
            init_val=args.init_val,
            max_trials=args.max_trials,
            steps_per_trial=args.steps_per_trial,
            max_val=args.max_val,
        )
        return 0 if size > 0 else 1
    if args.command == "find-lr":
        threshold = None if args.early_stop_threshold < 0 else args.early_stop_threshold
        suggested = find_lr(
            args.config,
            overrides=overrides,
            min_lr=args.min_lr,
            max_lr=args.max_lr,
            num_training_steps=args.num_training_steps,
            mode=args.mode,
            early_stop_threshold=threshold,
        )
        return 0 if suggested > 0 else 1
    raise SystemExit(f"unknown command {args.command!r}")


def _run_init(args: argparse.Namespace) -> int:
    try:
        out = init_project(
            args.directory,
            blueprint=args.blueprint,
            force=args.force,
        )
    except AnvilConfigError as exc:
        print(exc, file=__import__("sys").stderr)
        return 1
    print(f"wrote {out}")
    return 0


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="anvil", description="Config-driven DL experiments")
    sub = parser.add_subparsers(dest="command", required=True)
    forge_cmd = sub.add_parser("forge", help="Forge a training experiment")
    forge_cmd.add_argument("config", help="Path to the entrypoint YAML")
    forge_cmd.add_argument("--dry-run", action="store_true", help="Build + smoke; do not fit")
    forge_cmd.add_argument("--no-smoke", action="store_true", help="Skip pre-flight smoke check")
    resume_cmd = sub.add_parser("resume", help="Resume the latest run of a project")
    resume_cmd.add_argument("target", help="Run dir, project dir, or project/name")
    resume_cmd.add_argument(
        "--smoke",
        action="store_true",
        help="Run smoke check on resume (off by default)",
    )
    validate_cmd = sub.add_parser("validate", help="Run validation from a checkpoint")
    validate_cmd.add_argument("config", help="Path to the entrypoint YAML")
    validate_cmd.add_argument("--ckpt", required=True, help="Path to a .ckpt file")
    test_cmd = sub.add_parser("test", help="Run test from a checkpoint")
    test_cmd.add_argument("config", help="Path to the entrypoint YAML")
    test_cmd.add_argument("--ckpt", required=True, help="Path to a .ckpt file")
    export_cmd = sub.add_parser("export", help="Export inference graph to ONNX")
    export_cmd.add_argument("config", help="Path to the entrypoint YAML")
    export_cmd.add_argument("--ckpt", required=True, help="Path to a .ckpt file")
    export_cmd.add_argument("--out", required=True, help="Destination .onnx path")
    export_cmd.add_argument(
        "--input-shape",
        default=None,
        help="Dummy input shape as comma-separated ints (default: batch=1 from data)",
    )
    export_cmd.add_argument("--opset", type=int, default=17, help="ONNX opset (default: 17)")
    init_cmd = sub.add_parser("init", help="Scaffold a folder with a template config YAML")
    init_cmd.add_argument(
        "directory",
        nargs="?",
        default=".",
        help="Project directory to create/use (default: current directory)",
    )
    init_cmd.add_argument(
        "--blueprint",
        "--blueprints",
        dest="blueprint",
        default=None,
        metavar="DOTTED.PATH",
        help=("Fully-qualified blueprint Task path (e.g. anvil.blueprints.ResNet18Classification)"),
    )
    init_cmd.add_argument(
        "--force",
        action="store_true",
        help="Overwrite config.yaml if it already exists",
    )
    find_cmd = sub.add_parser(
        "find-batch-size",
        help="Search for the largest task.data.batch_size that fits in memory",
    )
    find_cmd.add_argument("config", help="Path to the entrypoint YAML")
    find_cmd.add_argument(
        "--mode",
        choices=("power", "binsearch"),
        default="power",
        help="Search strategy (default: power)",
    )
    find_cmd.add_argument("--init-val", type=int, default=2, help="Starting batch size")
    find_cmd.add_argument("--max-trials", type=int, default=25, help="Maximum search iterations")
    find_cmd.add_argument(
        "--steps-per-trial",
        type=int,
        default=3,
        help="Train steps per trial",
    )
    find_cmd.add_argument("--max-val", type=int, default=8192, help="Upper bound on batch size")
    lr_cmd = sub.add_parser("find-lr", help="Suggest an initial learning rate (LR range test)")
    lr_cmd.add_argument("config", help="Path to the entrypoint YAML")
    lr_cmd.add_argument("--min-lr", type=float, default=1e-8, help="Sweep start LR")
    lr_cmd.add_argument("--max-lr", type=float, default=1.0, help="Sweep end LR")
    lr_cmd.add_argument(
        "--num-training-steps",
        type=int,
        default=100,
        help="Steps in the range test",
    )
    lr_cmd.add_argument(
        "--mode",
        choices=("exponential", "linear"),
        default="exponential",
        help="LR schedule during the sweep",
    )
    lr_cmd.add_argument(
        "--early-stop-threshold",
        type=float,
        default=4.0,
        help="Divergence threshold (set <0 to disable)",
    )
    return parser


def _normalize_dotlist(dotlist: list[str]) -> list[str]:
    cleaned = [item for item in dotlist if item and not item.startswith("-")]
    bad = [item for item in cleaned if "=" not in item]
    if bad:
        raise SystemExit(f"override(s) must be key=value: {bad!r}")
    return cleaned


if __name__ == "__main__":
    raise SystemExit(main())
