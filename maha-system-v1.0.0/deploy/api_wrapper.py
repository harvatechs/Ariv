#!/usr/bin/env python3
"""
FastAPI Wrapper for Maha-System
Production-ready API for the Indian AI Orchestra
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict
import uvicorn
import logging
import yaml
from pathlib import Path

from core.orchestrator import JugaadOrchestrator
from core.trv_pipeline import TRVPipeline
from config import get_model_paths

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("MahaAPI")

# Initialize FastAPI app
app = FastAPI(
    title="Maha-System API",
    description="Sovereign Indian AI via Test-Time Compute Orchestration",
    version="1.0.0"
)

# Global orchestrator instance (loaded once, reused across requests)
orchestrator = None
pipeline = None

class QueryRequest(BaseModel):
    query: str
    language: str = "hindi"
    enable_critic: bool = True
    reasoning_model: str = "reasoner"
    max_tokens: int = 1024

class QueryResponse(BaseModel):
    answer: str
    reasoning_trace: Optional[List[Dict]] = None
    iterations: int = 0
    processing_time_ms: Optional[float] = None
    models_used: List[str]

@app.on_event("startup")
async def startup_event():
    """Initialize models on startup"""
    global orchestrator, pipeline

    logger.info("🚀 Starting Maha-System API...")

    model_paths = get_model_paths()

    # Verify models exist
    missing = [role for role, path in model_paths.items() if not Path(path).exists()]
    if missing:
        logger.warning(f"Missing models: {missing}. API will fail on first request.")

    orchestrator = JugaadOrchestrator(model_paths)

    # Load prompts
    try:
        with open("prompts/meta_prompts.yaml") as f:
            prompts = yaml.safe_load(f)
    except:
        prompts = {}

    pipeline = TRVPipeline(orchestrator, prompts)
    logger.info("✅ Maha-System ready")

@app.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """
    Process a query through the TRV pipeline

    - **query**: User question in vernacular language
    - **language**: Language code (hindi, tamil, telugu, etc.)
    - **enable_critic**: Enable adversarial verification (slower but more accurate)
    - **reasoning_model**: 'reasoner' (DeepSeek) or 'bridge' (OpenHathi)
    """
    import time

    if not pipeline:
        raise HTTPException(status_code=503, detail="System not initialized")

    start_time = time.time()

    try:
        result = pipeline.execute(
            query=request.query,
            language=request.language,
            enable_critic=request.enable_critic,
            reasoning_model=request.reasoning_model
        )

        processing_time = (time.time() - start_time) * 1000

        # Determine which models were used based on trace
        models_used = list(set(step['phase'] for step in result['reasoning_trace']))

        return QueryResponse(
            answer=result['final_answer'],
            reasoning_trace=result['reasoning_trace'] if request.enable_critic else None,
            iterations=result.get('iterations', 0),
            processing_time_ms=processing_time,
            models_used=models_used
        )

    except Exception as e:
        logger.error(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "models_loaded": orchestrator.current_role is not None if orchestrator else False,
        "available_models": list(get_model_paths().keys())
    }

@app.get("/models")
async def list_models():
    """List available models and their status"""
    paths = get_model_paths()
    status = {}

    for role, path in paths.items():
        exists = Path(path).exists()
        size = Path(path).stat().st_size / (1024**3) if exists else 0
        status[role] = {
            "path": path,
            "exists": exists,
            "size_gb": round(size, 2)
        }

    return status

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
