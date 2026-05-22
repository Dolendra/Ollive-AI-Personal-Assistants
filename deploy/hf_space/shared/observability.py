"""Logging, latency tracking, and basic observability."""

from __future__ import annotations

import json
import sqlite3
import time
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[1] / "data" / "logs" / "assistant_logs.db"


def _ensure_db() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts TEXT NOT NULL,
                assistant_type TEXT NOT NULL,
                user_message TEXT NOT NULL,
                assistant_response TEXT NOT NULL,
                latency_ms REAL,
                blocked INTEGER DEFAULT 0,
                guardrail_category TEXT,
                model_id TEXT,
                extra_json TEXT
            )
            """
        )
        conn.commit()


@contextmanager
def track_latency():
    start = time.perf_counter()
    yield
    elapsed_ms = (time.perf_counter() - start) * 1000
    track_latency.last_ms = elapsed_ms  # type: ignore[attr-defined]


track_latency.last_ms = 0.0


def log_interaction(
    *,
    assistant_type: str,
    user_message: str,
    assistant_response: str,
    latency_ms: float,
    blocked: bool = False,
    guardrail_category: str | None = None,
    model_id: str | None = None,
    extra: dict | None = None,
) -> None:
    _ensure_db()
    ts = datetime.now(timezone.utc).isoformat()
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            INSERT INTO interactions
            (ts, assistant_type, user_message, assistant_response,
             latency_ms, blocked, guardrail_category, model_id, extra_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                ts,
                assistant_type,
                user_message,
                assistant_response,
                latency_ms,
                1 if blocked else 0,
                guardrail_category,
                model_id,
                json.dumps(extra or {}),
            ),
        )
        conn.commit()


def get_latency_stats(assistant_type: str | None = None) -> dict:
    _ensure_db()
    query = "SELECT assistant_type, AVG(latency_ms), COUNT(*) FROM interactions"
    params: tuple = ()
    if assistant_type:
        query += " WHERE assistant_type = ?"
        params = (assistant_type,)
    query += " GROUP BY assistant_type"

    with sqlite3.connect(DB_PATH) as conn:
        rows = conn.execute(query, params).fetchall()

    return {
        row[0]: {"avg_latency_ms": round(row[1], 2), "count": row[2]}
        for row in rows
    }
