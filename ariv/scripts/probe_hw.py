"""Hardware probe utilities."""

from __future__ import annotations

import json
import os
import subprocess
from typing import Dict, Union

import psutil


def _probe_nvidia() -> Dict[str, str]:
    try:
        output = subprocess.check_output(
            ["nvidia-smi", "--query-gpu=name,memory.total", "--format=csv,noheader"],
            stderr=subprocess.DEVNULL,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        return {}
    line = output.decode("utf-8").strip().split("\n")[0]
    name, mem = [part.strip() for part in line.split(",")]
    mem_mb = int(mem.replace("MiB", "").strip())
    return {"device_name": name, "vram_mb": mem_mb}


def probe_hardware() -> Dict[str, Union[int, bool, str]]:
    gpu_info = _probe_nvidia()
    cpu_mem_mb = int(psutil.virtual_memory().total / (1024 * 1024))
    if gpu_info:
        return {
            "gpu": True,
            "vram_mb": int(gpu_info["vram_mb"]),
            "device_name": gpu_info["device_name"],
            "cpu_mem_mb": cpu_mem_mb,
        }
    return {
        "gpu": False,
        "vram_mb": int(os.getenv("ARIV_FAKE_VRAM_MB", "0")),
        "device_name": "cpu",
        "cpu_mem_mb": cpu_mem_mb,
    }


if __name__ == "__main__":
    print(json.dumps(probe_hardware(), indent=2))
