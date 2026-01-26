#!/usr/bin/env python3
"""Tests for Cache system"""

import pytest
import tempfile
import shutil
from utils.cache import MahaCache

@pytest.fixture
def temp_cache():
    """Create temporary cache directory"""
    temp_dir = tempfile.mkdtemp()
    cache = MahaCache(cache_dir=temp_dir, ttl_hours=1)
    yield cache
    shutil.rmtree(temp_dir)

def test_translation_cache(temp_cache):
    """Test translation caching"""
    # Cache miss
    result = temp_cache.get_translation("नमस्ते", "hindi")
    assert result is None

    # Set cache
    temp_cache.set_translation("नमस्ते", "hindi", "Hello")

    # Cache hit
    result = temp_cache.get_translation("नमस्ते", "hindi")
    assert result == "Hello"

def test_cache_expiration(temp_cache):
    """Test cache TTL"""
    temp_cache.set_translation("test", "hi", "value")

    # Should exist
    assert temp_cache.get_translation("test", "hi") == "value"

    # Clear expired (none expired yet)
    cleared = temp_cache.clear_expired()
    assert cleared == 0

    # Should still exist
    assert temp_cache.get_translation("test", "hi") == "value"

def test_cache_stats(temp_cache):
    """Test cache statistics"""
    stats = temp_cache.get_stats()
    assert "translation_entries" in stats
    assert "reasoning_entries" in stats

    temp_cache.set_translation("test", "hi", "value")
    stats = temp_cache.get_stats()
    assert stats["translation_entries"] == 1
