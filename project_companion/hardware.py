from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set

from project_companion.models import (
    ProjectSession,
    ProjectType,
    ProjectStage,
    Task,
    TaskStatus,
    Milestone,
    ProjectID,
    ProjectStateSummary,
    ProjectAuditEntry,
)
from project_companion.store import ProjectStore
from project_companion.policies import default_policies, ProjectSafetyPolicies, SafetyLevel

logger = logging.getLogger(__name__)


class CameraAccessStatus(Enum):
    """Status of camera access for hardware inspection."""
    NOT_REQUESTED = "not_requested"
    PENDING_USER_CONSENT = "pending_user_consent"
    ACTIVE = "active"
    PAUSED = "paused"
    DISABLED_BY_USER = "disabled_by_user"
    FAILED = "failed"


class ComponentStatus(Enum):
    """Status of a hardware component."""
    CONFIRMED = "confirmed"
    PROVISIONAL = "provisional"
    UNCERTAIN = "uncertain"
    UNAVAILABLE = "unavailable"


@dataclass
class ComponentRecord:
    """Record of a hardware component in the project."""
    name: str
    model: str = ""
    quantity: int = 1
    voltage: Optional[float] = None
    current: Optional[float] = None
    connections: List[str] = field(default_factory=list)
    pin_assignment: str = ""
    confirmed: bool = False
    status: ComponentStatus = ComponentStatus.UNCERTAIN
    notes: str = ""
    image_references: List[str] = field(default_factory=list)


@dataclass
class WiringConnection:
    """Record of a wiring connection between components."""
    from_component: str
    from_pin: str
    to_component: str
    to_pin: str
    wire_gauge: str = ""
    voltage_rating: Optional[float] = None
    current_rating: Optional[float] = None
    confirmed: bool = False
    safety_checked: bool = False


@dataclass
class HardwareInspectionResult:
    """Result of a camera-assisted hardware inspection."""
    timestamp: datetime
    observations: List[str] = field(default_factory=list)
    uncertainties: List[str] = field(default_factory=list)
    component_statuses: Dict[str, ComponentStatus] = field(default_factory=dict)
    wiring_issues: List[str] = field(default_factory=list)
    safety_concerns: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)


class HardwareProjectCompanion:
    """Companion for hardware project development workflow.

    Builds on the shared project-session engine with hardware-specific
    capabilities: camera-assisted inspection, component inventory,
    step-by-step stage tracking, and electrical safety checks.
    """

    def __init__(self, policies: Optional[ProjectSafetyPolicies] = None):
        self.policies = policies or default_policies()
        self.camera_status = CameraAccessStatus.NOT_REQUESTED
        self.component_inventory: Dict[str, ComponentRecord] = {}
        self.wiring_connections: List[WiringConnection] = []
        self.inspection_history: List[HardwareInspectionResult] = []
        self.current_stage: ProjectStage = ProjectStage.IDEATION
        self.camera_permission_granted = False

    def start_hardware_project(self, project_session: ProjectSession) -> ProjectSession:
        """Start a hardware project workflow.

        Gathers hardware-specific information through structured questions.
        """
        from project_companion.orchestrator import ProjectOrchestrator

        # Ensure project is marked as hardware type
        if project_session.project_type != ProjectType.HARDWARE:
            project_session.project_type = ProjectType.HARDWARE

        # Hardware-specific initialization
        project_session.stage = ProjectStage.IDEATION
        project_session.confirmed_facts = {}

        # Store hardware-specific artifacts
        project_session.artifacts["component_inventory"] = "pending"
        project_session.artifacts["wiring_diagram"] = "pending"
        project_session.artifacts["safety_checks"] = "pending"

        # Record audit
        ProjectStore._record_audit(
            project_session.id.value,
            "hardware_project_start",
            {"project_type": "hardware"},
            project_session.to_dict(),
        )

        logger.info(f"Hardware project started: {project_session.name}")
        return project_session

    def request_camera_access(self) -> CameraAccessStatus:
        """Request camera access for hardware inspection.

        In the existing ZENITH GUI, this would trigger a visible camera
        preview that the user must explicitly allow. The camera must not
        activate secretly or continuously without permission.
        """
        if self.camera_status == CameraAccessStatus.ACTIVE:
            return CameraAccessStatus.ACTIVE

        if self.camera_status == CameraAccessStatus.DISABLED_BY_USER:
            return CameraAccessStatus.DISABLED_BY_USER

        self.camera_status = CameraAccessStatus.PENDING_USER_CONSENT
        logger.info("Camera access requested - awaiting user consent")
        return CameraAccessStatus.PENDING_USER_CONSENT

    def grant_camera_access(self) -> CameraAccessStatus:
        """Grant camera access (called from GUI after user consent)."""
        self.camera_status = CameraAccessStatus.ACTIVE
        self.camera_permission_granted = True
        logger.info("Camera access granted by user")
        return CameraAccessStatus.ACTIVE

    def revoke_camera_access(self) -> CameraAccessStatus:
        """Revoke camera access (called when user says stop/close)."""
        self.camera_status = CameraAccessStatus.DISABLED_BY_USER
        self.camera_permission_granted = False
        # Close any active camera stream
        logger.info("Camera access revoked by user")
        return CameraAccessStatus.DISABLED_BY_USER

    def add_component(self, name: str, model: str = "", quantity: int = 1,
                      voltage: Optional[float] = None, current: Optional[float] = None,
                      connections: Optional[List[str]] = None,
                      pin_assignment: str = "") -> ComponentRecord:
        """Add a component to the project inventory."""
        component = ComponentRecord(
            name=name,
            model=model,
            quantity=quantity,
            voltage=voltage,
            current=current,
            connections=connections or [],
            pin_assignment=pin_assignment,
            status=ComponentStatus.PROVISIONAL,
        )

        self.component_inventory[name] = component
        logger.info(f"Component added: {name} ({model})")
        return component

    def confirm_component(self, name: str) -> bool:
        """Confirm a component's identity and availability."""
        if name in self.component_inventory:
            self.component_inventory[name].confirmed = True
            self.component_inventory[name].status = ComponentStatus.CONFIRMED
            logger.info(f"Component confirmed: {name}")
            return True
        return False

    def set_component_uncertain(self, name: str) -> bool:
        """Mark a component as uncertain (e.g., user unsure of model)."""
        if name in self.component_inventory:
            self.component_inventory[name].status = ComponentStatus.UNCERTAIN
            logger.info(f"Component marked uncertain: {name}")
            return True
        return False

    def add_wiring_connection(self, from_component: str, from_pin: str,
                            to_component: str, to_pin: str,
                            wire_gauge: str = "",
                            voltage_rating: Optional[float] = None,
                            current_rating: Optional[float] = None) -> Optional[WiringConnection]:
        """Add a wiring connection between components."""
        # Check both components are in inventory
        if from_component not in self.component_inventory:
            logger.warning(f"Component not in inventory: {from_component}")
            return None
        if to_component not in self.component_inventory:
            logger.warning(f"Component not in inventory: {to_component}")
            return None

        connection = WiringConnection(
            from_component=from_component,
            from_pin=from_pin,
            to_component=to_component,
            to_pin=to_pin,
            wire_gauge=wire_gauge,
            voltage_rating=voltage_rating,
            current_rating=current_rating,
        )

        self.wiring_connections.append(connection)
        logger.info(f"Wiring connection added: {from_component}:{from_pin} -> {to_component}:{to_pin}")
        return connection

    def mark_connection_safe(self, from_component: str, to_component: str) -> bool:
        """Mark a wiring connection as safety-checked."""
        for conn in self.wiring_connections:
            if (conn.from_component == from_component and
                conn.to_component == to_component):
                conn.safety_checked = True
                logger.info(f"Connection safety-checked: {from_component} -> {to_component}")
                return True
        return False

    def run_inspection(self) -> HardwareInspectionResult:
        """Run a hardware inspection using camera (if available).

        In the existing ZENITH GUI, this would:
        1. Offer to open the camera from the GUI
        2. Request user permission before camera access
        3. Let the user show the incomplete prototype
        4. Capture a frame or sequence of frames
        5. Analyze visible components, board layout, assembly stage
        6. Separate observations from uncertain guesses
        7. Ask for a closer view when important details cannot be determined
        8. Never claim a connection/component value is verified merely because
           it appears plausible in an image
        """
        result = HardwareInspectionResult(timestamp=datetime.now())

        # Check camera availability
        if self.camera_status == CameraAccessStatus.ACTIVE:
            # In a real implementation, would capture and analyze frame
            # For now, note that camera was active
            result.observations.append(
                "Camera was active during inspection. "
                "User visually assessed the prototype."
            )
            result.uncertainties.append(
                "Camera image analysis not implemented in this version; "
                "user observation relied upon."
            )
        elif self.camera_status == CameraAccessStatus.PENDING_USER_CONSENT:
            result.observations.append(
                "Camera access pending user consent. "
                "User must grant camera access via GUI before inspection."
            )
        else:
            result.observations.append(
                "Camera not activated. Inspection based on component inventory "
                "and wiring records only."
            )
            result.uncertainties.append(
                "No camera inspection performed. "
                "All assessments based on stored component data."
            )

        # Analyze component confirmations
        confirmed_components = []
        uncertain_components = []
        for name, comp in self.component_inventory.items():
            if comp.confirmed:
                confirmed_components.append(f"{name} ({comp.model})")
            else:
                uncertain_components.append(f"{name} ({comp.status.value})")

        if confirmed_components:
            result.observations.append(
                f"Confirmed components: {', '.join(confirmed_components)}"
            )
        if uncertain_components:
            result.observations.append(
                f"Uncertain components: {', '.join(uncertain_components)}. "
                "User should verify before continuing."
            )

        # Analyze wiring connections
        unsafe_connections = []
        for conn in self.wiring_connections:
            if not conn.safety_checked:
                unsafe_connections.append(
                    f"{conn.from_component}:{conn.from_pin} -> "
                    f"{conn.to_component}:{conn.to_pin}"
                )

        if unsafe_connections:
            result.safety_concerns.append(
                f"{len(unsafe_connections)} connection(s) not safety-checked: "
                f"{', '.join(unsafe_connections[:3])}"
                + ("..." if len(unsafe_connections) > 3 else "")
            )

        # Electrical safety checks
        result.recommendations.append(
            "Safety check: Verify all voltage/current ratings before powering circuit"
        )
        result.recommendations.append(
            "Safety check: Ensure no exposed conductors or damaged insulation"
        )
        result.recommendations.append(
            "Safety check: Confirm proper grounding for any AC mains connections"
        )

        # Store inspection result
        self.inspection_history.append(result)

        logger.info(f"Hardware inspection completed: {len(result.observations)} observations, "
                      f"{len(result.safety_concerns)} safety concerns")
        return result

    def save_component_inventory(self, project_session: ProjectSession) -> None:
        """Save the current component inventory to the project session."""
        inventory_data = {}
        for name, comp in self.component_inventory.items():
            inventory_data[name] = {
                "model": comp.model,
                "quantity": comp.quantity,
                "voltage": comp.voltage,
                "current": comp.current,
                "confirmed": comp.confirmed,
                "status": comp.status.value,
                "notes": comp.notes,
                "connections": comp.connections,
                "pin_assignment": comp.pin_assignment,
            }
        project_session.artifacts["component_inventory"] = inventory_data
        logger.info(f"Component inventory saved for project {project_session.id.value}")

    def save_wiring_diagram(self, project_session: ProjectSession) -> None:
        """Save the current wiring connections to the project session."""
        wiring_data = []
        for conn in self.wiring_connections:
            wiring_data.append({
                "from_component": conn.from_component,
                "from_pin": conn.from_pin,
                "to_component": conn.to_component,
                "to_pin": conn.to_pin,
                "wire_gauge": conn.wire_gauge,
                "voltage_rating": conn.voltage_rating,
                "current_rating": conn.current_rating,
                "safety_checked": conn.safety_checked,
            })
        project_session.artifacts["wiring_diagram"] = wiring_data
        logger.info(f"Wiring diagram saved for project {project_session.id.value}")

    def update_stage(self, project_session: ProjectSession, new_stage: ProjectStage) -> ProjectSession:
        """Update the hardware project stage with hardware-specific logic."""
        from project_companion.orchestrator import ProjectOrchestrator

        # Hardware-specific stage transitions
        valid_transitions = {
            ProjectStage.IDEATION: [ProjectStage.PLANNING, ProjectStage.IDEATION],
            ProjectStage.PLANNING: [ProjectStage.BUILDING, ProjectStage.IDEATION],
            ProjectStage.BUILDING: [ProjectStage.TESTING, ProjectStage.PLANNING],
            ProjectStage.TESTING: [ProjectStage.VERIFYING, ProjectStage.BUILDING],
            ProjectStage.VERIFYING: [ProjectStage.COMPLETED, ProjectStage.TESTING],
            ProjectStage.COMPLETED: [ProjectStage.COMPLETED],
        }

        current = project_session.stage
        allowed = valid_transitions.get(current, [])
        if new_stage not in allowed:
            logger.warning(
                f"Invalid stage transition: {current.value} -> {new_stage.value}. "
                f"Allowed from {current.value}: {[a.value for a in allowed]}"
            )
            return project_session

        old_stage = project_session.stage
        project_session.stage = new_stage
        project_session.updated_at = datetime.now()

        # Save hardware-specific artifacts at certain stages
        if new_stage == ProjectStage.BUILDING:
            self.save_component_inventory(project_session)
            project_session.artifacts["wiring_diagram"] = "saved_at_building_stage"
        elif new_stage == ProjectStage.TESTING:
            self.save_wiring_diagram(project_session)

        ProjectStore._record_audit(
            project_session.id.value,
            "stage_transition",
            {"from": old_stage.value, "to": new_stage.value},
            project_session.to_dict(),
        )

        logger.info(f"Hardware project stage updated: {old_stage.value} -> {new_stage.value}")
        return project_session

    def get_next_recommended_action(self, project_session: ProjectSession) -> str:
        """Get the next recommended action for the hardware project."""
        stage = project_session.stage

        if stage == ProjectStage.IDEATION:
            # Check if we have confirmed components
            confirmed = [name for name, c in self.component_inventory.items() if c.confirmed]
            if not confirmed:
                return "Identify and confirm hardware components before planning"
            if len(confirmed) == 1:
                return f"Prepare for building: component confirmed: {confirmed[0]}"
            return "Components confirmed - plan the build sequence"

        if stage == ProjectStage.PLANNING:
            pending_tasks = [t for t in project_session.tasks.values()
                           if t.status == TaskStatus.PENDING]
            if pending_tasks:
                return f"Start first pending task: {pending_tasks[0].name}"
            return "All planning tasks complete - move to building stage"

        if stage == ProjectStage.BUILDING:
            building_tasks = [t for t in project_session.tasks.values()
                            if t.stage == ProjectStage.BUILDING
                            and t.status in (TaskStatus.PENDING, TaskStatus.IN_PROGRESS)]
            if not building_tasks:
                return "Building phase complete - move to testing stage"
            return f"Continue building: {building_tasks[0].name}"

        if stage == ProjectStage.TESTING:
            testing_tasks = [t for t in project_session.tasks.values()
                           if t.stage == ProjectStage.TESTING]
            unverified = [t for t in testing_tasks if t.status != TaskStatus.VERIFIED]
            if not unverified:
                return "All tests verified - move to verifying stage"
            return f"Run verification for: {unverified[0].name}"

        if stage == ProjectStage.VERIFYING:
            return "Complete verification and review acceptance criteria"

        if stage == ProjectStage.COMPLETED:
            return "Project complete - conduct final review and close"

        return "Review project status"