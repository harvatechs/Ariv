"""Wrapper to stream tokens from llama.cpp CLI."""

from __future__ import annotations

import asyncio
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import AsyncIterator, Dict, List, Optional


@dataclass
class LlamaResult:
    text: str
    tokens: List[str]


class LlamaCLI:
    def __init__(self, binary: Optional[str] = None) -> None:
        self._binary = binary or os.getenv("LLAMA_CPP_BIN", "llama-cli")

    async def stream_chat(
        self,
        model_path: str,
        prompt: str,
        num_gpu_layers: int,
        max_tokens: int = 128,
        temperature: float = 0.2,
    ) -> AsyncIterator[str]:
        if os.getenv("ARIV_MOCK_LLAMA", "") == "1":
            for token in prompt.split()[:max_tokens]:
                yield f"{token} "
            return

        model = Path(model_path)
        if not model.exists():
            raise FileNotFoundError(f"Model not found: {model_path}")

        args = [
            self._binary,
            "-m",
            str(model),
            "-p",
            prompt,
            "-n",
            str(max_tokens),
            "--temp",
            str(temperature),
            "--mmap",
            "--use-mlock",
            "--num-gpu-layers",
            str(num_gpu_layers),
            "--json",
        ]

        process = await asyncio.create_subprocess_exec(
            *args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        assert process.stdout
        stderr_chunks: List[bytes] = []

        async def _collect_stderr() -> None:
            assert process.stderr
            async for chunk in process.stderr:
                stderr_chunks.append(chunk)

        stderr_task = asyncio.create_task(_collect_stderr())

        async for raw_line in process.stdout:
            line = raw_line.decode("utf-8").strip()
            if not line:
                continue
            if line.startswith("data:"):
                line = line.split("data:", 1)[1].strip()
            try:
                payload = json.loads(line)
            except json.JSONDecodeError:
                yield line
                continue
            token = payload.get("token") or payload.get("content") or payload.get("text")
            if token:
                yield str(token)

        await process.wait()
        await stderr_task

        if process.returncode != 0:
            stderr_tail = b"".join(stderr_chunks).decode("utf-8", errors="replace").strip()
            if len(stderr_tail) > 1200:
                stderr_tail = stderr_tail[-1200:]
            raise RuntimeError(
                "llama-cli failed: "
                f"binary={self._binary}, model={model_path}, exit_code={process.returncode}, "
                f"stderr={stderr_tail or '<empty>'}"
            )

    async def run_chat(
        self,
        model_path: str,
        prompt: str,
        num_gpu_layers: int,
        max_tokens: int = 128,
        temperature: float = 0.2,
    ) -> LlamaResult:
        tokens: List[str] = []
        async for token in self.stream_chat(
            model_path=model_path,
            prompt=prompt,
            num_gpu_layers=num_gpu_layers,
            max_tokens=max_tokens,
            temperature=temperature,
        ):
            tokens.append(token)
        return LlamaResult(text="".join(tokens), tokens=tokens)


async def stream_tokens(
    model_path: str,
    prompt: str,
    num_gpu_layers: int,
    max_tokens: int,
    temperature: float,
) -> AsyncIterator[str]:
    client = LlamaCLI()
    async for token in client.stream_chat(
        model_path=model_path,
        prompt=prompt,
        num_gpu_layers=num_gpu_layers,
        max_tokens=max_tokens,
        temperature=temperature,
    ):
        yield token
