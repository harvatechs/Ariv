"""
module: ariv/scripts/probe_hw.py
purpose: Hardware capability probing with zero-hard-fail semantics for ARIV model routing
author: Ariv Engineering
version: 2.1.0
dependencies: ariv/models/__init__.py
"""

from __future__ import annotations

import importlib
import importlib.util
import json
import os
import platform
import subprocess
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field


class HardwareProfile(BaseModel):
    """Runtime hardware snapshot used by routing and deployment checks."""

    gpu: bool
    vram_mb: int = Field(ge=0)
    device_name: str
    cpu_cores: int = Field(ge=1)
    cpu_threads: int = Field(ge=1)
    cpu_mem_mb: int = Field(ge=0)
    available_mem_mb: int = Field(ge=0)
    platform: str
    environment: str
    suggested_models: list[str]
    supports_full_pipeline: bool


def _load_psutil() -> Any | None:
    if importlib.util.find_spec("psutil") is None:
        return None
    return importlib.import_module("psutil")


def _safe_int(value: str | None, default: int = 0) -> int:
    try:
        return int((value or str(default)).strip())
    except (TypeError, ValueError):
        return default


def _detect_environment() -> str:
    if os.getenv("COLAB_RELEASE_TAG"):
        return "colab"
    if os.getenv("KAGGLE_KERNEL_RUN_TYPE"):
        return "kaggle"
    if os.getenv("CI"):
        return "ci"
    return "local"


def _detect_platform() -> str:
    system = platform.system().lower()
    if system.startswith("darwin"):
        return "macos"
    if system.startswith("windows"):
        return "windows"
    if system.startswith("linux"):
        return "linux"
    return system or "unknown"


def _probe_nvidia() -> tuple[str, int] | None:
    try:
        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=name,memory.total", "--format=csv,noheader"],
            check=True,
            capture_output=True,
            text=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None

    first_line = result.stdout.strip().splitlines()[0] if result.stdout.strip() else ""
    if not first_line or "," not in first_line:
        return None

    name, mem = [part.strip() for part in first_line.split(",", maxsplit=1)]
    mem_mb = _safe_int(mem.replace("MiB", ""), default=0)
    if mem_mb <= 0:
        return None
    return name, mem_mb


def _probe_memory_mb() -> tuple[int, int, int, int]:
    psutil = _load_psutil()
    if psutil is not None:
        vm = psutil.virtual_memory()
        cores = psutil.cpu_count(logical=False) or 1
        threads = psutil.cpu_count(logical=True) or cores
        total_mb = int(vm.total / (1024 * 1024))
        available_mb = int(vm.available / (1024 * 1024))
        return cores, threads, total_mb, available_mb

    cores = os.cpu_count() or 1
    threads = cores

    if hasattr(os, "sysconf"):
        try:
            page_size = int(os.sysconf("SC_PAGE_SIZE"))
            total_pages = int(os.sysconf("SC_PHYS_PAGES"))
            avail_pages = int(os.sysconf("SC_AVPHYS_PAGES"))
            total_mb = (page_size * total_pages) // (1024 * 1024)
            available_mb = (page_size * avail_pages) // (1024 * 1024)
            if total_mb > 0:
                return cores, threads, total_mb, max(available_mb, 0)
        except (OSError, ValueError, TypeError):
            pass

    meminfo = Path("/proc/meminfo")
    if meminfo.exists():
        total_kb = 0
        available_kb = 0
        for line in meminfo.read_text(encoding="utf-8").splitlines():
            if line.startswith("MemTotal:"):
                total_kb = _safe_int(line.split()[1], default=0)
            elif line.startswith("MemAvailable:"):
                available_kb = _safe_int(line.split()[1], default=0)
        if total_kb > 0:
            return cores, threads, total_kb // 1024, available_kb // 1024

    return cores, threads, 0, 0


def _suggest_models(vram_mb: int, cpu_mem_mb: int) -> list[str]:
    try:
        from ariv.models import ModelRegistry

        registry = ModelRegistry.from_yaml(Path("ariv/models/models.yaml"))
        candidates = [
            model
            for model in registry.list_models()
            if model.family != "mock" and model.vram_mb <= max(vram_mb, 1)
        ]
        candidates = sorted(
            candidates,
            key=lambda model: (model.vram_mb, "q4_k_m" in model.name, "sarvam" in model.name),
            reverse=True,
        )
        suggested = [model.name for model in candidates]
        if suggested:
            return suggested[:3]
    except (FileNotFoundError, ModuleNotFoundError, ImportError):
        pass

    if vram_mb >= 3072:
        return ["qwen-2.5-3b-q4_k_m", "sarvam-2b-q4_k_m", "llama-3.2-1b-q4_k_m"]
    if cpu_mem_mb >= 8000:
        return ["sarvam-2b-q4_0", "llama-3.2-1b-q4_k_m"]
    return ["llama-3.2-1b-q4_k_m"]


def probe_hardware_profile() -> HardwareProfile:
    gpu_probe = _probe_nvidia()
    fake_vram = max(_safe_int(os.getenv("ARIV_FAKE_VRAM_MB"), default=0), 0)
    vram_mb = gpu_probe[1] if gpu_probe else fake_vram
    device_name = gpu_probe[0] if gpu_probe else "cpu"
    cpu_cores, cpu_threads, cpu_mem_mb, available_mem_mb = _probe_memory_mb()

    supports_full_pipeline = vram_mb >= 4096 and cpu_mem_mb >= 8192
    return HardwareProfile(
        gpu=vram_mb > 0,
        vram_mb=vram_mb,
        device_name=device_name,
        cpu_cores=cpu_cores,
        cpu_threads=cpu_threads,
        cpu_mem_mb=cpu_mem_mb,
        available_mem_mb=available_mem_mb,
        platform=_detect_platform(),
        environment=_detect_environment(),
        suggested_models=_suggest_models(vram_mb=vram_mb, cpu_mem_mb=cpu_mem_mb),
        supports_full_pipeline=supports_full_pipeline,
    )


def probe_hardware() -> dict[str, Any]:
    """Backwards-compatible dict view for legacy callers."""
    return probe_hardware_profile().model_dump()


if __name__ == "__main__":
    print(json.dumps(probe_hardware(), indent=2))
