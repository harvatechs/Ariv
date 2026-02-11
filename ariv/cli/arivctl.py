"""CLI for ARIV orchestration."""

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path
from typing import List

from ariv.models import ModelRegistry
from ariv.scripts.probe_hw import probe_hardware


def _registry() -> ModelRegistry:
    return ModelRegistry.from_yaml(Path("ariv/models/models.yaml"))


def cmd_status() -> None:
    registry = _registry()
    hw = probe_hardware()
    print("Hardware:", hw)
    for model in registry.list_models():
        exists = "yes" if model.local_path and Path(model.local_path).exists() else "no"
        print(
            f"{model.name}: quant={model.quant} vram={model.vram_mb}MB "
            f"local={exists} task={model.task}"
        )


def cmd_start(host: str, port: int) -> None:
    subprocess.check_call(
        [
            "uvicorn",
            "ariv.runner.app:app",
            "--host",
            host,
            "--port",
            str(port),
        ]
    )


def cmd_bench(models: List[str], lang: str, subset: str) -> None:
    from benchmarks.run_bench import run_benchmark

    run_benchmark(
        models=models, lang=lang, subset=subset, output_dir=Path("benchmarks/results")
    )


def cmd_download(dry_run: bool) -> None:
    script = Path("ariv/scripts/download_models.sh")
    args = [str(script)]
    if dry_run:
        args.append("--dry-run")
    subprocess.check_call(args)


def main() -> None:
    parser = argparse.ArgumentParser(description="ARIV control CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("status")

    start = sub.add_parser("start")
    start.add_argument("--host", default="0.0.0.0")
    start.add_argument("--port", type=int, default=8000)

    bench = sub.add_parser("bench")
    bench.add_argument("--models", nargs="+", required=True)
    bench.add_argument("--lang", required=True)
    bench.add_argument("--subset", default="dev")

    download = sub.add_parser("download")
    download.add_argument("--dry-run", action="store_true")

    args = parser.parse_args()

    if args.command == "status":
        cmd_status()
    elif args.command == "start":
        cmd_start(args.host, args.port)
    elif args.command == "bench":
        cmd_bench(args.models, args.lang, args.subset)
    elif args.command == "download":
        cmd_download(args.dry_run)


if __name__ == "__main__":
    main()
