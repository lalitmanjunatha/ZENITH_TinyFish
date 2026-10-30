from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from memory.memory_manager import (
    load_memory,
    save_memory,
)

from project_companion.models import ProjectSession

logger = logging.getLogger(__name__)


PROJECTS_DIR = Path(__file__).parent / "project_data"
PROJECTS_DIR.mkdir(parents=True, exist_ok=True)


class ProjectStore:
    """Persistence layer for project sessions using the existing memory system.

    Projects are stored under the 'projects' category in memory/long_term.json,
    following the same conventions as the existing memory system.
    """

    @staticmethod
    def _project_key(project_id: str) -> str:
        return f"project_{project_id}"

    @staticmethod
    def _ensure_projects_category() -> None:
        """Ensure the 'projects' category exists in memory."""
        memory = load_memory()
        if "projects" not in memory:
            memory["projects"] = {}
            save_memory(memory)

    @staticmethod
    def save_project(session: "ProjectSession") -> None:
        """Save a project session to persistent storage.

        Projects are stored as JSON strings under the 'projects' category in memory.
        Uses direct memory manipulation to avoid the remember() wrapper that
        adds {"value": ...} which breaks round-trip persistence.
        """
        try:
            key = ProjectStore._project_key(session.id.value)
            ProjectStore._ensure_projects_category()
            # Convert session to serializable dict, then serialize to JSON string
            data = session.to_dict()
            data_str = json.dumps(data, ensure_ascii=False)
            # Store directly in memory under the projects category
            # Use direct dict manipulation to avoid update_memory's _recursive_update
            # which wraps values in {"value": ...}
            memory = load_memory()
            if "projects" not in memory:
                memory["projects"] = {}
            # Store the JSON string directly (not wrapped)
            memory["projects"][key] = data_str
            save_memory(memory)
            session.updated_at = datetime.now()
            session.last_accessed = datetime.now()
            logger.info(f"Project saved: {session.name} ({session.id.value})")
        except Exception as e:
            logger.error(f"Failed to save project {session.id.value}: {e}")
            raise

    @staticmethod
    def load_project(project_id: str) -> Optional["ProjectSession"]:
        """Load a project session from persistent storage.

        Returns None if no project found with the given ID.
        """
        try:
            # Direct access to the projects category in memory
            # Projects are stored as JSON strings under keys "project_{id}"
            memory = load_memory()
            projects_data = memory.get("projects", {})
            project_key_str = f"project_{project_id}"

            if project_key_str not in projects_data:
                return None

            project_data_str = projects_data[project_key_str]
            if not project_data_str:
                return None

            # The data may be stored as a raw JSON string or as a dict (e.g., after checkpoint upgrade)
            if isinstance(project_data_str, dict):
                # Upgrade: convert dict to JSON string for persistence
                project_data_str = json.dumps(project_data_str, ensure_ascii=False)
            try:
                project_dict = json.loads(project_data_str)
            except json.JSONDecodeError:
                # Try parsing the string as-is
                project_dict = json.loads(str(project_data_str))
            session = ProjectSession.from_dict(project_dict)
            session.last_accessed = datetime.now()
            logger.info(f"Project loaded: {session.name} ({project_id})")
            return session
        except Exception as e:
            logger.error(f"Failed to load project {project_id}: {e}")
            import traceback
            traceback.print_exc()
            return None

    @staticmethod
    def list_projects() -> list[dict[str, str]]:
        """List all stored project IDs and names."""
        try:
            memory = load_memory()
            projects_data = memory.get("projects", {})
            projects = []
            for key, value in projects_data.items():
                if key.startswith("project_"):
                    # Handle both JSON string and dict formats
                    if isinstance(value, str):
                        try:
                            proj_dict = json.loads(value)
                        except Exception:
                            proj_dict = {}
                    elif isinstance(value, dict):
                        proj_dict = value
                    else:
                        proj_dict = {}
                    name = proj_dict.get("name", key)
                    projects.append({"id": key, "name": name})
            return projects
        except Exception as e:
            logger.error(f"Failed to list projects: {e}")
            return []

    @staticmethod
    def delete_project(project_id: str) -> bool:
        """Delete a project session from storage."""
        try:
            key = ProjectStore._project_key(project_id)
            memory = load_memory()
            projects_data = memory.get("projects", {})
            if key in projects_data:
                del projects_data[key]
                save_memory(memory)
            logger.info(f"Project deleted: {project_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete project {project_id}: {e}")
            return False

    @staticmethod
    def get_project_ids() -> list[str]:
        """Get list of all project IDs."""
        try:
            memory = load_memory()
            projects_data = memory.get("projects", {})
            ids = []
            for key in projects_data:
                if key.startswith("project_"):
                    pid = key.replace("project_", "", 1)
                    ids.append(pid)
            return ids
        except Exception as e:
            logger.error(f"Failed to get project IDs: {e}")
            return []


@dataclass
class ProjectCheckpoint:
    """Manages checkpoints for project state recovery.

    Provides save_checkpoint and restore_checkpoint static methods
    for project state snapshots. Uses ProjectStore for persistence.
    Checkpoints are stored in a separate 'checkpoints' category in memory,
    keeping the project data format used by ProjectStore unchanged.
    """

    @staticmethod
    def _ensure_checkpoints_category() -> None:
        """Ensure the 'checkpoints' category exists in memory."""
        memory = load_memory()
        if "checkpoints" not in memory:
            memory["checkpoints"] = {}
            save_memory(memory)

    @staticmethod
    def save_checkpoint(project_id: str, label: str, audit_action: str = "") -> bool:
        """Save a checkpoint of the current project state."""
        try:
            session = ProjectStore.load_project(project_id)
            if session is None:
                return False
            ProjectCheckpoint._ensure_checkpoints_category()
            memory = load_memory()
            checkpoints = memory.setdefault("checkpoints", {})
            project_checkpoints = checkpoints.setdefault(project_id, {})

            # Keep only last 5 checkpoints per project
            existing_checkpoints = [
                k for k in project_checkpoints.keys() if k.startswith("checkpoint_")
            ]
            if len(existing_checkpoints) >= 5:
                for old_key in existing_checkpoints[:-5]:
                    del project_checkpoints[old_key]

            checkpoint_name = f"checkpoint_{label}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            project_checkpoints[checkpoint_name] = {
                "snapshot": session.to_dict(),
                "timestamp": datetime.now().isoformat(),
            }
            save_memory(memory)
            return True
        except Exception as e:
            logger.error(f"Failed to save checkpoint for project {project_id}: {e}")
            return False

    @staticmethod
    def restore_checkpoint(project_id: str, checkpoint_name: str) -> Optional["ProjectSession"]:
        """Restore a project from a checkpoint."""
        try:
            memory = load_memory()
            checkpoints = memory.get("checkpoints", {})
            project_checkpoints = checkpoints.get(project_id, {})

            # Find the checkpoint key that matches the given name.
            # Checkpoints are stored with keys like "checkpoint_{label}_{timestamp}".
            matching_key = None
            for key in project_checkpoints.keys():
                if key.startswith(f"checkpoint_{checkpoint_name}_"):
                    matching_key = key
                    break
                # Also check exact match in case the format differs
                if key == f"checkpoint_{checkpoint_name}":
                    matching_key = key
                    break

            if matching_key is None:
                return None

            snapshot = project_checkpoints[matching_key].get("snapshot", {})
            session = ProjectSession.from_dict(snapshot)
            session.last_accessed = datetime.now()
            return session
        except Exception as e:
            logger.error(f"Failed to restore checkpoint for project {project_id}: {e}")
            import traceback
            traceback.print_exc()
            return None