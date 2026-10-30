"""Tests for project_companion orchestrator."""

import os
import sys

sys.path.insert(0, os.path.dirname(__file__) + "/../")

from project_companion.orchestrator import ProjectOrchestrator
from project_companion.models import (
    ProjectSession,
    ProjectType,
    ProjectStage,
    Task,
    TaskStatus,
    Milestone,
    ProjectID,
)
from project_companion.store import ProjectStore


def setup_function():
    """Reset memory before each test."""
    import json
    from memory.memory_manager import load_memory, save_memory, _empty_memory
    # Tests run from project_companion/tests/, go up two levels to ZENITH_V- root
    test_file_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.dirname(os.path.dirname(test_file_dir))
    memory_path = os.path.join(repo_root, "memory", "long_term.json")
    with open(memory_path, "w", encoding="utf-8") as f:
        json.dump(_empty_memory(), f, indent=2)


def test_orchestrator_create_project():
    """Test orchestrator create_project."""
    setup_function()

    orch = ProjectOrchestrator()
    session = orch.create_project(
        name="Created Project",
        description="A project created via orchestrator",
        project_type=ProjectType.SOFTWARE,
        problem_statement="What problem does this solve?",
        goals=["goal1", "goal2"],
        acceptance_criteria=["criteria met"],
        constraints=["constraint1"],
    )

    assert session is not None
    assert session.name == "Created Project"
    assert session.project_type == ProjectType.SOFTWARE
    assert session.stage == ProjectStage.IDEATION
    assert len(session.goals) == 2
    assert len(session.acceptance_criteria) == 1
    assert len(session.constraints) == 1

    # Verify it's persisted
    loaded = ProjectStore.load_project("proj_created_project")  # This won't work with ID scheme, check manually
    # Instead verify by listing
    projects = ProjectStore.list_projects()
    assert any("Created Project" in p["name"] for p in projects)

    print("  test_orchestrator_create_project PASSED")


def test_orchestrator_update_stage():
    """Test orchestrator update_stage."""
    setup_function()

    orch = ProjectOrchestrator()

    # Create project
    session = orch.create_project(
        name="Stage Test",
        description="Testing stage updates",
        project_type=ProjectType.SOFTWARE,
    )

    # Update stage from IDEATION to PLANNING
    updated = orch.update_stage(session.id.value, ProjectStage.PLANNING)
    assert updated is not None
    assert updated.stage == ProjectStage.PLANNING

    # Update stage from PLANNING to BUILDING
    updated2 = orch.update_stage(session.id.value, ProjectStage.BUILDING)
    assert updated2 is not None
    assert updated2.stage == ProjectStage.BUILDING

    # Try invalid transition (BUILDING -> IDEATION should be invalid per default policy)
    # But the orchestrator doesn't enforce this by default - it just saves
    # Let's test a valid transition
    updated3 = orch.update_stage(session.id.value, ProjectStage.TESTING)
    assert updated3 is not None
    assert updated3.stage == ProjectStage.TESTING

    print("  test_orchestrator_update_stage PASSED")


def test_orchestrator_add_milestone():
    """Test orchestrator add_milestone."""
    setup_function()

    orch = ProjectOrchestrator()

    session = orch.create_project(
        name="Milestone Test",
        description="Testing milestones",
        project_type=ProjectType.HARDWARE,
    )

    # Add milestones
    session = orch.add_milestone(
        project_id=session.id.value,
        name="Design",
        description="Hardware design phase",
        stage=ProjectStage.IDEATION,
    )
    assert session is not None
    assert len(session.milestones) == 1
    assert session.milestones[0].name == "Design"

    session = orch.add_milestone(
        project_id=session.id.value,
        name="Build",
        description="Build prototype",
        stage=ProjectStage.BUILDING,
    )
    assert session is not None
    assert len(session.milestones) == 2

    # Verify persistence
    loaded = ProjectStore.load_project(session.id.value)
    assert loaded is not None
    assert len(loaded.milestones) == 2

    print("  test_orchestrator_add_milestone PASSED")


def test_orchestrator_add_task():
    """Test orchestrator add_task."""
    setup_function()

    orch = ProjectOrchestrator()

    session = orch.create_project(
        name="Task Test",
        description="Testing tasks",
        project_type=ProjectType.SOFTWARE,
    )

    # Add tasks
    t1 = orch.add_task(
        project_id=session.id.value,
        name="Write code",
        description="Implement the feature",
        stage=ProjectStage.BUILDING,
    )
    assert t1 is not None
    assert t1.name == "Write code"
    assert t1.status == TaskStatus.PENDING

    t2 = orch.add_task(
        project_id=session.id.value,
        name="Run tests",
        description="Execute test suite",
        stage=ProjectStage.TESTING,
        dependencies=["Write code"],
    )
    assert t2 is not None
    assert t2.name == "Run tests"
    assert t2.dependencies == ["Write code"]

    # Verify persistence
    loaded = ProjectStore.load_project(session.id.value)
    assert loaded is not None
    assert len(loaded.tasks) == 2

    print("  test_orchestrator_add_task PASSED")


def test_orchestrator_update_task_status():
    """Test orchestrator update_task_status."""
    setup_function()

    orch = ProjectOrchestrator()

    session = orch.create_project(
        name="Task Status Test",
        description="Testing task status updates",
        project_type=ProjectType.SOFTWARE,
    )

    # Add a task
    t = orch.add_task(
        project_id=session.id.value,
        name="Test task",
        description="A test task",
        stage=ProjectStage.TESTING,
    )
    assert t is not None

    # Update status to IN_PROGRESS
    session = orch.update_task_status(
        project_id=session.id.value,
        task_id=t.id,
        status=TaskStatus.IN_PROGRESS,
    )
    assert session is not None
    assert session.tasks[t.id].status == TaskStatus.IN_PROGRESS

    # Update status to VERIFIED with test results
    session = orch.update_task_status(
        project_id=session.id.value,
        task_id=t.id,
        status=TaskStatus.VERIFIED,
        test_results=["test1 passed", "test2 passed"],
    )
    assert session is not None
    assert session.tasks[t.id].status == TaskStatus.VERIFIED
    assert session.tasks[t.id].test_results == ["test1 passed", "test2 passed"]

    # Update status to COMPLETED
    session = orch.update_task_status(
        project_id=session.id.value,
        task_id=t.id,
        status=TaskStatus.COMPLETED,
    )
    assert session is not None
    assert session.tasks[t.id].status == TaskStatus.COMPLETED

    # Verify persistence
    loaded = ProjectStore.load_project(session.id.value)
    assert loaded is not None
    assert loaded.tasks[t.id].status == TaskStatus.COMPLETED

    print("  test_orchestrator_update_task_status PASSED")


def test_orchestrator_add_confirmed_fact():
    """Test orchestrator add_confirmed_fact."""
    setup_function()

    orch = ProjectOrchestrator()

    session = orch.create_project(
        name="Fact Test",
        description="Testing confirmed facts",
        project_type=ProjectType.SOFTWARE,
    )

    # Add confirmed facts
    session = orch.add_confirmed_fact(
        project_id=session.id.value,
        key="target_frequency",
        value="433 MHz",
    )
    assert session is not None
    assert session.confirmed_facts["target_frequency"] == "433 MHz"

    session = orch.add_confirmed_fact(
        project_id=session.id.value,
        key="power_supply",
        value="5V 2A",
    )
    assert session is not None
    assert session.confirmed_facts["power_supply"] == "5V 2A"

    # Verify persistence
    loaded = ProjectStore.load_project(session.id.value)
    assert loaded is not None
    assert loaded.confirmed_facts["target_frequency"] == "433 MHz"

    print("  test_orchestrator_add_confirmed_fact PASSED")


def test_orchestrator_add_assumption():
    """Test orchestrator add_assumption."""
    setup_function()

    orch = ProjectOrchestrator()

    session = orch.create_project(
        name="Assumption Test",
        description="Testing assumptions",
        project_type=ProjectType.SOFTWARE,
    )

    # Add assumptions
    session = orch.add_assumption(
        project_id=session.id.value,
        assumption="The component will operate at 25°C",
    )
    assert session is not None
    assert len(session.assumptions) == 1
    assert session.assumptions[0] == "The component will operate at 25°C"

    session = orch.add_assumption(
        project_id=session.id.value,
        assumption="The power supply is stable",
    )
    assert session is not None
    assert len(session.assumptions) == 2

    # Verify persistence
    loaded = ProjectStore.load_project(session.id.value)
    assert loaded is not None
    assert len(loaded.assumptions) == 2

    print("  test_orchestrator_add_assumption PASSED")


def test_orchestrator_add_unresolved_question():
    """Test orchestrator add_unresolved_question."""
    setup_function()

    orch = ProjectOrchestrator()

    session = orch.create_project(
        name="Question Test",
        description="Testing unresolved questions",
        project_type=ProjectType.SOFTWARE,
    )

    # Add unresolved questions
    session = orch.add_unresolved_question(
        project_id=session.id.value,
        question="What is the component timeout?",
    )
    assert session is not None
    assert len(session.unresolved_questions) == 1

    session = orch.add_unresolved_question(
        project_id=session.id.value,
        question="What is the expected lifespan?",
    )
    assert session is not None
    assert len(session.unresolved_questions) == 2

    # Verify persistence
    loaded = ProjectStore.load_project(session.id.value)
    assert loaded is not None
    assert len(loaded.unresolved_questions) == 2

    print("  test_orchestrator_add_unresolved_question PASSED")


def test_orchestrator_add_decision():
    """Test orchestrator add_decision."""
    setup_function()

    orch = ProjectOrchestrator()

    session = orch.create_project(
        name="Decision Test",
        description="Testing decisions",
        project_type=ProjectType.SOFTWARE,
    )

    # Add decisions
    session = orch.add_decision(
        project_id=session.id.value,
        decision="Use ESP32 for WiFi connectivity",
    )
    assert session is not None
    assert len(session.decisions) == 1
    assert "ESP32" in session.decisions[0]

    session = orch.add_decision(
        project_id=session.id.value,
        decision="Use 3.3V logic level",
    )
    assert session is not None
    assert len(session.decisions) == 2

    # Verify persistence
    loaded = ProjectStore.load_project(session.id.value)
    assert loaded is not None
    assert len(loaded.decisions) == 2

    print("  test_orchestrator_add_decision PASSED")


def test_orchestrator_add_artifact():
    """Test orchestrator add_artifact."""
    setup_function()

    orch = ProjectOrchestrator()

    session = orch.create_project(
        name="Artifact Test",
        description="Testing artifacts",
        project_type=ProjectType.SOFTWARE,
    )

    # Add artifact
    session = orch.add_artifact(
        project_id=session.id.value,
        path="docs/design.pdf",
        description="Design documentation",
    )
    assert session is not None
    assert "docs/design.pdf" in session.artifacts
    assert session.artifacts["docs/design.pdf"] == "Design documentation"

    # Verify persistence
    loaded = ProjectStore.load_project(session.id.value)
    assert loaded is not None
    assert loaded.artifacts["docs/design.pdf"] == "Design documentation"

    print("  test_orchestrator_add_artifact PASSED")


def test_orchestrator_add_diagnostic_report():
    """Test orchestrator add_diagnostic_report."""
    setup_function()

    orch = ProjectOrchestrator()

    session = orch.create_project(
        name="Report Test",
        description="Testing diagnostic reports",
        project_type=ProjectType.HARDWARE,
    )

    # Add diagnostic report
    session = orch.add_diagnostic_report(
        project_id=session.id.value,
        report_path="reports/initial_inspection.md",
    )
    assert session is not None
    assert "reports/initial_inspection.md" in session.diagnostic_reports

    # Verify persistence
    loaded = ProjectStore.load_project(session.id.value)
    assert loaded is not None
    assert "reports/initial_inspection.md" in loaded.diagnostic_reports

    print("  test_orchestrator_add_diagnostic_report PASSED")


def test_orchestrator_state_summary():
    """Test orchestrator get_state_summary."""
    setup_function()

    orch = ProjectOrchestrator()

    session = orch.create_project(
        name="Summary Test",
        description="Testing state summaries",
        project_type=ProjectType.SOFTWARE,
    )

    # Add some tasks
    t1 = orch.add_task(
        project_id=session.id.value,
        name="Task 1",
        description="First task",
        stage=ProjectStage.BUILDING,
    )
    t2 = orch.add_task(
        project_id=session.id.value,
        name="Task 2",
        description="Second task",
        stage=ProjectStage.TESTING,
    )
    t3 = orch.add_task(
        project_id=session.id.value,
        name="Task 3",
        description="Third task",
        stage=ProjectStage.BUILDING,
    )

    # Mark task 2 as verified/completed
    orch.update_task_status(
        project_id=session.id.value,
        task_id=t2.id,
        status=TaskStatus.VERIFIED,
        test_results=["pass"],
    )

    # Mark task 1 as completed
    orch.update_task_status(
        project_id=session.id.value,
        task_id=t1.id,
        status=TaskStatus.COMPLETED,
    )

    # Get state summary
    summary = orch.get_state_summary(session.id.value)
    assert summary is not None
    assert summary.name == "Summary Test"
    assert summary.stage == ProjectStage.IDEATION  # No stage transition done
    assert summary.task_count == 3
    assert summary.completed_tasks == 1  # Only task 1 is COMPLETED
    assert summary.pending_tasks == 1  # task 3 (PENDING); VERIFIED is distinct from PENDING

    # The exact counts depend on status logic; just verify structure
    assert summary.next_recommended_action is not None

    print("  test_orchestrator_state_summary PASSED")


def test_orchestrator_invalid_project():
    """Test orchestrator with invalid/nonexistent project."""
    setup_function()

    orch = ProjectOrchestrator()

    # Try to update stage on nonexistent project
    result = orch.update_stage("nonexistent", ProjectStage.PLANNING)
    assert result is None

    # Try to add task to nonexistent project
    result = orch.add_task(project_id="nonexistent", name="test", description="desc", stage=ProjectStage.BUILDING)
    assert result is None

    print("  test_orchestrator_invalid_project PASSED")


def test_orchestrator_next_action_ideation():
    """Test next recommended action in IDEATION stage."""
    setup_function()

    orch = ProjectOrchestrator()

    session = orch.create_project(
        name="Next Action Test",
        description="Testing next action recommendations",
        project_type=ProjectType.SOFTWARE,
    )

    # No milestones -> should define milestones
    summary = orch.get_state_summary(session.id.value)
    assert summary.next_recommended_action == "Define milestones and break down project into tasks"

    # Add milestone
    orch.add_milestone(
        project_id=session.id.value,
        name="Design",
        description="Design phase",
        stage=ProjectStage.IDEATION,
    )

    summary = orch.get_state_summary(session.id.value)
    # Has milestones but not all completed -> complete pending milestones
    assert "Complete pending milestones" in summary.next_recommended_action

    print("  test_orchestrator_next_action_ideation PASSED")


if __name__ == "__main__":
    print("Running orchestrator tests...")
    test_orchestrator_create_project()
    test_orchestrator_update_stage()
    test_orchestrator_add_milestone()
    test_orchestrator_add_task()
    test_orchestrator_update_task_status()
    test_orchestrator_add_confirmed_fact()
    test_orchestrator_add_assumption()
    test_orchestrator_add_unresolved_question()
    test_orchestrator_add_decision()
    test_orchestrator_add_artifact()
    test_orchestrator_add_diagnostic_report()
    test_orchestrator_state_summary()
    test_orchestrator_invalid_project()
    test_orchestrator_next_action_ideation()
    print("\nAll orchestrator tests PASSED!")