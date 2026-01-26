#!/usr/bin/env python3
"""Tests for JugaadOrchestrator"""

import pytest
import os
from unittest.mock import Mock, patch
from core.orchestrator import JugaadOrchestrator

def test_orchestrator_init():
    """Test orchestrator initialization"""
    config = {
        "translator": "/fake/path/sarvam.gguf",
        "reasoner": "/fake/path/deepseek.gguf"
    }

    with pytest.raises(FileNotFoundError):
        orch = JugaadOrchestrator(config)
        orch.load_model("translator")  # Should fail if file doesn't exist

def test_model_caching():
    """Test that same model isn't reloaded"""
    config = {"test": "/fake/path.gguf"}
    orch = JugaadOrchestrator(config)
    orch.current_model = Mock()
    orch.current_role = "test"

    # Should return cached model
    result = orch.load_model("test")
    assert result == orch.current_model

def test_unload():
    """Test model unloading"""
    orch = JugaadOrchestrator({})
    orch.current_model = Mock()
    orch.current_role = "test"

    orch.unload_model()
    assert orch.current_model is None
    assert orch.current_role is None
