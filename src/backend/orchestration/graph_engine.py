"""
LangGraph state machine for the Agentic Hallucination Guardrail pipeline.

Defines all node functions, state types, and the build_graph() factory that
wires the complete inference → validation → correction → response flow.
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal, Protocol, TypedDict, runtime_checkable

import httpx
from langgraph.graph import END, StateGraph

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

_CONFIG_PATH = Path(__file__).resolve().parent.parent / "config" / "validation_rules.json"


def _load_rules() -> dict[str, Any]:
    with open(_CONFIG_PATH) as f:
        return json.load(f)


RULES = _load_rules()
DEFAULT_CONFIG: dict[str, Any] = RULES["config"]

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")

# ---------------------------------------------------------------------------
# Callback Protocols (dependency injection — avoids circular imports)
# ---------------------------------------------------------------------------


@runtime_checkable
class BudgetCallback(Protocol):
    async def __call__(self, state: "GuardrailState") -> bool:
        """Return True if budget allows the next LLM call, False to halt."""
        ...


@runtime_checkable
class EventCallback(Protocol):
    async def __call__(self, event: dict[str, Any]) -> None:
        """Emit an SSE-compatible event dict."""
        ...


# ---------------------------------------------------------------------------
# Supporting Types
# ---------------------------------------------------------------------------


class InferenceMetadata(TypedDict, total=False):
    model: str
    prompt_tokens: int
    completion_tokens: int
    latency_ms: float
    prompt_template: str


class MetricBreakdown(TypedDict, total=False):
    faithfulness: float
    answer_relevancy: float
    hallucination: float
    toxicity: float


class CorrectionRecord(TypedDict, total=False):
    attempt: int
    critique: str
    corrected_prompt: str
    resulting_score: float | None


class CriticOutput(TypedDict, total=False):
    critique_text: str
    suggested_fixes: list[str]
    critic_model: str
    critic_latency_ms: float


class FinalResponse(TypedDict, total=False):
    response_text: str
    confidence_score: float
    metric_breakdown: MetricBreakdown | None
    retry_count: int
    trace_id: str
    model_used: str
    latency_ms: float
    status: str  # "VALIDATED" | "CIRCUIT_BREAK" | "STUB"
    failure_reasons: list[str] | None
    suggestion: str | None


class ConfigSlice(TypedDict, total=False):
    pass_threshold: float
    max_retries: int
    temperature_init: float
    temperature_decay: float
    inference_timeout: int
    critic_timeout: int
    critic_model: str
    enable_toxicity: bool
    token_ceiling: int
    heartbeat_interval: int


# ---------------------------------------------------------------------------
# State Schema (LangGraph shared state)
# ---------------------------------------------------------------------------


class GuardrailState(TypedDict, total=False):
    # Identity & Tracing
    trace_id: str
    session_id: str | None
    timestamp_start: float
    timestamp_end: float | None

    # Query
    query: str
    context: str | None
    conversation_history: list[dict[str, Any]]

    # Inference
    raw_response: str | None
    corrected_prompt: str | None
    temperature: float
    inference_metadata: InferenceMetadata | None
    is_stub: bool

    # Validation
    validation_score: float | None
    validation_flags: list[str]
    validation_details: str | None
    metric_breakdown: MetricBreakdown | None

    # Correction & Retry
    retry_count: int
    correction_history: list[CorrectionRecord]

    # Critic
    critic_output: CriticOutput | None

    # Final Output
    final_response: FinalResponse | None

    # Configuration
    config: ConfigSlice

    # Schema versioning
    schema_version: int

    # Internal: callbacks (not serialized)
    _budget_callback: Any
    _event_callback: Any


# ---------------------------------------------------------------------------
# RetryPolicy
# ---------------------------------------------------------------------------


@dataclass
class RetryPolicy:
    max_retries: int = 3
    backoff_base: float = 2.0
    backoff_max: float = 10.0
    jitter: bool = True


# ---------------------------------------------------------------------------
# State hashing (loop detection)
# ---------------------------------------------------------------------------


def compute_state_hash(state: GuardrailState) -> str:
    """SHA-256 hash of mutable state fields for loop detection."""
    hashable = {
        "query": state.get("query", ""),
        "raw_response": state.get("raw_response", ""),
        "validation_score": state.get("validation_score"),
        "retry_count": state.get("retry_count", 0),
        "corrected_prompt": state.get("corrected_prompt", ""),
    }
    payload = json.dumps(hashable, sort_keys=True, default=str)
    return hashlib.sha256(payload.encode()).hexdigest()


# ---------------------------------------------------------------------------
# Helper: emit event
# ---------------------------------------------------------------------------


async def _emit(state: GuardrailState, agent: str, action: str, **extra: Any) -> None:
    cb = state.get("_event_callback")
    if cb is not None:
        event = {
            "agent": agent,
            "action": action,
            "timestamp": time.time(),
            **extra,
        }
        try:
            await cb(event)
        except Exception:
            logger.debug("Event callback failed", exc_info=True)


# ---------------------------------------------------------------------------
# Node 1: User Query (Entry Point)
# ---------------------------------------------------------------------------


async def user_query_node(state: GuardrailState) -> dict[str, Any]:
    """Validate query, generate trace_id, and initialize state."""
    query = state.get("query", "").strip()
    if not query:
        raise ValueError("Query must not be empty")

    cfg: ConfigSlice = state.get("config", {})
    trace_id = state.get("trace_id") or str(uuid.uuid4())

    await _emit(state, "user_query", "init", trace_id=trace_id)

    return {
        "trace_id": trace_id,
        "query": query,
        "timestamp_start": time.time(),
        "temperature": cfg.get("temperature_init", DEFAULT_CONFIG["temperature_init"]),
        "retry_count": 0,
        "validation_score": None,
        "validation_flags": [],
        "correction_history": [],
        "raw_response": None,
        "corrected_prompt": None,
        "is_stub": False,
        "final_response": None,
        "schema_version": 1,
    }


# ---------------------------------------------------------------------------
# Node 2: Inference Node
# ---------------------------------------------------------------------------


async def inference_node(state: GuardrailState) -> dict[str, Any]:
    """Call Ollama for LLM inference. Falls back to a stub response if unavailable."""
    cfg: ConfigSlice = state.get("config", {})
    temperature = state.get("temperature", cfg.get("temperature_init", 0.7))
    timeout_ms = cfg.get("inference_timeout", DEFAULT_CONFIG["inference_timeout"])

    # Use corrected prompt if available, otherwise original query
    prompt = state.get("corrected_prompt") or state.get("query", "")
    model = cfg.get("critic_model", DEFAULT_CONFIG["critic_model"])

    await _emit(state, "inference", "start", retry_count=state.get("retry_count", 0))

    # Check budget
    budget_cb = state.get("_budget_callback")
    if budget_cb is not None:
        allowed = await budget_cb(state)
        if not allowed:
            logger.warning("Budget exceeded — skipping inference")
            return {"raw_response": None}

    start = time.monotonic()

    try:
        async with httpx.AsyncClient(timeout=timeout_ms / 1000) as client:
            resp = await client.post(
                f"{OLLAMA_HOST}/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": temperature},
                },
            )
            resp.raise_for_status()
            data = resp.json()

        latency = (time.monotonic() - start) * 1000
        raw_response = data.get("response", "")

        metadata: InferenceMetadata = {
            "model": data.get("model", model),
            "prompt_tokens": data.get("prompt_eval_count", 0),
            "completion_tokens": data.get("eval_count", 0),
            "latency_ms": latency,
            "prompt_template": prompt[:200],
        }

        await _emit(
            state,
            "inference",
            "complete",
            latency_ms=latency,
            tokens=metadata.get("completion_tokens", 0),
        )

        return {
            "raw_response": raw_response,
            "inference_metadata": metadata,
            "is_stub": False,
        }

    except Exception as exc:
        logger.warning("Ollama unavailable, using stub response: %s", exc)
        latency = (time.monotonic() - start) * 1000

        # Stub fallback for development
        stub_response = (
            "This is a stub response for development purposes. "
            "The Ollama inference server is not currently available."
        )

        metadata = {
            "model": "stub",
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "latency_ms": latency,
            "prompt_template": prompt[:200],
        }

        await _emit(state, "inference", "stub_fallback", reason=str(exc))

        return {
            "raw_response": stub_response,
            "inference_metadata": metadata,
            "is_stub": True,
        }


# ---------------------------------------------------------------------------
# Node 3: Validator Node
# ---------------------------------------------------------------------------


async def validator_node(state: GuardrailState) -> dict[str, Any]:
    """Evaluate the response for hallucination. Uses stub scoring in P0."""
    raw_response = state.get("raw_response")
    if not raw_response:
        return {
            "validation_score": 0.0,
            "validation_flags": ["NO_RESPONSE"],
            "validation_details": "No response was generated by inference.",
        }

    await _emit(state, "validator", "start")

    # P0 stub: use env var for configurable score, default 0.85
    stub_score_env = os.getenv("STUB_VALIDATION_SCORE")
    if stub_score_env is not None:
        score = float(stub_score_env)
    else:
        score = 0.85

    flags: list[str] = []
    cfg: ConfigSlice = state.get("config", {})
    threshold = cfg.get("pass_threshold", DEFAULT_CONFIG["pass_threshold"])

    # Simulate metric checks
    breakdown: MetricBreakdown = {
        "faithfulness": min(score + 0.05, 1.0),
        "answer_relevancy": min(score + 0.03, 1.0),
        "hallucination": max(1.0 - score - 0.1, 0.0),
        "toxicity": 0.01,
    }

    if breakdown["faithfulness"] < 0.5:
        flags.append("UNFAITHFUL")
    if breakdown["answer_relevancy"] < 0.4:
        flags.append("IRRELEVANT")
    if breakdown["hallucination"] > 0.5:
        flags.append("HALLUCINATED")

    # Check banned patterns
    banned = RULES.get("banned_patterns", [])
    import re

    for pattern in banned:
        if re.search(pattern, raw_response, re.IGNORECASE):
            flags.append("BANNED_PATTERN")
            break

    details = f"Stub validation: composite={score:.2f}, flags={flags}"

    await _emit(state, "validator", "complete", score=score, flags=flags)

    return {
        "validation_score": score,
        "validation_flags": flags,
        "validation_details": details,
        "metric_breakdown": breakdown,
    }


# ---------------------------------------------------------------------------
# Node 4: Decision Gate (pure routing — implemented as conditional edge)
# ---------------------------------------------------------------------------


def decision_gate(state: GuardrailState) -> Literal["response", "corrector", "fallback"]:
    """Pure routing: no state mutation, only branching logic."""
    flags = state.get("validation_flags", [])
    score = state.get("validation_score")
    cfg: ConfigSlice = state.get("config", {})
    threshold = cfg.get("pass_threshold", DEFAULT_CONFIG["pass_threshold"])

    # Toxicity → immediate circuit break
    if "TOXIC" in flags:
        return "fallback"

    # No score means inference failed
    if score is None:
        return "fallback"

    # Pass
    if score >= threshold and "TOXIC" not in flags:
        return "response"

    # Fail → correction attempt
    return "corrector"


# ---------------------------------------------------------------------------
# Node 5: Corrector Node
# ---------------------------------------------------------------------------


async def corrector_node(state: GuardrailState) -> dict[str, Any]:
    """Increment retry, decrease temperature, construct corrected prompt."""
    cfg: ConfigSlice = state.get("config", {})
    retry_count = state.get("retry_count", 0) + 1
    temperature_decay = cfg.get("temperature_decay", DEFAULT_CONFIG["temperature_decay"])
    current_temp = state.get("temperature", cfg.get("temperature_init", 0.7))
    new_temp = max(current_temp - temperature_decay, 0.05)

    flags = state.get("validation_flags", [])
    raw_response = state.get("raw_response", "")
    query = state.get("query", "")

    await _emit(
        state,
        "corrector",
        "correct",
        retry_count=retry_count,
        temperature=new_temp,
    )

    # Build corrected prompt with failure context
    correction_instructions = []
    if "UNFAITHFUL" in flags:
        correction_instructions.append(
            "Your previous response contained claims not supported by the context. "
            "Only include information that is directly supported by the provided sources."
        )
    if "IRRELEVANT" in flags:
        correction_instructions.append(
            "Your previous response did not adequately address the question. "
            "Focus specifically on answering the user's query."
        )
    if "HALLUCINATED" in flags:
        correction_instructions.append(
            "Your previous response contained hallucinated content. "
            "Do not fabricate facts, entities, or relationships."
        )
    if "BANNED_PATTERN" in flags:
        correction_instructions.append(
            "Your previous response contained a disallowed phrase. "
            "Avoid meta-commentary about being an AI."
        )

    if not correction_instructions:
        correction_instructions.append(
            "Your previous response did not meet quality thresholds. "
            "Please provide a more accurate and grounded answer."
        )

    corrected_prompt = (
        f"Original question: {query}\n\n"
        f"Your previous answer was rejected for the following reasons:\n"
        f"- " + "\n- ".join(correction_instructions) + "\n\n"
        f"Previous answer (for reference):\n{raw_response[:500]}\n\n"
        f"Please provide an improved answer that addresses these issues."
    )

    # Record correction history
    correction_record: CorrectionRecord = {
        "attempt": retry_count,
        "critique": "; ".join(correction_instructions),
        "corrected_prompt": corrected_prompt[:500],
        "resulting_score": None,
    }

    history = list(state.get("correction_history", []))
    history.append(correction_record)

    return {
        "retry_count": retry_count,
        "temperature": new_temp,
        "corrected_prompt": corrected_prompt,
        "correction_history": history,
    }


# ---------------------------------------------------------------------------
# Corrector → Inference routing (conditional edge after corrector)
# ---------------------------------------------------------------------------


def corrector_routing(state: GuardrailState) -> Literal["inference", "fallback"]:
    """Route back to inference if retries remain, otherwise fallback."""
    cfg: ConfigSlice = state.get("config", {})
    max_retries = cfg.get("max_retries", DEFAULT_CONFIG["max_retries"])
    retry_count = state.get("retry_count", 0)

    if retry_count >= max_retries:
        return "fallback"
    return "inference"


# ---------------------------------------------------------------------------
# Inference → Validator routing (check if response exists)
# ---------------------------------------------------------------------------


def inference_routing(state: GuardrailState) -> Literal["validator", "fallback", "response"]:
    """Route to validator if real response, response if stub, fallback if no response."""
    raw_response = state.get("raw_response")
    if raw_response is None:
        return "fallback"
    if state.get("is_stub", False):
        return "response"
    return "validator"


# ---------------------------------------------------------------------------
# Node 6: Response Node
# ---------------------------------------------------------------------------


async def response_node(state: GuardrailState) -> dict[str, Any]:
    """Package the final response — validated or stub."""
    timestamp_end = time.time()
    timestamp_start = state.get("timestamp_start", timestamp_end)
    latency_ms = (timestamp_end - timestamp_start) * 1000
    metadata = state.get("inference_metadata") or {}
    is_stub = state.get("is_stub", False)

    final: FinalResponse = {
        "response_text": state.get("raw_response", ""),
        "confidence_score": None if is_stub else state.get("validation_score", 0.0),
        "metric_breakdown": None if is_stub else state.get("metric_breakdown"),
        "retry_count": state.get("retry_count", 0),
        "trace_id": state.get("trace_id", ""),
        "model_used": metadata.get("model", "unknown"),
        "latency_ms": latency_ms,
        "status": "STUB" if is_stub else "VALIDATED",
        "failure_reasons": None,
        "suggestion": "Ollama is offline. Start the inference server for real validation." if is_stub else None,
    }

    await _emit(
        state,
        "response",
        "complete",
        status=final["status"],
        confidence=final["confidence_score"],
    )

    return {
        "final_response": final,
        "timestamp_end": timestamp_end,
    }


# ---------------------------------------------------------------------------
# Node 7: Fallback Node
# ---------------------------------------------------------------------------


async def fallback_node(state: GuardrailState) -> dict[str, Any]:
    """Deterministic fallback — no LLM call."""
    timestamp_end = time.time()
    timestamp_start = state.get("timestamp_start", timestamp_end)
    latency_ms = (timestamp_end - timestamp_start) * 1000
    flags = state.get("validation_flags", [])

    # Summarize failure reasons
    if flags:
        flag_summary = ", ".join(flags)
        reason_text = f"Validation flags: {flag_summary}."
    else:
        reason_text = "The pipeline could not produce a verified response."

    final: FinalResponse = {
        "response_text": (
            "I wasn't able to generate a verified answer to your question. "
            f"{reason_text} "
            "Please try rephrasing your question or providing more context."
        ),
        "confidence_score": 0.0,
        "metric_breakdown": state.get("metric_breakdown"),
        "retry_count": state.get("retry_count", 0),
        "trace_id": state.get("trace_id", ""),
        "model_used": (state.get("inference_metadata") or {}).get("model", "none"),
        "latency_ms": latency_ms,
        "status": "CIRCUIT_BREAK",
        "failure_reasons": flags,
        "suggestion": "Try rephrasing your question or providing more context.",
    }

    await _emit(
        state,
        "fallback",
        "circuit_break",
        retry_count=state.get("retry_count", 0),
        flags=flags,
    )

    return {
        "final_response": final,
        "timestamp_end": timestamp_end,
    }


# ---------------------------------------------------------------------------
# Graph Factory
# ---------------------------------------------------------------------------


def build_graph(
    budget_callback: BudgetCallback | None = None,
    event_callback: EventCallback | None = None,
) -> Any:
    """
    Construct and compile the LangGraph state machine.

    Accepts optional callbacks for budget enforcement and event emission,
    avoiding circular imports with mother_agent.
    """
    graph = StateGraph(GuardrailState)

    # Register nodes
    graph.add_node("user_query", user_query_node)
    graph.add_node("inference", inference_node)
    graph.add_node("validator", validator_node)
    graph.add_node("corrector", corrector_node)
    graph.add_node("response", response_node)
    graph.add_node("fallback", fallback_node)

    # Entry point
    graph.set_entry_point("user_query")

    # Edges
    # user_query → inference (always)
    graph.add_edge("user_query", "inference")

    # inference → validator or fallback (conditional on response)
    graph.add_conditional_edges("inference", inference_routing, {
        "validator": "validator",
        "fallback": "fallback",
        "response": "response",
    })

    # validator → decision_gate (conditional routing)
    graph.add_conditional_edges("validator", decision_gate, {
        "response": "response",
        "corrector": "corrector",
        "fallback": "fallback",
    })

    # corrector → inference or fallback (conditional on retry count)
    graph.add_conditional_edges("corrector", corrector_routing, {
        "inference": "inference",
        "fallback": "fallback",
    })

    # Terminal nodes
    graph.add_edge("response", END)
    graph.add_edge("fallback", END)

    compiled = graph.compile()
    logger.info("LangGraph compiled successfully")
    return compiled
