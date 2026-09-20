"""Voice tools for ZENITH's paired-device fabric.

They only queue encrypted requests. A remote device decides whether it can and
may execute a request; no phone operation is performed by this module itself.
"""
from __future__ import annotations

import asyncio
import json
import os
from pathlib import Path

from livekit.agents import function_tool

from fabric.crypto import SharedSecret
from fabric.models import ActionRequest, EventType, RiskLevel
from fabric.node import FabricNode
from fabric.transport import HttpRelayTransport

_BASE = Path(__file__).resolve().parent.parent
_CONFIG = _BASE / "config" / "fabric.json"
_STORE = _BASE / "data" / "fabric" / "laptop.db"
_NODE: FabricNode | None = None

TOOL = {
    "name": "fabric_status",
    "description": "Check ZENITH paired-device fabric status and local capabilities.",
    "parameters": {"type": "OBJECT", "properties": {}},
    "handler": "fabric_status",
}


def _load_config() -> dict:
    if not _CONFIG.exists():
        return {}
    return json.loads(_CONFIG.read_text(encoding="utf-8"))


def _node() -> FabricNode | None:
    global _NODE
    if _NODE:
        return _NODE
    config = _load_config()
    secret = config.get("pairing_secret")
    if not secret:
        return None
    _NODE = FabricNode(config.get("device_id", "laptop"), SharedSecret.from_export(secret), _STORE)
    return _NODE


def _save_pairing(secret: SharedSecret) -> dict:
    _CONFIG.parent.mkdir(parents=True, exist_ok=True)
    config = {"device_id": "laptop", "pairing_secret": secret.export(), "relay_url": "", "relay_token": ""}
    _CONFIG.write_text(json.dumps(config, indent=2), encoding="utf-8")
    return {"protocol": "zenith-fabric-v1", "device_id": "laptop", "pairing_secret": secret.export()}


@function_tool()
async def fabric_create_pairing() -> str:
    """Create a one-time pairing payload to turn into a QR code on the laptop."""
    if _node():
        return "This laptop is already paired. Revoke its current pairing before creating another."
    payload = await asyncio.to_thread(_save_pairing, SharedSecret.new())
    return "Pairing payload created. Keep it private and encode it as a QR code in the ZENITH setup screen: " + json.dumps(payload)


@function_tool()
async def fabric_status() -> str:
    node = _node()
    if not node:
        return "ZENITH is not paired to a phone yet. Create a secure pairing payload first."
    return json.dumps({"paired": True, "device_id": node.device_id, "local_capabilities": node.capabilities(),
                       "queued_events": len(node.store.pending_outbox())})


@function_tool()
async def fabric_request_action(target_device: str, action_name: str, parameters_json: str = "{}",
                                trusted_low_risk: bool = False) -> str:
    """Queue an encrypted remote device request; sensitive commands require target approval."""
    node = _node()
    if not node:
        return "ZENITH is not paired to a phone yet."
    try:
        parameters = json.loads(parameters_json)
    except json.JSONDecodeError:
        return "parameters_json must be valid JSON."
    risk = RiskLevel.LOW if trusted_low_risk else RiskLevel.SENSITIVE
    event, _ = node.request_action(ActionRequest(action_name, parameters, risk, target_device,
                                                  trusted=trusted_low_risk))
    return f"Encrypted action request {event.event_id} queued for {target_device}."


@function_tool()
async def fabric_sync() -> str:
    """Send queued encrypted requests and collect any messages waiting for this laptop."""
    node, config = _node(), _load_config()
    if not node:
        return "ZENITH is not paired to a phone yet."
    if not config.get("relay_url") or not config.get("relay_token"):
        return "Pairing exists, but relay_url and relay_token are not configured in config/fabric.json."
    try:
        transport = HttpRelayTransport(config["relay_url"], config["relay_token"])
        sent, received = await asyncio.to_thread(transport.flush, node), await asyncio.to_thread(transport.receive, node)
        return json.dumps({"sent": sent, "received": received})
    except Exception as exc:
        return f"Fabric sync failed; local tools remain available: {exc}"


@function_tool()
async def fabric_pending_call_reports() -> str:
    node = _node()
    if not node:
        return "ZENITH is not paired to a phone yet."
    reports = [event.payload for event in node.store.unread_call_reports()]
    return json.dumps({"pending_call_reports": reports})
