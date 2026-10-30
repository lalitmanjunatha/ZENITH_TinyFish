"""Tests for project_companion store."""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__) + "/../")

from project_companion.store import ProjectStore, ProjectCheckpoint
from project_companion.models import ProjectSession, ProjectType, ProjectID, ProjectStage
from memory.memory_manager import load_memory, save_memory, _empty_memory


def setup_function():
    """Reset memory before each test."""
    # Determine repo root: this file is at project_companion/tests/test_store.py
    # Two levels up is the ZENITH_V- root
    test_file_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.dirname(os.path.dirname(test_file_dir))
    # memory directory is at <repo_root>/memory/
    memory_path = os.path.join(repo_root, "memory", "long_term.json")
    with open(memory_path, "w", encoding="utf-8") as f:
        json.dump(_empty_memory(), f, indent=2)


def test_store_save_and_load_project():
    """Test saving and loading a project through the store."""
    setup_function()

    session = ProjectSession(
        id=ProjectID(value="proj_store_001"),
        name="Store Test Project",
        description="Testing project store",
        project_type=ProjectType.SOFTWARE,
        problem_statement="Test problem for store",
        goals=["goal1"],
        acceptance_criteria=["criteria1"],
        constraints=["constraint1"],
    )

    # Save project
    ProjectStore.save_project(session)

    # Load project
    loaded = ProjectStore.load_project("proj_store_001")
    assert loaded is not None
    assert loaded.name == "Store Test Project"
    assert loaded.project_type == ProjectType.SOFTWARE
    assert loaded.stage == ProjectStage.IDEATION

    # Verify key fields
    assert loaded.problem_statement == "Test problem for store"
    assert loaded.goals == ["goal1"]
    assert loaded.acceptance_criteria == ["criteria1"]
    assert loaded.constraints == ["constraint1"]

    print("  test_store_save_and_load_project PASSED")


def test_store_list_projects():
    """Test listing projects."""
    setup_function()

    # Create and save multiple projects
    for i in range(3):
        session = ProjectSession(
            id=ProjectID(value=f"proj_list_{i}"),
            name=f"Project {i}",
            description=f"Project {i} description",
            project_type=ProjectType.SOFTWARE,
            problem_statement=f"Problem {i}",
        )
        ProjectStore.save_project(session)

    # List projects
    projects = ProjectStore.list_projects()
    assert len(projects) == 3
    project_ids = {p["id"] for p in projects}
    assert any("proj_list_0" in pid for pid in project_ids)
    assert any("proj_list_1" in pid for pid in project_ids)
    assert any("proj_list_2" in pid for pid in project_ids)

    print("  test_store_list_projects PASSED")


def test_store_load_nonexistent():
    """Test loading a project that doesn't exist."""
    setup_function()

    loaded = ProjectStore.load_project("nonexistent_project")
    assert loaded is None

    print("  test_store_load_nonexistent PASSED")


def test_store_delete_project():
    """Test deleting a project."""
    setup_function()

    # Create and save a project
    session = ProjectSession(
        id=ProjectID(value="proj_delete_001"),
        name="Delete Me",
        description="Will be deleted",
        project_type=ProjectType.SOFTWARE,
        problem_statement="Problem to delete",
    )
    ProjectStore.save_project(session)

    # Delete it
    result = ProjectStore.delete_project("proj_delete_001")
    assert result == True

    # Verify it's gone
    loaded = ProjectStore.load_project("proj_delete_001")
    assert loaded is None

    print("  test_store_delete_project PASSED")


def test_store_project_ids():
    """Test getting project IDs."""
    setup_function()

    # Create and save projects
    for i in range(3):
        session = ProjectSession(
            id=ProjectID(value=f"proj_ids_{i}"),
            name=f"IDs Project {i}",
            description=f"Project {i}",
            project_type=ProjectType.SOFTWARE,
            problem_statement=f"Problem {i}",
        )
        ProjectStore.save_project(session)

    pids = ProjectStore.get_project_ids()
    assert len(pids) == 3
    for pid in pids:
        assert pid in ["proj_ids_0", "proj_ids_1", "proj_ids_2"]

    print("  test_store_project_ids PASSED")


def test_checkpoint_save_and_restore():
    """Test checkpoint save and restore."""
    setup_function()

    # Create and save a project
    session = ProjectSession(
        id=ProjectID(value="proj_ckpt_001"),
        name="Checkpoint Test",
        description="Testing checkpoints",
        project_type=ProjectType.SOFTWARE,
        problem_statement="Testing checkpoints",
    )
    ProjectStore.save_project(session)

    # Save checkpoint
    success = ProjectCheckpoint.save_checkpoint(
        "proj_ckpt_001",
        "initial",
        "initial_checkpoint",
    )
    assert success == True

    # Modify the project
    from project_companion.models import Task, TaskStatus, Milestone
    session2 = ProjectStore.load_project("proj_ckpt_001")
    if session2:
        t = Task(id="t1", name="Test task", description="A test task", stage=session2.stage)
        session2.tasks["t1"] = t
        ProjectStore.save_project(session2)

    # Restore checkpoint
    restored = ProjectCheckpoint.restore_checkpoint("proj_ckpt_001", "initial")
    assert restored is not None
    assert restored.name == "Checkpoint Test"
    # The restored project should NOT have the task we added after the checkpoint
    assert "t1" not in restored.tasks

    print("  test_checkpoint_save_and_restore PASSED")


def test_checkpoint_restore_nonexistent():
    """Test restoring a checkpoint that doesn't exist."""
    setup_function()

    restored = ProjectCheckpoint.restore_checkpoint("nonexistent", "some_checkpoint")
    assert restored is None

    print("  test_checkpoint_restore_nonexistent PASSED")


if __name__ == "__main__":
    print("Running store tests...")
    test_store_save_and_load_project()
    test_store_list_projects()
    test_store_load_nonexistent()
    test_store_delete_project()
    test_store_project_ids()
    test_checkpoint_save_and_restore()
    test_checkpoint_restore_nonexistent()
    print("\nAll store tests PASSED!")