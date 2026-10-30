from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from .models import ProjectSession, ProjectType, ProjectStage, Task, TaskStatus

logger = logging.getLogger(__name__)


class SafetyLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class SafetyPolicy:
    name: str
    description: str
    safety_level: SafetyLevel
    requires_authorization: bool = False
    authorized_by: Optional[str] = None
    authorized_at: Optional[datetime] = None
    enabled: bool = True

    def check(self, session: ProjectSession, context: dict[str, Any]) -> bool:
        """Check if this policy applies to the given context.
        Returns True if the action is allowed, False if blocked."""
        if not self.enabled:
            return True
        return self._evaluate(session, context)

    def _evaluate(self, session: ProjectSession, context: dict[str, Any]) -> bool:
        """Subclasses should implement this method."""
        return True


@dataclass
class ProjectSafetyPolicies:
    """Collection of safety policies for project operations."""

    policies: list[SafetyPolicy] = field(default_factory=list)

    def add(self, policy: SafetyPolicy) -> None:
        self.policies.append(policy)

    def check_all(self, session: ProjectSession, context: dict[str, Any]) -> dict[str, bool]:
        """Run all policies and return a dict of policy_name -> allowed."""
        results: dict[str, bool] = {}
        for policy in self.policies:
            try:
                allowed = policy.check(session, context)
                results[policy.name] = allowed
            except Exception as e:
                logger.error(f"Policy '{policy.name}' error: {e}")
                results[policy.name] = False
        return results

    def is_any_blocked(self, session: ProjectSession, context: dict[str, Any]) -> bool:
        """Return True if any policy blocks the action."""
        results = self.check_all(session, context)
        return any(not allowed for allowed in results.values())


# ── Concrete Policies ────────────────────────────────────────────────

class StageTransitionPolicy(SafetyPolicy):
    """Policy: Only allow stage transitions in a valid progression."""

    def _evaluate(self, session: ProjectSession, context: dict[str, Any]) -> bool:
        from .orchestrator import ProjectOrchestrator
        new_stage: ProjectStage = context.get("new_stage", ProjectStage.IDEATION)

        # Define valid transitions
        valid_transitions = {
            ProjectStage.IDEATION: [ProjectStage.PLANNING, ProjectStage.IDEATION],
            ProjectStage.PLANNING: [ProjectStage.BUILDING, ProjectStage.IDEATION],
            ProjectStage.BUILDING: [ProjectStage.TESTING, ProjectStage.PLANNING],
            ProjectStage.TESTING: [ProjectStage.VERIFYING, ProjectStage.BUILDING],
            ProjectStage.VERIFYING: [ProjectStage.COMPLETED, ProjectStage.TESTING],
            ProjectStage.COMPLETED: [ProjectStage.COMPLETED],
        }

        current = session.stage
        allowed_transitions = valid_transitions.get(current, [])
        return new_stage in allowed_transitions


class TaskCompletionPolicy(SafetyPolicy):
    """Policy: Tasks cannot be marked COMPLETED without test results if testing stage."""

    def _evaluate(self, session: ProjectSession, context: dict[str, Any]) -> bool:
        task: Task = context.get("task")
        if task is None:
            return True

        # If task is in testing stage and being completed, require verification
        if task.stage == ProjectStage.TESTING and task.status == TaskStatus.COMPLETED:
            if not task.test_results:
                logger.warning(
                    f"Task {task.id} marked COMPLETED in TESTING stage without test results"
                )
                return False
        return True


class FactInsertionPolicy(SafetyPolicy):
    """Policy: Confirmed facts must have non-empty values."""

    def _evaluate(self, session: ProjectSession, context: dict[str, Any]) -> bool:
        key: str = context.get("key", "")
        value: str = context.get("value", "")
        if not key or not value:
            return False
        return True


class AssumptionLimitsPolicy(SafetyPolicy):
    """Policy: Limit the number of assumptions in a project."""

    max_assumptions: int = 20

    def _evaluate(self, session: ProjectSession, context: dict[str, Any]) -> bool:
        current_count = len(session.assumptions)
        if current_count >= self.max_assumptions:
            logger.warning(
                f"Assumption limit reached ({self.max_assumptions}) for project {session.id.value}"
            )
            return False
        return True


class TaskDependencyPolicy(SafetyPolicy):
    """Policy: Prevent circular task dependencies."""

    def _evaluate(self, session: ProjectSession, context: dict[str, Any]) -> bool:
        task_id: str = context.get("task_id", "")
        new_dependency: str = context.get("new_dependency", "")

        tasks = session.tasks
        if task_id not in tasks or new_dependency not in tasks:
            return True

        # Check if adding this dependency would create a cycle
        visited: set[str] = set()

        def _has_cycle(current_id: str, target_id: str, path: set[str]) -> bool:
            if current_id == target_id:
                return True
            if current_id in path:
                return False
            path.add(current_id)
            task = tasks.get(current_id)
            if task is None or not task.dependencies:
                return False
            for dep in task.dependencies:
                if _has_cycle(dep, target_id, path):
                    return True
            return False

        # Check if adding new_dependency to task task_id creates a cycle
        # by seeing if task new_dependency can reach task_id
        target_task = tasks.get(new_dependency)
        if target_task is None:
            return True

        # Temporarily add the dependency and check
        original_deps = target_task.dependencies.copy()
        target_task.dependencies.append(task_id)
        try:
            # Check if task_id can reach new_dependency (would create cycle)
            result = _has_cycle(new_dependency, task_id, set())
            return not result  # If cycle detected, return False
        finally:
            target_task.dependencies = original_deps


# ── Pre-configured Policy Sets ────────────────────────────────────────

def default_policies() -> ProjectSafetyPolicies:
    """Create a default set of safety policies for project operations."""
    policies = ProjectSafetyPolicies()

    policies.add(StageTransitionPolicy(
        name="stage_transition",
        description="Only allow valid stage transitions",
        safety_level=SafetyLevel.MEDIUM,
    ))

    policies.add(TaskCompletionPolicy(
        name="task_completion",
        description="Require test results for tasks in testing stage",
        safety_level=SafetyLevel.MEDIUM,
    ))

    policies.add(FactInsertionPolicy(
        name="fact_insertion",
        description="Confirmed facts must have non-empty values",
        safety_level=SafetyLevel.LOW,
    ))

    policies.add(AssumptionLimitsPolicy(
        name="assumption_limits",
        description="Maximum 20 assumptions per project",
        safety_level=SafetyLevel.LOW,
    ))

    return policies