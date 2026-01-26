#!/usr/bin/env python3
"""
Example: Batch Processing
Process multiple queries efficiently with caching
"""

import sys
sys.path.insert(0, '..')

from core.orchestrator import JugaadOrchestrator
from core.trv_pipeline import TRVPipeline
from utils.cache import MahaCache
from config import get_model_paths
import json
from concurrent.futures import ThreadPoolExecutor
import time

def batch_process(queries: list, language: str = "hindi", max_workers: int = 1):
    """
    Process multiple queries with caching and progress tracking

    Args:
        queries: List of query strings
        language: Language code
        max_workers: Parallel workers (1 for sequential VRAM management)
    """

    model_paths = get_model_paths()
    orchestrator = JugaadOrchestrator(model_paths)
    cache = MahaCache()
    pipeline = TRVPipeline(orchestrator, {})

    results = []
    cache_hits = 0

    print(f"Processing {len(queries)} queries...")
    start_time = time.time()

    for i, query in enumerate(queries):
        print(f"[{i+1}/{len(queries)}] {query[:50]}...", end=" ")

        # Check cache
        cached = cache.get_translation(query, language)
        if cached:
            print("[CACHE HIT]")
            results.append({"query": query, "answer": cached, "cached": True})
            cache_hits += 1
            continue

        # Process
        result = pipeline.execute(query, language, enable_critic=False)
        results.append({
            "query": query,
            "answer": result['final_answer'],
            "cached": False
        })

        # Cache result
        cache.set_translation(query, language, result['final_answer'])
        print("[DONE]")

    elapsed = time.time() - start_time

    print(f"\nCompleted in {elapsed:.1f}s")
    print(f"Cache hits: {cache_hits}/{len(queries)} ({cache_hits/len(queries)*100:.1f}%)")
    print(f"Avg time per query: {elapsed/len(queries):.1f}s")

    return results

if __name__ == "__main__":
    # Sample batch queries
    queries = [
        "भारत की राजधानी क्या है?",
        "What is the capital of India?",  # Will translate to Hindi
        "भारत की राजधानी क्या है?",  # Duplicate - should hit cache
        "भारत में कितने राज्य हैं?",
        "ताज महल कहाँ स्थित है?"
    ]

    results = batch_process(queries, language="hindi")

    # Save results
    with open("batch_results.json", "w") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print("\nResults saved to batch_results.json")
