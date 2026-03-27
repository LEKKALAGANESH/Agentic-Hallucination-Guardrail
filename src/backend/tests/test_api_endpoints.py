"""Tests for api.py — FastAPI endpoint validation."""

from __future__ import annotations

import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from httpx import AsyncClient, ASGITransport

from src.backend.api import app


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture
async def client(mock_ollama):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


class TestPostQuery:
    @pytest.mark.asyncio
    async def test_returns_202_accepted(self, client):
        resp = await client.post("/api/query", json={"query": "What is AI?"})
        assert resp.status_code == 202
        data = resp.json()
        assert "trace_id" in data
        assert data["status"] == "ACCEPTED"

    @pytest.mark.asyncio
    async def test_empty_query_returns_400(self, client):
        resp = await client.post("/api/query", json={"query": ""})
        assert resp.status_code == 422 or resp.status_code == 400

    @pytest.mark.asyncio
    async def test_missing_query_returns_422(self, client):
        resp = await client.post("/api/query", json={})
        assert resp.status_code == 422


class TestGetHealth:
    @pytest.mark.asyncio
    async def test_returns_valid_json(self, client):
        resp = await client.get("/api/health")
        assert resp.status_code == 200
        data = resp.json()
        assert "status" in data
        assert "agents" in data
        assert "version" in data


class TestGetConfig:
    @pytest.mark.asyncio
    async def test_returns_config(self, client):
        resp = await client.get("/api/config")
        assert resp.status_code == 200
        data = resp.json()
        assert "pass_threshold" in data
        assert "max_retries" in data
        assert data["pass_threshold"] == 0.7


class TestGetTrace:
    @pytest.mark.asyncio
    async def test_nonexistent_trace_returns_404(self, client):
        resp = await client.get("/api/traces/nonexistent-id")
        assert resp.status_code == 404
        data = resp.json()
        assert data["error"]["code"] == "TRACE_NOT_FOUND"
