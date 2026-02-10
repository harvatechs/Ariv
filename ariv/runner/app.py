"""FastAPI server for ARIV runner."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import AsyncIterator, Dict, List, Optional

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from ariv.models import ModelRegistry
from ariv.orchestrator import HardwareProfile, ModelManager, Router
from ariv.runner.llama_cli import stream_tokens
from ariv.scripts.probe_hw import probe_hardware


class ChatRequest(BaseModel):
    user_id: str
    text: str
    preferred_lang: Optional[str] = None
    task_hint: Optional[str] = None


class EvalRequest(BaseModel):
    models: List[str]
    lang: str
    subset: str = "dev"


def _registry_path() -> Path:
    env_path = os.getenv("ARIV_MODELS_YAML")
    if env_path:
        return Path(env_path).expanduser().resolve()
    return (Path(__file__).resolve().parents[1] / "models" / "models.yaml").resolve()


app = FastAPI(title="ARIV Runner", version="0.2.0")
registry = ModelRegistry.from_yaml(_registry_path())
router = Router(registry)
manager = ModelManager(max_loaded=2)


@app.get("/v1/models")
async def list_models() -> Dict[str, Dict[str, str]]:
    return {
        model.name: {
            "quant": model.quant,
            "vram_mb": str(model.vram_mb),
            "local_path": model.local_path or "",
            "task": model.task,
        }
        for model in registry.list_models()
    }


@app.post("/v1/chat")
async def chat(request: ChatRequest) -> StreamingResponse:
    hw_info = probe_hardware()
    hardware = HardwareProfile(
        gpu=hw_info["gpu"],
        vram_mb=hw_info["vram_mb"],
        cpu_mem_mb=hw_info["cpu_mem_mb"],
        device_name=hw_info["device_name"],
    )
    decision = router.choose_model(
        hardware=hardware,
        preferred_lang=request.preferred_lang,
        task_hint=request.task_hint,
        text=request.text,
    )
    model_path = decision.model.local_path or decision.model.name
    evicted = manager.touch(decision.model.name)

    async def token_stream() -> AsyncIterator[str]:
        metadata = {
            "model": decision.model.name,
            "vram_used": decision.estimated_vram_mb,
            "fallback": decision.fallback or "",
            "evicted": evicted,
            "reason": decision.reason,
        }
        yield json.dumps({"metadata": metadata}) + "\n"
        async for token in stream_tokens(
            model_path=model_path,
            prompt=request.text,
            num_gpu_layers=decision.num_gpu_layers,
            max_tokens=256,
            temperature=0.2,
        ):
            yield token

    return StreamingResponse(token_stream(), media_type="text/plain")


@app.post("/v1/eval")
async def run_eval(request: EvalRequest) -> Dict[str, str]:
    from benchmarks.run_bench import run_benchmark

    output_csv, output_md = run_benchmark(
        models=request.models,
        lang=request.lang,
        subset=request.subset,
        output_dir=Path("benchmarks/results"),
    )
    return {"csv": str(output_csv), "md": str(output_md)}
