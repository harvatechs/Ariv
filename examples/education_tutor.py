#!/usr/bin/env python3
"""
Example: Personalized Education Tutor
Explains concepts in student's mother tongue with SOTA reasoning
"""

import sys
sys.path.insert(0, '..')

from core.orchestrator import JugaadOrchestrator
from core.trv_pipeline import TRVPipeline
from config import get_model_paths

class MahaTutor:
    """
    Educational tutor that adapts explanations to student's level
    and language preference
    """

    def __init__(self, student_class: int = 10, language: str = "hindi"):
        self.student_class = student_class
        self.language = language

        model_paths = get_model_paths()
        self.orchestrator = JugaadOrchestrator(model_paths)

        # Grade-appropriate prompts
        self.prompts = self._get_grade_prompts()
        self.pipeline = TRVPipeline(self.orchestrator, self.prompts)

    def _get_grade_prompts(self):
        """Get age-appropriate explanation prompts"""
        if self.student_class <= 5:
            style = "very simple language, use analogies from daily life, short sentences"
        elif self.student_class <= 8:
            style = "simple language with examples, encourage curiosity"
        elif self.student_class <= 10:
            style = "clear explanations with real-world applications"
        else:
            style = "detailed explanations with technical depth"

        return {
            'reasoning': f"You are a patient teacher for Class {self.student_class} students. "
                        f"Explain concepts using {style}. "
                        f"If math is involved, solve step-by-step. "
                        f"Encourage the student and check understanding."
        }

    def explain(self, concept: str, subject: str = "science"):
        """
        Explain a concept to the student

        Args:
            concept: Topic to explain (e.g., "photosynthesis")
            subject: Subject area (science, math, history, etc.)
        """
        query = f"Explain {concept} in {subject}"

        result = self.pipeline.execute(
            query=query,
            language=self.language,
            enable_critic=True  # Ensure accuracy for education
        )

        return result['final_answer']

    def solve_problem(self, problem: str, subject: str = "math"):
        """Solve a homework problem with detailed steps"""
        query = f"Solve this {subject} problem step by step: {problem}"

        result = self.pipeline.execute(
            query=query,
            language=self.language,
            enable_critic=True
        )

        return result['final_answer']

if __name__ == "__main__":
    print("📚 Maha-Tutor: Personalized Education")
    print("="*60)

    # Create tutor for Class 8 student
    tutor = MahaTutor(student_class=8, language="hindi")

    # Example queries
    queries = [
        ("What is photosynthesis?", "science"),
        ("How do fractions work?", "math"),
        ("Why is the sky blue?", "science")
    ]

    for query, subject in queries:
        print(f"\n❓ Student asks: {query}")
        explanation = tutor.explain(query, subject)
        print(f"👨‍🏫 Tutor: {explanation[:300]}...")
        print("-"*60)
