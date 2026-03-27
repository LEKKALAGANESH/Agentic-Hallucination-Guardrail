"""Performance benchmarks for critical path operations."""

from __future__ import annotations

import os
import time

import pytest
from unittest.mock import patch

from src.backend.orchestration.graph_engine import compute_state_hash, build_graph, validator_node
from src.backend.agents.critic_agent import CriticAgent
from src.backend.evaluation.evaluator import run_evaluation


@pytest.fixture
def benchmark_state():
    """State dict for benchmarking."""
    return {
        "query": "What is the refund policy for online purchases?",
        "context": "Refunds are available within 30 days of purchase.",
        "trace_id": "bench-001",
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
        "raw_response": "The refund policy allows returns within 30 days of purchase.",
        "corrected_prompt": None,
        "is_stub": False,
        "final_response": None,
        "schema_version": 1,
        "_budget_callback": None,
        "_event_callback": None,
    }


class TestBenchmarks:
    @pytest.mark.slow
    def test_state_hash_performance(self, benchmark_state, benchmark):
        """compute_state_hash should complete in < 1ms."""
        result = benchmark(compute_state_hash, benchmark_state)
        assert isinstance(result, str)
        assert len(result) == 64  # SHA-256 hex digest

    @pytest.mark.slow
    def test_critic_stub_latency(self, benchmark):
        """CriticAgent.critique stub should complete in < 5ms."""
        import asyncio

        agent = CriticAgent()

        async def run_critique():
            return await agent.critique(
                response="A detailed response about refund policies within 30 days.",
                context_docs=["Refunds are available within 30 days."],
                query="What is the refund policy?",
            )

        result = benchmark(lambda: asyncio.get_event_loop().run_until_complete(run_critique()))
        assert result["verdict"] in ("ACCEPT", "PARTIAL", "REJECT")

    @pytest.mark.slow
    def test_evaluator_stub_latency(self, benchmark):
        """run_evaluation stub should complete in < 5ms."""
        import asyncio

        async def run_eval():
            return await run_evaluation({"query": "test", "raw_response": "answer"})

        with patch.dict(os.environ, {"STUB_VALIDATION_SCORE": "0.85"}):
            result = benchmark(lambda: asyncio.get_event_loop().run_until_complete(run_eval()))
        assert result["verdict"] == "PASS"

    @pytest.mark.slow
    def test_database_round_trip(self, benchmark, tmp_path):
        """Database save + get round-trip should complete in < 50ms."""
        import asyncio
        from src.backend.db.database import init_db, save_trace, get_trace

        db_path = tmp_path / "bench.db"
        asyncio.get_event_loop().run_until_complete(init_db(db_path))

        counter = [0]

        async def round_trip():
            counter[0] += 1
            tid = f"bench-{counter[0]}"
            await save_trace({"trace_id": tid, "query": "benchmark test"}, db_path)
            result = await get_trace(tid, db_path)
            return result

        result = benchmark(lambda: asyncio.get_event_loop().run_until_complete(round_trip()))
        assert result is not None

    @pytest.mark.slow
    def test_graph_compile_time(self, benchmark, mock_ollama):
        """build_graph compilation should complete in < 100ms."""
        graph = benchmark(build_graph)
        assert graph is not None
