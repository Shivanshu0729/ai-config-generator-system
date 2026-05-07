from __future__ import annotations

import sqlite3
import threading
import time

from fastapi import Request

from app.config import RATE_LIMIT_DB_PATH, RATE_LIMIT_TOTAL, RATE_LIMIT_WINDOW_SECONDS


_LOCK = threading.Lock()


def _ensure_storage() -> None:
    RATE_LIMIT_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(RATE_LIMIT_DB_PATH) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS api_rate_limits (
                request_key TEXT PRIMARY KEY,
                window_start INTEGER NOT NULL,
                request_count INTEGER NOT NULL
            )
            """
        )
        connection.commit()


def get_client_identifier(request: Request) -> str:
    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()

    if request.client and request.client.host:
        return request.client.host

    return "unknown"


def consume_rate_limit(
    request: Request,
    *,
    limit_total: int = RATE_LIMIT_TOTAL,
    window_seconds: int = RATE_LIMIT_WINDOW_SECONDS,
) -> dict:
    _ensure_storage()

    now = int(time.time())
    window_start = now - (now % window_seconds)
    reset_at = window_start + window_seconds
    request_key = get_client_identifier(request)

    with _LOCK:
        with sqlite3.connect(RATE_LIMIT_DB_PATH, timeout=5) as connection:
            connection.row_factory = sqlite3.Row
            connection.execute("BEGIN IMMEDIATE")

            row = connection.execute(
                "SELECT window_start, request_count FROM api_rate_limits WHERE request_key = ?",
                (request_key,),
            ).fetchone()

            if row is None or int(row["window_start"]) != window_start:
                request_count = 1
                connection.execute(
                    """
                    INSERT INTO api_rate_limits (request_key, window_start, request_count)
                    VALUES (?, ?, ?)
                    ON CONFLICT(request_key) DO UPDATE SET
                        window_start = excluded.window_start,
                        request_count = excluded.request_count
                    """,
                    (request_key, window_start, request_count),
                )
            else:
                request_count = int(row["request_count"])
                if request_count >= limit_total:
                    return {
                        "allowed": False,
                        "total_limit": limit_total,
                        "used": request_count,
                        "remaining": 0,
                        "reset_at": reset_at,
                        "reset_after_seconds": max(0, reset_at - now),
                        "request_key": request_key,
                        "window_start": window_start,
                    }

                request_count += 1
                connection.execute(
                    """
                    UPDATE api_rate_limits
                    SET request_count = ?, window_start = ?
                    WHERE request_key = ?
                    """,
                    (request_count, window_start, request_key),
                )

            connection.commit()

    return {
        "allowed": True,
        "total_limit": limit_total,
        "used": request_count,
        "remaining": max(0, limit_total - request_count),
        "reset_at": reset_at,
        "reset_after_seconds": max(0, reset_at - now),
        "request_key": request_key,
        "window_start": window_start,
    }


def get_rate_limit_status(
    request: Request,
    *,
    limit_total: int = RATE_LIMIT_TOTAL,
    window_seconds: int = RATE_LIMIT_WINDOW_SECONDS,
) -> dict:
    _ensure_storage()

    now = int(time.time())
    window_start = now - (now % window_seconds)
    reset_at = window_start + window_seconds
    request_key = get_client_identifier(request)

    with sqlite3.connect(RATE_LIMIT_DB_PATH, timeout=5) as connection:
        connection.row_factory = sqlite3.Row
        row = connection.execute(
            "SELECT window_start, request_count FROM api_rate_limits WHERE request_key = ?",
            (request_key,),
        ).fetchone()

    if row is None or int(row["window_start"]) != window_start:
        used = 0
    else:
        used = int(row["request_count"])

    return {
        "allowed": used < limit_total,
        "total_limit": limit_total,
        "used": used,
        "remaining": max(0, limit_total - used),
        "reset_at": reset_at,
        "reset_after_seconds": max(0, reset_at - now),
        "request_key": request_key,
        "window_start": window_start,
    }