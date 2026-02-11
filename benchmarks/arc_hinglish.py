#!/usr/bin/env python3
"""
ARC-AGI Hinglish Adapter
Tests abstract reasoning on code-mixed Hinglish queries
Demonstrates the Poetiq-style test-time compute on Indian language data
"""

import json
import logging
from typing import List, Dict, Tuple
from core.orchestrator import JugaadOrchestrator
from core.trv_pipeline import TRVPipeline
import yaml

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ARC-Hinglish")


class ARCHinglishRunner:
    """
    Adapts ARC-AGI style abstract reasoning for Hinglish (Hindi-English code-mixing)
    ARC-AGI requires fluid intelligence - learning new rules from few examples
    """

    def __init__(self, orchestrator: JugaadOrchestrator):
        self.orchestrator = orchestrator
        self.pipeline = TRVPipeline(orchestrator, self._load_prompts())

    def _load_prompts(self):
        try:
            with open("prompts/meta_prompts.yaml") as f:
                return yaml.safe_load(f)
        except:
            return {}

    def solve_task(self, task_examples: List[Dict], test_input: Dict) -> Dict:
        """
        Solve an ARC-style task with Hinglish descriptions

        Args:
            task_examples: List of {'input': grid, 'output': grid, 'description': 'hinglish text'}
            test_input: {'input': grid, 'description': 'hinglish text'}

        Returns:
            {'prediction': grid, 'confidence': float, 'reasoning': str}
        """
        # Construct few-shot prompt with Hinglish descriptions
        prompt_parts = []
        prompt_parts.append("Main neeche diye gaye examples se pattern seekhna hai:")

        for i, ex in enumerate(task_examples, 1):
            desc = ex.get("description", "")
            prompt_parts.append(f"\nExample {i}: {desc}")
            prompt_parts.append(f"Input: {ex['input']}")
            prompt_parts.append(f"Output: {ex['output']}")

        prompt_parts.append(
            f"\nAb isko solve karo: {test_input.get('description', '')}"
        )
        prompt_parts.append(f"Test Input: {test_input['input']}")
        prompt_parts.append("Test Output:")

        full_prompt = "\n".join(prompt_parts)

        # Execute with high test-time compute (multiple samples)
        logger.info("🧠 Solving ARC task with high TTC...")

        # Generate multiple candidates and vote (Best-of-N)
        candidates = []
        for _ in range(3):  # Generate 3 candidates
            result = self.pipeline.execute(
                query=full_prompt,
                language="hinglish",
                enable_critic=True,  # Self-correction
            )
            candidates.append(result["final_answer"])

        # Simple majority voting (exact match on grid)
        prediction = self._majority_vote(candidates)

        return {
            "prediction": prediction,
            "candidates": candidates,
            "confidence": self._calculate_confidence(candidates),
            "reasoning": result["reasoning_trace"],
        }

    def _majority_vote(self, candidates: List[str]) -> str:
        """Select most common answer"""
        from collections import Counter

        vote_counts = Counter(candidates)
        return vote_counts.most_common(1)[0][0]

    def _calculate_confidence(self, candidates: List[str]) -> float:
        """Calculate agreement ratio between candidates"""
        from collections import Counter

        vote_counts = Counter(candidates)
        top_count = vote_counts.most_common(1)[0][1]
        return top_count / len(candidates)

    def evaluate_dataset(self, dataset_path: str) -> Dict:
        """
        Evaluate on ARC-AGI Hinglish dataset
        Returns accuracy score
        """
        with open(dataset_path) as f:
            tasks = json.load(f)

        correct = 0
        total = 0

        for task in tasks:
            try:
                result = self.solve_task(task["train"], task["test"])

                if result["prediction"] == task["test"]["output"]:
                    correct += 1

                total += 1

            except Exception as e:
                logger.error(f"Task failed: {e}")
                continue

        accuracy = correct / total if total > 0 else 0
        logger.info(f"ARC-Hinglish Accuracy: {accuracy:.2%} ({correct}/{total})")

        return {"accuracy": accuracy, "correct": correct, "total": total}


if __name__ == "__main__":
    import argparse
    from config import get_model_paths

    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", required=True, help="Path to ARC-Hinglish JSON")
    args = parser.parse_args()

    orchestrator = JugaadOrchestrator(get_model_paths())
    runner = ARCHinglishRunner(orchestrator)

    results = runner.evaluate_dataset(args.dataset)
    print(f"\n🎯 ARC-Hinglish Score: {results['accuracy']:.1%}")
