"""
VRAM Manager - The "Flush Protocol" Implementation
Handles aggressive memory management for sequential model loading on T4 (16GB)
"""

import gc
import torch
import logging
from typing import Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("VRAMManager")

class VRAMManager:
    """
    Implements the strict 'Flush Protocol' from the Maha-System Manifesto:
    1. Explicit deletion
    2. Force garbage collection  
    3. Clear CUDA cache
    4. Synchronize CUDA operations
    """

    @staticmethod
    def flush():
        """Aggressive VRAM cleanup - the Jugaad way"""
        logger.info("🧹 Executing VRAM Flush Protocol...")

        # Step 1: Collect garbage
        gc.collect()

        # Step 2: Clear PyTorch CUDA cache
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            torch.cuda.synchronize()

            # Log memory status
            allocated = torch.cuda.memory_allocated() / 1024**3
            reserved = torch.cuda.memory_reserved() / 1024**3
            logger.info(f"💾 VRAM Status: {allocated:.2f}GB allocated, {reserved:.2f}GB reserved")

    @staticmethod
    def get_memory_stats():
        """Get current GPU memory statistics"""
        if not torch.cuda.is_available():
            return {"available": False}

        return {
            "allocated_gb": torch.cuda.memory_allocated() / 1024**3,
            "reserved_gb": torch.cuda.memory_reserved() / 1024**3,
            "total_gb": torch.cuda.get_device_properties(0).total_memory / 1024**3,
            "available": True
        }
