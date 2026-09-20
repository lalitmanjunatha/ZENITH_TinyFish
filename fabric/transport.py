"""Transport for a local LAN relay or the same relay deployed to Render."""
from __future__ import annotations

import json
from urllib.error import URLError
from urllib.request import Request, urlopen

from .models import DeviceEvent
from .node import FabricNode


class HttpRelayTransport:
    def __init__(self, base_url: str, token: str, timeout_seconds: int = 10):
        self.base_url = base_url.rstrip("/")
        self.token = token
        self.timeout_seconds = timeout_seconds

    def _request(self, path: str, method: str, body: dict | None = None) -> dict:
        data = json.dumps(body).encode() if body is not None else None
        request = Request(self.base_url + path, data=data, method=method,
                          headers={"Authorization": f"Bearer {self.token}", "Content-Type": "application/json"})
        with urlopen(request, timeout=self.timeout_seconds) as response:  # nosec B310: user-configured Render/LAN endpoint
            return json.loads(response.read().decode())

    def flush(self, node: FabricNode) -> int:
        sent = 0
        for event, envelope in node.store.pending_outbox():
            if not event.target_device_id:
                continue
            self._request("/v1/events", "POST", {"target_device_id": event.target_device_id, "envelope": envelope})
            node.store.mark_sent(event.event_id)
            sent += 1
        return sent

    def receive(self, node: FabricNode) -> list[str]:
        data = self._request(f"/v1/events/{node.device_id}", "GET")
        return [node.receive_envelope(envelope)[1] or "received" for envelope in data.get("events", [])]
