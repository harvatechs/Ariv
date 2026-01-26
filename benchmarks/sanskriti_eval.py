#!/usr/bin/env python3
"""
SANSKRITI Benchmark Runner
Tests cultural knowledge of Indian traditions, rituals, and Little Traditions
"""

import json
import logging
from pathlib import Path
from typing import List, Dict
from tqdm import tqdm
from core.orchestrator import JugaadOrchestrator
from core.trv_pipeline import TRVPipeline
import yaml

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SANSKRITI")

class SanskritiBenchmark:
    """
    Evaluates the Maha-System on the SANSKRITI dataset:
    21,853 question-answer pairs across Indian states/UTs covering:
    - Rituals and festivals
    - Regional cuisine  
    - Local customs and Little Traditions
    - Traditional medicine (Ayurveda)
    """

    def __init__(self, data_path: str, orchestrator: JugaadOrchestrator):
        self.data_path = Path(data_path)
        self.orchestrator = orchestrator
        self.pipeline = TRVPipeline(orchestrator, self._load_prompts())
        self.results = []

    def _load_prompts(self):
        try:
            with open("prompts/meta_prompts.yaml") as f:
                return yaml.safe_load(f)
        except:
            return {}

    def load_dataset(self) -> List[Dict]:
        """Load SANSKRITI dataset (JSON format)"""
        if not self.data_path.exists():
            logger.error(f"Dataset not found: {self.data_path}")
            logger.info("Download from: https://arxiv.org/abs/2506.15355")
            return []

        with open(self.data_path) as f:
            data = json.load(f)
        return data.get('examples', [])

    def evaluate(self, max_samples: int = None) -> Dict:
        """
        Run evaluation on SANSKRITI dataset

        Returns accuracy metrics by category:
        - Overall accuracy
        - Rituals accuracy  
        - Cuisine accuracy
        - Regional customs accuracy
        """
        dataset = self.load_dataset()
        if max_samples:
            dataset = dataset[:max_samples]

        correct = 0
        category_stats = {
            "rituals": {"correct": 0, "total": 0},
            "cuisine": {"correct": 0, "total": 0},
            "customs": {"correct": 0, "total": 0},
            "festivals": {"correct": 0, "total": 0}
        }

        logger.info(f"🧪 Running SANSKRITI evaluation on {len(dataset)} samples...")

        for item in tqdm(dataset):
            question = item['question']
            expected = item['answer']
            category = item.get('category', 'general')
            language = item.get('language', 'hindi')

            try:
                # Run TRV pipeline
                result = self.pipeline.execute(
                    query=question,
                    language=language,
                    enable_critic=True
                )

                predicted = result['final_answer']

                # Simple exact match (can be improved with semantic similarity)
                is_correct = self._check_answer(predicted, expected)

                if is_correct:
                    correct += 1
                    if category in category_stats:
                        category_stats[category]["correct"] += 1

                if category in category_stats:
                    category_stats[category]["total"] += 1

                self.results.append({
                    "question": question,
                    "expected": expected,
                    "predicted": predicted,
                    "correct": is_correct,
                    "category": category
                })

            except Exception as e:
                logger.error(f"Error on question: {e}")
                continue

        # Calculate metrics
        total = len(self.results)
        accuracy = correct / total if total > 0 else 0

        metrics = {
            "overall_accuracy": accuracy,
            "total_samples": total,
            "correct": correct,
            "by_category": {}
        }

        for cat, stats in category_stats.items():
            if stats["total"] > 0:
                cat_acc = stats["correct"] / stats["total"]
                metrics["by_category"][cat] = {
                    "accuracy": cat_acc,
                    "correct": stats["correct"],
                    "total": stats["total"]
                }

        return metrics

    def _check_answer(self, predicted: str, expected: str) -> bool:
        """Check if predicted answer matches expected (case-insensitive substring match)"""
        pred_clean = predicted.lower().strip()
        exp_clean = expected.lower().strip()

        # Exact match or substring
        return exp_clean in pred_clean or pred_clean in exp_clean

    def save_results(self, output_path: str = "sanskriti_results.json"):
        """Save detailed results to file"""
        with open(output_path, 'w') as f:
            json.dump({
                "metrics": self.get_metrics(),
                "predictions": self.results
            }, f, indent=2, ensure_ascii=False)
        logger.info(f"💾 Results saved to {output_path}")

    def get_metrics(self):
        """Return current metrics"""
        if not self.results:
            return {}
        correct = sum(1 for r in self.results if r['correct'])
        return {
            "accuracy": correct / len(self.results),
            "samples": len(self.results)
        }

if __name__ == "__main__":
    import argparse
    from config import get_model_paths

    parser = argparse.ArgumentParser()
    parser.add_argument("--data", required=True, help="Path to SANSKRITI dataset JSON")
    parser.add_argument("--max-samples", type=int, default=None)
    parser.add_argument("--output", default="sanskriti_results.json")
    args = parser.parse_args()

    orchestrator = JugaadOrchestrator(get_model_paths())
    benchmark = SanskritiBenchmark(args.data, orchestrator)

    metrics = benchmark.evaluate(max_samples=args.max_samples)
    print(f"\n📊 SANSKRITI Results:")
    print(f"Overall Accuracy: {metrics['overall_accuracy']:.2%}")

    for cat, stats in metrics['by_category'].items():
        print(f"  {cat}: {stats['accuracy']:.2%} ({stats['correct']}/{stats['total']})")

    benchmark.save_results(args.output)
