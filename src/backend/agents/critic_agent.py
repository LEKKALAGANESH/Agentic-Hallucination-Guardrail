"""
Critic Agent — wraps local Ollama model for structured response critique.

P0: Returns rule-based fallback critique (no actual LLM call).
P1: Will call DeepSeek-R1 via Ollama for real critique generation.
"""

from __future__ import annotations

import logging
import os
import time
from typing import Any, TypedDict

import httpx

logger = logging.getLogger(__name__)

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")

CRITIQUE_SYSTEM_PROMPT = (
    "You are a factual grounding critic. Evaluate the following response "
    "against the provided context documents. Assess factual accuracy, "
    "grounding in sources, completeness, and citation accuracy. "
    "Return your assessment as JSON with fields: verdict, confidence, "
    "factual_accuracy, grounding_score, completeness, issues_found, "
    "suggested_corrections."
)


class CritiqueResult(TypedDict, total=False):
    verdict: str  # "ACCEPT" | "REJECT" | "PARTIAL" | "ERROR"
    confidence: float
    factual_accuracy: float
    grounding_score: float
    completeness: float
    issues_found: list[str]
    suggested_corrections: list[str]


class CriticAgent:
    """Stateless agent that evaluates responses against context."""

    def __init__(
        self,
        model_name: str = "deepseek-r1:latest",
        ollama_url: str | None = None,
        timeout: float = 30.0,
    ) -> None:
        self.model_name = model_name
        self.ollama_url = ollama_url or OLLAMA_HOST
        self.timeout = timeout

    async def critique(
        self,
        response: str,
        context_docs: list[str] | None = None,
        query: str = "",
    ) -> CritiqueResult:
        """
        Evaluate a response. P0 stub returns rule-based fallback.
        """
        start = time.monotonic()

        # P0: Rule-based fallback critique
        issues: list[str] = []
        suggestions: list[str] = []

        if not response or len(response.strip()) < 10:
            issues.append("Response is too short or empty")
            suggestions.append("Provide a more detailed answer")

        if context_docs and not any(
            doc_fragment.lower() in response.lower()
            for doc_fragment in context_docs
            if len(doc_fragment) > 5
        ):
            issues.append("Response may not be grounded in provided context")
            suggestions.append("Reference the provided source documents")

        # Determine verdict based on issues
        if not issues:
            verdict = "ACCEPT"
            confidence = 0.85
        elif len(issues) == 1:
            verdict = "PARTIAL"
            confidence = 0.60
        else:
            verdict = "REJECT"
            confidence = 0.30

        latency = (time.monotonic() - start) * 1000
        logger.debug("Critic stub completed in %.1fms: %s", latency, verdict)

        return CritiqueResult(
            verdict=verdict,
            confidence=confidence,
            factual_accuracy=confidence,
            grounding_score=confidence * 0.9,
            completeness=confidence * 0.95,
            issues_found=issues,
            suggested_corrections=suggestions,
        )

    async def health_check(self) -> dict[str, Any]:
        """Ping Ollama to verify model availability."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(f"{self.ollama_url}/api/tags")
                if resp.status_code == 200:
                    models = resp.json().get("models", [])
                    loaded = any(
                        m.get("name", "").startswith(self.model_name.split(":")[0])
                        for m in models
                    )
                    return {"status": "ok", "latency_ms": 0, "model_loaded": loaded}
        except Exception:
            pass
        return {"status": "error", "latency_ms": 0, "model_loaded": False}
