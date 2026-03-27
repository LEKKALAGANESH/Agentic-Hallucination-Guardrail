"""
Mother Agent — top-level orchestrator for the hallucination guardrail pipeline.

Manages the lifecycle of each query: initializes state, enforces token budget,
invokes the LangGraph pipeline, and returns the final result. Event callbacks
are passed per-invocation to isolate concurrent queries.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, TypedDict

import httpx

from src.backend.orchestration.graph_engine import (
    DEFAULT_CONFIG,
    ConfigSlice,
    GuardrailState,
    build_graph,
    compute_state_hash,
)

logger = logging.getLogger(__name__)

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
_CONFIG_PATH = Path(__file__).resolve().parent.parent / "config" / "validation_rules.json"


# ---------------------------------------------------------------------------
# Token Ledger
# ---------------------------------------------------------------------------


@dataclass
class TokenLedgerEntry:
    agent: str
    tokens: int
    timestamp: float


@dataclass
class TokenLedger:
    budget_total: int = 8192
    budget_used: int = 0
    entries: list[TokenLedgerEntry] = field(default_factory=list)

    @property
    def budget_remaining(self) -> int:
        return max(self.budget_total - self.budget_used, 0)

    def record(self, agent: str, tokens: int) -> None:
        self.budget_used += tokens
        self.entries.append(TokenLedgerEntry(agent=agent, tokens=tokens, timestamp=time.time()))

    def can_afford(self, projected: int) -> bool:
        return self.budget_remaining >= projected


# ---------------------------------------------------------------------------
# Health Status
# ---------------------------------------------------------------------------


class AgentStatuses(TypedDict, total=False):
    mother_agent: str
    inference: str
    validator: str
    corrector: str
    critic: str
    ux_renderer: str


class BudgetStatus(TypedDict):
    ceiling: int
    consumed: int
    remaining: int


class HealthStatus(TypedDict):
    status: str  # "healthy" | "degraded" | "unhealthy"
    agents: AgentStatuses
    budget: BudgetStatus
    uptime_ms: float
    version: str
    ollama_status: str  # "connected" | "disconnected"
    model_loaded: bool


# ---------------------------------------------------------------------------
# Mother Agent
# ---------------------------------------------------------------------------


class MotherAgent:
    """
    Top-level orchestrator. Stateless between queries — each `run()` call
    produces an independent pipeline execution.
    """

    def __init__(self, config: dict[str, Any] | None = None) -> None:
        self._rules = self._load_rules()
        self._config: dict[str, Any] = {**DEFAULT_CONFIG}
        if config:
            self._config.update(config)

        self._start_time = time.monotonic()
        self._version = "0.1.0"

        # Build graph with injected budget callback
        # Event callback is set per-invocation in run()
        self._graph = build_graph(budget_callback=None, event_callback=None)

    @staticmethod
    def _load_rules() -> dict[str, Any]:
        with open(_CONFIG_PATH) as f:
            return json.load(f)

    # -------------------------------------------------------------------
    # Primary entry point
    # -------------------------------------------------------------------

    async def run(
        self,
        query: str,
        session_id: str | None = None,
        config_overrides: dict[str, Any] | None = None,
        event_callback: Callable[..., Any] | None = None,
    ) -> GuardrailState:
        """
        Execute the full guardrail pipeline for a single query.

        Args:
            query: The user's natural-language question.
            session_id: Optional session grouping key.
            config_overrides: Per-query config overrides.
            event_callback: Async callable that receives event dicts.

        Returns:
            The final GuardrailState after pipeline completion.
        """
        # Merge config
        run_config: ConfigSlice = {**self._config}
        if config_overrides:
            for key in ("pass_threshold", "max_retries", "temperature_init", "token_ceiling"):
                if key in config_overrides and config_overrides[key] is not None:
                    run_config[key] = config_overrides[key]  # type: ignore[literal-required]

        # Initialize ledger for this run
        ledger = TokenLedger(budget_total=run_config.get("token_ceiling", 8192))

        # Build budget callback that captures this run's ledger
        async def budget_callback(state: GuardrailState) -> bool:
            return await self.enforce_budget(state, ledger)

        # Rebuild graph with per-run callbacks
        graph = build_graph(
            budget_callback=budget_callback,
            event_callback=event_callback,
        )

        trace_id = str(uuid.uuid4())

        # Initial state
        initial_state: GuardrailState = {
            "trace_id": trace_id,
            "session_id": session_id,
            "query": query,
            "config": run_config,
            "context": None,
            "conversation_history": [],
            "raw_response": None,
            "corrected_prompt": None,
            "temperature": run_config.get("temperature_init", 0.7),
            "inference_metadata": None,
            "validation_score": None,
            "validation_flags": [],
            "validation_details": None,
            "metric_breakdown": None,
            "retry_count": 0,
            "correction_history": [],
            "critic_output": None,
            "final_response": None,
            "schema_version": 1,
            "_budget_callback": budget_callback,
            "_event_callback": event_callback,
        }

        # Emit start event
        if event_callback:
            try:
                await event_callback({
                    "agent": "mother_agent",
                    "action": "pipeline_start",
                    "trace_id": trace_id,
                    "timestamp": time.time(),
                })
            except Exception:
                logger.debug("Event callback failed on start", exc_info=True)

        # Run pipeline with timeout
        pipeline_timeout = self._rules.get("timeout", {}).get(
            "total_pipeline_timeout_seconds", 120
        )

        try:
            final_state = await asyncio.wait_for(
                graph.ainvoke(initial_state),
                timeout=pipeline_timeout,
            )
        except asyncio.TimeoutError:
            logger.error("Pipeline timeout after %ds for trace %s", pipeline_timeout, trace_id)
            final_state = {
                **initial_state,
                "final_response": {
                    "response_text": (
                        "The processing pipeline timed out. "
                        "Please try a simpler question."
                    ),
                    "confidence_score": 0.0,
                    "metric_breakdown": None,
                    "retry_count": initial_state.get("retry_count", 0),
                    "trace_id": trace_id,
                    "model_used": "none",
                    "latency_ms": pipeline_timeout * 1000,
                    "status": "CIRCUIT_BREAK",
                    "failure_reasons": ["PIPELINE_TIMEOUT"],
                    "suggestion": "Try a simpler question.",
                },
                "timestamp_end": time.time(),
            }

        except Exception as exc:
            logger.exception("Pipeline error for trace %s", trace_id)
            final_state = {
                **initial_state,
                "final_response": {
                    "response_text": f"An internal error occurred: {exc}",
                    "confidence_score": 0.0,
                    "metric_breakdown": None,
                    "retry_count": initial_state.get("retry_count", 0),
                    "trace_id": trace_id,
                    "model_used": "none",
                    "latency_ms": 0.0,
                    "status": "CIRCUIT_BREAK",
                    "failure_reasons": ["INTERNAL_ERROR"],
                    "suggestion": "Please try again.",
                },
                "timestamp_end": time.time(),
            }

        # Emit completion event
        if event_callback:
            try:
                fr = final_state.get("final_response") or {}
                await event_callback({
                    "agent": "mother_agent",
                    "action": "pipeline_complete",
                    "trace_id": trace_id,
                    "timestamp": time.time(),
                    "status": fr.get("status", "UNKNOWN"),
                })
            except Exception:
                logger.debug("Event callback failed on complete", exc_info=True)

        # Track token usage from inference metadata
        metadata = final_state.get("inference_metadata")
        if metadata:
            total_tokens = metadata.get("prompt_tokens", 0) + metadata.get(
                "completion_tokens", 0
            )
            ledger.record("inference", total_tokens)

        return final_state

    # -------------------------------------------------------------------
    # Budget enforcement
    # -------------------------------------------------------------------

    async def enforce_budget(
        self, state: GuardrailState, ledger: TokenLedger | None = None
    ) -> bool:
        """
        Check whether the budget allows the next LLM call.
        Returns True if allowed, False to halt.
        """
        if ledger is None:
            return True

        # Estimate next call cost (rough: 500 tokens for a typical inference)
        projected = 500
        if not ledger.can_afford(projected):
            logger.warning(
                "Budget exceeded: used=%d, remaining=%d, projected=%d",
                ledger.budget_used,
                ledger.budget_remaining,
                projected,
            )
            return False
        return True

    # -------------------------------------------------------------------
    # Health check
    # -------------------------------------------------------------------

    async def health_check(self) -> HealthStatus:
        """Return system health status including Ollama connectivity."""
        uptime_ms = (time.monotonic() - self._start_time) * 1000

        # Probe Ollama
        ollama_status = "disconnected"
        model_loaded = False
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(f"{OLLAMA_HOST}/api/tags")
                if resp.status_code == 200:
                    ollama_status = "connected"
                    tags = resp.json()
                    models = tags.get("models", [])
                    model_loaded = any(
                        m.get("name", "").startswith("deepseek")
                        for m in models
                    )
        except Exception:
            ollama_status = "disconnected"

        # Determine overall status
        if ollama_status == "connected":
            status = "healthy"
        else:
            status = "degraded"

        return HealthStatus(
            status=status,
            agents={
                "mother_agent": "running",
                "inference": "running" if ollama_status == "connected" else "degraded",
                "validator": "running",
                "corrector": "running",
                "critic": "running" if ollama_status == "connected" else "stopped",
                "ux_renderer": "running",
            },
            budget=BudgetStatus(
                ceiling=self._config.get("token_ceiling", 8192),
                consumed=0,
                remaining=self._config.get("token_ceiling", 8192),
            ),
            uptime_ms=uptime_ms,
            version=self._version,
            ollama_status=ollama_status,
            model_loaded=model_loaded,
        )

    # -------------------------------------------------------------------
    # Config access
    # -------------------------------------------------------------------

    def get_config(self) -> dict[str, Any]:
        """Return the active configuration slice."""
        return {
            "pass_threshold": self._config.get("pass_threshold", 0.7),
            "max_retries": self._config.get("max_retries", 3),
            "temperature_init": self._config.get("temperature_init", 0.7),
            "temperature_decay": self._config.get("temperature_decay", 0.15),
            "inference_timeout": self._config.get("inference_timeout", 60000),
            "critic_model": self._config.get("critic_model", "deepseek-r1:latest"),
            "enable_toxicity": self._config.get("enable_toxicity", True),
            "token_ceiling": self._config.get("token_ceiling", 8192),
        }
