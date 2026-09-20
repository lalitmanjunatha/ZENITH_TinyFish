"""Minimal Render-ready encrypted envelope relay.

Set ZENITH_RELAY_TOKEN in Render.  The relay stores opaque envelopes only.
"""
from __future__ import annotations

import os
from collections import defaultdict
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel

app = FastAPI(title="ZENITH Device Fabric Relay")
_queues: dict[str, list[dict]] = defaultdict(list)
_token = os.getenv("ZENITH_RELAY_TOKEN", "")

class Envelope(BaseModel):
    target_device_id: str
    envelope: dict

def _authorize(token: str | None) -> None:
    if not _token or token != _token:
        raise HTTPException(401, "Unauthorized")

@app.post("/v1/events")
def publish(item: Envelope, authorization: str | None = Header(default=None)):
    _authorize(authorization.removeprefix("Bearer ") if authorization else None)
    _queues[item.target_device_id].append(item.envelope)
    return {"accepted": True}

@app.get("/v1/events/{device_id}")
def consume(device_id: str, authorization: str | None = Header(default=None)):
    _authorize(authorization.removeprefix("Bearer ") if authorization else None)
    items = _queues.pop(device_id, [])
    return {"events": items}
