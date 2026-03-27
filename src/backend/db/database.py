"""
SQLite async wrapper for trace persistence.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

import aiosqlite

logger = logging.getLogger(__name__)

DEFAULT_DB_PATH = Path(__file__).resolve().parent.parent.parent.parent / "data" / "traces.db"


async def init_db(db_path: str | Path | None = None) -> None:
    """Create the traces table if it doesn't exist."""
    path = str(db_path or DEFAULT_DB_PATH)
    Path(path).parent.mkdir(parents=True, exist_ok=True)

    async with aiosqlite.connect(path) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS traces (
                trace_id        TEXT PRIMARY KEY,
                session_id      TEXT,
                query           TEXT NOT NULL,
                status          TEXT NOT NULL DEFAULT 'pending',
                created_at      TEXT NOT NULL DEFAULT (datetime('now')),
                completed_at    TEXT,
                total_latency_ms REAL,
                retry_count     INTEGER DEFAULT 0,
                confidence_score REAL,
                metric_breakdown TEXT,
                correction_history TEXT,
                trace_log       TEXT,
                final_response  TEXT,
                raw_state       TEXT
            )
        """)
        await db.commit()
    logger.info("Database initialized at %s", path)


async def save_trace(state: dict[str, Any], db_path: str | Path | None = None) -> None:
    """Insert or replace a trace record from pipeline state."""
    path = str(db_path or DEFAULT_DB_PATH)

    trace_id = state.get("trace_id", "unknown")
    final = state.get("final_response") or {}

    # Serialize complex fields to JSON
    def _json(obj: Any) -> str | None:
        if obj is None:
            return None
        return json.dumps(obj, default=str)

    async with aiosqlite.connect(path) as db:
        await db.execute(
            """
            INSERT OR REPLACE INTO traces
                (trace_id, session_id, query, status, completed_at,
                 total_latency_ms, retry_count, confidence_score,
                 metric_breakdown, correction_history, final_response, raw_state)
            VALUES (?, ?, ?, ?, datetime('now'), ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                trace_id,
                state.get("session_id"),
                state.get("query", ""),
                final.get("status", "unknown"),
                final.get("latency_ms"),
                state.get("retry_count", 0),
                state.get("validation_score"),
                _json(state.get("metric_breakdown")),
                _json(state.get("correction_history")),
                _json(final),
                _json({k: v for k, v in state.items() if not k.startswith("_")}),
            ),
        )
        await db.commit()
    logger.debug("Trace %s saved", trace_id)


async def get_trace(trace_id: str, db_path: str | Path | None = None) -> dict[str, Any] | None:
    """Retrieve a trace by ID. Returns None if not found."""
    path = str(db_path or DEFAULT_DB_PATH)

    try:
        async with aiosqlite.connect(path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT * FROM traces WHERE trace_id = ?", (trace_id,)
            )
            row = await cursor.fetchone()
            if row is None:
                return None

            result = dict(row)
            # Parse JSON fields
            for field in ("metric_breakdown", "correction_history", "final_response", "raw_state"):
                if result.get(field):
                    try:
                        result[field] = json.loads(result[field])
                    except (json.JSONDecodeError, TypeError):
                        pass
            return result
    except Exception:
        logger.debug("Could not read trace %s", trace_id, exc_info=True)
        return None
