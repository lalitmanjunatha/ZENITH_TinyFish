"""
ZENITH Autonomous Intelligence Engine
=====================================
An agentic research system that autonomously investigates topics using
the Internet and local computer files, producing cited intelligence reports.

Architecture:
  Director -> Planner -> Research Loop -> Knowledge Engine -> Report

Components:
  director.py      - Orchestrates entire research sessions
  planner.py       - Generates and adapts research plans
  loop.py          - Core autonomous research loop
  web_engine.py    - Internet research (search, scrape, extract)
  local_engine.py  - Local file intelligence (search, read, index)
  knowledge.py     - Evidence tracking, verification, contradiction detection
  knowledge_graph.py - Entity/relationship graph
  permissions.py   - Safety and permission system
  events.py        - Real-time event stream for UI
  config.py        - Configuration management
  models.py        - Data models (Evidence, Claim, Task, Session, etc.)
"""

__version__ = "1.0.0"
__author__ = "Lalit Manjunatha"

from .config import ResearchConfig
from .director import ResearchDirector
from .models import (
    ResearchSession, ResearchTask, Evidence, Claim,
    KnowledgeGap, ResearchReport, TaskStatus, EvidenceType
)
from .events import EventBus, Event, EventType

__all__ = [
    "ResearchConfig", "ResearchDirector",
    "ResearchSession", "ResearchTask", "Evidence", "Claim",
    "KnowledgeGap", "ResearchReport", "TaskStatus", "EvidenceType",
    "EventBus", "Event", "EventType",
]
