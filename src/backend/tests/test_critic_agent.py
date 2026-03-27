"""Tests for agents/critic_agent.py — rule-based critique and health check."""

from __future__ import annotations

import os
import pytest
from unittest.mock import AsyncMock, patch, MagicMock

import httpx

from src.backend.agents.critic_agent import CriticAgent, CritiqueResult


# ---------------------------------------------------------------------------
# TestCriticInit
# ---------------------------------------------------------------------------


class TestCriticInit:
    def test_default_init(self):
        """CriticAgent should initialize with default model and URL."""
        agent = CriticAgent()
        assert agent.model_name == "deepseek-r1:latest"
        assert "localhost" in agent.ollama_url
        assert agent.timeout == 30.0

    def test_custom_params(self):
        """CriticAgent should accept custom model, URL, and timeout."""
        agent = CriticAgent(
            model_name="llama3:8b",
            ollama_url="http://custom:11434",
            timeout=10.0,
        )
        assert agent.model_name == "llama3:8b"
        assert agent.ollama_url == "http://custom:11434"
        assert agent.timeout == 10.0

    def test_ollama_host_env_var(self):
        """Should use OLLAMA_HOST env var when no URL is provided."""
        with patch.dict(os.environ, {"OLLAMA_HOST": "http://remote:11434"}):
            # Re-import to pick up env var
            from importlib import reload
            import src.backend.agents.critic_agent as mod
            reload(mod)
            agent = mod.CriticAgent()
            assert agent.ollama_url == "http://remote:11434"


# ---------------------------------------------------------------------------
# TestCritique
# ---------------------------------------------------------------------------


class TestCritique:
    @pytest.mark.asyncio
    async def test_accept_verdict_for_good_response(self):
        """A well-grounded response should get ACCEPT verdict."""
        agent = CriticAgent()
        result = await agent.critique(
            response="Refunds are available within 30 days of purchase.",
            context_docs=["Refunds are available within 30 days of purchase."],
            query="What is the refund policy?",
        )
        assert result["verdict"] == "ACCEPT"
        assert result["confidence"] == 0.85

    @pytest.mark.asyncio
    async def test_partial_verdict_for_ungrounded(self):
        """Response not grounded in context should get PARTIAL (one issue)."""
        agent = CriticAgent()
        result = await agent.critique(
            response="The refund policy allows returns within 60 days with full credit.",
            context_docs=["Refunds are available within 30 days of purchase."],
            query="What is the refund policy?",
        )
        assert result["verdict"] == "PARTIAL"
        assert result["confidence"] == 0.60

    @pytest.mark.asyncio
    async def test_reject_verdict_for_short_and_ungrounded(self):
        """Short AND ungrounded response should get REJECT (two issues)."""
        agent = CriticAgent()
        result = await agent.critique(
            response="No.",
            context_docs=["Refunds are available within 30 days of purchase."],
            query="What is the refund policy?",
        )
        assert result["verdict"] == "REJECT"
        assert result["confidence"] == 0.30

    @pytest.mark.asyncio
    async def test_empty_response(self):
        """Empty response should have 'too short or empty' issue."""
        agent = CriticAgent()
        result = await agent.critique(response="", context_docs=[], query="test")
        assert result["verdict"] in ("PARTIAL", "REJECT")
        assert any("short" in i.lower() or "empty" in i.lower() for i in result["issues_found"])

    @pytest.mark.asyncio
    async def test_short_response(self):
        """Response under 10 chars should flag as too short."""
        agent = CriticAgent()
        result = await agent.critique(response="Yes", context_docs=None, query="test")
        assert any("short" in i.lower() for i in result["issues_found"])

    @pytest.mark.asyncio
    async def test_ungrounded_response_flagged(self):
        """Response not containing any context fragment should flag as ungrounded."""
        agent = CriticAgent()
        result = await agent.critique(
            response="This is a completely unrelated answer about quantum physics and string theory.",
            context_docs=["The company was founded in 2020 in San Francisco."],
            query="When was the company founded?",
        )
        assert any("grounded" in i.lower() for i in result["issues_found"])

    @pytest.mark.asyncio
    async def test_case_insensitive_matching(self):
        """Context matching should be case-insensitive."""
        agent = CriticAgent()
        result = await agent.critique(
            response="REFUNDS ARE AVAILABLE within 30 days of purchase for all customers.",
            context_docs=["refunds are available within 30 days of purchase"],
            query="What is the refund policy?",
        )
        assert result["verdict"] == "ACCEPT"

    @pytest.mark.asyncio
    async def test_none_context_docs(self):
        """None context_docs should not cause errors."""
        agent = CriticAgent()
        result = await agent.critique(
            response="This is a valid long response about the topic at hand.",
            context_docs=None,
            query="test",
        )
        # No grounding check when context_docs is None
        assert result["verdict"] == "ACCEPT"

    @pytest.mark.asyncio
    async def test_empty_context_docs(self):
        """Empty context_docs list should not cause errors."""
        agent = CriticAgent()
        result = await agent.critique(
            response="This is a valid long response about the topic at hand.",
            context_docs=[],
            query="test",
        )
        assert result["verdict"] == "ACCEPT"

    @pytest.mark.asyncio
    async def test_short_fragments_skipped(self):
        """Context fragments <= 5 chars should be skipped in matching."""
        agent = CriticAgent()
        result = await agent.critique(
            response="This response talks about something completely different from the sources.",
            context_docs=["Hi", "No", "The company was founded in San Francisco"],
            query="test",
        )
        # Only the long fragment matters, and it's not in the response
        assert any("grounded" in i.lower() for i in result["issues_found"])

    @pytest.mark.asyncio
    async def test_critique_result_structure(self):
        """CritiqueResult should have all expected fields."""
        agent = CriticAgent()
        result = await agent.critique(
            response="A sufficiently long response for testing structure.",
            context_docs=None,
            query="test",
        )
        assert "verdict" in result
        assert "confidence" in result
        assert "factual_accuracy" in result
        assert "grounding_score" in result
        assert "completeness" in result
        assert "issues_found" in result
        assert "suggested_corrections" in result

    @pytest.mark.asyncio
    async def test_derived_scores(self):
        """Derived scores should be proportional to confidence."""
        agent = CriticAgent()
        result = await agent.critique(
            response="A sufficiently long response for testing derived scores.",
            context_docs=None,
            query="test",
        )
        confidence = result["confidence"]
        assert result["factual_accuracy"] == confidence
        assert result["grounding_score"] == pytest.approx(confidence * 0.9)
        assert result["completeness"] == pytest.approx(confidence * 0.95)


# ---------------------------------------------------------------------------
# TestCriticHealthCheck
# ---------------------------------------------------------------------------


class TestCriticHealthCheck:
    @pytest.mark.asyncio
    async def test_model_loaded(self, mock_ollama):
        """Health check should report model_loaded=True when model is present."""
        agent = CriticAgent()
        result = await agent.health_check()
        assert result["status"] == "ok"
        assert result["model_loaded"] is True

    @pytest.mark.asyncio
    async def test_model_not_found(self):
        """Health check should report model_loaded=False when model is absent."""
        with patch("httpx.AsyncClient") as mock_cls:
            mock_client = AsyncMock()
            mock_resp = AsyncMock()
            mock_resp.status_code = 200
            mock_resp.json = MagicMock(return_value={
                "models": [{"name": "llama3:8b"}]
            })
            mock_client.get = AsyncMock(return_value=mock_resp)
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=False)
            mock_cls.return_value = mock_client

            agent = CriticAgent()
            result = await agent.health_check()
            assert result["status"] == "ok"
            assert result["model_loaded"] is False

    @pytest.mark.asyncio
    async def test_connection_error(self, mock_ollama_down):
        """Health check should report error status when Ollama is down."""
        agent = CriticAgent()
        result = await agent.health_check()
        assert result["status"] == "error"
        assert result["model_loaded"] is False

    @pytest.mark.asyncio
    async def test_http_500(self):
        """Health check should handle HTTP 500 from Ollama."""
        with patch("httpx.AsyncClient") as mock_cls:
            mock_client = AsyncMock()
            mock_resp = AsyncMock()
            mock_resp.status_code = 500
            mock_client.get = AsyncMock(return_value=mock_resp)
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=False)
            mock_cls.return_value = mock_client

            agent = CriticAgent()
            result = await agent.health_check()
            assert result["status"] == "error"

    @pytest.mark.asyncio
    async def test_prefix_matching(self, mock_ollama):
        """Model matching should use prefix (deepseek matches deepseek-r1:latest)."""
        agent = CriticAgent(model_name="deepseek-r1:latest")
        result = await agent.health_check()
        assert result["model_loaded"] is True
