"""
ZENITH Mathematics Simulation Module
Implements: Function Graphing, Vectors, Derivatives, Integrals, Probability, Fractals
"""

import math
import numpy as np
from typing import Any, Dict, List, Optional
from .core import BaseSimulation, VisHelper, get_engine

try:
    import numpy as _np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

try:
    import matplotlib.pyplot as plt
    from matplotlib.figure import Figure
    HAS_MPL = True
except ImportError:
    HAS_MPL = False


# =========================================
# 2D FUNCTION GRAPHING
# =========================================

class FunctionGraph2D(BaseSimulation):
    SIM_TYPE = "function_graph_2d"
    SIM_NAME = "2D Function Graph"

    def __init__(self, params=None):
        defaults = {
            "expression": "sin(x)",
            "x_min": -10, "x_max": 10,
            "num_points": 500,
            "title": "2D Function",
            "second_function": None,
        }
        p = {**defaults, **(params or {})}
        super().__init__(p)

    def _safe_eval(self, expr, x_val):
        """Evaluate math expression safely."""
        local_vars = {
            "x": x_val, "pi": math.pi, "e": math.e,
            "sin": math.sin, "cos": math.cos, "tan": math.tan,
            "exp": math.exp, "log": math.log, "sqrt": math.sqrt,
            "abs": abs, "asin": math.asin, "acos": math.acos, "atan": math.atan,
            "sinh": math.sinh, "cosh": math.cosh, "tanh": math.tanh,
            "floor": math.floor, "ceil": math.ceil, "pow": pow,
        }
        try:
            return float(eval(expr, {"__builtins__": {}}, local_vars))
        except Exception:
            return 0.0

    def initialize(self):
        super().initialize()
        x_min = self.params["x_min"]
        x_max = self.params["x_max"]
        n = self.params["num_points"]
        expr = self.params["expression"]
        if HAS_NUMPY:
            self.x_vals = np.linspace(x_min, x_max, n)
            self.y_vals = np.array([self._safe_eval(expr, x) for x in self.x_vals])
            self.metrics["min_y"] = float(np.min(self.y_vals))
            self.metrics["max_y"] = float(np.max(self.y_vals))
            self.metrics["num_points"] = n

    def step(self, dt=0.02):
        super().step(dt)
        self.metrics["evaluated"] = True

    def visualize(self, output_dir=None):
        if not HAS_MPL or not HAS_NUMPY:
            return "matplotlib/numpy not available"
        output_dir = output_dir or get_engine().output_dir
        fig, ax = plt.subplots(figsize=(12, 7))
        fig.patch.set_facecolor('#0a0a0f')
        vis = VisHelper()
        ax.set_facecolor('#0a0a0f')

        ax.plot(self.x_vals, self.y_vals, color=vis.COLORS["cyan"], linewidth=1.5, label=f"y = {self.params['expression']}")
        ax.axhline(y=0, color='#334155', linewidth=0.8)
        ax.axvline(x=0, color='#334155', linewidth=0.8)

        if self.params.get("second_function"):
            y2 = np.array([self._safe_eval(self.params["second_function"], x) for x in self.x_vals])
            ax.plot(self.x_vals, y2, color=vis.COLORS["orange"], linewidth=1.5, label=f"y = {self.params['second_function']}")

        ax.set_title(self.params.get("title", "Function Graph"), color='white', fontsize=14)
        ax.legend(fontsize=11, facecolor='#111827', edgecolor='#334155', labelcolor='white')
        vis.label_axes(ax, "x", "y")
        vis.add_grid(ax)
        plt.tight_layout()
        return VisHelper.save_figure(fig, f"func2d_{int(self.time*1000)}.png", output_dir)


# =========================================
# DERIVATIVE VISUALIZATION
# =========================================

class DerivativeSim(BaseSimulation):
    SIM_TYPE = "derivative"
    SIM_NAME = "Derivative Visualization"

    def __init__(self, params=None):
        defaults = {
            "expression": "x**2", "x_min": -5, "x_max": 5,
            "tangent_x": 1.0, "num_points": 500,
        }
        p = {**defaults, **(params or {})}
        super().__init__(p)

    def _safe_eval(self, expr, x_val):
        local_vars = {
            "x": x_val, "pi": math.pi, "e": math.e,
            "sin": math.sin, "cos": math.cos, "tan": math.tan,
            "exp": math.exp, "log": math.log, "sqrt": math.sqrt,
            "abs": abs, "asin": math.asin, "acos": math.acos, "atan": math.atan,
            "pow": pow,
        }
        try:
            return float(eval(expr, {"__builtins__": {}}, local_vars))
        except Exception:
            return 0.0

    def initialize(self):
        super().initialize()
        if HAS_NUMPY:
            x = np.linspace(self.params["x_min"], self.params["x_max"], self.params["num_points"])
            self.x_vals = x
            self.y_vals = np.array([self._safe_eval(self.params["expression"], xi) for xi in x])
            # Numerical derivative
            dx = x[1] - x[0]
            self.dydx = np.gradient(self.y_vals, dx)
            # Tangent line at point
            xt = self.params["tangent_x"]
            yt = self._safe_eval(self.params["expression"], xt)
            dyt = float(np.interp(xt, x, self.dydx))
            self.tangent_x = x
            self.tangent_y = yt + dyt * (x - xt)
            self.metrics["derivative_at_point"] = dyt
            self.metrics["tangent_point"] = {"x": xt, "y": yt}

    def step(self, dt=0.02):
        super().step(dt)

    def visualize(self, output_dir=None):
        if not HAS_MPL or not HAS_NUMPY:
            return "matplotlib/numpy not available"
        output_dir = output_dir or get_engine().output_dir
        fig, axes = plt.subplots(1, 2, figsize=(14, 6))
        fig.patch.set_facecolor('#0a0a0f')
        vis = VisHelper()

        ax = axes[0]; ax.set_facecolor('#0a0a0f')
        ax.plot(self.x_vals, self.y_vals, color=vis.COLORS["cyan"], linewidth=1.5, label=f"f(x) = {self.params['expression']}")
        ax.plot(self.tangent_x, self.tangent_y, color=vis.COLORS["orange"], linewidth=1, linestyle='--', label="Tangent Line")
        xt = self.params["tangent_x"]
        yt = self.metrics["tangent_point"]["y"]
        ax.plot(xt, yt, 'o', color=vis.COLORS["yellow"], markersize=8)
        ax.set_title("Function + Tangent", color='white', fontsize=13)
        ax.legend(fontsize=10, facecolor='#111827', edgecolor='#334155', labelcolor='white')
        vis.label_axes(ax, "x", "f(x)")
        vis.add_grid(ax)

        ax = axes[1]; ax.set_facecolor('#0a0a0f')
        ax.plot(self.x_vals, self.dydx, color=vis.COLORS["green"], linewidth=1.5, label=f"f'(x)")
        ax.set_title("Derivative", color='white', fontsize=13)
        ax.legend(fontsize=10, facecolor='#111827', edgecolor='#334155', labelcolor='white')
        vis.label_axes(ax, "x", "f'(x)")
        vis.add_grid(ax)

        plt.tight_layout()
        return VisHelper.save_figure(fig, f"derivative_{int(self.time*1000)}.png", output_dir)


# =========================================
# INTEGRAL VISUALIZATION
# =========================================

class IntegralSim(BaseSimulation):
    SIM_TYPE = "integral"
    SIM_NAME = "Integral Visualization"

    def __init__(self, params=None):
        defaults = {
            "expression": "sin(x)", "a": 0, "b": math.pi,
            "x_min": -1, "x_max": 4, "num_points": 500,
        }
        p = {**defaults, **(params or {})}
        super().__init__(p)

    def _safe_eval(self, expr, x_val):
        local_vars = {
            "x": x_val, "pi": math.pi, "e": math.e,
            "sin": math.sin, "cos": math.cos, "exp": math.exp,
            "log": math.log, "sqrt": math.sqrt, "pow": pow, "abs": abs,
        }
        try:
            return float(eval(expr, {"__builtins__": {}}, local_vars))
        except:
            return 0.0

    def initialize(self):
        super().initialize()
        if HAS_NUMPY:
            self.x_vals = np.linspace(self.params["x_min"], self.params["x_max"], self.params["num_points"])
            self.y_vals = np.array([self._safe_eval(self.params["expression"], x) for x in self.x_vals])
            a, b = self.params["a"], self.params["b"]
            idx_a = np.searchsorted(self.x_vals, a)
            idx_b = np.searchsorted(self.x_vals, b)
            self.x_fill = self.x_vals[idx_a:idx_b]
            self.y_fill = self.y_vals[idx_a:idx_b]
            dx = self.x_vals[1] - self.x_vals[0]
            self.area = float(np.sum(self.y_fill) * dx)
            self.metrics["area"] = self.area
            self.metrics["a"] = a
            self.metrics["b"] = b

    def step(self, dt=0.02):
        super().step(dt)

    def visualize(self, output_dir=None):
        if not HAS_MPL or not HAS_NUMPY:
            return "matplotlib/numpy not available"
        output_dir = output_dir or get_engine().output_dir
        fig, ax = plt.subplots(figsize=(12, 7))
        fig.patch.set_facecolor('#0a0a0f')
        vis = VisHelper()
        ax.set_facecolor('#0a0a0f')

        ax.plot(self.x_vals, self.y_vals, color=vis.COLORS["cyan"], linewidth=1.5)
        ax.fill_between(self.x_fill, 0, self.y_fill, alpha=0.3, color=vis.COLORS["purple"], label=f"Area = {self.area:.4f}")
        ax.axhline(y=0, color='#334155', linewidth=0.8)
        ax.set_title(f"Integral of {self.params['expression']} from {self.params['a']:.2f} to {self.params['b']:.2f}", color='white', fontsize=13)
        ax.legend(fontsize=11, facecolor='#111827', edgecolor='#334155', labelcolor='white')
        vis.label_axes(ax, "x", "f(x)")
        vis.add_grid(ax)
        plt.tight_layout()
        return VisHelper.save_figure(fig, f"integral_{int(self.time*1000)}.png", output_dir)


# =========================================
# FRACTAL GENERATOR
# =========================================

class FractalSim(BaseSimulation):
    SIM_TYPE = "fractal"
    SIM_NAME = "Fractal Generator"

    def __init__(self, params=None):
        defaults = {
            "fractal_type": "mandelbrot",
            "x_min": -2.5, "x_max": 1.0, "y_min": -1.25, "y_max": 1.25,
            "resolution": 400, "max_iter": 100,
        }
        p = {**defaults, **(params or {})}
        super().__init__(p)

    def initialize(self):
        super().initialize()
        if HAS_NUMPY:
            res = self.params["resolution"]
            x = np.linspace(self.params["x_min"], self.params["x_max"], res)
            y = np.linspace(self.params["y_min"], self.params["y_max"], res)
            self.X, self.Y = np.meshgrid(x, y)
            self.Z = self.X + 1j * self.Y

    def _mandelbrot(self):
        res = self.params["resolution"]
        max_iter = self.params["max_iter"]
        c = self.Z.copy()
        z = np.zeros_like(c)
        iterations = np.zeros(c.shape, dtype=float)
        mask = np.ones(c.shape, dtype=bool)
        for i in range(max_iter):
            z[mask] = z[mask]**2 + c[mask]
            diverged = mask & (np.abs(z) > 2)
            iterations[diverged] = i
            mask[diverged] = False
        iterations[mask] = max_iter
        return iterations

    def _julia(self):
        res = self.params["resolution"]
        max_iter = self.params["max_iter"]
        c = -0.7 + 0.27015j
        z = self.Z.copy()
        iterations = np.zeros(z.shape, dtype=float)
        mask = np.ones(z.shape, dtype=bool)
        for i in range(max_iter):
            z[mask] = z[mask]**2 + c
            diverged = mask & (np.abs(z) > 2)
            iterations[diverged] = i
            mask[diverged] = False
        iterations[mask] = max_iter
        return iterations

    def step(self, dt=0.02):
        super().step(dt)

    def visualize(self, output_dir=None):
        if not HAS_MPL or not HAS_NUMPY:
            return "matplotlib/numpy not available"
        output_dir = output_dir or get_engine().output_dir

        if self.params["fractal_type"] == "mandelbrot":
            data = self._mandelbrot()
            title = "Mandelbrot Set"
        else:
            data = self._julia()
            title = "Julia Set"

        fig, ax = plt.subplots(figsize=(10, 10))
        fig.patch.set_facecolor('#0a0a0f')
        ax.imshow(data, cmap='inferno', extent=[self.params["x_min"], self.params["x_max"],
                                                  self.params["y_min"], self.params["y_max"]])
        ax.set_title(title, color='white', fontsize=14, pad=15)
        ax.set_xlabel("Re(c)", color='white')
        ax.set_ylabel("Im(c)", color='white')
        plt.tight_layout()
        return VisHelper.save_figure(fig, f"fractal_{self.params['fractal_type']}_{int(self.time*1000)}.png", output_dir)


# =========================================
# VECTOR VISUALIZATION
# =========================================

class VectorSim(BaseSimulation):
    SIM_TYPE = "vectors"
    SIM_NAME = "Vector Visualization"

    def __init__(self, params=None):
        defaults = {
            "vectors": [[3, 4], [-2, 1], [1, -3]],
            "show_resultant": True,
            "show_components": False,
        }
        p = {**defaults, **(params or {})}
        super().__init__(p)

    def initialize(self):
        super().initialize()
        vecs = self.params["vectors"]
        self.vx = [v[0] for v in vecs]
        self.vy = [v[1] for v in vecs]
        self.resultant = [sum(self.vx), sum(self.vy)]
        self.magnitudes = [math.sqrt(v[0]**2 + v[1]**2) for v in vecs]
        self.resultant_mag = math.sqrt(self.resultant[0]**2 + self.resultant[1]**2)
        self.metrics["magnitudes"] = self.magnitudes
        self.metrics["resultant"] = self.resultant
        self.metrics["resultant_magnitude"] = self.resultant_mag

    def step(self, dt=0.02):
        super().step(dt)

    def visualize(self, output_dir=None):
        if not HAS_MPL:
            return "matplotlib not available"
        output_dir = output_dir or get_engine().output_dir
        fig, ax = plt.subplots(figsize=(8, 8))
        fig.patch.set_facecolor('#0a0a0f')
        vis = VisHelper()
        ax.set_facecolor('#0a0a0f')

        colors = [vis.COLORS["cyan"], vis.COLORS["orange"], vis.COLORS["green"],
                  vis.COLORS["purple"], vis.COLORS["pink"]]
        cx, cy = 0, 0
        for i, (vx, vy) in enumerate(zip(self.vx, self.vy)):
            ax.annotate('', xy=(cx+vx, cy+vy), xytext=(cx, cy),
                        arrowprops=dict(arrowstyle='->', color=colors[i % len(colors)], lw=2.5))
            ax.text(cx + vx/2, cy + vy/2 + 0.2, f"|v{i+1}|={self.magnitudes[i]:.2f}",
                    color=colors[i % len(colors)], fontsize=10, ha='center')
            cx += vx
            cy += vy

        if self.params["show_resultant"]:
            ax.annotate('', xy=(self.resultant[0], self.resultant[1]), xytext=(0, 0),
                        arrowprops=dict(arrowstyle='->', color=vis.COLORS["yellow"], lw=3, linestyle='--'))
            ax.text(self.resultant[0]/2, self.resultant[1]/2 - 0.3,
                    f"R={self.resultant_mag:.2f}", color=vis.COLORS["yellow"], fontsize=11, fontweight='bold')

        ax.set_xlim(-6, 6); ax.set_ylim(-6, 6)
        ax.set_aspect('equal')
        ax.set_title("Vector Addition", color='white', fontsize=14)
        vis.add_grid(ax)
        plt.tight_layout()
        return VisHelper.save_figure(fig, f"vectors_{int(self.time*1000)}.png", output_dir)


# =========================================
# PROBABILITY DISTRIBUTION
# =========================================

class ProbabilitySim(BaseSimulation):
    SIM_TYPE = "probability"
    SIM_NAME = "Probability Distribution"

    def __init__(self, params=None):
        defaults = {
            "distribution": "normal", "n_samples": 10000,
            "mean": 0, "std": 1, "bins": 60,
        }
        p = {**defaults, **(params or {})}
        super().__init__(p)

    def initialize(self):
        super().initialize()
        if HAS_NUMPY:
            n = self.params["n_samples"]
            dist = self.params["distribution"]
            if dist == "normal":
                self.data = np.random.normal(self.params["mean"], self.params["std"], n)
            elif dist == "uniform":
                self.data = np.random.uniform(-3, 3, n)
            elif dist == "exponential":
                self.data = np.random.exponential(1.0, n)
            elif dist == "poisson":
                self.data = np.random.poisson(5, n).astype(float)
            else:
                self.data = np.random.normal(0, 1, n)

            self.metrics["mean"] = float(np.mean(self.data))
            self.metrics["std"] = float(np.std(self.data))
            self.metrics["median"] = float(np.median(self.data))
            self.metrics["min"] = float(np.min(self.data))
            self.metrics["max"] = float(np.max(self.data))

    def step(self, dt=0.02):
        super().step(dt)

    def visualize(self, output_dir=None):
        if not HAS_MPL or not HAS_NUMPY:
            return "matplotlib/numpy not available"
        output_dir = output_dir or get_engine().output_dir
        fig, ax = plt.subplots(figsize=(10, 6))
        fig.patch.set_facecolor('#0a0a0f')
        vis = VisHelper()
        ax.set_facecolor('#0a0a0f')

        ax.hist(self.data, bins=self.params["bins"], color=vis.COLORS["cyan"], alpha=0.7,
                density=True, edgecolor='white', linewidth=0.3)
        ax.axvline(self.metrics["mean"], color=vis.COLORS["yellow"], linewidth=2, linestyle='--', label=f"Mean={self.metrics['mean']:.3f}")
        ax.axvline(self.metrics["median"], color=vis.COLORS["orange"], linewidth=1.5, linestyle=':', label=f"Median={self.metrics['median']:.3f}")
        ax.set_title(f"{self.params['distribution'].title()} Distribution (n={self.params['n_samples']})", color='white', fontsize=13)
        ax.legend(fontsize=10, facecolor='#111827', edgecolor='#334155', labelcolor='white')
        vis.label_axes(ax, "Value", "Density")
        vis.add_grid(ax)
        plt.tight_layout()
        return VisHelper.save_figure(fig, f"prob_{self.params['distribution']}_{int(self.time*1000)}.png", output_dir)


# =========================================
# REGISTER ALL MATH SIMS
# =========================================

def register_math_simulations(engine=None):
    engine = engine or get_engine()
    engine.register_simulation("function_graph_2d", FunctionGraph2D)
    engine.register_simulation("derivative", DerivativeSim)
    engine.register_simulation("integral", IntegralSim)
    engine.register_simulation("fractal", FractalSim)
    engine.register_simulation("vectors", VectorSim)
    engine.register_simulation("probability", ProbabilitySim)
