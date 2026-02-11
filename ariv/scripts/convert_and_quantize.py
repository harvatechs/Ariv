"""Wrapper to convert HF checkpoints to GGUF and quantize."""

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path


def run(cmd: str) -> None:
    print(f"[run] {cmd}")
    subprocess.check_call(cmd, shell=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert and quantize models to GGUF")
    parser.add_argument("--hf-repo", required=True, help="Hugging Face repo path")
    parser.add_argument("--output", required=True, help="Output GGUF path")
    parser.add_argument("--quant", default="Q4_K_M", choices=["Q4_K_M", "Q5_0", "Q4_0"])
    parser.add_argument(
        "--llama-cpp", default="llama.cpp", help="Path to llama.cpp repo"
    )
    args = parser.parse_args()

    llama_dir = Path(args.llama_cpp)
    convert_script = llama_dir / "convert_hf_to_gguf.py"
    quantize_bin = llama_dir / "llama-quantize"

    if not convert_script.exists() or not quantize_bin.exists():
        raise FileNotFoundError("llama.cpp tools not found in provided path")

    intermediate = Path(args.output).with_suffix(".f16.gguf")
    run(f"python {convert_script} {args.hf_repo} --outfile {intermediate}")
    run(f"{quantize_bin} {intermediate} {args.output} {args.quant}")


if __name__ == "__main__":
    main()
