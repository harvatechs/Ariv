"""
TRV Pipeline - Translate-Reason-Verify Loop
"""

import logging
from typing import Dict, List, Optional
from .orchestrator import JugaadOrchestrator

logger = logging.getLogger("TRVPipeline")

class TRVPipeline:
    """Translate-Reason-Verify Pipeline"""

    def __init__(self, orchestrator: JugaadOrchestrator, prompts_config: Dict):
        self.orchestrator = orchestrator
        self.prompts = prompts_config
        self.max_iterations = 3

    def execute(self, query: str, language: str = "hindi", enable_critic: bool = True, reasoning_model: str = "reasoner"):
        trace = []

        # Phase 1
        logger.info("Phase 1: Cultural Decoding")
        english_prompt = self._phase1_ingestion(query, language)
        trace.append({"phase": "ingestion", "output": english_prompt})

        # Phase 2
        logger.info("Phase 2: Deep Reasoning")
        solution = self._phase2_reasoning(english_prompt, reasoning_model)
        trace.append({"phase": "reasoning", "output": solution})

        # Phase 3
        if enable_critic:
            for i in range(self.max_iterations):
                critique = self._phase3_critic(english_prompt, solution)
                if "PASS" in critique.upper():
                    break
                else:
                    revision_prompt = f"Problem: {english_prompt}\nPrevious: {solution}\nFeedback: {critique}\nCorrected:"
                    solution = self._phase2_reasoning(revision_prompt, reasoning_model)

        # Phase 4
        final_answer = self._phase4_synthesis(solution, language, query)

        return {
            "final_answer": final_answer,
            "reasoning_trace": trace,
            "language": language
        }

    def _phase1_ingestion(self, query: str, language: str) -> str:
        system_prompt = self.prompts.get('ingestion', 
            "Translate to English with cultural context explained for: ")
        full_prompt = f"{system_prompt}\n{language}: {query}\nEnglish:"
        return self.orchestrator.generate("translator", full_prompt, max_tokens=1024, temperature=0.3)

    def _phase2_reasoning(self, prompt: str, model_role: str) -> str:
        system_prompt = self.prompts.get('reasoning', 
            "Solve step-by-step. Use Chain of Thought. FINAL ANSWER:")
        full_prompt = f"{system_prompt}\n{prompt}"
        return self.orchestrator.generate(model_role, full_prompt, max_tokens=2048, temperature=0.7)

    def _phase3_critic(self, problem: str, solution: str) -> str:
        system_prompt = self.prompts.get('critic', 
            "Critique this solution. Find flaws or say PASS:")
        full_prompt = f"{system_prompt}\nProblem: {problem}\nSolution: {solution}\nCritique:"
        return self.orchestrator.generate("critic", full_prompt, max_tokens=512, temperature=0.5)

    def _phase4_synthesis(self, solution: str, lang: str, original: str) -> str:
        system_prompt = self.prompts.get('synthesis', 
            f"Transcreate to {lang} naturally:")
        full_prompt = f"{system_prompt}\nOriginal: {original}\nEnglish: {solution}\n{lang}:"
        return self.orchestrator.generate("translator", full_prompt, max_tokens=1024, temperature=0.4)
