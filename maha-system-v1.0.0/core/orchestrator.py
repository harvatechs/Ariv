"""
JugaadOrchestrator - Sequential Hot-Swap Model Manager
Loads models as 'cartridges' - one at a time to fit in 16GB T4 VRAM
"""

import os
from typing import Dict, Optional, Any
from llama_cpp import Llama
from .vram_manager import VRAMManager
import logging

logger = logging.getLogger("JugaadOrchestrator")

class JugaadOrchestrator:
    """
    The 'Cartridge Loader' - manages models in a sequential pipeline.
    Only one model (plus small context) resides in VRAM at any moment.
    """

    def __init__(self, models_config: Dict[str, str]):
        """
        Args:
            models_config: Dict mapping model roles to GGUF file paths
                e.g., {'translator': '/path/to/sarvam-1-2b-q4.gguf', ...}
        """
        self.models_config = models_config
        self.current_model: Optional[Llama] = None
        self.current_role: Optional[str] = None
        self.vram_manager = VRAMManager()

    def load_model(self, role: str, n_ctx: int = 4096, n_gpu_layers: int = -1) -> Llama:
        """
        Load a model by role. Unloads current model first if necessary.

        Args:
            role: The role key (e.g., 'translator', 'reasoner', 'critic')
            n_ctx: Context window size (default 4096 for Colab safety)
            n_gpu_layers: -1 = offload all to GPU (fastest), 0 = CPU only
        """
        if role not in self.models_config:
            raise ValueError(f"Role {role} not found in config. Available: {list(self.models_config.keys())}")

        model_path = self.models_config[role]

        # Skip if already loaded
        if self.current_role == role and self.current_model is not None:
            logger.info(f"✅ Model '{role}' already loaded")
            return self.current_model

        # Hot-swap: Unload current before loading new
        if self.current_model is not None:
            self.unload_model()

        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found: {model_path}")

        logger.info(f"⏳ Loading '{role}' from {model_path}...")

        try:
            # Load with GGUF - memory mapped for faster loading
            self.current_model = Llama(
                model_path=model_path,
                n_gpu_layers=n_gpu_layers,
                n_ctx=n_ctx,
                verbose=False,
                use_mmap=True,  # Essential for fast hot-swapping
                use_mlock=False # Don't lock memory (Colab constraint)
            )
            self.current_role = role

            stats = self.vram_manager.get_memory_stats()
            logger.info(f"✅ '{role}' loaded. VRAM: {stats['allocated_gb']:.2f}GB used")

            return self.current_model

        except Exception as e:
            logger.error(f"❌ Failed to load {role}: {e}")
            self.vram_manager.flush()
            raise

    def unload_model(self):
        """Unload current model and flush VRAM completely"""
        if self.current_model is not None:
            logger.info(f"🔄 Unloading '{self.current_role}'...")

            # Explicit deletion
            del self.current_model
            self.current_model = None
            self.current_role = None

            # Aggressive flush
            self.vram_manager.flush()
            logger.info("✅ Model unloaded and VRAM flushed")

    def generate(self, 
                 role: str, 
                 prompt: str, 
                 max_tokens: int = 512,
                 temperature: float = 0.7,
                 stop: Optional[list] = None,
                 **kwargs) -> str:
        """
        Convenience method: Load model (if needed), generate, keep loaded for potential reuse
        """
        model = self.load_model(role)

        response = model(
            prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            stop=stop or [],
            **kwargs
        )

        return response['choices'][0]['text'].strip()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.unload_model()
