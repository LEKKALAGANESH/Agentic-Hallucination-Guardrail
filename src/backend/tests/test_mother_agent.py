"""Tests for mother_agent.py — orchestration, budget, and health."""

from __future__ import annotations

import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from src.backend.orchestration.mother_agent import MotherAgent, TokenLedger


class TestTokenLedger:
    def test_initial_state(self):
        ledger = TokenLedger(budget_total=1000)
        assert ledger.budget_remaining == 1000
        assert ledger.budget_used == 0

    def test_record_tokens(self):
        ledger = TokenLedger(budget_total=1000)
        ledger.record("inference", 300)
        assert ledger.budget_used == 300
        assert ledger.budget_remaining == 700

    def test_can_afford(self):
        ledger = TokenLedger(budget_total=1000)
        ledger.record("inference", 900)
        assert ledger.can_afford(50) is True
        assert ledger.can_afford(200) is False


class TestBudgetEnforcement:
    @pytest.mark.asyncio
    async def test_allows_within_budget(self):
        agent = MotherAgent()
        ledger = TokenLedger(budget_total=5000)
        result = await agent.enforce_budget({}, ledger)
        assert result is True

    @pytest.mark.asyncio
    async def test_denies_over_budget(self):
        agent = MotherAgent()
        ledger = TokenLedger(budget_total=100)
        ledger.record("prev", 100)
        result = await agent.enforce_budget({}, ledger)
        assert result is False


class TestMotherAgentRun:
    @pytest.mark.asyncio
    async def test_run_returns_final_state(self, mock_ollama):
        """Pipeline run should produce a final_response."""
        import os
        with patch.dict(os.environ, {"STUB_VALIDATION_SCORE": "0.85"}):
            agent = MotherAgent()
            state = await agent.run(query="What is the refund policy?")
        assert state is not None
        assert "final_response" in state
        assert state["final_response"]["status"] in ("VALIDATED", "CIRCUIT_BREAK")

    @pytest.mark.asyncio
    async def test_run_with_event_callback(self, mock_ollama):
        """Event callback should be called during pipeline."""
        import os
        events: list = []

        async def collector(event):
            events.append(event)

        with patch.dict(os.environ, {"STUB_VALIDATION_SCORE": "0.85"}):
            agent = MotherAgent()
            await agent.run(query="Test query", event_callback=collector)
        assert len(events) > 0


class TestHealthCheck:
    @pytest.mark.asyncio
    async def test_health_returns_valid_structure(self, mock_ollama):
        agent = MotherAgent()
        health = await agent.health_check()
        assert "status" in health
        assert "agents" in health
        assert "budget" in health
        assert "version" in health
        assert health["version"] == "0.1.0"


class TestGetConfig:
    def test_returns_expected_keys(self):
        agent = MotherAgent()
        config = agent.get_config()
        assert "pass_threshold" in config
        assert "max_retries" in config
        assert "temperature_init" in config
        assert "token_ceiling" in config
        assert config["pass_threshold"] == 0.7


# ---------------------------------------------------------------------------
# Phase 5: Enhanced test classes
# ---------------------------------------------------------------------------


class TestMotherAgentRunEdgeCases:
    @pytest.mark.asyncio
    async def test_config_overrides(self, mock_ollama):
        """Per-query config overrides should be applied."""
        import os
        with patch.dict(os.environ, {"STUB_VALIDATION_SCORE": "0.85"}):
            agent = MotherAgent()
            state = await agent.run(
                query="Test override",
                config_overrides={"pass_threshold": 0.5, "max_retries": 1},
            )
        assert state is not None
        assert state["final_response"]["status"] in ("VALIDATED", "CIRCUIT_BREAK")

    @pytest.mark.asyncio
    async def test_timeout_produces_circuit_break(self, mock_ollama):
        """Pipeline timeout should produce CIRCUIT_BREAK status."""
        import os

        agent = MotherAgent()
        # Patch the rules to have a very short timeout
        original_rules = agent._rules.copy()
        agent._rules["timeout"] = {"total_pipeline_timeout_seconds": 0.001}

        # Patch graph.ainvoke to simulate a long-running task
        async def slow_invoke(state):
            import asyncio
            await asyncio.sleep(10)
            return state

        with patch.dict(os.environ, {"STUB_VALIDATION_SCORE": "0.85"}):
            with patch.object(agent, '_graph') as mock_graph:
                # We need to rebuild the graph inside run(), so let's patch build_graph
                from src.backend.orchestration.graph_engine import build_graph
                with patch("src.backend.orchestration.mother_agent.build_graph") as mock_bg:
                    mock_compiled = AsyncMock()
                    mock_compiled.ainvoke = slow_invoke
                    mock_bg.return_value = mock_compiled
                    state = await agent.run(query="Timeout test")

        assert state["final_response"]["status"] == "CIRCUIT_BREAK"
        assert "PIPELINE_TIMEOUT" in state["final_response"]["failure_reasons"]

    @pytest.mark.asyncio
    async def test_exception_produces_circuit_break(self, mock_ollama):
        """Unexpected exception should produce CIRCUIT_BREAK status."""
        agent = MotherAgent()

        with patch("src.backend.orchestration.mother_agent.build_graph") as mock_bg:
            mock_compiled = AsyncMock()
            mock_compiled.ainvoke = AsyncMock(side_effect=RuntimeError("Unexpected failure"))
            mock_bg.return_value = mock_compiled
            state = await agent.run(query="Exception test")

        assert state["final_response"]["status"] == "CIRCUIT_BREAK"
        assert "INTERNAL_ERROR" in state["final_response"]["failure_reasons"]

    @pytest.mark.asyncio
    async def test_token_tracking(self, mock_ollama):
        """Token usage should be tracked from inference metadata."""
        import os
        with patch.dict(os.environ, {"STUB_VALIDATION_SCORE": "0.85"}):
            agent = MotherAgent()
            state = await agent.run(query="Token test")
        # Pipeline should have inference_metadata with token counts
        metadata = state.get("inference_metadata")
        if metadata:
            assert "prompt_tokens" in metadata
            assert "completion_tokens" in metadata


class TestTokenLedgerEdgeCases:
    def test_never_negative_remaining(self):
        """budget_remaining should never go negative."""
        ledger = TokenLedger(budget_total=100)
        ledger.record("inference", 200)  # Over-spend
        assert ledger.budget_remaining == 0
        assert ledger.budget_used == 200

    def test_cumulative_records(self):
        """Multiple record calls should accumulate."""
        ledger = TokenLedger(budget_total=10000)
        ledger.record("inference", 100)
        ledger.record("critic", 200)
        ledger.record("inference", 300)
        assert ledger.budget_used == 600
        assert ledger.budget_remaining == 9400
        assert len(ledger.entries) == 3


class TestHealthCheckEdgeCases:
    @pytest.mark.asyncio
    async def test_ollama_down_degraded(self, mock_ollama_down):
        """Health check should report degraded when Ollama is unreachable."""
        agent = MotherAgent()
        health = await agent.health_check()
        assert health["status"] == "degraded"
        assert health["ollama_status"] == "disconnected"
        assert health["model_loaded"] is False

    @pytest.mark.asyncio
    async def test_model_not_loaded(self):
        """Health check should report model_loaded=False when model is not in tags."""
        with patch("httpx.AsyncClient") as mock_cls:
            mock_client = AsyncMock()
            mock_resp = AsyncMock()
            mock_resp.status_code = 200
            mock_resp.json = MagicMock(return_value={
                "models": [{"name": "llama3:8b"}]  # Not deepseek
            })
            mock_client.get = AsyncMock(return_value=mock_resp)
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=False)
            mock_cls.return_value = mock_client

            agent = MotherAgent()
            health = await agent.health_check()
            assert health["status"] == "healthy"  # Connected but wrong model
            assert health["model_loaded"] is False
