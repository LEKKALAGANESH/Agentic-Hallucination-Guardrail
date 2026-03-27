"""Extended tests for api.py — API edge cases not covered in test_api_endpoints.py."""

from __future__ import annotations

import asyncio
import json
import os
import re

import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from httpx import AsyncClient, ASGITransport

from src.backend.api import app, _trace_store


@pytest.fixture
async def client(mock_ollama):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


# ---------------------------------------------------------------------------
# TestQueryEdgeCases
# ---------------------------------------------------------------------------


class TestQueryEdgeCases:
    @pytest.mark.asyncio
    async def test_config_overrides(self, client):
        """POST /api/query with config_overrides should accept."""
        resp = await client.post("/api/query", json={
            "query": "What is AI?",
            "config_overrides": {"pass_threshold": 0.8, "max_retries": 5},
        })
        assert resp.status_code == 202
        assert "trace_id" in resp.json()

    @pytest.mark.asyncio
    async def test_session_id(self, client):
        """POST /api/query with session_id should accept."""
        resp = await client.post("/api/query", json={
            "query": "What is AI?",
            "session_id": "sess-test-123",
        })
        assert resp.status_code == 202

    @pytest.mark.asyncio
    async def test_whitespace_only_returns_error(self, client):
        """Whitespace-only query should be rejected."""
        resp = await client.post("/api/query", json={"query": "   "})
        # FastAPI validates min_length=1 on stripped or raw string
        # The endpoint also checks .strip() for empty
        assert resp.status_code in (400, 422)

    @pytest.mark.asyncio
    async def test_long_query_10k_chars(self, client):
        """10K character query should be accepted."""
        long_query = "a" * 10000
        resp = await client.post("/api/query", json={"query": long_query})
        assert resp.status_code == 202

    @pytest.mark.asyncio
    async def test_unicode_query(self, client):
        """Unicode characters in query should be accepted."""
        resp = await client.post("/api/query", json={
            "query": "什么是人工智能？ ¿Qué es la IA? 🤖"
        })
        assert resp.status_code == 202

    @pytest.mark.asyncio
    async def test_special_chars_query(self, client):
        """Special characters should not cause injection or errors."""
        resp = await client.post("/api/query", json={
            "query": 'SELECT * FROM users; DROP TABLE traces; --'
        })
        assert resp.status_code == 202  # Should accept, not execute


# ---------------------------------------------------------------------------
# TestHealthEdgeCases
# ---------------------------------------------------------------------------


class TestHealthEdgeCases:
    @pytest.mark.asyncio
    async def test_ollama_down_degraded(self, mock_ollama_down):
        """Health check with Ollama down should return degraded status."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get("/api/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "degraded"
        assert data["ollama_status"] == "disconnected"

    @pytest.mark.asyncio
    async def test_budget_info_present(self, client):
        """Health response should contain budget info."""
        resp = await client.get("/api/health")
        data = resp.json()
        assert "budget" in data
        budget = data["budget"]
        assert "ceiling" in budget
        assert "consumed" in budget
        assert "remaining" in budget

    @pytest.mark.asyncio
    async def test_uptime_ms(self, client):
        """Health response should have uptime_ms >= 0."""
        resp = await client.get("/api/health")
        data = resp.json()
        assert "uptime_ms" in data
        assert data["uptime_ms"] >= 0


# ---------------------------------------------------------------------------
# TestConfigEdgeCases
# ---------------------------------------------------------------------------


class TestConfigEdgeCases:
    @pytest.mark.asyncio
    async def test_all_expected_keys(self, client):
        """Config endpoint should return all expected configuration keys."""
        resp = await client.get("/api/config")
        data = resp.json()
        expected_keys = {
            "pass_threshold", "max_retries", "temperature_init",
            "temperature_decay", "inference_timeout", "critic_model",
            "enable_toxicity", "token_ceiling",
        }
        assert expected_keys.issubset(set(data.keys()))

    @pytest.mark.asyncio
    async def test_values_match_validation_rules(self, client):
        """Config values should match the validation_rules.json defaults."""
        resp = await client.get("/api/config")
        data = resp.json()
        assert data["pass_threshold"] == 0.7
        assert data["max_retries"] == 3
        assert data["temperature_init"] == 0.7
        assert data["temperature_decay"] == 0.15
        assert data["token_ceiling"] == 8192
        assert data["critic_model"] == "deepseek-r1:latest"


# ---------------------------------------------------------------------------
# TestTraceExtended
# ---------------------------------------------------------------------------


class TestTraceExtended:
    @pytest.mark.asyncio
    async def test_trace_from_memory_store(self, client):
        """Trace from in-memory store should return 200."""
        trace_id = "mem-trace-001"
        _trace_store[trace_id] = {
            "trace_id": trace_id,
            "session_id": "s1",
            "query": "Test query",
            "retry_count": 0,
            "timestamp_start": 1000.0,
            "timestamp_end": 1001.0,
            "metric_breakdown": {"faithfulness": 0.9},
            "correction_history": [],
            "final_response": {
                "status": "VALIDATED",
                "response_text": "Answer",
                "confidence_score": 0.9,
                "model_used": "deepseek-r1:latest",
                "latency_ms": 1000.0,
                "suggestion": None,
            },
        }

        resp = await client.get(f"/api/traces/{trace_id}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["trace_id"] == trace_id

        # Cleanup
        _trace_store.pop(trace_id, None)

    @pytest.mark.asyncio
    async def test_response_structure(self, client):
        """Trace response should have all expected fields."""
        trace_id = "struct-trace-001"
        _trace_store[trace_id] = {
            "trace_id": trace_id,
            "session_id": None,
            "query": "Test",
            "retry_count": 1,
            "timestamp_start": 1000.0,
            "timestamp_end": 1500.0,
            "metric_breakdown": None,
            "correction_history": [],
            "final_response": {
                "status": "CIRCUIT_BREAK",
                "response_text": "Fallback",
                "confidence_score": 0.0,
                "model_used": "none",
                "latency_ms": 500.0,
                "suggestion": "Try again.",
            },
        }

        resp = await client.get(f"/api/traces/{trace_id}")
        data = resp.json()
        expected_fields = {
            "trace_id", "query", "status", "retry_count",
            "confidence_score", "final_response",
        }
        assert expected_fields.issubset(set(data.keys()))

        _trace_store.pop(trace_id, None)

    @pytest.mark.asyncio
    async def test_uuid_format(self, client):
        """Trace IDs from POST /api/query should be valid UUID format."""
        resp = await client.post("/api/query", json={"query": "What is AI?"})
        trace_id = resp.json()["trace_id"]
        uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
        assert re.match(uuid_pattern, trace_id)

    @pytest.mark.asyncio
    async def test_query_text_match(self, client):
        """Trace should preserve the original query text."""
        trace_id = "qt-trace-001"
        query_text = "What is the meaning of life?"
        _trace_store[trace_id] = {
            "trace_id": trace_id,
            "session_id": None,
            "query": query_text,
            "retry_count": 0,
            "timestamp_start": 1000.0,
            "timestamp_end": 1001.0,
            "metric_breakdown": None,
            "correction_history": [],
            "final_response": {
                "status": "VALIDATED",
                "response_text": "42",
                "confidence_score": 0.95,
                "model_used": "deepseek-r1:latest",
                "latency_ms": 100.0,
                "suggestion": None,
            },
        }

        resp = await client.get(f"/api/traces/{trace_id}")
        data = resp.json()
        assert data["query"] == query_text

        _trace_store.pop(trace_id, None)
