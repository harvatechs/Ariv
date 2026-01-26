#!/usr/bin/env python3
"""Tests for VRAM Manager"""

import pytest
import torch
from core.vram_manager import VRAMManager

def test_vram_stats():
    """Test VRAM stats collection"""
    if not torch.cuda.is_available():
        pytest.skip("CUDA not available")

    stats = VRAMManager.get_memory_stats()
    assert stats['available'] == True
    assert 'allocated_gb' in stats
    assert 'total_gb' in stats
    assert stats['total_gb'] > 0

def test_flush_protocol():
    """Test VRAM flush doesn't crash"""
    if not torch.cuda.is_available():
        pytest.skip("CUDA not available")

    # Allocate some memory
    x = torch.randn(1000, 1000).cuda()
    del x

    # Should not raise
    VRAMManager.flush()

    # Memory should be reduced (or at least not crash)
    stats = VRAMManager.get_memory_stats()
    assert stats['available'] == True
