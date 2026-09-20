"""
ZENITH 3D Visualization Module
Implements: 3D Surface, Parametric Curves, 3D Scatter, Vector Field
"""

import math
import numpy as np
from typing import Any, Dict
from .core import BaseSimulation, VisHelper, get_engine

try:
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d import Axes3D
    from matplotlib.figure import Figure
    HAS_MPL = True
except ImportError:
    HAS_MPL = False

try:
    import numpy as _np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False


class SurfacePlot3DSim(BaseSimulation):
    SIM_TYPE = "surface_3d"
    SIM_NAME = "3D Surface Plot"

    def __init__(self, params=None):
        defaults = {
            "function": "sin(sqrt(x**2 + y**2))",
            "x_range": [-5, 5], "y_range": [-5, 5],
            "resolution": 50,
            "colormap": "cool",
        }
        p = {**defaults, **(params or {})}
        super().__init__(p)

    def initialize(self):
        super().initialize()
        if not HAS_NUMPY or not HAS_MPL:
            return
        x = np.linspace(self.params["x_range"][0], self.params["x_range"][1], self.params["resolution"])
        y = np.linspace(self.params["y_range"][0], self.params["y_range"][1], self.params["resolution"])
        self.X, self.Y = np.meshgrid(x, y)
        try:
            self.Z = eval(self.params["function"], {"__builtins__": {}},
                         {"x": self.X, "y": self.Y, "sin": np.sin, "cos": np.cos,
                          "tan": np.tan, "sqrt": np.sqrt, "abs": np.abs,
                          "exp": np.exp, "log": np.log, "pi": np.pi, "e": np.e})
        except Exception:
            self.Z = np.sin(np.sqrt(self.X**2 + self.Y**2))

    def step(self, dt=0.02):
        super().step(dt)

    def visualize(self, output_dir=None):
        if not HAS_MPL or not HAS_NUMPY:
            return "matplotlib/numpy not available"
        output_dir = output_dir or get_engine().output_dir
        vis = VisHelper()
        fig = plt.figure(figsize=(10, 8))
        fig.patch.set_facecolor('#0a0a0f')
        ax = fig.add_subplot(111, projection='3d')
        ax.set_facecolor('#0a0a0f')
        ax.plot_surface(self.X, self.Y, self.Z, cmap=self.params["colormap"],
                       edgecolor='none', alpha=0.8)
        ax.set_title(f"3D Surface: {self.params['function']}", color='white', fontsize=13)
        ax.xaxis.label.set_color('white'); ax.yaxis.label.set_color('white'); ax.zaxis.label.set_color('white')
        ax.tick_params(colors='gray')
        plt.tight_layout()
        return VisHelper.save_figure(fig, f"surface_3d_{int(self.time*1000)}.png", output_dir)


class ParametricCurve3DSim(BaseSimulation):
    SIM_TYPE = "parametric_3d"
    SIM_NAME = "3D Parametric Curve"

    def __init__(self, params=None):
        defaults = {
            "curve_type": "helix",
            "t_range": [0, 6.28],
            "resolution": 500,
        }
        p = {**defaults, **(params or {})}
        super().__init__(p)

    def initialize(self):
        super().initialize()
        if not HAS_NUMPY or not HAS_MPL:
            return
        t = np.linspace(self.params["t_range"][0], self.params["t_range"][1], self.params["resolution"])
        ct = self.params["curve_type"]
        if ct == "helix":
            self.X = np.cos(t); self.Y = np.sin(t); self.Z = t / (2 * np.pi)
        elif ct == "torus_knot":
            p, q = 2, 3
            self.X = (2 + np.cos(q * t)) * np.cos(p * t)
            self.Y = (2 + np.cos(q * t)) * np.sin(p * t)
            self.Z = np.sin(q * t)
        elif ct == "lissajous":
            a, b = 3, 2
            self.X = np.sin(a * t); self.Y = np.sin(b * t); self.Z = np.sin((a + b) * t)
        elif ct == "spiral":
            self.X = t * np.cos(t); self.Y = t * np.sin(t); self.Z = t
        else:
            self.X = np.cos(t); self.Y = np.sin(t); self.Z = np.sin(2 * t)

    def step(self, dt=0.02):
        super().step(dt)

    def visualize(self, output_dir=None):
        if not HAS_MPL or not HAS_NUMPY:
            return "matplotlib/numpy not available"
        output_dir = output_dir or get_engine().output_dir
        vis = VisHelper()
        fig = plt.figure(figsize=(10, 8))
        fig.patch.set_facecolor('#0a0a0f')
        ax = fig.add_subplot(111, projection='3d')
        ax.set_facecolor('#0a0a0f')
        ax.plot(self.X, self.Y, self.Z, color=vis.COLORS["cyan"], linewidth=1.5)
        ax.set_title(f"3D Parametric: {self.params['curve_type']}", color='white', fontsize=13)
        ax.xaxis.label.set_color('white'); ax.yaxis.label.set_color('white'); ax.zaxis.label.set_color('white')
        ax.tick_params(colors='gray')
        plt.tight_layout()
        return VisHelper.save_figure(fig, f"parametric_3d_{int(self.time*1000)}.png", output_dir)


class VectorField3DSim(BaseSimulation):
    SIM_TYPE = "vector_field_3d"
    SIM_NAME = "3D Vector Field"

    def __init__(self, params=None):
        defaults = {
            "field": "vortex",
            "grid_size": 10,
        }
        p = {**defaults, **(params or {})}
        super().__init__(p)

    def initialize(self):
        super().initialize()
        if not HAS_NUMPY or not HAS_MPL:
            return
        n = self.params["grid_size"]
        self.X, self.Y, self.Z = np.meshgrid(
            np.linspace(-2, 2, n), np.linspace(-2, 2, n), np.linspace(-2, 2, n))
        field = self.params["field"]
        if field == "vortex":
            self.U = -self.Y; self.V = self.X; self.W = np.zeros_like(self.X)
        elif field == "divergent":
            self.U = self.X; self.V = self.Y; self.W = self.Z
        elif field == "convergent":
            self.U = -self.X; self.V = -self.Y; self.W = -self.Z
        else:
            self.U = np.ones_like(self.X); self.V = np.ones_like(self.Y); self.W = np.ones_like(self.Z)

    def step(self, dt=0.02):
        super().step(dt)

    def visualize(self, output_dir=None):
        if not HAS_MPL or not HAS_NUMPY:
            return "matplotlib/numpy not available"
        output_dir = output_dir or get_engine().output_dir
        vis = VisHelper()
        fig = plt.figure(figsize=(10, 8))
        fig.patch.set_facecolor('#0a0a0f')
        ax = fig.add_subplot(111, projection='3d')
        ax.set_facecolor('#0a0a0f')
        ax.quiver(self.X, self.Y, self.Z, self.U, self.V, self.W,
                 color=vis.COLORS["cyan"], alpha=0.6, linewidth=0.5)
        ax.set_title(f"3D Vector Field: {self.params['field']}", color='white', fontsize=13)
        ax.xaxis.label.set_color('white'); ax.yaxis.label.set_color('white'); ax.zaxis.label.set_color('white')
        ax.tick_params(colors='gray')
        plt.tight_layout()
        return VisHelper.save_figure(fig, f"vector_field_3d_{int(self.time*1000)}.png", output_dir)


def register_3d_simulations(engine=None):
    engine = engine or get_engine()
    engine.register_simulation("surface_3d", SurfacePlot3DSim)
    engine.register_simulation("parametric_3d", ParametricCurve3DSim)
    engine.register_simulation("vector_field_3d", VectorField3DSim)
