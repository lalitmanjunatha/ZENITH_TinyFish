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
        self._db = sqlite3.connect(self.path)
        self._db.execute("""CREATE TABLE IF NOT EXISTS events (
            event_id TEXT PRIMARY KEY, direction TEXT NOT NULL, event_json TEXT NOT NULL,
            envelope_json TEXT NOT NULL, status TEXT NOT NULL, created_at REAL NOT NULL)""")
        self._db.commit()

    def queue_outbox(self, event: DeviceEvent, envelope: dict) -> None:
        self._put(event, envelope, "outbox", "pending")

    def receive(self, event: DeviceEvent, envelope: dict) -> bool:
        row = self._db.execute("SELECT 1 FROM events WHERE event_id = ?", (event.event_id,)).fetchone()
        if row:
            return False
        self._put(event, envelope, "inbox", "received")
        return True

    def _put(self, event: DeviceEvent, envelope: dict, direction: str, status: str) -> None:
        self._db.execute("INSERT OR IGNORE INTO events VALUES (?, ?, ?, ?, ?, ?)", (
            event.event_id, direction, json.dumps(event.to_dict()), json.dumps(envelope), status, time.time()))
        self._db.commit()

    def pending_outbox(self) -> list[tuple[DeviceEvent, dict]]:
        rows = self._db.execute("SELECT event_json, envelope_json FROM events WHERE direction='outbox' AND status='pending'").fetchall()
        return [(DeviceEvent.from_dict(json.loads(event)), json.loads(envelope)) for event, envelope in rows]

    def mark_sent(self, event_id: str) -> None:
        self._db.execute("UPDATE events SET status='sent' WHERE event_id=?", (event_id,))
        self._db.commit()

    def unread_call_reports(self) -> list[DeviceEvent]:
        rows = self._db.execute("SELECT event_json FROM events WHERE direction='inbox' AND status='received'").fetchall()
        return [event for (raw,) in rows if (event := DeviceEvent.from_dict(json.loads(raw))).event_type.value == "call_report"]

    def close(self) -> None:
        self._db.close()
