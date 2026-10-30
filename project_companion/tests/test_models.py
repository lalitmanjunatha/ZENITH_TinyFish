"""Tests for project_companion models."""

import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(__file__) + "/../")

from project_companion.models import (
    ProjectSession,
    ProjectType,
    ProjectStage,
    Task,
    TaskStatus,
    Milestone,
    ProjectID,
    ProjectAuditEntry,
    ProjectStateSummary,
)


def test_project_id():
    pid = ProjectID(value="test_123")
    assert str(pid) == "test_123"


def test_project_session_creation():
    """Test basic project session creation and persistence round-trip."""
    session = ProjectSession(
        id=ProjectID(value="proj_001"),
        name="Test Project",
        description="A test project",
        project_type=ProjectType.SOFTWARE,
        problem_statement="Test problem",
        goals=["goal1", "goal2"],
        acceptance_criteria=["criteria1"],
        constraints=["constraint1"],
    )

    # Verify initial state
    assert session.name == "Test Project"
    assert session.project_type == ProjectType.SOFTWARE
    assert session.stage == ProjectStage.IDEATION
    assert len(session.goals) == 2
    assert len(session.acceptance_criteria) == 1
    assert len(session.constraints) == 1

    # Test to_dict / from_dict round-trip
    data = session.to_dict()
    assert "id" in data
    assert "name" in data
    assert "project_type" in data
    assert "stage" in data

    # Round-trip
    restored = ProjectSession.from_dict(data)
    assert restored.name == session.name
    assert restored.project_type == session.project_type
    assert restored.stage == session.stage
    assert restored.problem_statement == session.problem_statement
    assert restored.goals == session.goals
    assert restored.acceptance_criteria == session.acceptance_criteria
    assert restored.constraints == session.constraints

    print("  test_project_session_creation PASSED")


def test_milestone():
    """Test Milestone dataclass."""
    ms = Milestone(
        id="ms_001",
        name="Design",
        description="Design phase",
        stage=ProjectStage.IDEATION,
    )
    assert ms.name == "Design"
    assert ms.stage == ProjectStage.IDEATION
    assert ms.completed == False

    # Test completed milestone
    ms2 = Milestone(
        id="ms_002",
        name="Build",
        description="Build phase",
        stage=ProjectStage.BUILDING,
        completed=True,
        completed_at="2024-01-15T10:30:00",
    )
    assert ms2.completed == True
    assert ms2.completed_at is not None


def test_task():
    """Test Task dataclass."""
    task = Task(
        id="task_001",
        name="Write code",
        description="Implement the feature",
        stage=ProjectStage.BUILDING,
    )
    assert task.name == "Write code"
    assert task.status == TaskStatus.PENDING
    assert task.dependencies == []

    # Test with dependencies
    task2 = Task(
        id="task_002",
        name="Run tests",
        description="Execute test suite",
        stage=ProjectStage.TESTING,
        dependencies=["task_001"],
    )
    assert task2.dependencies == ["task_001"]

    # Test status update
    task2.status = TaskStatus.IN_PROGRESS
    assert task2.status == TaskStatus.IN_PROGRESS
    task2.result = "passed"
    assert task2.result == "passed"

    # Test VERIFIED status
    task2.status = TaskStatus.VERIFIED
    assert task2.status == TaskStatus.VERIFIED


def test_project_audit_entry():
    """Test ProjectAuditEntry dataclass."""
    entry = ProjectAuditEntry(
        action="test_action",
        details="test details",
    )
    assert entry.action == "test_action"
    assert entry.details == "test details"

    # With ID
    entry2 = ProjectAuditEntry(
        id="audit_001",
        action="test_action",
    )
    assert entry2.id == "audit_001"


def test_project_state_summary():
    """Test ProjectStateSummary construction."""
    summary = ProjectStateSummary(
        project_id=ProjectID(value="proj_001"),
        name="Test Project",
        stage=ProjectStage.BUILDING,
        task_count=5,
        completed_tasks=2,
        pending_tasks=3,
        next_recommended_action="Continue building",
    )
    assert summary.project_id.value == "proj_001"
    assert summary.stage == ProjectStage.BUILDING
    assert summary.task_count == 5
    assert summary.completed_tasks == 2
    assert summary.pending_tasks == 3


def test_project_state_summary_with_recent_audit():
    """Test ProjectStateSummary with recent audit."""
    audit_entry = ProjectAuditEntry(
        id="audit_001",
        action="create",
        details="Project created",
    )
    summary = ProjectStateSummary(
        project_id=ProjectID(value="proj_001"),
        name="Test Project",
        stage=ProjectStage.IDEATION,
        task_count=0,
        completed_tasks=0,
        pending_tasks=0,
        next_recommended_action="Define milestones",
        recent_audit=audit_entry,
    )
    assert summary.recent_audit is not None
    assert summary.recent_audit.action == "create"


def test_project_session_with_tasks_and_milestones():
    """Test project session with tasks and milestones round-trip."""
    session = ProjectSession(
        id=ProjectID(value="proj_002"),
        name="Complex Project",
        description="A complex test project",
        project_type=ProjectType.HARDWARE,
        problem_statement="Build a hardware device",
        goals=["Functional device", "Safe operation"],
        acceptance_criteria=["Device works", "No safety issues"],
        constraints=["Budget < $100", "Power < 12V"],
        stage=ProjectStage.PLANNING,
    )

    # Add milestones
    session.add_milestone = None  # Skip, we'll set directly
    from project_companion.models import Milestone
    ms1 = Milestone(id="ms_1", name="Design", description="Hardware design", stage=ProjectStage.IDEATION)
    ms2 = Milestone(id="ms_2", name="Build", description="Build prototype", stage=ProjectStage.BUILDING, completed=True)
    session.milestones = [ms1, ms2]

    # Add tasks
    from project_companion.models import Task, TaskStatus
    t1 = Task(id="t1", name="Schematic", description="Create schematic", stage=ProjectStage.PLANNING)
    t2 = Task(id="t2", name="PCB", description="Design PCB", stage=ProjectStage.BUILDING, dependencies=["t1"])
    t3 = Task(id="t3", name="Assembly", description="Build assembly", stage=ProjectStage.BUILDING)
    t4 = Task(id="t4", name="Test", description="Test device", stage=ProjectStage.TESTING, dependencies=["t2"])
    t5 = Task(id="t5", name="Documentation", description="Write docs", stage=ProjectStage.IDEATION)

    session.tasks = {"t1": t1, "t2": t2, "t3": t3, "t4": t4, "t5": t5}

    # Round-trip
    data = session.to_dict()
    restored = ProjectSession.from_dict(data)

    assert restored.name == session.name
    assert len(restored.milestones) == 2
    assert len(restored.tasks) == 5
    assert restored.stage == session.stage
    assert restored.project_type == session.project_type

    # Check task details
    assert "t1" in restored.tasks
    assert restored.tasks["t1"].name == "Schematic"
    assert restored.tasks["t2"].dependencies == ["t1"]
    assert restored.tasks["t4"].stage == ProjectStage.TESTING

    print("  test_project_session_with_tasks_and_milestones PASSED")


if __name__ == "__main__":
    print("Running model tests...")
    test_project_id()
    test_project_session_creation()
    test_milestone()
    test_task()
    test_project_audit_entry()
    test_project_state_summary()
    test_project_state_summary_with_recent_audit()
    test_project_session_with_tasks_and_milestones()
    print("\nAll model tests PASSED!")