"""
Event system for real-time UI updates during autonomous research.
"""
import json
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional


class EventType(Enum):
    # Session lifecycle
    RESEARCH_STARTED = "research_started"
    RESEARCH_COMPLETED = "research_completed"
    RESEARCH_PAUSED = "research_paused"
    RESEARCH_ERROR = "research_error"

    # Planning
    PLAN_CREATED = "plan_created"
    PLAN_UPDATED = "plan_updated"

    # Tasks
    TASK_CREATED = "task_created"
    TASK_STARTED = "task_started"
    TASK_COMPLETED = "task_completed"
    TASK_FAILED = "task_failed"

    # Web research
    SEARCH_STARTED = "search_started"
    SEARCH_COMPLETED = "search_completed"
    PAGE_OPENED = "page_opened"
    PAGE_READ = "page_read"
    PAGE_EXTRACTED = "page_extracted"
    LINK_FOLLOWED = "link_followed"
    TAB_OPENED = "tab_opened"
    TAB_CLOSED = "tab_closed"

    # Local intelligence
    LOCAL_SEARCH_STARTED = "local_search_started"
    LOCAL_SEARCH_COMPLETED = "local_search_completed"
    FILE_FOUND = "file_found"
    FILE_READ = "file_read"
    FILE_INDEXED = "file_indexed"
    CODE_ANALYZED = "code_analyzed"

    # Knowledge
    KNOWLEDGE_EXTRACTED = "knowledge_extracted"
    CLAIM_CREATED = "claim_created"
    CLAIM_VERIFIED = "claim_verified"
    EVIDENCE_FOUND = "evidence_found"
    CONTRADICTION_FOUND = "contradiction_found"
    KNOWLEDGE_GAP_IDENTIFIED = "knowledge_gap_identified"
    KNOWLEDGE_GRAPH_UPDATED = "knowledge_graph_updated"

    # Memory
    MEMORY_UPDATED = "memory_updated"

    # Report
    REPORT_GENERATED = "report_generated"

    # Status
    STATUS_UPDATE = "status_update"
    PROGRESS_UPDATE = "progress_update"
    ERROR_OCCURRED = "error_occurred"


@dataclass
class Event:
    """A single event in the research stream."""
    event_type: EventType
    data: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    session_id: str = ""
    task_id: str = ""

    def to_dict(self) -> dict:
        return {
            "event_type": self.event_type.value,
            "data": self.data,
            "timestamp": self.timestamp,
            "session_id": self.session_id,
            "task_id": self.task_id,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), default=str)


class EventBus:
    """Publish-subscribe event bus for research events."""

    def __init__(self):
        self._subscribers: Dict[EventType, List[Callable]] = {}
        self._all_subscribers: List[Callable] = []
        self._history: List[Event] = []
        self._max_history = 500

    def subscribe(self, event_type: EventType, callback: Callable):
        """Subscribe to a specific event type."""
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(callback)

    def subscribe_all(self, callback: Callable):
        """Subscribe to all events."""
        self._all_subscribers.append(callback)

    def unsubscribe(self, event_type: EventType, callback: Callable):
        """Unsubscribe from an event type."""
        if event_type in self._subscribers:
            self._subscribers[event_type] = [
                cb for cb in self._subscribers[event_type] if cb != callback
            ]

    def emit(self, event: Event):
        """Emit an event to all subscribers."""
        self._history.append(event)
        if len(self._history) > self._max_history:
            self._history = self._history[-self._max_history:]

        # Notify specific subscribers
        for callback in self._subscribers.get(event.event_type, []):
            try:
                callback(event)
            except Exception:
                pass

        # Notify all-event subscribers
        for callback in self._all_subscribers:
            try:
                callback(event)
            except Exception:
                pass

    def get_history(self, event_type: EventType = None, limit: int = 50) -> List[Event]:
        """Get event history, optionally filtered by type."""
        events = self._history
        if event_type:
            events = [e for e in events if e.event_type == event_type]
        return events[-limit:]

    def get_recent(self, limit: int = 10) -> List[Dict]:
        """Get recent events as dictionaries."""
        return [e.to_dict() for e in self._history[-limit:]]

    def clear_history(self):
        """Clear event history."""
        self._history.clear()


def create_event(
    event_type: EventType,
    session_id: str = "",
    task_id: str = "",
    **kwargs
) -> Event:
    """Helper to create and return an event."""
    return Event(
        event_type=event_type,
        data=kwargs,
        session_id=session_id,
        task_id=task_id,
    )
