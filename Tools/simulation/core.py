"""
ZENITH Simulation Core
Central engine that manages all simulations with modular architecture.
"""

import time
import json
import math
import threading
from enum import Enum
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, List, Optional, Callable

try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches
    from matplotlib.figure import Figure
    import matplotlib.animation as animation
    HAS_MPL = True
except ImportError:
    HAS_MPL = False

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False


# =========================================
# SIMULATION STATE
# =========================================

class SimState(Enum):
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPED = "stopped"
    ERROR = "error"


# =========================================
# BASE SIMULATION CLASS
# =========================================

class BaseSimulation:
    """
    Base class for all simulations.
    Every simulation module inherits from this.
    """

    SIM_TYPE = "base"
    SIM_NAME = "Base Simulation"

    def __init__(self, params: Dict[str, Any] = None):
        self.params = params or {}
        self.state = SimState.IDLE
        self.time = 0.0
        self.step_count = 0
        self.history = []
        self.metrics = {}
        self.created_at = datetime.now().isoformat()
        self._events = []

    def initialize(self):
        """Set up the simulation. Override in subclass."""
        self.state = SimState.IDLE
        self.time = 0.0
        self.step_count = 0
        self.history = []
        self.metrics = {}
        self._events = []

    def step(self, dt: float = 0.02):
        """Advance simulation by one timestep. Override in subclass."""
        self.time += dt
        self.step_count += 1

    def get_state(self) -> Dict[str, Any]:
        """Return current simulation state. Override in subclass."""
        return {
            "type": self.SIM_TYPE,
            "name": self.SIM_NAME,
            "state": self.state.value,
            "time": self.time,
            "step_count": self.step_count,
            "params": self.params,
            "metrics": self.metrics,
        }

    def set_param(self, name: str, value: Any):
        """Modify a parameter by name."""
        if name in self.params:
            self.params[name] = value
            self._log_event(f"param_changed:{name}={value}")
        else:
            self.params[name] = value
            self._log_event(f"param_added:{name}={value}")

    def reset(self):
        """Reset simulation to initial state."""
        self.initialize()

    def start(self):
        self.state = SimState.RUNNING
        self._log_event("started")

    def pause(self):
        self.state = SimState.PAUSED
        self._log_event("paused")

    def resume(self):
        self.state = SimState.RUNNING
        self._log_event("resumed")

    def stop(self):
        self.state = SimState.STOPPED
        self._log_event("stopped")

    def get_history(self) -> List[Dict]:
        return self.history

    def get_metrics(self) -> Dict[str, Any]:
        return self.metrics

    def export_data(self) -> Dict[str, Any]:
        return {
            "meta": self.get_state(),
            "history": self.history[-1000:],
            "metrics": self.metrics,
            "events": self._events[-100:],
        }

    def _log_event(self, event: str):
        self._events.append({"time": self.time, "event": event})

    def _record(self, data: Dict[str, Any]):
        data["t"] = self.time
        data["step"] = self.step_count
        self.history.append(data)


# =========================================
# VISUALIZATION HELPERS
# =========================================

class VisHelper:
    """Shared visualization utilities."""

    COLORS = {
        "bg": "#0a0a0f",
        "panel": "#111827",
        "grid": "#1e293b",
        "text": "#e2e8f0",
        "accent": "#06b6d4",
        "red": "#ef4444",
        "green": "#22c55e",
        "blue": "#3b82f6",
        "yellow": "#eab308",
        "purple": "#a855f7",
        "orange": "#f97316",
        "pink": "#ec4899",
        "cyan": "#06b6d4",
    }

    @staticmethod
    def create_figure(figsize=(10, 7), title=""):
        if not HAS_MPL:
            return None, None
        fig, ax = plt.subplots(figsize=figsize)
        fig.patch.set_facecolor(VisHelper.COLORS["bg"])
        ax.set_facecolor(VisHelper.COLORS["bg"])
        ax.tick_params(colors=VisHelper.COLORS["text"], labelsize=9)
        for spine in ax.spines.values():
            spine.set_color(VisHelper.COLORS["grid"])
        if title:
            ax.set_title(title, color=VisHelper.COLORS["text"], fontsize=14, pad=15, fontweight='bold')
        return fig, ax

    @staticmethod
    def save_figure(fig, filename: str, output_dir: Path) -> str:
        filepath = output_dir / filename
        output_dir.mkdir(parents=True, exist_ok=True)
        fig.savefig(str(filepath), dpi=130, bbox_inches='tight',
                    facecolor=fig.get_facecolor(), edgecolor='none')
        plt.close(fig)
        return str(filepath)

    @staticmethod
    def label_axes(ax, x_label="", y_label=""):
        if x_label:
            ax.set_xlabel(x_label, color=VisHelper.COLORS["text"], fontsize=11)
        if y_label:
            ax.set_ylabel(y_label, color=VisHelper.COLORS["text"], fontsize=11)

    @staticmethod
    def add_grid(ax, alpha=0.3):
        ax.grid(True, alpha=alpha, color=VisHelper.COLORS["grid"], linestyle='--')


# =========================================
# SIMULATION MANAGER (CORE ENGINE)
# =========================================

class SimulationManager:
    """
    Central engine that manages all simulations.
    Supports starting, stopping, pausing, saving, loading, and running multiple simulations.
    """

    def __init__(self, output_dir: Path = None):
        self.output_dir = output_dir or Path.home() / "Downloads" / "zenith_simulations"
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.active_simulation: Optional[BaseSimulation] = None
        self.sim_history: List[Dict] = []
        self.saved_simulations: Dict[str, Dict] = {}
        self.sim_registry: Dict[str, type] = {}

        self.vis = VisHelper()

    def register_simulation(self, sim_type: str, sim_class: type):
        """Register a new simulation type."""
        self.sim_registry[sim_type] = sim_class

    def create(self, sim_type: str, params: Dict[str, Any] = None) -> str:
        """Create and initialize a new simulation."""
        if sim_type not in self.sim_registry:
            available = list(self.sim_registry.keys())
            return f"Unknown simulation: {sim_type}. Available: {available}"

        sim_class = self.sim_registry[sim_type]
        self.active_simulation = sim_class(params or {})
        self.active_simulation.initialize()
        self.active_simulation.start()
        return f"Simulation '{sim_type}' created and started."

    def step(self, n_steps: int = 1, dt: float = 0.02) -> str:
        """Advance active simulation."""
        if not self.active_simulation:
            return "No active simulation."
        for _ in range(n_steps):
            self.active_simulation.step(dt)
        return f"Advanced {n_steps} steps. t={self.active_simulation.time:.3f}s"

    def run(self, duration: float = 5.0, dt: float = 0.02) -> str:
        """Run simulation for a duration."""
        if not self.active_simulation:
            return "No active simulation."
        steps = int(duration / dt)
        self.active_simulation.start()
        for _ in range(steps):
            self.active_simulation.step(dt)
        self.active_simulation.stop()
        return f"Simulation completed. {steps} steps, t={self.active_simulation.time:.3f}s"

    def pause(self) -> str:
        if not self.active_simulation:
            return "No active simulation."
        self.active_simulation.pause()
        return "Simulation paused."

    def resume(self) -> str:
        if not self.active_simulation:
            return "No active simulation."
        self.active_simulation.resume()
        return "Simulation resumed."

    def stop(self) -> str:
        if not self.active_simulation:
            return "No active simulation."
        self.active_simulation.stop()
        return "Simulation stopped."

    def reset(self) -> str:
        if not self.active_simulation:
            return "No active simulation."
        self.active_simulation.reset()
        return "Simulation reset."

    def set_param(self, name: str, value) -> str:
        if not self.active_simulation:
            return "No active simulation."
        self.active_simulation.set_param(name, value)
        return f"Parameter '{name}' set to {value}."

    def get_state(self) -> Dict:
        if not self.active_simulation:
            return {"status": "no active simulation"}
        return self.active_simulation.get_state()

    def visualize(self) -> str:
        """Generate visualization of active simulation."""
        if not self.active_simulation:
            return "No active simulation."
        sim = self.active_simulation
        if hasattr(sim, 'visualize'):
            return sim.visualize(self.output_dir)
        return f"Simulation '{sim.SIM_TYPE}' has no visualization."

    def explain(self) -> str:
        """Explain the current simulation."""
        if not self.active_simulation:
            return "No active simulation."
        sim = self.active_simulation
        state = sim.get_state()
        lines = [
            f"Simulation: {sim.SIM_NAME}",
            f"Type: {sim.SIM_TYPE}",
            f"State: {state['state']}",
            f"Time: {sim.time:.3f}s",
            f"Steps: {sim.step_count}",
        ]
        if sim.metrics:
            lines.append("Metrics:")
            for k, v in sim.metrics.items():
                lines.append(f"  {k}: {v}")
        if hasattr(sim, 'explain'):
            lines.append(sim.explain())
        return "\n".join(lines)

    def save(self, name: str = None) -> str:
        if not self.active_simulation:
            return "No active simulation."
        sim = self.active_simulation
        save_name = name or f"{sim.SIM_TYPE}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.saved_simulations[save_name] = sim.export_data()
        filepath = self.output_dir / f"{save_name}.json"
        with open(filepath, 'w') as f:
            json.dump(sim.export_data(), f, indent=2, default=str)
        return f"Simulation saved: {filepath}"

    def get_available(self) -> List[str]:
        return list(self.sim_registry.keys())

    def list_saved(self) -> List[str]:
        return list(self.saved_simulations.keys())

    def run_n_times(self, n: int = 10, duration: float = 2.0, dt: float = 0.02) -> str:
        """Run simulation N times and collect results."""
        if not self.active_simulation:
            return "No active simulation."
        results = []
        for i in range(n):
            self.active_simulation.reset()
            self.active_simulation.start()
            steps = int(duration / dt)
            for _ in range(steps):
                self.active_simulation.step(dt)
            self.active_simulation.stop()
            results.append(self.active_simulation.get_metrics())
        self.sim_history.append({
            "type": self.active_simulation.SIM_TYPE,
            "runs": n,
            "results": results,
            "timestamp": datetime.now().isoformat()
        })
        return f"Completed {n} runs. Results stored."


# =========================================
# GLOBAL ENGINE INSTANCE
# =========================================

_engine = SimulationManager()


def get_engine() -> SimulationManager:
    return _engine
