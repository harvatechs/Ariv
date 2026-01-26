#!/usr/bin/env python3
"""Integration tests for TRV Pipeline"""

import pytest
from unittest.mock import Mock, patch
from core.trv_pipeline import TRVPipeline
from core.orchestrator import JugaadOrchestrator

def test_pipeline_phases():
    """Test that all 4 phases execute"""
    mock_orch = Mock()
    mock_orch.generate.return_value = "test output"

    pipeline = TRVPipeline(mock_orch, {})

    # Mock the phase methods to track calls
    pipeline._phase1_ingestion = Mock(return_value="english")
    pipeline._phase2_reasoning = Mock(return_value="solution")
    pipeline._phase3_critic = Mock(return_value="PASS")
    pipeline._phase4_synthesis = Mock(return_value="final")

    result = pipeline.execute("query", "hindi", enable_critic=True)

    # Verify all phases called
    pipeline._phase1_ingestion.assert_called_once()
    pipeline._phase2_reasoning.assert_called_once()
    pipeline._phase3_critic.assert_called_once()
    pipeline._phase4_synthesis.assert_called_once()

    assert result["final_answer"] == "final"

def test_critic_loop():
    """Test critic iteration logic"""
    mock_orch = Mock()
    pipeline = TRVPipeline(mock_orch, {})

    # First critic fails, second passes
    pipeline._phase3_critic = Mock(side_effect=["FAIL", "PASS"])
    pipeline._phase2_reasoning = Mock(return_value="solution")
    pipeline._phase1_ingestion = Mock(return_value="english")
    pipeline._phase4_synthesis = Mock(return_value="final")

    result = pipeline.execute("query", "hindi", enable_critic=True)

    # Should have 2 critic calls (fail then pass)
    assert pipeline._phase3_critic.call_count == 2
    # Should have 2 reasoning calls (initial + revision)
    assert pipeline._phase2_reasoning.call_count == 2
