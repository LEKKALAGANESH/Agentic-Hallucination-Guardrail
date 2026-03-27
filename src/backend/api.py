"""
FastAPI application — 5 endpoints for the Agentic Hallucination Guardrail.

POST /api/query       → 202 Accepted, launches pipeline as background task
GET  /api/stream/{id} → SSE stream of agent events
GET  /api/health      → System health status
GET  /api/config      → Active configuration
GET  /api/traces/{id} → Stored trace data
"""

from __future__ import annotations

import asyncio
import logging
import time
import uuid
from contextlib import asynccontextmanager
from typing import Any

from fastapi import BackgroundTasks, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from sse_starlette.sse import EventSourceResponse

from src.backend.db.database import get_trace, init_db, save_trace
from src.backend.orchestration.mother_agent import MotherAgent

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Application state (module-level singletons)
# ---------------------------------------------------------------------------

_agent: MotherAgent | None = None
_event_queues: dict[str, asyncio.Queue] = {}
_trace_store: dict[str, dict[str, Any]] = {}  # In-memory trace cache


def _get_agent() -> MotherAgent:
    global _agent
    if _agent is None:
        _agent = MotherAgent()
    return _agent


# ---------------------------------------------------------------------------
# Lifespan
# ---------------------------------------------------------------------------


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database and mother agent on startup."""
    global _agent
    await init_db()
    _agent = MotherAgent()
    logger.info("Application started")
    yield
    logger.info("Application shutting down")


# ---------------------------------------------------------------------------
# FastAPI App
# ---------------------------------------------------------------------------

app = FastAPI(
    title="Agentic Hallucination Guardrail",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Request / Response Models
# ---------------------------------------------------------------------------


class ConfigOverrides(BaseModel):
    pass_threshold: float | None = None
    max_retries: int | None = None
    temperature_init: float | None = None


class QueryRequest(BaseModel):
    query: str = Field(..., min_length=1, description="The user question")
    session_id: str | None = None
    config_overrides: ConfigOverrides | None = None


class QueryAccepted(BaseModel):
    trace_id: str
    status: str = "ACCEPTED"


class ErrorDetail(BaseModel):
    code: str
    message: str
    trace_id: str | None = None


class ErrorResponse(BaseModel):
    error: ErrorDetail


# ---------------------------------------------------------------------------
# Background pipeline runner
# ---------------------------------------------------------------------------


async def _run_pipeline(trace_id: str, request: QueryRequest) -> None:
    """Execute the guardrail pipeline and push events to the SSE queue."""
    agent = _get_agent()
    queue = _event_queues.get(trace_id)
    seq = 0

    async def event_callback(event: dict[str, Any]) -> None:
        nonlocal seq
        seq += 1
        event["seq"] = seq
        event["trace_id"] = trace_id
        if "timestamp" not in event:
            event["timestamp"] = time.time()
        if queue:
            await queue.put(("agent_update", event))

    try:
        overrides = {}
        if request.config_overrides:
            overrides = request.config_overrides.model_dump(exclude_none=True)

        state = await agent.run(
            query=request.query,
            session_id=request.session_id,
            config_overrides=overrides or None,
            event_callback=event_callback,
        )

        # Store trace
        _trace_store[trace_id] = state
        try:
            await save_trace(state)
        except Exception:
            logger.debug("Failed to persist trace %s to DB", trace_id, exc_info=True)

        # Emit terminal event
        final = state.get("final_response") or {}
        if queue:
            await queue.put((
                "complete",
                {
                    "trace_id": trace_id,
                    "final_response": final.get("response_text", ""),
                    "confidence_score": final.get("confidence_score"),
                    "retry_count": state.get("retry_count", 0),
                    "status": final.get("status", "unknown"),
                    "model_used": final.get("model_used", "unknown"),
                },
            ))

    except Exception as exc:
        logger.exception("Pipeline failed for trace %s", trace_id)
        if queue:
            await queue.put((
                "error",
                {
                    "trace_id": trace_id,
                    "error": {
                        "code": "INTERNAL_ERROR",
                        "message": str(exc),
                    },
                },
            ))


# ---------------------------------------------------------------------------
# Endpoint 1: POST /api/query
# ---------------------------------------------------------------------------


@app.post(
    "/api/query",
    response_model=QueryAccepted,
    status_code=202,
    responses={400: {"model": ErrorResponse}},
)
async def submit_query(request: QueryRequest, background_tasks: BackgroundTasks):
    """Submit a query for processing. Returns immediately with a trace_id."""
    if not request.query.strip():
        return JSONResponse(
            status_code=400,
            content={
                "error": {
                    "code": "QUERY_EMPTY",
                    "message": "The query field is missing or blank.",
                    "trace_id": None,
                }
            },
        )

    trace_id = str(uuid.uuid4())
    _event_queues[trace_id] = asyncio.Queue()

    background_tasks.add_task(_run_pipeline, trace_id, request)

    return QueryAccepted(trace_id=trace_id)


# ---------------------------------------------------------------------------
# Endpoint 2: GET /api/stream/{trace_id}
# ---------------------------------------------------------------------------


@app.get("/api/stream/{trace_id}")
async def stream_events(trace_id: str, request: Request):
    """SSE stream of agent events for a given trace."""

    queue = _event_queues.get(trace_id)
    if queue is None:
        raise HTTPException(
            status_code=404,
            detail={
                "error": {
                    "code": "TRACE_NOT_FOUND",
                    "message": f"No active trace with id {trace_id}",
                }
            },
        )

    async def event_generator():
        import json

        while True:
            if await request.is_disconnected():
                break
            try:
                event_type, data = await asyncio.wait_for(queue.get(), timeout=30.0)
                yield {
                    "event": event_type,
                    "data": json.dumps(data, default=str),
                }
                if event_type in ("complete", "error"):
                    break
            except asyncio.TimeoutError:
                # Send keepalive
                yield {"event": "ping", "data": "{}"}

    return EventSourceResponse(event_generator())


# ---------------------------------------------------------------------------
# Endpoint 3: GET /api/health
# ---------------------------------------------------------------------------


@app.get("/api/health")
async def health_check():
    """Return operational status of the system."""
    agent = _get_agent()
    status = await agent.health_check()
    return status


# ---------------------------------------------------------------------------
# Endpoint 4: GET /api/config
# ---------------------------------------------------------------------------


@app.get("/api/config")
async def get_config():
    """Return the active system configuration."""
    agent = _get_agent()
    return agent.get_config()


# ---------------------------------------------------------------------------
# Endpoint 5: GET /api/traces/{trace_id}
# ---------------------------------------------------------------------------


@app.get(
    "/api/traces/{trace_id}",
    responses={404: {"model": ErrorResponse}},
)
async def get_trace_endpoint(trace_id: str):
    """Retrieve the full trace for a completed query."""
    # Check in-memory store first
    if trace_id in _trace_store:
        state = _trace_store[trace_id]
        final = state.get("final_response") or {}
        return {
            "trace_id": trace_id,
            "session_id": state.get("session_id"),
            "query": state.get("query", ""),
            "status": final.get("status", "unknown"),
            "model_used": final.get("model_used", "unknown"),
            "created_at": state.get("timestamp_start"),
            "completed_at": state.get("timestamp_end"),
            "total_latency_ms": final.get("latency_ms"),
            "retry_count": state.get("retry_count", 0),
            "confidence_score": final.get("confidence_score"),
            "metric_breakdown": state.get("metric_breakdown"),
            "correction_history": state.get("correction_history", []),
            "final_response": final.get("response_text", ""),
            "suggestion": final.get("suggestion"),
        }

    # Check database
    db_trace = await get_trace(trace_id)
    if db_trace is not None:
        return db_trace

    return JSONResponse(
        status_code=404,
        content={
            "error": {
                "code": "TRACE_NOT_FOUND",
                "message": f"No trace exists with id {trace_id}",
                "trace_id": trace_id,
            }
        },
    )
