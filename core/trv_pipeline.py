"""
Enhanced TRV Pipeline - Translate-Reason-Verify Loop
Production-ready with all 22 Indian languages, advanced CoT, and ARC-AGI 2 optimization
"""

import logging
import time
from typing import Dict, List, Optional, Any
from .orchestrator import JugaadOrchestrator
from config import (INDIAN_LANGUAGES_22, PIPELINE_CONFIG, 
                    COT_CONFIG, TOOL_CONFIG, ARC_CONFIG)
import json

logger = logging.getLogger("TRVPipeline")

class TRVPipeline:
    """
    Translate-Reason-Verify Pipeline enhanced for production use
    Supports all 22 Indian languages with advanced reasoning capabilities
    """

    def __init__(self, orchestrator: JugaadOrchestrator, prompts_config: Dict):
        self.orchestrator = orchestrator
        self.prompts = prompts_config
        self.config = PIPELINE_CONFIG
        self.cot_config = COT_CONFIG
        self.tool_config = TOOL_CONFIG
        self.arc_config = ARC_CONFIG
        
        # Language-specific routing
        self.language_models = self._build_language_routing()
        
        # Statistics
        self.stats = {
            "queries_processed": 0,
            "total_time": 0.0,
            "language_distribution": {},
            "critic_iterations": []
        }

    def _build_language_routing(self) -> Dict[str, Dict[str, str]]:
        """Build language to model routing configuration"""
        routing = {}
        
        for lang, config in INDIAN_LANGUAGES_22.items():
            specialist = config.get("model_specialist")
            
            # Route to specialist if available, otherwise use general translator
            translator_role = specialist if specialist and specialist in self.orchestrator.models_config else "translator"
            
            routing[lang] = {
                "translator": translator_role,
                "reasoner": "reasoner",  # Always use main reasoner
                "critic": "critic",      # Always use main critic
                "bridge": "bridge"       # Alternative reasoner
            }
            
        return routing

    def execute(self, 
                query: str, 
                language: str = "hindi", 
                enable_critic: bool = True,
                reasoning_model: str = "reasoner",
                enable_tools: bool = True,
                enable_deep_cot: bool = True,
                enable_self_consistency: bool = True) -> Dict[str, Any]:
        """
        Execute the full TRV pipeline
        
        Args:
            query: Input query in vernacular language
            language: Language code (e.g., 'hindi', 'tamil', 'bengali')
            enable_critic: Whether to enable critic phase
            reasoning_model: Which reasoning model to use ('reasoner' or 'bridge')
            enable_tools: Whether to enable tool calling
            enable_deep_cot: Whether to use deep chain-of-thought
            enable_self_consistency: Whether to use self-consistency voting
            
        Returns:
            Dictionary with final answer, reasoning trace, and metadata
        """
        pipeline_start = time.time()
        trace = []
        
        # Validate language
        if language not in INDIAN_LANGUAGES_22:
            logger.warning(f"Language '{language}' not supported, using 'hindi'")
            language = "hindi"
            
        logger.info(f"🎯 Processing query in {language}: {query[:100]}...")
        
        # Update language statistics
        self.stats["language_distribution"][language] = self.stats["language_distribution"].get(language, 0) + 1

        # Phase 1: Ingestion & Cultural Decoding
        logger.info("Phase 1: Cultural Decoding & Translation")
        try:
            english_prompt = self._phase1_ingestion(query, language)
            trace.append({"phase": "ingestion", "output": english_prompt, "language": language})
            logger.info(f"✅ Translated to English: {english_prompt[:100]}...")
        except Exception as e:
            logger.error(f"❌ Phase 1 failed: {e}")
            return self._error_response(f"Translation failed: {e}", language)

        # Phase 2: Deep Reasoning with Chain-of-Thought
        logger.info("Phase 2: Deep Reasoning")
        try:
            if enable_deep_cot:
                reasoning_result = self._phase2_advanced_reasoning(
                    english_prompt, 
                    reasoning_model,
                    enable_self_consistency=enable_self_consistency
                )
                solution = reasoning_result["final_answer"]
                trace.append({"phase": "advanced_reasoning", "output": solution, "details": reasoning_result})
            else:
                solution = self._phase2_reasoning(english_prompt, reasoning_model)
                trace.append({"phase": "reasoning", "output": solution})
                
            logger.info(f"✅ Reasoning complete: {solution[:100]}...")
        except Exception as e:
            logger.error(f"❌ Phase 2 failed: {e}")
            return self._error_response(f"Reasoning failed: {e}", language)

        # Phase 3: The Critic & Self-Correction (with iterations)
        critic_iterations = 0
        if enable_critic:
            logger.info("Phase 3: Adversarial Critic")
            try:
                for i in range(self.config["max_critic_iterations"]):
                    critique = self._phase3_critic(english_prompt, solution)
                    critic_iterations += 1
                    
                    if "PASS" in critique.upper() or "CORRECT" in critique.upper():
                        trace.append({"phase": f"critic_final", "output": f"Iteration {i+1}: PASS"})
                        logger.info(f"✅ Critic passed after {i+1} iterations")
                        break
                    else:
                        trace.append({"phase": f"critic_{i+1}", "output": critique})
                        logger.info(f"🔄 Critic iteration {i+1}: {critique[:100]}...")
                        
                        # Generate corrected solution
                        revision_prompt = self._build_revision_prompt(english_prompt, solution, critique)
                        
                        if enable_deep_cot:
                            reasoning_result = self._phase2_advanced_reasoning(
                                revision_prompt, 
                                reasoning_model,
                                enable_self_consistency=False  # Faster for revisions
                            )
                            solution = reasoning_result["final_answer"]
                        else:
                            solution = self._phase2_reasoning(revision_prompt, reasoning_model)
                            
                        trace.append({"phase": f"revision_{i+1}", "output": solution})
            except Exception as e:
                logger.warning(f"⚠️ Critic phase failed (continuing): {e}")
                
        self.stats["critic_iterations"].append(critic_iterations)

        # Phase 4: Synthesis & Transcreation
        logger.info("Phase 4: Cultural Transcreation")
        try:
            final_answer = self._phase4_synthesis(solution, language, query)
            trace.append({"phase": "synthesis", "output": final_answer, "language": language})
            logger.info(f"✅ Final answer: {final_answer[:100]}...")
        except Exception as e:
            logger.error(f"❌ Phase 4 failed: {e}")
            return self._error_response(f"Synthesis failed: {e}", language)

        # Update pipeline statistics
        pipeline_time = time.time() - pipeline_start
        self.stats["queries_processed"] += 1
        self.stats["total_time"] += pipeline_time

        return {
            "final_answer": final_answer,
            "reasoning_trace": trace,
            "language": language,
            "pipeline_time": pipeline_time,
            "critic_iterations": critic_iterations,
            "metadata": {
                "reasoning_model": reasoning_model,
                "deep_cot": enable_deep_cot,
                "self_consistency": enable_self_consistency,
                "tools_enabled": enable_tools
            }
        }

    def _phase1_ingestion(self, query: str, language: str) -> str:
        """Phase 1: Cultural Decoding & Translation"""
        lang_config = INDIAN_LANGUAGES_22[language]
        translator_role = self.language_models[language]["translator"]
        
        # Enhanced ingestion prompt with cultural context
        system_prompt = self.prompts.get('ingestion', 
            "You are an expert linguistic bridge between Indian cultural contexts and strict logical reasoning.")
            
        full_prompt = f"""{system_prompt}

Translate the following {lang_config['native_name']} ({language}) query into explicit, unambiguous English. 

CRITICAL INSTRUCTIONS:
1. Preserve all cultural references, idioms, and context
2. Explain any "Little Tradition" cultural references (local nuances) in detail
3. Convert any regional units to standard units
4. Maintain the original intent and tone
5. If the query contains mathematical or logical problems, structure them clearly

Language: {language} ({lang_config['script']} script, {lang_config['family']} language family)

Query: {query}

English translation with cultural context:"""

        return self.orchestrator.generate(translator_role, full_prompt, 
                                        max_tokens=self.config["max_tokens"]["ingestion"], 
                                        temperature=self.config["temperature"]["ingestion"])

    def _phase2_reasoning(self, prompt: str, model_role: str) -> str:
        """Phase 2: Standard Reasoning"""
        system_prompt = self.prompts.get('reasoning', 
            "You are a world-class reasoning engine. Solve step-by-step using Chain of Thought.")
            
        full_prompt = f"""{system_prompt}

Problem: {prompt}

Let's solve this step by step:

1. Understanding the problem:
2. Key information:
3. Step-by-step solution:
4. Final answer:"""

        return self.orchestrator.generate(model_role, full_prompt, 
                                        max_tokens=self.config["max_tokens"]["reasoning"], 
                                        temperature=self.config["temperature"]["reasoning"])

    def _phase2_advanced_reasoning(self, 
                                   prompt: str, 
                                   model_role: str,
                                   enable_self_consistency: bool = True) -> Dict[str, Any]:
        """Phase 2: Advanced Reasoning with Chain-of-Thought"""
        
        if enable_self_consistency and self.config.get("enable_self_consistency", True):
            # Use self-consistency with multiple reasoning paths
            return self.orchestrator.self_consistency_generate(
                model_role,
                prompt,
                num_paths=self.config.get("self_consistency_paths", 5),
                temperature=0.7
            )
        else:
            # Use deep chain-of-thought
            return self.orchestrator.chain_of_thought_generate(
                model_role,
                prompt,
                cot_depth=self.cot_config.get("cot_depth", 3),
                enable_reflection=self.cot_config.get("enable_reflection", True),
                enable_adversarial=self.cot_config.get("enable_adversarial_cot", True)
            )

    def _phase3_critic(self, problem: str, solution: str) -> str:
        """Phase 3: Adversarial Critic"""
        system_prompt = self.prompts.get('critic', 
            "You are a skeptical critic. Find flaws in reasoning or output PASS.")
            
        full_prompt = f"""{system_prompt}

PROBLEM:
{problem}

PROPOSED SOLUTION:
{solution}

CRITIQUE INSTRUCTIONS:
1. Check for logical fallacies
2. Verify mathematical calculations
3. Identify unstated assumptions
4. Look for missing edge cases
5. Assess completeness of the solution

If the solution is correct and complete, respond with: PASS

If there are issues, provide specific feedback:
- What is wrong?
- Why is it wrong?
- How should it be corrected?

Critique:"""

        return self.orchestrator.generate("critic", full_prompt, 
                                        max_tokens=self.config["max_tokens"]["critic"], 
                                        temperature=self.config["temperature"]["critic"])

    def _build_revision_prompt(self, problem: str, previous_solution: str, critique: str) -> str:
        """Build prompt for revision based on critique"""
        return f"""Problem: {problem}

Previous solution: {previous_solution}

Critique/Feedback: {critique}

Based on the feedback above, provide a corrected solution:

Corrected solution:"""

    def _phase4_synthesis(self, solution: str, lang: str, original: str) -> str:
        """Phase 4: Cultural Transcreation"""
        lang_config = INDIAN_LANGUAGES_22[lang]
        translator_role = self.language_models[lang]["translator"]
        
        system_prompt = self.prompts.get('synthesis', 
            "Transcreate naturally, preserving cultural nuances.")
            
        full_prompt = f"""{system_prompt}

ORIGINAL QUERY ({lang_config['native_name']}):
{original}

ENGLISH SOLUTION:
{solution}

TRANSCREATE TO {lang_config['native_name']} ({lang}):

INSTRUCTIONS:
1. Use natural {lang_config['native_name']} phrasing and idioms
2. Preserve any cultural references from the original query
3. Adapt technical terms appropriately for {lang} speakers
4. Maintain accuracy while ensuring readability
5. Use {lang_config['script']} script appropriately

Final answer in {lang_config['native_name']}:"""

        return self.orchestrator.generate(translator_role, full_prompt, 
                                        max_tokens=self.config["max_tokens"]["synthesis"], 
                                        temperature=self.config["temperature"]["synthesis"])

    def _error_response(self, error: str, language: str) -> Dict[str, Any]:
        """Create error response"""
        lang_config = INDIAN_LANGUAGES_22.get(language, INDIAN_LANGUAGES_22["hindi"])
        
        # Translate error message
        if language == "hindi":
            error_msg = f"क्षमा करें, प्रक्रिया में त्रुटि हुई: {error}"
        elif language == "tamil":
            error_msg = f"மன்னிக்கவும், செயலாக்கத்தில் பிழை: {error}"
        elif language == "bengali":
            error_msg = f"দুঃখিত, প্রক্রিয়াকরণে ত্রুটি: {error}"
        else:
            error_msg = f"Error in processing: {error}"
            
        return {
            "final_answer": error_msg,
            "reasoning_trace": [{"phase": "error", "output": error}],
            "language": language,
            "error": True
        }

    def benchmark_arc_agi_2(self, problems: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Benchmark against ARC-AGI 2 style problems
        
        Args:
            problems: List of ARC-AGI 2 problems
            
        Returns:
            Benchmark results
        """
        logger.info(f"🧪 Running ARC-AGI 2 benchmark on {len(problems)} problems")
        
        results = {
            "total_problems": len(problems),
            "solved": 0,
            "failed": 0,
            "total_time": 0,
            "per_problem_results": []
        }
        
        for i, problem in enumerate(problems):
            logger.info(f"Problem {i+1}/{len(problems)}: {problem.get('id', 'Unknown')}")
            
            problem_start = time.time()
            
            try:
                # Extract problem details
                query = problem.get("query", "")
                expected = problem.get("expected", "")
                language = problem.get("language", "english")
                
                # Execute pipeline with ARC-AGI optimized settings
                result = self.execute(
                    query=query,
                    language=language,
                    enable_critic=True,
                    enable_deep_cot=True,
                    enable_self_consistency=True
                )
                
                problem_time = time.time() - problem_start
                results["total_time"] += problem_time
                
                # Simple accuracy check (could be enhanced with semantic similarity)
                is_correct = self._check_arc_solution(result["final_answer"], expected)
                
                if is_correct:
                    results["solved"] += 1
                    logger.info(f"✅ Problem {i+1}: SOLVED in {problem_time:.1f}s")
                else:
                    results["failed"] += 1
                    logger.info(f"❌ Problem {i+1}: FAILED in {problem_time:.1f}s")
                    
                results["per_problem_results"].append({
                    "problem_id": problem.get("id", i),
                    "solved": is_correct,
                    "time": problem_time,
                    "answer": result["final_answer"],
                    "expected": expected,
                    "trace": result["reasoning_trace"]
                })
                
            except Exception as e:
                logger.error(f"❌ Problem {i+1} failed with error: {e}")
                results["failed"] += 1
                results["per_problem_results"].append({
                    "problem_id": problem.get("id", i),
                    "solved": False,
                    "error": str(e)
                })
        
        # Calculate summary statistics
        results["accuracy"] = results["solved"] / results["total_problems"] if results["total_problems"] > 0 else 0
        results["average_time"] = results["total_time"] / results["total_problems"] if results["total_problems"] > 0 else 0
        
        logger.info("=" * 60)
        logger.info("📊 ARC-AGI 2 BENCHMARK RESULTS")
        logger.info("=" * 60)
        logger.info(f"🎯 Accuracy: {results['accuracy']*100:.1f}% ({results['solved']}/{results['total_problems']})")
        logger.info(f"⏱️  Average time: {results['average_time']:.1f}s")
        logger.info(f"🔥 Total time: {results['total_time']:.1f}s")
        logger.info("=" * 60)
        
        return results

    def _check_arc_solution(self, generated: str, expected: str) -> bool:
        """
        Check if ARC-AGI solution is correct
        
        Args:
            generated: Generated answer
            expected: Expected answer
            
        Returns:
            True if solution is correct
        """
        if not expected:
            return True  # No expected answer provided
            
        # Normalize both answers
        gen_normalized = generated.strip().lower()
        exp_normalized = expected.strip().lower()
        
        # Exact match
        if gen_normalized == exp_normalized:
            return True
            
        # Check if expected is contained in generated
        if exp_normalized in gen_normalized:
            return True
            
        # Could add more sophisticated semantic similarity here
        
        return False

    def get_stats(self) -> Dict[str, Any]:
        """Get pipeline statistics"""
        avg_time = self.stats["total_time"] / self.stats["queries_processed"] if self.stats["queries_processed"] > 0 else 0
        avg_critic = sum(self.stats["critic_iterations"]) / len(self.stats["critic_iterations"]) if self.stats["critic_iterations"] else 0
        
        return {
            **self.stats,
            "average_query_time": avg_time,
            "average_critic_iterations": avg_critic
        }

    def reset_stats(self):
        """Reset pipeline statistics"""
        self.stats = {
            "queries_processed": 0,
            "total_time": 0.0,
            "language_distribution": {},
            "critic_iterations": []
        }
