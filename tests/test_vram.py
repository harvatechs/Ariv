#!/usr/bin/env python3
"""Tests for VRAM Manager"""

import pytest
from core.vram_manager import VRAMManager, torch

def test_vram_stats():
    """Test VRAM stats collection"""
    if torch is None or not torch.cuda.is_available():
        pytest.skip("CUDA not available")

    manager = VRAMManager()
    stats = manager.get_memory_stats()
    assert stats.total_gb > 0
    assert stats.available_gb >= 0
    assert stats.allocated_gb >= 0

def test_flush_protocol():
    """Test VRAM flush doesn't crash"""
    if torch is None or not torch.cuda.is_available():
        pytest.skip("CUDA not available")

    # Allocate some memory
    x = torch.randn(1000, 1000).cuda()
    del x

    # Should not raise
    manager = VRAMManager()
    manager.flush()

    # Memory should be reduced (or at least not crash)
    stats = manager.get_memory_stats()
    assert stats.available_gb >= 0
