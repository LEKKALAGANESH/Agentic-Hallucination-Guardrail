"""Shared test fixtures for the backend test suite."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest
from unittest.mock import AsyncMock, patch, MagicMock

import httpx


@pytest.fixture
def mock_ollama():
    """Patch httpx.AsyncClient to serve canned Ollama responses."""
    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.json = MagicMock(return_value={
        "model": "deepseek-r1:latest",
        "response": "Canned validated answer for testing purposes.",
        "done": True,
        "prompt_eval_count": 50,
        "eval_count": 100,
    })
    mock_response.raise_for_status = MagicMock()

    with patch("httpx.AsyncClient") as mock_client_class:
        mock_client = AsyncMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client.get = AsyncMock(return_value=AsyncMock(
            status_code=200,
            json=MagicMock(return_value={"models": [{"name": "deepseek-r1:latest"}]}),
        ))
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client_class.return_value = mock_client
        yield mock_client


@pytest.fixture
def sample_state():
    """Baseline GuardrailState dict for graph engine tests."""
    return {
        "query": "What is the refund policy?",
        "context": "Refunds are available within 30 days of purchase.",
        "trace_id": "test-trace-001",
        "session_id": None,
        "config": {
            "pass_threshold": 0.7,
            "max_retries": 3,
            "temperature_init": 0.7,
            "temperature_decay": 0.15,
            "inference_timeout": 60000,
            "critic_timeout": 30000,
            "critic_model": "deepseek-r1:latest",
            "enable_toxicity": True,
            "token_ceiling": 8192,
            "heartbeat_interval": 1000,
        },
        "temperature": 0.7,
        "retry_count": 0,
        "validation_score": None,
        "validation_flags": [],
        "correction_history": [],
        "raw_response": None,
        "corrected_prompt": None,
        "is_stub": False,
        "final_response": None,
        "schema_version": 1,
        "_budget_callback": None,
        "_event_callback": None,
    }


@pytest.fixture
def compiled_graph(mock_ollama):
    """Return a compiled LangGraph wired to mock Ollama."""
    from src.backend.orchestration.graph_engine import build_graph
    return build_graph()


@pytest.fixture
def tmp_db_path(tmp_path):
    """Provide a temporary SQLite path with initialized schema."""
    import asyncio
    from src.backend.db.database import init_db

    db_path = tmp_path / "test_traces.db"
    asyncio.get_event_loop().run_until_complete(init_db(db_path))
    return db_path


@pytest.fixture
def golden_test_set():
    """Load the golden 100 test set from fixtures."""
    fixture_path = Path(__file__).parent / "fixtures" / "golden_100.json"
    with open(fixture_path) as f:
        return json.load(f)


@pytest.fixture
def mock_ollama_down():
    """Patch httpx to raise ConnectError, simulating Ollama being unavailable."""
    with patch("httpx.AsyncClient") as mock_client_class:
        mock_client = AsyncMock()
        mock_client.post = AsyncMock(side_effect=httpx.ConnectError("Connection refused"))
        mock_client.get = AsyncMock(side_effect=httpx.ConnectError("Connection refused"))
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client_class.return_value = mock_client
        yield mock_client


@pytest.fixture
def event_collector():
    """Async callable + list for event callback testing."""
    events: list = []

    async def collector(event: dict) -> None:
        events.append(event)

    collector.events = events
    return collector
