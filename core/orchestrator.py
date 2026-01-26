"""
Enhanced JugaadOrchestrator - Advanced Sequential Hot-Swap Model Manager
Production-ready with tool calling, chain-of-thought, and multi-language support
"""

import os
import time
from typing import Dict, Optional, Any, List, Callable
from llama_cpp import Llama
from .vram_manager import VRAMManager, MemoryProfiler
from ..tools.registry import ToolRegistry
import logging

logger = logging.getLogger("JugaadOrchestrator")

class ModelLoadError(Exception):
    """Exception raised when model loading fails"""
    pass

class JugaadOrchestrator:
    """
    The 'Cartridge Loader' - manages models in a sequential pipeline.
    Only one model (plus small context) resides in VRAM at any moment.
    
    Enhanced with:
    - Tool calling support
    - Advanced chain-of-thought
    - Multi-language routing
    - Performance monitoring
    """

    def __init__(self, models_config: Dict[str, str], enable_tools: bool = True):
        """
        Args:
            models_config: Dict mapping model roles to GGUF file paths
                e.g., {'translator': '/path/to/sarvam-1-2b-q4.gguf', ...}
            enable_tools: Whether to enable tool calling capabilities
        """
        self.models_config = models_config
        self.current_model: Optional[Llama] = None
        self.current_role: Optional[str] = None
        self.vram_manager = VRAMManager()
        self.tool_registry = ToolRegistry() if enable_tools else None
        self.load_times = {}
        self.generation_stats = []
        
        # Statistics tracking
        self.stats = {
            "models_loaded": 0,
            "total_generation_time": 0.0,
            "total_tokens_generated": 0,
            "tool_calls_made": 0
        }

    def load_model(self, 
                   role: str, 
                   n_ctx: int = 4096, 
                   n_gpu_layers: int = -1,
                   force_reload: bool = False) -> Llama:
        """
        Load a model by role. Unloads current model first if necessary.

        Args:
            role: The role key (e.g., 'translator', 'reasoner', 'critic')
            n_ctx: Context window size (default 4096 for Colab safety)
            n_gpu_layers: -1 = offload all to GPU (fastest), 0 = CPU only
            force_reload: Force reload even if same model is loaded
        """
        if role not in self.models_config:
            raise ValueError(f"Role {role} not found in config. Available: {list(self.models_config.keys())}")

        model_path = self.models_config[role]

        # Skip if already loaded and not forcing reload
        if self.current_role == role and self.current_model is not None and not force_reload:
            logger.info(f"✅ Model '{role}' already loaded")
            return self.current_model

        # Hot-swap: Unload current before loading new
        if self.current_model is not None:
            self.unload_model()

        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found: {model_path}")

        logger.info(f"⏳ Loading '{role}' from {model_path}...")
        load_start = time.time()

        try:
            # Get memory optimization recommendations
            model_size_gb = os.path.getsize(model_path) / (1024**3)
            mem_opt = self.vram_manager.optimize_for_model(model_size_gb)
            
            # Use recommended GPU layers if not explicitly set
            if n_gpu_layers == -1 and not mem_opt["can_load"]:
                n_gpu_layers = mem_opt["recommended_gpu_layers"]
                logger.warning(f"Adjusting GPU layers to {n_gpu_layers} due to memory constraints")

            # Load with GGUF - memory mapped for faster loading
            self.current_model = Llama(
                model_path=model_path,
                n_gpu_layers=n_gpu_layers,
                n_ctx=n_ctx,
                verbose=False,
                use_mmap=True,  # Essential for fast hot-swapping
                use_mlock=False,  # Don't lock memory (Colab constraint)
                logits_all=False,  # Save memory
                embedding=False    # We don't need embeddings
            )
            self.current_role = role
            self.stats["models_loaded"] += 1

            load_time = time.time() - load_start
            self.load_times[role] = load_time

            stats = self.vram_manager.get_memory_stats()
            logger.info(f"✅ '{role}' loaded in {load_time:.2f}s. VRAM: {stats.allocated_gb:.2f}GB used")

            return self.current_model

        except Exception as e:
            logger.error(f"❌ Failed to load {role}: {e}")
            self.vram_manager.flush()
            raise ModelLoadError(f"Failed to load model {role}: {e}")

    def unload_model(self):
        """Unload current model and flush VRAM completely"""
        if self.current_model is not None:
            logger.info(f"🔄 Unloading '{self.current_role}'...")

            # Explicit deletion
            del self.current_model
            self.current_model = None
            self.current_role = None

            # Aggressive flush
            self.vram_manager.flush(aggressive=True)
            logger.info("✅ Model unloaded and VRAM flushed")

    def generate(self, 
                 role: str, 
                 prompt: str, 
                 max_tokens: int = 512,
                 temperature: float = 0.7,
                 stop: Optional[List[str]] = None,
                 stream: bool = False,
                 **kwargs) -> str:
        """
        Convenience method: Load model (if needed), generate, keep loaded for potential reuse
        
        Args:
            role: Model role to use
            prompt: Input prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            stop: Stop sequences
            stream: Whether to stream output
            **kwargs: Additional generation parameters
            
        Returns:
            Generated text
        """
        generation_start = time.time()
        
        # Load model if needed
        model = self.load_model(role)
        
        # Prepare generation parameters
        gen_params = {
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stop": stop or [],
            "top_p": 0.95,
            "top_k": 40,
            "repeat_penalty": 1.1,
            "frequency_penalty": 0.0,
            "presence_penalty": 0.0,
            **kwargs
        }

        try:
            response = model(prompt, **gen_params)
            
            generated_text = response['choices'][0]['text'].strip()
            tokens_generated = len(generated_text.split())  # Rough estimate
            
            # Update statistics
            generation_time = time.time() - generation_start
            self.stats["total_generation_time"] += generation_time
            self.stats["total_tokens_generated"] += tokens_generated
            
            # Store generation stats
            self.generation_stats.append({
                "role": role,
                "time": generation_time,
                "tokens": tokens_generated,
                "tokens_per_second": tokens_generated / generation_time if generation_time > 0 else 0
            })
            
            logger.debug(f"📝 Generated {tokens_generated} tokens in {generation_time:.2f}s ({tokens_generated/generation_time:.1f} tok/s)")
            
            return generated_text
            
        except Exception as e:
            logger.error(f"❌ Generation failed for role {role}: {e}")
            raise

    def generate_with_tools(self,
                           role: str,
                           prompt: str,
                           max_tokens: int = 2048,
                           temperature: float = 0.7,
                           tools: Optional[List[str]] = None,
                           max_tool_calls: int = 10) -> Dict[str, Any]:
        """
        Generate with tool calling support
        
        Args:
            role: Model role to use
            prompt: Input prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            tools: List of tool names to enable (None = all)
            max_tool_calls: Maximum number of tool calls allowed
            
        Returns:
            Dict containing generated text, tool calls, and metadata
        """
        if not self.tool_registry:
            raise ValueError("Tool registry not enabled")

        tool_calls = []
        final_response = ""
        
        # Add tool information to prompt
        tool_info = self.tool_registry.get_tool_info(tools)
        enhanced_prompt = f"""You have access to the following tools:
{tool_info}

Use tools when needed by writing TOOL_CALL: <tool_name>(<parameters>)

User: {prompt}
"""

        # Generate initial response
        response = self.generate(role, enhanced_prompt, max_tokens, temperature)
        
        # Parse and execute tool calls
        if "TOOL_CALL:" in response:
            # Extract tool calls and execute them
            lines = response.split('\n')
            for line in lines:
                if "TOOL_CALL:" in line:
                    try:
                        tool_call_str = line.split("TOOL_CALL:")[1].strip()
                        result = self.tool_registry.execute_tool_call(tool_call_str)
                        tool_calls.append({
                            "call": tool_call_str,
                            "result": result
                        })
                        self.stats["tool_calls_made"] += 1
                        
                        # Add tool result to context and regenerate
                        if len(tool_calls) < max_tool_calls:
                            follow_up_prompt = f"""{enhanced_prompt}

Tool result: {result}

Please provide your final answer based on the tool result:"""
                            response = self.generate(role, follow_up_prompt, max_tokens, temperature)
                    except Exception as e:
                        logger.error(f"Tool call failed: {e}")
                        
        return {
            "text": response,
            "tool_calls": tool_calls,
            "model_role": role
        }

    def chain_of_thought_generate(self,
                                  role: str,
                                  prompt: str,
                                  cot_depth: int = 3,
                                  enable_reflection: bool = True,
                                  enable_adversarial: bool = True) -> Dict[str, Any]:
        """
        Generate using advanced chain-of-thought reasoning
        
        Args:
            role: Model role to use
            prompt: Input prompt
            cot_depth: Depth of reasoning chain
            enable_reflection: Enable self-reflection step
            enable_adversarial: Enable devil's advocate reasoning
            
        Returns:
            Dict containing reasoning chain and final answer
        """
        reasoning_chain = []
        
        # Initial reasoning
        cot_prompt = f"""Let's think step by step:

Problem: {prompt}

Step-by-step reasoning:"""

        reasoning = self.generate(role, cot_prompt, max_tokens=2048, temperature=0.6)
        reasoning_chain.append({"step": "initial_reasoning", "content": reasoning})
        
        # Deep reasoning iterations
        for i in range(cot_depth - 1):
            deep_prompt = f"""Let's analyze this problem more deeply:

Problem: {prompt}

Previous reasoning: {reasoning}

Deeper analysis (consider edge cases, alternatives, and implications):"""
            
            reasoning = self.generate(role, deep_prompt, max_tokens=2048, temperature=0.5)
            reasoning_chain.append({"step": f"deep_analysis_{i+1}", "content": reasoning})
            
        # Reflection step
        if enable_reflection:
            reflection_prompt = f"""Reflect on your reasoning:

Problem: {prompt}

Your reasoning: {reasoning}

Are there any flaws or biases in this reasoning? What might you have missed?

Reflection:"""
            
            reflection = self.generate(role, reflection_prompt, max_tokens=1024, temperature=0.4)
            reasoning_chain.append({"step": "reflection", "content": reflection})
            
        # Adversarial reasoning
        if enable_adversarial:
            adversarial_prompt = f"""Play devil's advocate:

Problem: {prompt}

Claimed solution: {reasoning}

What are the strongest counterarguments or alternative viewpoints?"""
            
            adversarial = self.generate(role, adversarial_prompt, max_tokens=1024, temperature=0.5)
            reasoning_chain.append({"step": "adversarial", "content": adversarial})
            
            # Final synthesis
            synthesis_prompt = f"""Synthesize the final answer:

Problem: {prompt}

Reasoning: {reasoning}

Reflection: {reflection if enable_reflection else 'N/A'}

Adversarial considerations: {adversarial if enable_adversarial else 'N/A'}

Final answer (concise and actionable):"""
            
            final_answer = self.generate(role, synthesis_prompt, max_tokens=1024, temperature=0.3)
            reasoning_chain.append({"step": "final_synthesis", "content": final_answer})
            
        else:
            final_answer = reasoning
            
        return {
            "final_answer": final_answer,
            "reasoning_chain": reasoning_chain,
            "cot_depth": cot_depth
        }

    def self_consistency_generate(self,
                                  role: str,
                                  prompt: str,
                                  num_paths: int = 5,
                                  temperature: float = 0.7) -> Dict[str, Any]:
        """
        Generate multiple reasoning paths and select the most consistent answer
        
        Args:
            role: Model role to use
            prompt: Input prompt
            num_paths: Number of reasoning paths to generate
            temperature: Temperature for generation (higher = more diverse)
            
        Returns:
            Dict containing final answer and reasoning paths
        """
        paths = []
        
        for i in range(num_paths):
            cot_result = self.chain_of_thought_generate(
                role, 
                prompt, 
                cot_depth=2,  # Shorter chains for efficiency
                enable_reflection=False,
                enable_adversarial=False
            )
            paths.append({
                "path_id": i,
                "answer": cot_result["final_answer"],
                "reasoning": cot_result["reasoning_chain"]
            })
            
        # Find most consistent answer (simplified voting)
        answers = [p["answer"] for p in paths]
        
        # Simple majority voting (could be enhanced with semantic similarity)
        answer_counts = {}
        for ans in answers:
            # Normalize answer for comparison
            normalized = ans.strip().lower()
            if normalized not in answer_counts:
                answer_counts[normalized] = 0
            answer_counts[normalized] += 1
            
        # Select most frequent answer
        most_frequent = max(answer_counts.keys(), key=lambda k: answer_counts[k])
        final_answer = most_frequent
        
        # Get full reasoning for the selected answer
        selected_path = next(p for p in paths if p["answer"].strip().lower() == most_frequent)
        
        return {
            "final_answer": final_answer,
            "reasoning_paths": paths,
            "consistency_score": answer_counts[most_frequent] / num_paths,
            "selected_path": selected_path
        }

    def get_stats(self) -> Dict[str, Any]:
        """Get orchestrator statistics"""
        avg_time = (self.stats["total_generation_time"] / len(self.generation_stats) 
                   if self.generation_stats else 0)
        avg_tokens = (self.stats["total_tokens_generated"] / len(self.generation_stats) 
                     if self.generation_stats else 0)
        avg_tokens_per_sec = avg_tokens / avg_time if avg_time > 0 else 0
        
        return {
            **self.stats,
            "average_generation_time": avg_time,
            "average_tokens_per_generation": avg_tokens,
            "average_tokens_per_second": avg_tokens_per_sec,
            "recent_generations": self.generation_stats[-10:] if self.generation_stats else []
        }

    def reset_stats(self):
        """Reset statistics"""
        self.stats = {
            "models_loaded": 0,
            "total_generation_time": 0.0,
            "total_tokens_generated": 0,
            "tool_calls_made": 0
        }
        self.generation_stats = []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.unload_model()
        self.vram_manager.log_memory_summary()
