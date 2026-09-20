from __future__ import annotations

import json
import sqlite3
import time
from pathlib import Path

from .models import DeviceEvent


class FabricStore:
    """Small durable outbox/inbox. The relay never substitutes this local copy."""

    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        # Ensure table exists on first use
        self._init_db()

    def _init_db(self) -> None:
        with sqlite3.connect(self.path) as conn:
            conn.execute(
                """CREATE TABLE IF NOT EXISTS events (
                    event_id TEXT PRIMARY KEY, direction TEXT NOT NULL, event_json TEXT NOT NULL,
                    envelope_json TEXT NOT NULL, status TEXT NOT NULL, created_at REAL NOT NULL)"""
            )
            conn.commit()

    def queue_outbox(self, event: DeviceEvent, envelope: dict) -> None:
        self._put(event, envelope, "outbox", "pending")

    def receive(self, event: DeviceEvent, envelope: dict) -> bool:
        row = self._db_execute(
            "SELECT 1 FROM events WHERE event_id = ?",
            (event.event_id,),
            fetchone=True,
        )
        if row:
            return False
        self._put(event, envelope, "inbox", "received")
        return True

    def _put(self, event: DeviceEvent, envelope: dict, direction: str, status: str) -> None:
        with sqlite3.connect(self.path) as conn:
            conn.execute(
                "INSERT OR IGNORE INTO events VALUES (?, ?, ?, ?, ?, ?)",
                (
                    event.event_id,
                    direction,
                    json.dumps(event.to_dict()),
                    json.dumps(envelope),
                    status,
                    time.time(),
                ),
            )
            conn.commit()

    def pending_outbox(self) -> list[tuple[DeviceEvent, dict]]:
        with sqlite3.connect(self.path) as conn:
            rows = conn.execute(
                "SELECT event_json, envelope_json FROM events WHERE direction='outbox' AND status='pending'"
            ).fetchall()
            return [
                (DeviceEvent.from_dict(json.loads(event)), json.loads(envelope))
                for event, envelope in rows
            ]

    def mark_sent(self, event_id: str) -> None:
        with sqlite3.connect(self.path) as conn:
            conn.execute("UPDATE events SET status='sent' WHERE event_id=?", (event_id,))
            conn.commit()

    def mark_received(self, event_id: str) -> None:
        with sqlite3.connect(self.path) as conn:
            conn.execute("UPDATE events SET status='received' WHERE event_id=?", (event_id,))
            conn.commit()

    # Helper to execute a query and optionally fetch
    def _db_execute(
        self,
        sql: str,
        params: tuple = (),
        *,
        fetchone: bool = False,
        fetchall: bool = False,
    ):
        with sqlite3.connect(self.path) as conn:
            cur = conn.execute(sql, params)
            if fetchone:
                result = cur.fetchone()
            elif fetchall:
                result = cur.fetchall()
            else:
                result = None
            conn.commit()
            return result