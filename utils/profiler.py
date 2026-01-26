#!/usr/bin/env python3
"""
Performance Profiler for Maha-System
Tracks latency, throughput, and bottleneck analysis
"""

import time
import logging
from typing import Dict, List
from dataclasses import dataclass, asdict
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Profiler")

@dataclass
class PhaseMetrics:
    """Metrics for a single pipeline phase"""
    phase_name: str
    model_loaded: str
    load_time_sec: float
    inference_time_sec: float
    tokens_generated: int
    vram_peak_gb: float

class PipelineProfiler:
    """
    Profiles the TRV pipeline to identify bottlenecks

    Usage:
        profiler = PipelineProfiler()
        with profiler.track_phase("ingestion", "sarvam-1"):
            result = model.generate(...)

        report = profiler.generate_report()
    """

    def __init__(self):
        self.phases: List[PhaseMetrics] = []
        self.current_phase = None
        self.start_time = None

    def track_phase(self, phase_name: str, model_name: str):
        """Context manager for tracking a phase"""
        return self._PhaseContext(self, phase_name, model_name)

    class _PhaseContext:
        def __init__(self, profiler, phase_name, model_name):
            self.profiler = profiler
            self.phase_name = phase_name
            self.model_name = model_name
            self.metrics = {"phase_name": phase_name, "model_loaded": model_name}

        def __enter__(self):
            import torch
            self.start_time = time.time()
            self.start_vram = torch.cuda.memory_allocated() / (1024**3) if torch.cuda.is_available() else 0
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            import torch
            end_time = time.time()
            end_vram = torch.cuda.memory_allocated() / (1024**3) if torch.cuda.is_available() else 0

            self.metrics.update({
                "load_time_sec": getattr(self, 'load_time', 0),
                "inference_time_sec": end_time - self.start_time,
                "vram_peak_gb": max(end_vram, self.start_vram)
            })

            self.profiler.phases.append(PhaseMetrics(**self.metrics))

        def record_load_time(self, load_time: float):
            """Record model loading time"""
            self.metrics["load_time"] = load_time

    def generate_report(self) -> Dict:
        """Generate performance report"""
        if not self.phases:
            return {}

        total_time = sum(p.inference_time_sec for p in self.phases)
        total_load_time = sum(p.load_time_sec for p in self.phases)

        report = {
            "summary": {
                "total_pipeline_time_sec": total_time,
                "total_load_time_sec": total_load_time,
                "inference_time_sec": total_time - total_load_time,
                "phases_count": len(self.phases),
                "avg_phase_time_sec": total_time / len(self.phases)
            },
            "phases": [asdict(p) for p in self.phases],
            "bottlenecks": self._identify_bottlenecks()
        }

        return report

    def _identify_bottlenecks(self) -> List[str]:
        """Identify slow phases"""
        if not self.phases:
            return []

        avg_time = sum(p.inference_time_sec for p in self.phases) / len(self.phases)
        bottlenecks = []

        for phase in self.phases:
            if phase.inference_time_sec > avg_time * 1.5:
                bottlenecks.append(
                    f"{phase.phase_name} ({phase.model_loaded}): "
                    f"{phase.inference_time_sec:.2f}s (avg: {avg_time:.2f}s)"
                )

        return bottlenecks

    def print_report(self):
        """Print formatted report"""
        report = self.generate_report()

        print("\n" + "="*70)
        print("📊 PIPELINE PERFORMANCE REPORT")
        print("="*70)

        summary = report['summary']
        print(f"Total Time:        {summary['total_pipeline_time_sec']:.2f}s")
        print(f"Model Loading:     {summary['total_load_time_sec']:.2f}s ({summary['total_load_time_sec']/summary['total_pipeline_time_sec']*100:.1f}%)")
        print(f"Inference:         {summary['inference_time_sec']:.2f}s")
        print(f"Phases:            {summary['phases_count']}")

        if report['bottlenecks']:
            print("\n⚠️ BOTTLENECKS:")
            for b in report['bottlenecks']:
                print(f"  • {b}")

        print("\n📈 PHASE DETAILS:")
        for phase in report['phases']:
            print(f"  {phase['phase_name']:15} | {phase['model_loaded']:20} | "
                  f"{phase['inference_time_sec']:6.2f}s | {phase['vram_peak_gb']:5.2f}GB")

        print("="*70)

    def save_report(self, filename: str = "profile_report.json"):
        """Save report to JSON"""
        with open(filename, 'w') as f:
            json.dump(self.generate_report(), f, indent=2)
        logger.info(f"📄 Report saved to {filename}")

if __name__ == "__main__":
    # Demo
    profiler = PipelineProfiler()

    with profiler.track_phase("ingestion", "sarvam-1"):
        time.sleep(0.5)  # Simulate work

    with profiler.track_phase("reasoning", "deepseek-r1"):
        time.sleep(1.2)  # Simulate slower reasoning

    profiler.print_report()
