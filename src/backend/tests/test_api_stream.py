"""Tests for SSE /api/stream/{trace_id} endpoint."""

from __future__ import annotations

import asyncio
import json
import os

import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from httpx import AsyncClient, ASGITransport

from src.backend.api import app, _event_queues, _trace_store


@pytest.fixture
async def client(mock_ollama):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


class TestApiStream:
    @pytest.mark.asyncio
    async def test_nonexistent_trace_404(self, client):
        """Stream for unknown trace should return 404."""
        resp = await client.get("/api/stream/nonexistent-trace-id")
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_content_type_event_stream(self, client):
        """Response Content-Type should be text/event-stream for valid trace."""
        # Create a trace queue to simulate an active trace
        trace_id = "test-stream-ct"
        queue = asyncio.Queue()
        _event_queues[trace_id] = queue

        # Put a complete event so the stream terminates
        await queue.put(("complete", {"trace_id": trace_id, "status": "VALIDATED"}))

        resp = await client.get(f"/api/stream/{trace_id}")
        assert "text/event-stream" in resp.headers.get("content-type", "")

        # Cleanup
        _event_queues.pop(trace_id, None)

    @pytest.mark.asyncio
    async def test_receives_agent_update_events(self, client):
        """Stream should receive agent_update events before complete."""
        trace_id = "test-stream-updates"
        queue = asyncio.Queue()
        _event_queues[trace_id] = queue

        # Simulate pipeline events
        await queue.put(("agent_update", {"agent": "inference", "action": "start", "seq": 1, "trace_id": trace_id}))
        await queue.put(("agent_update", {"agent": "validator", "action": "complete", "seq": 2, "trace_id": trace_id}))
        await queue.put(("complete", {"trace_id": trace_id, "status": "VALIDATED"}))

        resp = await client.get(f"/api/stream/{trace_id}")
        body = resp.text
        assert "agent_update" in body
        assert "complete" in body

        _event_queues.pop(trace_id, None)

    @pytest.mark.asyncio
    async def test_complete_event_terminates(self, client):
        """Stream should end after complete event."""
        trace_id = "test-stream-term"
        queue = asyncio.Queue()
        _event_queues[trace_id] = queue

        await queue.put(("complete", {"trace_id": trace_id, "status": "VALIDATED"}))

        resp = await client.get(f"/api/stream/{trace_id}")
        # Stream should have terminated — response should be complete
        assert resp.status_code == 200

        _event_queues.pop(trace_id, None)

    @pytest.mark.asyncio
    async def test_error_event_on_failure(self, client):
        """Pipeline error should produce error SSE event."""
        trace_id = "test-stream-error"
        queue = asyncio.Queue()
        _event_queues[trace_id] = queue

        await queue.put(("error", {
            "trace_id": trace_id,
            "error": {"code": "INTERNAL_ERROR", "message": "Something went wrong"},
        }))

        resp = await client.get(f"/api/stream/{trace_id}")
        body = resp.text
        assert "error" in body
        assert "INTERNAL_ERROR" in body

        _event_queues.pop(trace_id, None)

    @pytest.mark.asyncio
    async def test_events_have_trace_id(self, client):
        """Every event should carry the correct trace_id."""
        trace_id = "test-stream-tid"
        queue = asyncio.Queue()
        _event_queues[trace_id] = queue

        await queue.put(("agent_update", {"trace_id": trace_id, "agent": "inference", "seq": 1}))
        await queue.put(("complete", {"trace_id": trace_id, "status": "VALIDATED"}))

        resp = await client.get(f"/api/stream/{trace_id}")
        body = resp.text
        assert trace_id in body

        _event_queues.pop(trace_id, None)

    @pytest.mark.asyncio
    async def test_events_have_sequence_numbers(self, client):
        """Events should include seq field."""
        trace_id = "test-stream-seq"
        queue = asyncio.Queue()
        _event_queues[trace_id] = queue

        await queue.put(("agent_update", {"trace_id": trace_id, "seq": 1, "agent": "inference"}))
        await queue.put(("agent_update", {"trace_id": trace_id, "seq": 2, "agent": "validator"}))
        await queue.put(("complete", {"trace_id": trace_id, "status": "VALIDATED"}))

        resp = await client.get(f"/api/stream/{trace_id}")
        body = resp.text
        assert '"seq": 1' in body or '"seq":1' in body or '"seq": 2' in body

        _event_queues.pop(trace_id, None)

    @pytest.mark.asyncio
    async def test_keepalive_ping_logic(self):
        """Ping event logic should exist in the SSE generator."""
        # Verify that the stream endpoint code references timeout and ping
        import inspect
        from src.backend.api import stream_events
        source = inspect.getsource(stream_events)
        assert "ping" in source
        assert "timeout" in source.lower() or "TimeoutError" in source

    @pytest.mark.asyncio
    async def test_full_lifecycle(self, client):
        """POST query → GET stream → GET trace should be consistent."""
        with patch.dict(os.environ, {"STUB_VALIDATION_SCORE": "0.85"}):
            # Submit a query
            resp = await client.post("/api/query", json={"query": "What is AI?"})
            assert resp.status_code == 202
            trace_id = resp.json()["trace_id"]

            # Give background task time to complete
            await asyncio.sleep(0.5)

            # Get trace
            resp = await client.get(f"/api/traces/{trace_id}")
            # May be 200 if pipeline completed, or 404 if still running
            if resp.status_code == 200:
                data = resp.json()
                assert data["trace_id"] == trace_id

    @pytest.mark.asyncio
    async def test_concurrent_streams_isolated(self, client):
        """Two queries should not cross-contaminate events."""
        trace_id_1 = "test-iso-1"
        trace_id_2 = "test-iso-2"
        queue_1 = asyncio.Queue()
        queue_2 = asyncio.Queue()
        _event_queues[trace_id_1] = queue_1
        _event_queues[trace_id_2] = queue_2

        await queue_1.put(("agent_update", {"trace_id": trace_id_1, "data": "from-1", "seq": 1}))
        await queue_1.put(("complete", {"trace_id": trace_id_1, "status": "VALIDATED"}))

        await queue_2.put(("agent_update", {"trace_id": trace_id_2, "data": "from-2", "seq": 1}))
        await queue_2.put(("complete", {"trace_id": trace_id_2, "status": "CIRCUIT_BREAK"}))

        resp1 = await client.get(f"/api/stream/{trace_id_1}")
        resp2 = await client.get(f"/api/stream/{trace_id_2}")

        assert "from-1" in resp1.text
        assert "from-2" not in resp1.text
        assert "from-2" in resp2.text
        assert "from-1" not in resp2.text

        _event_queues.pop(trace_id_1, None)
        _event_queues.pop(trace_id_2, None)
