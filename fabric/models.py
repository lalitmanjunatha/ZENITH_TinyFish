from __future__ import annotations

import time
import uuid
from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any


class EventType(str, Enum):
    PRESENCE = "presence"
    CAPABILITY = "capability"
    NOTIFICATION = "notification"
    ACTION_REQUEST = "action_request"
    ACTION_RESULT = "action_result"
    CONTEXT_DELTA = "context_delta"
    FILE_OFFER = "file_offer"
    FILE_REQUEST = "file_request"
    CALL_REPORT = "call_report"
    ACK = "ack"


class RiskLevel(str, Enum):
    LOW = "low"
    SENSITIVE = "sensitive"


@dataclass(frozen=True)
class DeviceEvent:
    event_type: EventType
    origin_device_id: str
    payload: dict[str, Any]
    target_device_id: str | None = None
    expires_at: float | None = None
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: float = field(default_factory=time.time)
    protocol_version: int = 1

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["event_type"] = self.event_type.value
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "DeviceEvent":
        return cls(
            event_type=EventType(data["event_type"]),
            origin_device_id=data["origin_device_id"],
            payload=data.get("payload", {}),
            target_device_id=data.get("target_device_id"),
            expires_at=data.get("expires_at"),
            event_id=data["event_id"],
            created_at=data["created_at"],
            protocol_version=data.get("protocol_version", 1),
        )

    @property
    def expired(self) -> bool:
        return self.expires_at is not None and time.time() > self.expires_at


@dataclass(frozen=True)
class ActionRequest:
    action_name: str
    parameters: dict[str, Any]
    risk: RiskLevel
    target_device_id: str
    expires_in_seconds: int = 90
    trusted: bool = False

    def payload(self) -> dict[str, Any]:
        return {
            "action_name": self.action_name,
            "parameters": self.parameters,
            "risk": self.risk.value,
            "trusted": self.trusted,
        }
