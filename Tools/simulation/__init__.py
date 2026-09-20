"""ZENITH Simulation System - Modular Architecture"""
from .core import SimulationManager, BaseSimulation, SimState, VisHelper, get_engine

# Register all simulation modules
from . import physics
from . import mathematics
from . import ai_ml
from . import electronics
from . import biology
from . import robotics
from . import compsci
from . import visualization_3d
from . import signal

__all__ = [
    "SimulationManager", "BaseSimulation", "SimState", "VisHelper", "get_engine",
    "physics", "mathematics", "ai_ml", "electronics",
    "biology", "robotics", "compsci", "visualization_3d", "signal"
]
