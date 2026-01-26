"""
VRAM Manager - The "Flush Protocol" Implementation
Handles aggressive memory management for sequential model loading on T4 (16GB)
Enhanced for production with monitoring and optimization
"""

import gc
import torch
import logging
import time
from typing import Optional, Dict, Any
from dataclasses import dataclass

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("VRAMManager")

@dataclass
class MemoryStats:
    """Memory statistics data class"""
    allocated_gb: float
    reserved_gb: float
    total_gb: float
    available_gb: float
    fragmentation_ratio: float
    timestamp: float

class VRAMManager:
    """
    Implements the strict 'Flush Protocol' from the Maha-System Manifesto:
    1. Explicit deletion
    2. Force garbage collection  
    3. Clear CUDA cache
    4. Synchronize CUDA operations
    
    Enhanced with monitoring and optimization for production use.
    """

    def __init__(self):
        self.memory_history = []
        self.flush_count = 0
        
    def flush(self, aggressive: bool = True) -> Dict[str, Any]:
        """
        Aggressive VRAM cleanup - the Jugaad way
        
        Args:
            aggressive: Whether to perform aggressive cleanup including fragmentation reduction
            
        Returns:
            Dict with cleanup statistics
        """
        logger.info("🧹 Executing VRAM Flush Protocol...")
        start_time = time.time()
        
        # Store pre-cleanup stats
        pre_stats = self.get_memory_stats()
        
        # Step 1: Multiple rounds of garbage collection
        for i in range(3 if aggressive else 1):
            gc.collect()
            
        # Step 2: Clear PyTorch CUDA cache multiple times
        if torch.cuda.is_available():
            for i in range(2 if aggressive else 1):
                torch.cuda.empty_cache()
                
            # Step 3: Synchronize CUDA operations
            torch.cuda.synchronize()
            
            # Step 4: Additional fragmentation reduction (if available)
            if aggressive and hasattr(torch.cuda, 'memory_pool'):
                try:
                    torch.cuda.memory_pool.empty()
                except:
                    pass
                    
        self.flush_count += 1
        
        # Store post-cleanup stats
        post_stats = self.get_memory_stats()
        
        cleanup_stats = {
            "freed_gb": pre_stats.allocated_gb - post_stats.allocated_gb,
            "time_ms": (time.time() - start_time) * 1000,
            "flush_count": self.flush_count,
            "aggressive": aggressive
        }
        
        logger.info(f"💾 VRAM Freed: {cleanup_stats['freed_gb']:.2f}GB in {cleanup_stats['time_ms']:.1f}ms")
        
        return cleanup_stats

    def get_memory_stats(self) -> MemoryStats:
        """Get current GPU memory statistics with fragmentation analysis"""
        if not torch.cuda.is_available():
            return MemoryStats(
                allocated_gb=0,
                reserved_gb=0,
                total_gb=0,
                available_gb=0,
                fragmentation_ratio=0,
                timestamp=time.time()
            )

        allocated = torch.cuda.memory_allocated() / 1024**3
        reserved = torch.cuda.memory_reserved() / 1024**3
        total = torch.cuda.get_device_properties(0).total_memory / 1024**3
        available = total - allocated
        
        # Calculate fragmentation ratio
        fragmentation_ratio = (reserved - allocated) / reserved if reserved > 0 else 0
        
        stats = MemoryStats(
            allocated_gb=allocated,
            reserved_gb=reserved,
            total_gb=total,
            available_gb=available,
            fragmentation_ratio=fragmentation_ratio,
            timestamp=time.time()
        )
        
        # Store for history tracking
        self.memory_history.append(stats)
        
        # Keep only last 100 entries
        if len(self.memory_history) > 100:
            self.memory_history = self.memory_history[-100:]
            
        return stats

    def get_memory_trend(self, window: int = 10) -> Dict[str, float]:
        """Get memory usage trend over recent history"""
        if len(self.memory_history) < window:
            window = len(self.memory_history)
            
        if window == 0:
            return {"trend_gb_per_min": 0, "avg_fragmentation": 0}
            
        recent = self.memory_history[-window:]
        
        # Calculate trend (GB per minute)
        if len(recent) >= 2:
            time_span = (recent[-1].timestamp - recent[0].timestamp) / 60  # minutes
            memory_change = recent[-1].allocated_gb - recent[0].allocated_gb
            trend = memory_change / time_span if time_span > 0 else 0
        else:
            trend = 0
            
        # Average fragmentation
        avg_fragmentation = sum(s.fragmentation_ratio for s in recent) / len(recent)
        
        return {
            "trend_gb_per_min": trend,
            "avg_fragmentation": avg_fragmentation,
            "peak_usage_gb": max(s.allocated_gb for s in recent),
            "current_usage_gb": recent[-1].allocated_gb if recent else 0
        }

    def can_load_model(self, model_size_gb: float, safety_margin_gb: float = 2.0) -> bool:
        """
        Check if we can safely load a model of given size
        
        Args:
            model_size_gb: Size of the model in GB
            safety_margin_gb: Safety margin to keep free
            
        Returns:
            True if model can be loaded safely
        """
        stats = self.get_memory_stats()
        required = model_size_gb + safety_margin_gb
        
        return stats.available_gb >= required

    def optimize_for_model(self, model_size_gb: float) -> Dict[str, Any]:
        """
        Optimize memory configuration for loading a specific model
        
        Args:
            model_size_gb: Size of the model to load
            
        Returns:
            Optimization recommendations
        """
        stats = self.get_memory_stats()
        
        recommendations = {
            "can_load": stats.available_gb >= model_size_gb + 1.0,  # 1GB safety margin
            "recommended_gpu_layers": -1,  # Default: all layers on GPU
            "needs_aggressive_flush": False,
            "can_keep_loaded": stats.available_gb >= model_size_gb + 3.0
        }
        
        # Adjust recommendations based on available memory
        if stats.available_gb < model_size_gb + 2.0:
            recommendations["recommended_gpu_layers"] = 0  # CPU only
            recommendations["needs_aggressive_flush"] = True
        elif stats.available_gb < model_size_gb + 3.0:
            recommendations["recommended_gpu_layers"] = 20  # Partial offload
            
        return recommendations

    def log_memory_summary(self):
        """Log a comprehensive memory summary"""
        stats = self.get_memory_stats()
        trend = self.get_memory_trend()
        
        logger.info("=" * 60)
        logger.info("📊 VRAM SUMMARY")
        logger.info("=" * 60)
        logger.info(f"💾 Total VRAM: {stats.total_gb:.2f}GB")
        logger.info(f"📈 Allocated: {stats.allocated_gb:.2f}GB ({stats.allocated_gb/stats.total_gb*100:.1f}%)")
        logger.info(f"🟡 Reserved: {stats.reserved_gb:.2f}GB")
        logger.info(f"✅ Available: {stats.available_gb:.2f}GB")
        logger.info(f"🧩 Fragmentation: {stats.fragmentation_ratio*100:.1f}%")
        logger.info(f"📊 Trend: {trend['trend_gb_per_min']:+.2f}GB/min")
        logger.info(f"🔥 Peak Usage: {trend['peak_usage_gb']:.2f}GB")
        logger.info(f"🧹 Flush Count: {self.flush_count}")
        logger.info("=" * 60)

class MemoryProfiler:
    """Context manager for profiling memory usage of code blocks"""
    
    def __init__(self, name: str, vram_manager: VRAMManager):
        self.name = name
        self.vram_manager = vram_manager
        self.start_stats = None
        
    def __enter__(self):
        self.start_stats = self.vram_manager.get_memory_stats()
        logger.info(f"🔍 Profiling memory for: {self.name}")
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        end_stats = self.vram_manager.get_memory_stats()
        
        delta_allocated = end_stats.allocated_gb - self.start_stats.allocated_gb
        delta_reserved = end_stats.reserved_gb - self.start_stats.reserved_gb
        
        logger.info(f"📊 Memory Profile: {self.name}")
        logger.info(f"   Allocated: {delta_allocated:+.2f}GB")
        logger.info(f"   Reserved: {delta_reserved:+.2f}GB")
        
        if exc_type:
            logger.error(f"   Error: {exc_val}")
