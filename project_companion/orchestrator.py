from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from .models import (
    ProjectID,
    ProjectSession,
    ProjectType,
    ProjectStage,
    Task,
    TaskStatus,
    Milestone,
    ProjectAuditEntry,
    ProjectStateSummary,
)
from .store import ProjectStore, ProjectCheckpoint

logger = logging.getLogger(__name__)


class ProjectOrchestrator:
    """Manages project lifecycle: creation, stage transitions, task management,
    and audit tracking."""

    def __init__(self):
        self._audit_counter = 0

    def create_project(
        self,
        name: str,
        description: str,
        project_type: ProjectType,
        problem_statement: str = "",
        goals: Optional[list[str]] = None,
        acceptance_criteria: Optional[list[str]] = None,
        constraints: Optional[list[str]] = None,
    ) -> ProjectSession:
        """Create a new project session and persist it."""
        session = ProjectSession(
            id=ProjectID(value=f"proj_{datetime.now().timestamp()}"),
            name=name,
            description=description,
            project_type=project_type,
            problem_statement=problem_statement,
            goals=goals or [],
            acceptance_criteria=acceptance_criteria or [],
            constraints=constraints or [],
            stage=ProjectStage.IDEATION,
        )

        # Save to persistent storage
        ProjectStore.save_project(session)

        # Record audit entry
        self._record_audit(session.id.value, "create", None, session.to_dict())

        logger.info(f"Project created: {name} ({session.id.value})")
        return session

    def get_project(self, project_id: str) -> Optional[ProjectSession]:
        """Load a project by ID."""
        session = ProjectStore.load_project(project_id)
        if session:
            self._record_audit(session.id.value, "load", None, session.to_dict())
        return session

    def update_stage(self, project_id: str, new_stage: ProjectStage) -> Optional[ProjectSession]:
        """Update the project stage and save."""
        session = ProjectStore.load_project(project_id)
        if session is None:
            return None

        old_stage = session.stage
        session.stage = new_stage
        session.updated_at = datetime.now()
        session.last_accessed = datetime.now()

        ProjectStore.save_project(session)
        self._record_audit(project_id, "stage_transition", {"from": old_stage.value, "to": new_stage.value}, session.to_dict())

        logger.info(f"Project {project_id} stage updated: {old_stage.value} -> {new_stage.value}")
        return session

    def add_milestone(
        self,
        project_id: str,
        name: str,
        description: str,
        stage: ProjectStage,
    ) -> Optional[ProjectSession]:
        """Add a milestone to the project."""
        session = ProjectStore.load_project(project_id)
        if session is None:
            return None

        milestone = Milestone(
            id=f"milestone_{len(session.milestones) + 1}",
            name=name,
            description=description,
            stage=stage,
        )
        session.milestones.append(milestone)
        session.updated_at = datetime.now()
        session.last_accessed = datetime.now()

        ProjectStore.save_project(session)
        self._record_audit(project_id, "add_milestone", f"milestone:{name}", session.to_dict())

        logger.info(f"Milestone added to {project_id}: {name}")
        return session

    def add_task(
        self,
        project_id: str,
        name: str,
        description: str,
        stage: ProjectStage,
        dependencies: Optional[list[str]] = None,
    ) -> Optional[Task]:
        """Add a task to the project and return the task object."""
        session = ProjectStore.load_project(project_id)
        if session is None:
            return None

        task_id = f"task_{len(session.tasks) + 1}"
        task = Task(
            id=task_id,
            name=name,
            description=description,
            stage=stage,
            dependencies=dependencies or [],
        )
        session.tasks[task_id] = task
        session.updated_at = datetime.now()
        session.last_accessed = datetime.now()

        ProjectStore.save_project(session)
        self._record_audit(project_id, "add_task", f"task:{name}", session.to_dict())

        logger.info(f"Task added to {project_id}: {name}")
        return task

    def update_task_status(
        self,
        project_id: str,
        task_id: str,
        status: TaskStatus,
        result: str = "",
        test_results: Optional[list[str]] = None,
    ) -> Optional[ProjectSession]:
        """Update a task's status and record results."""
        session = ProjectStore.load_project(project_id)
        if session is None:
            return None

        task = session.tasks.get(task_id)
        if task is None:
            return None

        old_status = task.status
        task.status = status
        task.result = result
        if test_results is not None:
            task.test_results = test_results

        # If task is being completed, record timestamps
        now = datetime.now()
        if status == TaskStatus.COMPLETED and task.status == TaskStatus.COMPLETED:
            task.completed_at = now
        if status == TaskStatus.VERIFIED and task.status == TaskStatus.VERIFIED:
            task.started_at = now

        session.updated_at = datetime.now()
        session.last_accessed = datetime.now()

        ProjectStore.save_project(session)
        self._record_audit(
            project_id,
            "update_task_status",
            f"task:{task_id}:{old_status.value}->{status.value}",
            session.to_dict(),
        )

        logger.info(f"Task {task_id} status updated: {old_status.value} -> {status.value}")
        return session

    def add_confirmed_fact(self, project_id: str, key: str, value: str) -> Optional[ProjectSession]:
        """Add a confirmed fact to the project."""
        session = ProjectStore.load_project(project_id)
        if session is None:
            return None

        session.confirmed_facts[key] = value
        session.updated_at = datetime.now()
        session.last_accessed = datetime.now()

        ProjectStore.save_project(session)
        self._record_audit(project_id, "add_fact", f"fact:{key}", session.to_dict())

        logger.info(f"Confirmed fact added to {project_id}: {key}={value}")
        return session

    def add_assumption(self, project_id: str, assumption: str) -> Optional[ProjectSession]:
        """Add an assumption to the project."""
        session = ProjectStore.load_project(project_id)
        if session is None:
            return None

        session.assumptions.append(assumption)
        session.updated_at = datetime.now()
        session.last_accessed = datetime.now()

        ProjectStore.save_project(session)
        self._record_audit(project_id, "add_assumption", f"assumption:{assumption[:50]}", session.to_dict())

        logger.info(f"Assumption added to {project_id}")
        return session

    def add_unresolved_question(self, project_id: str, question: str) -> Optional[ProjectSession]:
        """Add an unresolved question to the project."""
        session = ProjectStore.load_project(project_id)
        if session is None:
            return None

        session.unresolved_questions.append(question)
        session.updated_at = datetime.now()
        session.last_accessed = datetime.now()

        ProjectStore.save_project(session)
        self._record_audit(project_id, "add_question", f"question:{question[:50]}", session.to_dict())

        logger.info(f"Unresolved question added to {project_id}")
        return session

    def add_decision(self, project_id: str, decision: str) -> Optional[ProjectSession]:
        """Add a recorded decision to the project."""
        session = ProjectStore.load_project(project_id)
        if session is None:
            return None

        session.decisions.append(decision)
        session.updated_at = datetime.now()
        session.last_accessed = datetime.now()

        ProjectStore.save_project(session)
        self._record_audit(project_id, "add_decision", f"decision:{decision[:50]}", session.to_dict())

        logger.info(f"Decision added to {project_id}")
        return session

    def add_artifact(self, project_id: str, path: str, description: str) -> Optional[ProjectSession]:
        """Add an artifact reference to the project."""
        session = ProjectStore.load_project(project_id)
        if session is None:
            return None

        session.artifacts[path] = description
        session.updated_at = datetime.now()
        session.last_accessed = datetime.now()

        ProjectStore.save_project(session)
        self._record_audit(project_id, "add_artifact", f"artifact:{path}", session.to_dict())

        logger.info(f"Artifact added to {project_id}: {path}")
        return session

    def add_diagnostic_report(self, project_id: str, report_path: str) -> Optional[ProjectSession]:
        """Add a diagnostic report reference to the project."""
        session = ProjectStore.load_project(project_id)
        if session is None:
            return None

        session.diagnostic_reports.append(report_path)
        session.updated_at = datetime.now()
        session.last_accessed = datetime.now()

        ProjectStore.save_project(session)
        self._record_audit(project_id, "add_report", f"report:{report_path}", session.to_dict())

        logger.info(f"Diagnostic report added to {project_id}: {report_path}")
        return session

    def _record_audit(
        self,
        project_id: str,
        action: str,
        details: str,
        before_state: Optional[dict] = None,
        after_state: Optional[dict] = None,
    ) -> None:
        """Record an audit trail entry."""
        self._audit_counter += 1
        entry = ProjectAuditEntry(
            id=f"audit_{project_id}_{self._audit_counter}_{datetime.now().timestamp()}",
            action=action,
            details=details,
            before_state=before_state,
            after_state=after_state,
        )

        # Store audit entry in memory under a special key
        try:
            memory = ProjectStore._ensure_projects_category_loaded()
            if "audit" not in memory:
                memory["audit"] = {}
            audit_key = f"project_{project_id}"
            if audit_key not in memory["audit"]:
                memory["audit"][audit_key] = []
            memory["audit"][audit_key].append(
                {
                    "id": entry.id,
                    "timestamp": entry.timestamp.isoformat(),
                    "action": entry.action,
                    "details": entry.details,
                    "before_state_keys": list((before_state or {}).keys()) if before_state else [],
                    "after_state_keys": list((after_state or {}).keys()) if after_state else [],
                }
            )
            # Keep only last 50 audit entries per project
            audit_entries = memory["audit"][audit_key]
            if len(audit_entries) > 50:
                memory["audit"][audit_key] = audit_entries[-50:]
            from memory.memory_manager import save_memory
            save_memory(memory)
        except Exception as e:
            logger.warning(f"Failed to record audit entry: {e}")

    def get_state_summary(self, project_id: str) -> Optional[ProjectStateSummary]:
        """Get a summary of the current project state."""
        session = ProjectStore.load_project(project_id)
        if session is None:
            return None

        tasks = session.tasks
        total_tasks = len(tasks)
        completed_tasks = sum(1 for t in tasks.values() if t.status == TaskStatus.COMPLETED)
        pending_tasks = sum(1 for t in tasks.values() if t.status in (TaskStatus.PENDING, TaskStatus.IN_PROGRESS))

        # Determine next recommended action
        next_action = self._determine_next_action(session)

        # Get recent audit
        recent_audit = self._get_recent_audit(project_id)

        return ProjectStateSummary(
            project_id=session.id,
            name=session.name,
            stage=session.stage,
            task_count=total_tasks,
            completed_tasks=completed_tasks,
            pending_tasks=pending_tasks,
            next_recommended_action=next_action,
            recent_audit=recent_audit,
        )

    def _determine_next_action(self, session: ProjectSession) -> str:
        """Determine the next recommended action based on project state."""
        if session.stage == ProjectStage.IDEATION:
            if not session.milestones:
                return "Define milestones and break down project into tasks"
            if not all(m.completed for m in session.milestones):
                return "Complete pending milestones before moving to planning"
            return "Move to planning stage"

        if session.stage == ProjectStage.PLANNING:
            pending_tasks = [t for t in session.tasks.values() if t.status == TaskStatus.PENDING]
            if not pending_tasks:
                return "All planning tasks complete - move to building stage"
            return f"Start first pending task: {pending_tasks[0].name}"

        if session.stage == ProjectStage.BUILDING:
            building_tasks = [t for t in session.tasks.values() if t.stage == ProjectStage.BUILDING and t.status in (TaskStatus.PENDING, TaskStatus.IN_PROGRESS)]
            if not building_tasks:
                return "Building phase complete - move to testing stage"
            return f"Continue building: {building_tasks[0].name}"

        if session.stage == ProjectStage.TESTING:
            testing_tasks = [t for t in session.tasks.values() if t.stage == ProjectStage.TESTING]
            unverified = [t for t in testing_tasks if t.status != TaskStatus.VERIFIED]
            if not unverified:
                return "All tests verified - move to verifying stage"
            return f"Run verification for: {unverified[0].name}"

        if session.stage == ProjectStage.VERIFYING:
            return "Complete verification and review acceptance criteria"

        if session.stage == ProjectStage.COMPLETED:
            return "Project complete - conduct final review and close"

        return "Review project status"

    def _get_recent_audit(self, project_id: str) -> Optional[ProjectAuditEntry]:
        """Get the most recent audit entry for a project."""
        try:
            memory = ProjectStore._ensure_projects_category_loaded()
            audit_key = f"project_{project_id}"
            if "audit" in memory and audit_key in memory["audit"]:
                entries = memory["audit"][audit_key]
                if entries:
                    last = entries[-1]
                    return ProjectAuditEntry(
                        id=last["id"],
                        action=last["action"],
                        details=last["details"],
                    )
        except Exception:
            pass
        return None

    @staticmethod
    def checkpoint_project(project_id: str, label: str) -> bool:
        """Save a project checkpoint."""
        return ProjectCheckpoint.save_checkpoint(project_id, label, "manual_checkpoint")

    @staticmethod
    def restore_checkpoint(project_id: str, checkpoint_name: str) -> Optional[ProjectSession]:
        """Restore a project from a checkpoint."""
        return ProjectCheckpoint.restore_checkpoint(project_id, checkpoint_name)