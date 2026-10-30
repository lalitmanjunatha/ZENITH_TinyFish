from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class ProjectType(Enum):
    HARDWARE = "hardware"
    SOFTWARE = "software"


class ProjectStage(Enum):
    IDEATION = "ideation"
    PLANNING = "planning"
    BUILDING = "building"
    TESTING = "testing"
    VERIFYING = "verifying"
    COMPLETED = "completed"


class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    VERIFIED = "verified"
    COMPLETED = "completed"
    BLOCKED = "blocked"


@dataclass
class ProjectID:
    value: str

    def __str__(self) -> str:
        return self.value


@dataclass
class Milestone:
    id: str
    name: str
    description: str
    stage: ProjectStage
    completed: bool = False
    completed_at: Optional[datetime] = None
    notes: str = ""


@dataclass
class Task:
    id: str
    name: str
    description: str
    stage: ProjectStage
    status: TaskStatus = TaskStatus.PENDING
    dependencies: list[str] = field(default_factory=list)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    notes: str = ""
    result: str = ""
    test_results: list[str] = field(default_factory=list)
    artifacts: list[str] = field(default_factory=list)


@dataclass
class ProjectSession:
    id: ProjectID
    name: str
    description: str
    project_type: ProjectType
    problem_statement: str
    goals: list[str] = field(default_factory=list)
    acceptance_criteria: list[str] = field(default_factory=list)
    constraints: list[str] = field(default_factory=list)
    stage: ProjectStage = ProjectStage.IDEATION
    milestones: list[Milestone] = field(default_factory=list)
    tasks: dict[str, Task] = field(default_factory=dict)
    confirmed_facts: dict[str, str] = field(default_factory=dict)
    assumptions: list[str] = field(default_factory=list)
    unresolved_questions: list[str] = field(default_factory=list)
    decisions: list[str] = field(default_factory=list)
    artifacts: dict[str, str] = field(default_factory=dict)  # path -> description
    diagnostic_reports: list[str] = field(default_factory=list)
    test_results: list[dict[str, Any]] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    last_accessed: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": str(self.id),
            "name": self.name,
            "description": self.description,
            "project_type": self.project_type.value,
            "problem_statement": self.problem_statement,
            "goals": self.goals,
            "acceptance_criteria": self.acceptance_criteria,
            "constraints": self.constraints,
            "stage": self.stage.value,
            "milestones": [
                {
                    "id": m.id,
                    "name": m.name,
                    "description": m.description,
                    "stage": m.stage.value,
                    "completed": m.completed,
                    "completed_at": m.completed_at.isoformat() if m.completed_at else None,
                    "notes": m.notes,
                }
                for m in self.milestones
            ],
            "tasks": {
                tid: {
                    "id": t.id,
                    "name": t.name,
                    "description": t.description,
                    "stage": t.stage.value,
                    "status": t.status.value,
                    "dependencies": t.dependencies,
                    "started_at": t.started_at.isoformat() if t.started_at else None,
                    "completed_at": t.completed_at.isoformat() if t.completed_at else None,
                    "notes": t.notes,
                    "result": t.result,
                    "test_results": t.test_results,
                    "artifacts": t.artifacts,
                }
                for tid, t in self.tasks.items()
            },
            "confirmed_facts": self.confirmed_facts,
            "assumptions": self.assumptions,
            "unresolved_questions": self.unresolved_questions,
            "decisions": self.decisions,
            "artifacts": self.artifacts,
            "diagnostic_reports": self.diagnostic_reports,
            "test_results": self.test_results,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "last_accessed": self.last_accessed.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ProjectSession:
        id_val = ProjectID(data["id"])
        stage = ProjectStage(data["stage"])
        ms_data = data.get("milestones", [])
        milestones = []
        for m in ms_data:
            milestones.append(
                Milestone(
                    id=m["id"],
                    name=m["name"],
                    description=m["description"],
                    stage=ProjectStage(m["stage"]),
                    completed=m.get("completed", False),
                    completed_at=(
                        datetime.fromisoformat(m["completed_at"]) if m.get("completed_at") else None
                    ),
                    notes=m.get("notes", ""),
                )
            )
        tasks_data = data.get("tasks", {})
        tasks = {}
        for tid, td in tasks_data.items():
            tasks[tid] = Task(
                id=ProjectID(tid) if False else tid,  # TODO: fix typing
                name=td["name"],
                description=td["description"],
                stage=ProjectStage(td["stage"]),
                status=TaskStatus(td["status"]),
                dependencies=td.get("dependencies", []),
                started_at=(
                    datetime.fromisoformat(td["started_at"]) if td.get("started_at") else None
                ),
                completed_at=(
                    datetime.fromisoformat(td["completed_at"]) if td.get("completed_at") else None
                ),
                notes=td.get("notes", ""),
                result=td.get("result", ""),
                test_results=td.get("test_results", []),
                artifacts=td.get("artifacts", []),
            )
        return cls(
            id=id_val,
            name=data["name"],
            description=data["description"],
            project_type=ProjectType(data["project_type"]),
            problem_statement=data["problem_statement"],
            goals=data.get("goals", []),
            acceptance_criteria=data.get("acceptance_criteria", []),
            constraints=data.get("constraints", []),
            stage=stage,
            milestones=milestones,
            tasks=tasks,
            confirmed_facts=data.get("confirmed_facts", {}),
            assumptions=data.get("assumptions", []),
            unresolved_questions=data.get("unresolved_questions", []),
            decisions=data.get("decisions", []),
            artifacts=data.get("artifacts", {}),
            diagnostic_reports=data.get("diagnostic_reports", []),
            test_results=data.get("test_results", []),
            created_at=(
                datetime.fromisoformat(data["created_at"]) if data.get("created_at") else datetime.now()
            ),
            updated_at=(
                datetime.fromisoformat(data["updated_at"]) if data.get("updated_at") else datetime.now()
            ),
            last_accessed=(
                datetime.fromisoformat(data["last_accessed"]) if data.get("last_accessed") else datetime.now()
            ),
        )


@dataclass
class ProjectAuditEntry:
    id: str = field(default_factory=lambda: f"audit_{datetime.now().timestamp()}")
    timestamp: datetime = field(default_factory=datetime.now)
    action: str = ""
    details: str = ""
    before_state: Optional[dict] = None
    after_state: Optional[dict] = None
    verified: bool = False


@dataclass
class ProjectStateSummary:
    project_id: ProjectID
    name: str
    stage: ProjectStage
    task_count: int
    completed_tasks: int
    pending_tasks: int
    next_recommended_action: str
    recent_audit: Optional[ProjectAuditEntry] = None