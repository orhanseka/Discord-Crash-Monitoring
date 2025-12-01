from __future__ import annotations

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Iterable

import pendulum


class CrashStore:
    def __init__(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(path)
        self.conn.row_factory = sqlite3.Row
        self._ensure_table()

    def _ensure_table(self) -> None:
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS incidents (
                id INTEGER PRIMARY KEY,
                timestamp TEXT NOT NULL,
                severity TEXT NOT NULL,
                title TEXT NOT NULL,
                details TEXT,
                origin TEXT,
                metadata TEXT
            )
            """
        )
        self.conn.commit()

    def log_incident(self, *, severity: str, title: str, details: str | None, origin: str | None, metadata: str | None) -> None:
        self.conn.execute(
            "INSERT INTO incidents (timestamp, severity, title, details, origin, metadata) VALUES (?, ?, ?, ?, ?, ?)",
            (
                pendulum.now("UTC").to_iso8601_string(),
                severity,
                title,
                details,
                origin,
                metadata,
            ),
        )
        self.conn.commit()

    def list_recent(self, limit: int = 10) -> list[sqlite3.Row]:
        cursor = self.conn.execute(
            "SELECT * FROM incidents ORDER BY timestamp DESC LIMIT ?",
            (limit,),
        )
        return cursor.fetchall()

    def summary(self, *, days: int = 7) -> list[dict[str, object]]:
        boundary = pendulum.now("UTC").subtract(days=days)
        cursor = self.conn.execute(
            "SELECT severity, COUNT(*) as total FROM incidents WHERE timestamp >= ? GROUP BY severity",
            (boundary.to_iso8601_string(),),
        )
        return [dict(row) for row in cursor.fetchall()]

    def close(self) -> None:
        self.conn.close()
