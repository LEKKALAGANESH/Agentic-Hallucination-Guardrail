"""Tests for db/database.py — SQLite async trace persistence."""

from __future__ import annotations

import asyncio
import json
import os
from datetime import datetime
from pathlib import Path

import pytest

from src.backend.db.database import init_db, save_trace, get_trace


# ---------------------------------------------------------------------------
# TestInitDb
# ---------------------------------------------------------------------------


class TestInitDb:
    @pytest.mark.asyncio
    async def test_creates_traces_table(self, tmp_path):
        """init_db should create a traces table in the database."""
        db_path = tmp_path / "test.db"
        await init_db(db_path)

        import aiosqlite
        async with aiosqlite.connect(str(db_path)) as db:
            cursor = await db.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='traces'"
            )
            row = await cursor.fetchone()
        assert row is not None
        assert row[0] == "traces"

    @pytest.mark.asyncio
    async def test_idempotent_init(self, tmp_path):
        """Calling init_db twice should not raise or corrupt data."""
        db_path = tmp_path / "test.db"
        await init_db(db_path)
        await init_db(db_path)  # Should not raise

        import aiosqlite
        async with aiosqlite.connect(str(db_path)) as db:
            cursor = await db.execute(
                "SELECT count(*) FROM sqlite_master WHERE type='table' AND name='traces'"
            )
            row = await cursor.fetchone()
        assert row[0] == 1

    @pytest.mark.asyncio
    async def test_creates_parent_directories(self, tmp_path):
        """init_db should create parent directories if they don't exist."""
        db_path = tmp_path / "nested" / "deep" / "test.db"
        await init_db(db_path)
        assert db_path.exists()

    @pytest.mark.asyncio
    async def test_default_path_uses_data_dir(self):
        """DEFAULT_DB_PATH should point to data/traces.db."""
        from src.backend.db.database import DEFAULT_DB_PATH
        assert DEFAULT_DB_PATH.name == "traces.db"
        assert "data" in str(DEFAULT_DB_PATH)


# ---------------------------------------------------------------------------
# TestSaveTrace
# ---------------------------------------------------------------------------


class TestSaveTrace:
    @pytest.mark.asyncio
    async def test_saves_minimal_state(self, tmp_path):
        """Should save a trace with minimal required fields."""
        db_path = tmp_path / "test.db"
        await init_db(db_path)
        state = {"trace_id": "t-001", "query": "Hello?"}
        await save_trace(state, db_path)

        result = await get_trace("t-001", db_path)
        assert result is not None
        assert result["trace_id"] == "t-001"
        assert result["query"] == "Hello?"

    @pytest.mark.asyncio
    async def test_saves_full_state(self, tmp_path):
        """Should save a trace with all fields populated."""
        db_path = tmp_path / "test.db"
        await init_db(db_path)
        state = {
            "trace_id": "t-002",
            "session_id": "sess-1",
            "query": "What is AI?",
            "retry_count": 2,
            "validation_score": 0.87,
            "metric_breakdown": {"faithfulness": 0.9, "hallucination": 0.05},
            "correction_history": [
                {"attempt": 1, "critique": "Too vague", "corrected_prompt": "Be specific"}
            ],
            "final_response": {
                "status": "VALIDATED",
                "response_text": "AI is...",
                "confidence_score": 0.87,
                "latency_ms": 1500.0,
            },
        }
        await save_trace(state, db_path)

        result = await get_trace("t-002", db_path)
        assert result is not None
        assert result["session_id"] == "sess-1"
        assert result["retry_count"] == 2
        assert result["confidence_score"] == pytest.approx(0.87)
        assert result["status"] == "VALIDATED"

    @pytest.mark.asyncio
    async def test_json_serialization_of_complex_fields(self, tmp_path):
        """metric_breakdown and correction_history should round-trip as JSON."""
        db_path = tmp_path / "test.db"
        await init_db(db_path)
        breakdown = {"faithfulness": 0.9, "answer_relevancy": 0.85}
        history = [{"attempt": 1, "critique": "test"}]
        state = {
            "trace_id": "t-003",
            "query": "test",
            "metric_breakdown": breakdown,
            "correction_history": history,
        }
        await save_trace(state, db_path)

        result = await get_trace("t-003", db_path)
        assert result["metric_breakdown"] == breakdown
        assert result["correction_history"] == history

    @pytest.mark.asyncio
    async def test_upsert_overwrites_existing(self, tmp_path):
        """Saving same trace_id twice should overwrite the record."""
        db_path = tmp_path / "test.db"
        await init_db(db_path)
        await save_trace({"trace_id": "t-004", "query": "v1"}, db_path)
        await save_trace({"trace_id": "t-004", "query": "v2"}, db_path)

        result = await get_trace("t-004", db_path)
        assert result["query"] == "v2"

    @pytest.mark.asyncio
    async def test_none_fields_handled(self, tmp_path):
        """None values in optional fields should not cause errors."""
        db_path = tmp_path / "test.db"
        await init_db(db_path)
        state = {
            "trace_id": "t-005",
            "query": "test",
            "session_id": None,
            "validation_score": None,
            "metric_breakdown": None,
            "correction_history": None,
            "final_response": None,
        }
        await save_trace(state, db_path)
        result = await get_trace("t-005", db_path)
        assert result is not None

    @pytest.mark.asyncio
    async def test_missing_trace_id_defaults_to_unknown(self, tmp_path):
        """Missing trace_id should default to 'unknown'."""
        db_path = tmp_path / "test.db"
        await init_db(db_path)
        await save_trace({"query": "no id"}, db_path)

        result = await get_trace("unknown", db_path)
        assert result is not None
        assert result["query"] == "no id"

    @pytest.mark.asyncio
    async def test_non_serializable_fields_handled(self, tmp_path):
        """Non-JSON-serializable objects should be converted via default=str."""
        db_path = tmp_path / "test.db"
        await init_db(db_path)
        state = {
            "trace_id": "t-006",
            "query": "test",
            "metric_breakdown": {"timestamp": datetime(2024, 1, 1)},
        }
        await save_trace(state, db_path)
        result = await get_trace("t-006", db_path)
        assert result is not None
        assert "2024" in str(result["metric_breakdown"]["timestamp"])

    @pytest.mark.asyncio
    async def test_complex_correction_history(self, tmp_path):
        """Multiple correction records should all persist."""
        db_path = tmp_path / "test.db"
        await init_db(db_path)
        history = [
            {"attempt": i, "critique": f"issue-{i}", "corrected_prompt": f"fix-{i}"}
            for i in range(1, 4)
        ]
        state = {
            "trace_id": "t-007",
            "query": "test",
            "correction_history": history,
        }
        await save_trace(state, db_path)
        result = await get_trace("t-007", db_path)
        assert len(result["correction_history"]) == 3
        assert result["correction_history"][2]["attempt"] == 3


# ---------------------------------------------------------------------------
# TestGetTrace
# ---------------------------------------------------------------------------


class TestGetTrace:
    @pytest.mark.asyncio
    async def test_existing_trace(self, tmp_path):
        """get_trace should return a dict for existing traces."""
        db_path = tmp_path / "test.db"
        await init_db(db_path)
        await save_trace({"trace_id": "t-100", "query": "hello"}, db_path)

        result = await get_trace("t-100", db_path)
        assert result is not None
        assert result["trace_id"] == "t-100"

    @pytest.mark.asyncio
    async def test_nonexistent_returns_none(self, tmp_path):
        """get_trace should return None for unknown trace_id."""
        db_path = tmp_path / "test.db"
        await init_db(db_path)

        result = await get_trace("nope", db_path)
        assert result is None

    @pytest.mark.asyncio
    async def test_json_parsing_of_stored_fields(self, tmp_path):
        """JSON fields should be deserialized back to Python dicts/lists."""
        db_path = tmp_path / "test.db"
        await init_db(db_path)
        state = {
            "trace_id": "t-101",
            "query": "test",
            "metric_breakdown": {"faith": 0.9},
            "final_response": {"status": "VALIDATED", "response_text": "ok"},
        }
        await save_trace(state, db_path)
        result = await get_trace("t-101", db_path)
        assert isinstance(result["metric_breakdown"], dict)
        assert isinstance(result["final_response"], dict)

    @pytest.mark.asyncio
    async def test_corrupt_json_resilience(self, tmp_path):
        """Corrupt JSON in stored fields should not raise, just leave raw."""
        db_path = tmp_path / "test.db"
        await init_db(db_path)

        import aiosqlite
        async with aiosqlite.connect(str(db_path)) as db:
            await db.execute(
                """INSERT INTO traces (trace_id, query, status, metric_breakdown)
                   VALUES (?, ?, ?, ?)""",
                ("t-corrupt", "test", "unknown", "{invalid json!!!"),
            )
            await db.commit()

        result = await get_trace("t-corrupt", db_path)
        assert result is not None
        # Should not crash — corrupt JSON is left as-is
        assert result["trace_id"] == "t-corrupt"

    @pytest.mark.asyncio
    async def test_missing_db_returns_none(self, tmp_path):
        """get_trace on a nonexistent database file should return None."""
        result = await get_trace("any-id", tmp_path / "does_not_exist.db")
        assert result is None

    @pytest.mark.asyncio
    async def test_round_trip(self, tmp_path):
        """Data saved should match data retrieved."""
        db_path = tmp_path / "test.db"
        await init_db(db_path)
        state = {
            "trace_id": "t-rt",
            "query": "round trip test",
            "session_id": "s-1",
            "retry_count": 1,
            "validation_score": 0.75,
        }
        await save_trace(state, db_path)
        result = await get_trace("t-rt", db_path)
        assert result["query"] == "round trip test"
        assert result["session_id"] == "s-1"
        assert result["retry_count"] == 1
        assert result["confidence_score"] == pytest.approx(0.75)

    @pytest.mark.asyncio
    async def test_multiple_traces(self, tmp_path):
        """Multiple traces should be independently retrievable."""
        db_path = tmp_path / "test.db"
        await init_db(db_path)
        for i in range(5):
            await save_trace({"trace_id": f"multi-{i}", "query": f"q-{i}"}, db_path)

        for i in range(5):
            result = await get_trace(f"multi-{i}", db_path)
            assert result is not None
            assert result["query"] == f"q-{i}"

    @pytest.mark.asyncio
    async def test_row_factory_returns_dict(self, tmp_path):
        """get_trace should return a dict, not a Row object."""
        db_path = tmp_path / "test.db"
        await init_db(db_path)
        await save_trace({"trace_id": "t-dict", "query": "test"}, db_path)

        result = await get_trace("t-dict", db_path)
        assert isinstance(result, dict)


# ---------------------------------------------------------------------------
# TestConcurrency
# ---------------------------------------------------------------------------


class TestConcurrency:
    @pytest.mark.asyncio
    async def test_concurrent_saves(self, tmp_path):
        """Multiple concurrent saves should not corrupt the database."""
        db_path = tmp_path / "test.db"
        await init_db(db_path)

        async def save_one(i: int):
            await save_trace({"trace_id": f"conc-{i}", "query": f"q-{i}"}, db_path)

        await asyncio.gather(*(save_one(i) for i in range(10)))

        for i in range(10):
            result = await get_trace(f"conc-{i}", db_path)
            assert result is not None

    @pytest.mark.asyncio
    async def test_save_then_get(self, tmp_path):
        """Save immediately followed by get should return the saved data."""
        db_path = tmp_path / "test.db"
        await init_db(db_path)
        await save_trace({"trace_id": "seq-1", "query": "sequential"}, db_path)
        result = await get_trace("seq-1", db_path)
        assert result is not None
        assert result["query"] == "sequential"

    @pytest.mark.asyncio
    async def test_full_lifecycle(self, tmp_path):
        """init → save → get → upsert → get should all work sequentially."""
        db_path = tmp_path / "test.db"
        await init_db(db_path)

        # Save v1
        await save_trace({"trace_id": "lc-1", "query": "v1"}, db_path)
        result = await get_trace("lc-1", db_path)
        assert result["query"] == "v1"

        # Upsert v2
        await save_trace(
            {
                "trace_id": "lc-1",
                "query": "v2",
                "final_response": {"status": "VALIDATED", "response_text": "done"},
            },
            db_path,
        )
        result = await get_trace("lc-1", db_path)
        assert result["query"] == "v2"
        assert result["final_response"]["status"] == "VALIDATED"
