"""Benchmark harness for ARIV models."""

from __future__ import annotations

import csv
import json
import time
from dataclasses import dataclass
from pathlib import Path
from statistics import median
from typing import Dict, Iterable, List, Tuple

import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from ariv.runner.llama_cli import LlamaCLI


@dataclass
class BenchResult:
    model: str
    lang: str
    subset: str
    bleu: float
    chrf: float
    throughput_tps: float
    latency_p50: float
    latency_p95: float


def _load_dataset(lang: str, subset: str) -> List[Tuple[str, str]]:
    path = Path("benchmarks/data/flores_sample.jsonl")
    if not path.exists():
        return []
    pairs: List[Tuple[str, str]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        item = json.loads(line)
        if item.get("lang") == lang and item.get("subset") == subset:
            pairs.append((item["source"], item["reference"]))
    return pairs


def _simple_bleu(hyp: str, ref: str) -> float:
    hyp_tokens = hyp.split()
    ref_tokens = ref.split()
    if not hyp_tokens or not ref_tokens:
        return 0.0
    overlap = sum(token in ref_tokens for token in hyp_tokens)
    return overlap / len(hyp_tokens)


def _simple_chrf(hyp: str, ref: str) -> float:
    if not hyp or not ref:
        return 0.0
    overlap = sum(char in ref for char in hyp)
    return overlap / len(hyp)


def _percentile(values: List[float], pct: float) -> float:
    if not values:
        return 0.0
    values = sorted(values)
    idx = int(len(values) * pct)
    idx = min(max(idx, 0), len(values) - 1)
    return values[idx]


def _run_model(model_path: str, prompt: str) -> Tuple[str, float, int]:
    client = LlamaCLI()
    start = time.time()
    result = []
    token_count = 0
    import asyncio

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    async def _collect() -> None:
        nonlocal token_count
        async for token in client.stream_chat(
            model_path=model_path,
            prompt=prompt,
            num_gpu_layers=10,
            max_tokens=64,
            temperature=0.2,
        ):
            token_count += 1
            result.append(token)

    loop.run_until_complete(_collect())
    loop.close()
    duration = max(time.time() - start, 1e-6)
    return "".join(result), duration, token_count


def run_benchmark(
    models: List[str], lang: str, subset: str, output_dir: Path
) -> Tuple[Path, Path]:
    dataset = _load_dataset(lang, subset)
    if not dataset:
        raise ValueError("Dataset not found or empty")
    output_dir.mkdir(parents=True, exist_ok=True)

    rows: List[BenchResult] = []
    for model in models:
        latencies: List[float] = []
        total_tokens = 0
        total_time = 0.0
        bleu_scores: List[float] = []
        chrf_scores: List[float] = []
        for source, reference in dataset:
            text, duration, tokens = _run_model(model, source)
            total_tokens += tokens
            total_time += duration
            latencies.append(duration)
            bleu_scores.append(_simple_bleu(text, reference))
            chrf_scores.append(_simple_chrf(text, reference))
        throughput = total_tokens / max(total_time, 1e-6)
        rows.append(
            BenchResult(
                model=model,
                lang=lang,
                subset=subset,
                bleu=round(sum(bleu_scores) / len(bleu_scores), 4),
                chrf=round(sum(chrf_scores) / len(chrf_scores), 4),
                throughput_tps=round(throughput, 2),
                latency_p50=round(median(latencies), 4),
                latency_p95=round(_percentile(latencies, 0.95), 4),
            )
        )

    csv_path = output_dir / f"{models[0].split('/')[-1]}-{lang}-{subset}.csv"
    md_path = output_dir / f"{models[0].split('/')[-1]}-{lang}-{subset}.md"

    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(
            [
                "model",
                "lang",
                "subset",
                "bleu",
                "chrf",
                "throughput_tps",
                "latency_p50",
                "latency_p95",
            ]
        )
        for row in rows:
            writer.writerow(
                [
                    row.model,
                    row.lang,
                    row.subset,
                    row.bleu,
                    row.chrf,
                    row.throughput_tps,
                    row.latency_p50,
                    row.latency_p95,
                ]
            )

    md_lines = [
        "# Benchmark Summary",
        "",
        "| Model | Lang | Subset | BLEU | chrF | Throughput (tok/s) | p50 Latency | p95 Latency |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        md_lines.append(
            f"| {row.model} | {row.lang} | {row.subset} | {row.bleu} | {row.chrf} | "
            f"{row.throughput_tps} | {row.latency_p50} | {row.latency_p95} |"
        )
    md_path.write_text("\n".join(md_lines) + "\n", encoding="utf-8")
    return csv_path, md_path


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Run ARIV benchmarks")
    parser.add_argument("--models", nargs="+", required=True)
    parser.add_argument("--lang", required=True)
    parser.add_argument("--subset", default="dev")
    args = parser.parse_args()

    run_benchmark(
        models=args.models,
        lang=args.lang,
        subset=args.subset,
        output_dir=Path("benchmarks/results"),
    )


if __name__ == "__main__":
    main()
