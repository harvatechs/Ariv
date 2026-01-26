#!/usr/bin/env python3
"""
Smart Cache for Maha-System
Caches translation and reasoning results to avoid redundant computation
"""

import hashlib
import json
import logging
from typing import Optional, Dict, Any
from pathlib import Path
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Cache")

class MahaCache:
    """
    Two-tier cache system:
    1. Translation Cache: Lang-specific queries -> English (saves Phase 1)
    2. Reasoning Cache: English prompts -> Solutions (saves Phase 2-3)

    Significantly speeds up repeated queries (e.g., FAQ bots)
    """

    def __init__(self, cache_dir: str = ".cache", ttl_hours: int = 24):
        """
        Args:
            cache_dir: Directory to store cache files
            ttl_hours: Time-to-live for cache entries (default 24h)
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.ttl_seconds = ttl_hours * 3600

        # In-memory cache for hot data
        self._mem_cache = {}

        logger.info(f"📦 Cache initialized at {cache_dir} (TTL: {ttl_hours}h)")

    def _get_hash(self, text: str) -> str:
        """Generate hash key for text"""
        return hashlib.md5(text.encode()).hexdigest()

    def _get_cache_path(self, key: str, tier: str) -> Path:
        """Get file path for cache entry"""
        return self.cache_dir / f"{tier}_{key}.json"

    def get_translation(self, query: str, language: str) -> Optional[str]:
        """Get cached translation (Phase 1 cache)"""
        key = self._get_hash(f"{language}:{query}")

        # Check memory first
        if key in self._mem_cache:
            return self._mem_cache[key]

        # Check disk
        cache_file = self._get_cache_path(key, "trans")
        if cache_file.exists():
            try:
                with open(cache_file) as f:
                    data = json.load(f)
                    if time.time() - data['timestamp'] < self.ttl_seconds:
                        self._mem_cache[key] = data['translation']
                        return data['translation']
                    else:
                        cache_file.unlink()  # Expired
            except Exception as e:
                logger.warning(f"Cache read error: {e}")

        return None

    def set_translation(self, query: str, language: str, translation: str):
        """Cache translation result"""
        key = self._get_hash(f"{language}:{query}")
        self._mem_cache[key] = translation

        cache_file = self._get_cache_path(key, "trans")
        try:
            with open(cache_file, 'w') as f:
                json.dump({
                    'translation': translation,
                    'timestamp': time.time(),
                    'language': language
                }, f)
        except Exception as e:
            logger.warning(f"Cache write error: {e}")

    def get_reasoning(self, english_prompt: str) -> Optional[Dict]:
        """Get cached reasoning result (Phase 2-3 cache)"""
        key = self._get_hash(english_prompt)

        if key in self._mem_cache:
            return self._mem_cache[key]

        cache_file = self._get_cache_path(key, "reason")
        if cache_file.exists():
            try:
                with open(cache_file) as f:
                    data = json.load(f)
                    if time.time() - data['timestamp'] < self.ttl_seconds:
                        self._mem_cache[key] = data
                        return data
            except:
                pass

        return None

    def set_reasoning(self, english_prompt: str, result: Dict):
        """Cache reasoning result"""
        key = self._get_hash(english_prompt)
        self._mem_cache[key] = result

        cache_file = self._get_cache_path(key, "reason")
        try:
            with open(cache_file, 'w') as f:
                json.dump({
                    **result,
                    'timestamp': time.time()
                }, f)
        except Exception as e:
            logger.warning(f"Cache write error: {e}")

    def clear_expired(self):
        """Remove expired cache entries"""
        count = 0
        for cache_file in self.cache_dir.glob("*.json"):
            try:
                with open(cache_file) as f:
                    data = json.load(f)
                if time.time() - data['timestamp'] > self.ttl_seconds:
                    cache_file.unlink()
                    count += 1
            except:
                pass

        logger.info(f"🧹 Cleared {count} expired cache entries")
        return count

    def get_stats(self) -> Dict:
        """Get cache statistics"""
        trans_count = len(list(self.cache_dir.glob("trans_*.json")))
        reason_count = len(list(self.cache_dir.glob("reason_*.json")))

        total_size = sum(f.stat().st_size for f in self.cache_dir.glob("*.json"))

        return {
            "translation_entries": trans_count,
            "reasoning_entries": reason_count,
            "memory_entries": len(self._mem_cache),
            "total_size_mb": total_size / (1024**2)
        }

    def print_stats(self):
        """Print cache statistics"""
        stats = self.get_stats()
        print("\n📦 CACHE STATISTICS")
        print(f"Translation entries: {stats['translation_entries']}")
        print(f"Reasoning entries:   {stats['reasoning_entries']}")
        print(f"Memory entries:      {stats['memory_entries']}")
        print(f"Total size:          {stats['total_size_mb']:.2f} MB")

if __name__ == "__main__":
    # Demo usage
    cache = MahaCache()

    # Simulate cache usage
    cache.set_translation("नमस्ते", "hindi", "Hello")
    result = cache.get_translation("नमस्ते", "hindi")
    print(f"Cached translation: {result}")

    cache.print_stats()
