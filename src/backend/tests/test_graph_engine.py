"""Tests for graph_engine.py — state machine node logic and routing."""

from __future__ import annotations

import os
import pytest
from unittest.mock import patch, AsyncMock

from src.backend.orchestration.graph_engine import (
    _emit,
    build_graph,
    compute_state_hash,
    corrector_node,
    corrector_routing,
    decision_gate,
    fallback_node,
    inference_routing,
    response_node,
    user_query_node,
    validator_node,
)


class TestUserQueryNode:
    @pytest.mark.asyncio
    async def test_initializes_state(self, sample_state):
        result = await user_query_node(sample_state)
        assert result["trace_id"] == "test-trace-001"
        assert result["query"] == "What is the refund policy?"
        assert result["retry_count"] == 0
        assert result["temperature"] == 0.7

    @pytest.mark.asyncio
    async def test_rejects_empty_query(self):
        with pytest.raises(ValueError, match="empty"):
            await user_query_node({"query": "   ", "config": {}})


class TestDecisionGate:
    def test_pass_route(self, sample_state):
        sample_state["validation_score"] = 0.85
        sample_state["validation_flags"] = []
        assert decision_gate(sample_state) == "response"

    def test_fail_route(self, sample_state):
        sample_state["validation_score"] = 0.5
        sample_state["validation_flags"] = ["UNFAITHFUL"]
        assert decision_gate(sample_state) == "corrector"

    def test_toxic_route(self, sample_state):
        sample_state["validation_score"] = 0.9
        sample_state["validation_flags"] = ["TOXIC"]
        assert decision_gate(sample_state) == "fallback"

    def test_none_score_routes_fallback(self, sample_state):
        sample_state["validation_score"] = None
        assert decision_gate(sample_state) == "fallback"


class TestInferenceRouting:
    def test_stub_routes_to_response(self, sample_state):
        sample_state["raw_response"] = "stub text"
        sample_state["is_stub"] = True
        assert inference_routing(sample_state) == "response"

    def test_real_routes_to_validator(self, sample_state):
        sample_state["raw_response"] = "real text"
        sample_state["is_stub"] = False
        assert inference_routing(sample_state) == "validator"

    def test_none_routes_to_fallback(self, sample_state):
        sample_state["raw_response"] = None
        assert inference_routing(sample_state) == "fallback"


class TestCorrectorNode:
    @pytest.mark.asyncio
    async def test_increments_retry(self, sample_state):
        sample_state["retry_count"] = 1
        sample_state["validation_flags"] = ["HALLUCINATED"]
        sample_state["raw_response"] = "Some hallucinated text"
        result = await corrector_node(sample_state)
        assert result["retry_count"] == 2

    @pytest.mark.asyncio
    async def test_decreases_temperature(self, sample_state):
        sample_state["temperature"] = 0.7
        sample_state["validation_flags"] = []
        sample_state["raw_response"] = "Some text"
        result = await corrector_node(sample_state)
        assert result["temperature"] == pytest.approx(0.55)

    @pytest.mark.asyncio
    async def test_records_correction_history(self, sample_state):
        sample_state["validation_flags"] = ["UNFAITHFUL"]
        sample_state["raw_response"] = "Bad response"
        result = await corrector_node(sample_state)
        assert len(result["correction_history"]) == 1
        assert result["correction_history"][0]["attempt"] == 1


class TestResponseNode:
    @pytest.mark.asyncio
    async def test_packages_validated_response(self, sample_state):
        sample_state["raw_response"] = "Good answer"
        sample_state["validation_score"] = 0.85
        sample_state["timestamp_start"] = 1000.0
        result = await response_node(sample_state)
        assert result["final_response"]["status"] == "VALIDATED"
        assert result["final_response"]["confidence_score"] == 0.85

    @pytest.mark.asyncio
    async def test_packages_stub_response(self, sample_state):
        sample_state["raw_response"] = "Stub text"
        sample_state["is_stub"] = True
        sample_state["timestamp_start"] = 1000.0
        result = await response_node(sample_state)
        assert result["final_response"]["status"] == "STUB"
        assert result["final_response"]["confidence_score"] is None
        assert result["final_response"]["metric_breakdown"] is None
        assert result["final_response"]["suggestion"] is not None


class TestFallbackNode:
    @pytest.mark.asyncio
    async def test_produces_circuit_break(self, sample_state):
        sample_state["validation_flags"] = ["HALLUCINATED", "UNFAITHFUL"]
        sample_state["timestamp_start"] = 1000.0
        result = await fallback_node(sample_state)
        assert result["final_response"]["status"] == "CIRCUIT_BREAK"
        assert result["final_response"]["confidence_score"] == 0.0


class TestComputeStateHash:
    def test_deterministic(self, sample_state):
        h1 = compute_state_hash(sample_state)
        h2 = compute_state_hash(sample_state)
        assert h1 == h2

    def test_different_for_different_state(self, sample_state):
        h1 = compute_state_hash(sample_state)
        sample_state["retry_count"] = 5
        h2 = compute_state_hash(sample_state)
        assert h1 != h2


class TestHappyPath:
    @pytest.mark.asyncio
    async def test_score_above_threshold_reaches_response(self, compiled_graph, sample_state):
        """Happy path: high validation score → VALIDATED response."""
        with patch.dict(os.environ, {"STUB_VALIDATION_SCORE": "0.85"}):
            result = await compiled_graph.ainvoke(sample_state)
        assert result["final_response"] is not None
        assert result["final_response"]["status"] == "VALIDATED"


class TestRetryPath:
    @pytest.mark.asyncio
    async def test_low_score_retries_then_fallback(self, compiled_graph, sample_state):
        """Low score → 3 retries → fallback."""
        with patch.dict(os.environ, {"STUB_VALIDATION_SCORE": "0.3"}):
            result = await compiled_graph.ainvoke(sample_state)
        assert result["final_response"] is not None
        assert result["final_response"]["status"] == "CIRCUIT_BREAK"
        assert result["retry_count"] == 3


class TestStubPath:
    @pytest.mark.asyncio
    async def test_stub_skips_validation_and_returns_stub_status(self, sample_state):
        """When Ollama is down, stub should bypass validation and get STUB status."""
        graph = build_graph()  # No mock_ollama — real connection will fail
        result = await graph.ainvoke(sample_state)
        assert result["final_response"]["status"] == "STUB"
        assert result["final_response"]["confidence_score"] is None
        assert result["final_response"]["model_used"] == "stub"
        assert result["final_response"]["metric_breakdown"] is None
        assert result["is_stub"] is True


class TestTemperatureDecay:
    @pytest.mark.asyncio
    async def test_temperature_decreases_across_retries(self, compiled_graph, sample_state):
        """Temperature should decay by 0.15 per retry."""
        with patch.dict(os.environ, {"STUB_VALIDATION_SCORE": "0.3"}):
            result = await compiled_graph.ainvoke(sample_state)
        # After 3 retries: 0.7 - 3*0.15 = 0.25
        assert result["temperature"] == pytest.approx(0.25, abs=0.05)


# ---------------------------------------------------------------------------
# Phase 5: New test classes for enhanced coverage
# ---------------------------------------------------------------------------


class TestValidatorNode:
    @pytest.mark.asyncio
    async def test_no_response_zero_score(self, sample_state):
        """No response should produce validation_score=0.0 with NO_RESPONSE flag."""
        sample_state["raw_response"] = None
        result = await validator_node(sample_state)
        assert result["validation_score"] == 0.0
        assert "NO_RESPONSE" in result["validation_flags"]

    @pytest.mark.asyncio
    async def test_banned_pattern_detection(self, sample_state):
        """Response containing banned patterns should flag BANNED_PATTERN."""
        sample_state["raw_response"] = "As an AI language model, I cannot verify this information."
        with patch.dict(os.environ, {"STUB_VALIDATION_SCORE": "0.85"}):
            result = await validator_node(sample_state)
        assert "BANNED_PATTERN" in result["validation_flags"]

    @pytest.mark.asyncio
    async def test_env_score_override(self, sample_state):
        """STUB_VALIDATION_SCORE env var should control the score."""
        sample_state["raw_response"] = "Some valid response text."
        with patch.dict(os.environ, {"STUB_VALIDATION_SCORE": "0.42"}):
            result = await validator_node(sample_state)
        assert result["validation_score"] == pytest.approx(0.42)

    @pytest.mark.asyncio
    async def test_metric_breakdown_structure(self, sample_state):
        """Metric breakdown should have faithfulness, answer_relevancy, hallucination, toxicity."""
        sample_state["raw_response"] = "A valid response for testing."
        with patch.dict(os.environ, {"STUB_VALIDATION_SCORE": "0.85"}):
            result = await validator_node(sample_state)
        breakdown = result["metric_breakdown"]
        assert "faithfulness" in breakdown
        assert "answer_relevancy" in breakdown
        assert "hallucination" in breakdown
        assert "toxicity" in breakdown


class TestCorrectorRouting:
    def test_routes_to_inference_under_max(self, sample_state):
        """Should route to inference when retry_count < max_retries."""
        sample_state["retry_count"] = 1
        assert corrector_routing(sample_state) == "inference"

    def test_routes_to_fallback_at_max(self, sample_state):
        """Should route to fallback when retry_count == max_retries."""
        sample_state["retry_count"] = 3
        assert corrector_routing(sample_state) == "fallback"

    def test_routes_to_fallback_over_max(self, sample_state):
        """Should route to fallback when retry_count > max_retries."""
        sample_state["retry_count"] = 5
        assert corrector_routing(sample_state) == "fallback"


class TestBuildGraph:
    def test_compiles_without_callbacks(self):
        """build_graph() with no callbacks should compile successfully."""
        graph = build_graph()
        assert graph is not None

    def test_compiles_with_callbacks(self):
        """build_graph() with callbacks should compile successfully."""
        async def budget_cb(state):
            return True

        async def event_cb(event):
            pass

        graph = build_graph(budget_callback=budget_cb, event_callback=event_cb)
        assert graph is not None


class TestEmitHelper:
    @pytest.mark.asyncio
    async def test_event_callback_invocation(self):
        """_emit should call the event callback with correct structure."""
        events = []

        async def collector(event):
            events.append(event)

        state = {"_event_callback": collector}
        await _emit(state, "test_agent", "test_action", extra_key="extra_val")
        assert len(events) == 1
        assert events[0]["agent"] == "test_agent"
        assert events[0]["action"] == "test_action"
        assert events[0]["extra_key"] == "extra_val"
        assert "timestamp" in events[0]
