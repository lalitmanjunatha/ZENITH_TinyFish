from __future__ import annotations

import time
from pathlib import Path
from typing import Callable

from .crypto import SharedSecret
from .models import ActionRequest, DeviceEvent, EventType, RiskLevel
from .store import FabricStore


class FabricNode:
    """Protocol core used by Windows now and mirrored by the Android app."""

    def __init__(self, device_id: str, secret: SharedSecret, store_path: str | Path):
        self.device_id, self.secret = device_id, secret
        self.store = FabricStore(store_path)
        self._handlers: dict[str, Callable[[dict], str]] = {}

    def capabilities(self) -> list[str]:
        return sorted(self._handlers)

    def register(self, name: str, handler: Callable[[dict], str]) -> None:
        self._handlers[name] = handler

    def make_event(self, event_type: EventType, payload: dict, target: str | None = None,
                   expires_in_seconds: int | None = None) -> tuple[DeviceEvent, dict]:
        event = DeviceEvent(event_type, self.device_id, payload, target,
                            time.time() + expires_in_seconds if expires_in_seconds else None)
        envelope = self.secret.seal(event.to_dict())
        self.store.queue_outbox(event, envelope)
        return event, envelope

    def request_action(self, request: ActionRequest) -> tuple[DeviceEvent, dict]:
        return self.make_event(EventType.ACTION_REQUEST, request.payload(), request.target_device_id,
                               request.expires_in_seconds)

    def receive_envelope(self, envelope: dict) -> tuple[DeviceEvent, str | None]:
        event = DeviceEvent.from_dict(self.secret.open(envelope))
        if event.expired:
            return event, "expired"
        if event.target_device_id not in (None, self.device_id):
            return event, "wrong_target"
        if not self.store.receive(event, envelope):
            return event, "duplicate"
        if event.event_type is not EventType.ACTION_REQUEST:
            return event, None
        return event, self._handle_action(event)

    def _handle_action(self, event: DeviceEvent) -> str:
        payload = event.payload
        if payload.get("risk") != RiskLevel.LOW.value or not payload.get("trusted"):
            return "approval_required"
        handler = self._handlers.get(payload.get("action_name", ""))
        if handler is None:
            return "unsupported_action"
        try:
            return handler(payload.get("parameters", {})) or "done"
        except Exception as exc:
            return f"failed: {exc}"
