"""Golden regression tests — 100 parameterized tests from golden_100.json."""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest
from unittest.mock import patch

from src.backend.orchestration.graph_engine import build_graph


# ---------------------------------------------------------------------------
# Load golden test set
# ---------------------------------------------------------------------------

FIXTURE_PATH = Path(__file__).parent / "fixtures" / "golden_100.json"


def _load_golden():
    with open(FIXTURE_PATH) as f:
        return json.load(f)


GOLDEN_CASES = _load_golden()


def _case_id(case):
    return f"{case['id']}-{case['category']}"


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def base_state():
    """Minimal state for golden tests."""
    return {
        "query": "",
        "context": None,
        "trace_id": "golden-test",
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


# ---------------------------------------------------------------------------
# Parameterized golden tests
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("case", GOLDEN_CASES, ids=[_case_id(c) for c in GOLDEN_CASES])
class TestGoldenRegression:
    @pytest.mark.asyncio
    async def test_golden_case(self, case, base_state, mock_ollama):
        """Each golden test case should produce expected category behavior."""
        # Configure state from fixture
        base_state["query"] = case["query"]
        base_state["context"] = case.get("context")
        base_state["trace_id"] = case["id"]

        stub_score = str(case["stub_validation_score"])
        query = case["query"].strip() if case["query"] else ""

        with patch.dict(os.environ, {"STUB_VALIDATION_SCORE": stub_score}):
            graph = build_graph()

            # Empty/whitespace queries should raise ValueError gracefully
            if not query:
                with pytest.raises(Exception):
                    await graph.ainvoke(base_state)
                return

            result = await graph.ainvoke(base_state)

        # Verify no unhandled exceptions — result should have final_response
        assert result is not None
        assert "final_response" in result
        assert result["final_response"] is not None

        status = result["final_response"]["status"]
        confidence = result["final_response"].get("confidence_score")
        category = case["category"]

        # Category-specific assertions
        if category == "happy_path":
            assert status == "VALIDATED", (
                f"{case['id']}: Expected VALIDATED for happy_path, got {status}"
            )
            if confidence is not None:
                assert confidence >= case.get("expected_min_confidence", 0.7), (
                    f"{case['id']}: Confidence {confidence} below minimum"
                )

        elif category == "hallucination":
            assert status == "CIRCUIT_BREAK", (
                f"{case['id']}: Expected CIRCUIT_BREAK for hallucination, got {status}"
            )

        elif category == "adversarial":
            # Adversarial inputs should either validate or gracefully fail
            assert status in ("VALIDATED", "CIRCUIT_BREAK", "STUB"), (
                f"{case['id']}: Unexpected status {status} for adversarial input"
            )

        elif category == "edge_case":
            # Edge cases near threshold may go either way
            assert status in ("VALIDATED", "CIRCUIT_BREAK"), (
                f"{case['id']}: Unexpected status {status} for edge_case"
            )
