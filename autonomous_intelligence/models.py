"""
Data models for the Autonomous Intelligence Engine.
"""
import uuid
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional


class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class EvidenceType(Enum):
    FACT = "fact"
    INFERENCE = "inference"
    HYPOTHESIS = "hypothesis"
    UNCERTAIN = "uncertain"
    CONFLICTING = "conflicting"


class SourceType(Enum):
    WEB_SEARCH = "web_search"
    WEB_PAGE = "web_page"
    LOCAL_FILE = "local_file"
    LOCAL_CODE = "local_code"
    DOCUMENT = "document"
    DATABASE = "database"
    MANUAL = "manual"


class ResearchPhase(Enum):
    INIT = "init"
    PLANNING = "planning"
    RESEARCHING = "researching"
    VERIFYING = "verifying"
    SYNTHESIZING = "synthesizing"
    REPORTING = "reporting"
    COMPLETED = "completed"
    PAUSED = "paused"
    ERROR = "error"


@dataclass
class Source:
    """A research source (URL, file path, etc.)."""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    source_type: SourceType = SourceType.WEB_PAGE
    url: str = ""
    path: str = ""
    title: str = ""
    domain: str = ""
    accessed_at: str = field(default_factory=lambda: datetime.now().isoformat())
    content_hash: str = ""
    relevance_score: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Evidence:
    """A piece of evidence from research."""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    claim: str = ""
    evidence_type: EvidenceType = EvidenceType.INFERENCE
    source: Optional[Source] = None
    context: str = ""
    confidence: float = 0.5
    supporting: List[str] = field(default_factory=list)
    contradicting: List[str] = field(default_factory=list)
    extracted_at: str = field(default_factory=lambda: datetime.now().isoformat())
    verified: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Claim:
    """A claim that may be supported or contradicted by evidence."""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    text: str = ""
    evidence_type: EvidenceType = EvidenceType.INFERENCE
    confidence: float = 0.5
    evidence_ids: List[str] = field(default_factory=list)
    source_ids: List[str] = field(default_factory=list)
    verified: bool = False
    contradictions: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class KnowledgeGap:
    """A gap in knowledge that needs research."""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    question: str = ""
    context: str = ""
    priority: int = 5
    related_claims: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    addressed: bool = False


@dataclass
class ResearchTask:
    """A single research task."""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    title: str = ""
    description: str = ""
    status: TaskStatus = TaskStatus.PENDING
    priority: int = 5
    search_queries: List[str] = field(default_factory=list)
    local_searches: List[str] = field(default_factory=list)
    urls_to_visit: List[str] = field(default_factory=list)
    results: List[str] = field(default_factory=list)
    evidence_ids: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    completed_at: str = ""
    error: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ResearchSession:
    """A complete research session."""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    objective: str = ""
    phase: ResearchPhase = ResearchPhase.INIT
    tasks: List[ResearchTask] = field(default_factory=list)
    evidence: List[Evidence] = field(default_factory=list)
    claims: List[Claim] = field(default_factory=list)
    knowledge_gaps: List[KnowledgeGap] = field(default_factory=list)
    sources: List[Source] = field(default_factory=list)
    report: Optional["ResearchReport"] = None
    start_time: str = field(default_factory=lambda: datetime.now().isoformat())
    end_time: str = ""
    error: str = ""
    stats: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ResearchReport:
    """Final research report."""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    title: str = ""
    objective: str = ""
    executive_summary: str = ""
    key_findings: List[str] = field(default_factory=list)
    local_findings: List[str] = field(default_factory=list)
    external_findings: List[str] = field(default_factory=list)
    comparison: str = ""
    evidence_summary: List[str] = field(default_factory=list)
    contradictions: List[str] = field(default_factory=list)
    knowledge_gaps: List[str] = field(default_factory=list)
    confidence: str = ""
    recommendations: List[str] = field(default_factory=list)
    sources: List[str] = field(default_factory=list)
    timeline: List[str] = field(default_factory=list)
    full_text: str = ""
    generated_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class BrowserTab:
    """Represents an active browser tab during research."""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    url: str = ""
    title: str = ""
    domain: str = ""
    status: str = "idle"
    action: str = ""
    relevance: float = 0.0
    opened_at: str = field(default_factory=lambda: datetime.now().isoformat())
