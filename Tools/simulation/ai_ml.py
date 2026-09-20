"""
ZENITH AI/ML Simulation Module
Implements: Neural Networks, Gradient Descent, Decision Trees, K-Means, Classification
"""

import math
import random
import numpy as np
from typing import Any, Dict, List
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
# NEURAL NETWORK VISUALIZATION
# =========================================

class NeuralNetworkSim(BaseSimulation):
    SIM_TYPE = "neural_network"
    SIM_NAME = "Neural Network"

    def __init__(self, params=None):
        defaults = {
            "layers": [2, 4, 3, 1],
            "activation": "sigmoid",
            "learning_rate": 0.1,
            "epochs": 50,
            "training_data": None,
        }
        p = {**defaults, **(params or {})}
        super().__init__(p)
        self._init_network()

    def _init_network(self):
        self.layers = self.params["layers"]
        self.L = len(self.layers)
        self.weights = []
        self.biases = []
        for i in range(self.L - 1):
            w = [[random.gauss(0, 0.5) for _ in range(self.layers[i])] for _ in range(self.layers[i+1])]
            b = [0.0] * self.layers[i+1]
            self.weights.append(w)
            self.biases.append(b)
        self.activations = [None] * self.L

    def _activate(self, z, func="sigmoid"):
        if func == "sigmoid":
            return 1.0 / (1.0 + math.exp(-max(-500, min(500, z))))
        elif func == "relu":
            return max(0, z)
        elif func == "tanh":
            return math.tanh(z)
        return z

    def _activate_deriv(self, a, func="sigmoid"):
        if func == "sigmoid":
            return a * (1 - a)
        elif func == "relu":
            return 1.0 if a > 0 else 0.0
        elif func == "tanh":
            return 1 - a**2
        return 1.0

    def forward(self, inputs):
        self.activations[0] = inputs
        for i in range(self.L - 1):
            new_act = []
            for j in range(self.layers[i + 1]):
                z = sum(self.weights[i][j][k] * self.activations[i][k] for k in range(self.layers[i])) + self.biases[i][j]
                new_act.append(self._activate(z, self.params["activation"]))
            self.activations[i + 1] = new_act
        return self.activations[-1]

    def initialize(self):
        super().initialize()
        self._init_network()
        self.metrics = {"weights_count": sum(len(w) * len(w[0]) for w in self.weights),
                        "layers": self.layers, "epoch": 0, "loss": None}

    def step(self, dt=0.02):
        super().step(dt)

    def train_step(self, inputs, targets):
        """Single training step with backpropagation."""
        output = self.forward(inputs)
        # Calculate output error
        lr = self.params["learning_rate"]
        output_errors = [targets[i] - output[i] for i in range(len(output))]

        # Backpropagate
        deltas = [None] * (self.L - 1)
        deltas[-1] = [output_errors[i] * self._activate_deriv(output[i], self.params["activation"])
                      for i in range(len(output_errors))]

        for i in range(self.L - 3, -1, -1):
            deltas[i] = []
            for j in range(self.layers[i + 1]):
                err = sum(self.weights[i + 1][k][j] * deltas[i + 1][k] for k in range(len(deltas[i + 1])))
                deltas[i].append(err * self._activate_deriv(self.activations[i + 1][j], self.params["activation"]))

        # Update weights
        for i in range(self.L - 1):
            for j in range(self.layers[i + 1]):
                for k in range(self.layers[i]):
                    self.weights[i][j][k] += lr * deltas[i][j] * self.activations[i][k]
                self.biases[i][j] += lr * deltas[i][j]

        return output_errors

    def visualize(self, output_dir=None):
        if not HAS_MPL:
            return "matplotlib not available"
        output_dir = output_dir or get_engine().output_dir
        fig, ax = plt.subplots(figsize=(14, 8))
        fig.patch.set_facecolor('#0a0a0f')
        vis = VisHelper()
        ax.set_facecolor('#0a0a0f')
        ax.set_xlim(-0.5, self.L - 0.5)
        ax.set_ylim(-1, max(self.layers) + 1)
        ax.set_aspect('auto')
        ax.set_title("Neural Network Architecture", color='white', fontsize=14, pad=15)

        # Draw connections
        for i in range(self.L - 1):
            for j in range(self.layers[i]):
                for k in range(self.layers[i + 1]):
                    weight = self.weights[i][k][j]
                    color = vis.COLORS["cyan"] if weight > 0 else vis.COLORS["red"]
                    alpha = min(abs(weight), 1.0) * 0.5 + 0.1
                    ax.plot([i, i+1], [j - self.layers[i]/2 + 0.5, k - self.layers[i+1]/2 + 0.5],
                            color=color, linewidth=0.5, alpha=alpha)

        # Draw neurons
        for i in range(self.L):
            for j in range(self.layers[i]):
                y = j - self.layers[i]/2 + 0.5
                act = self.activations[i][j] if self.activations[i] else 0.5
                color_intensity = min(max(act, 0), 1)
                circle = plt.Circle((i, y), 0.25, color=vis.COLORS["cyan"],
                                   ec='white', lw=1.5, alpha=0.3 + color_intensity * 0.7)
                ax.add_patch(circle)
                ax.text(i, y, f"{act:.1f}" if self.activations[i] else "", ha='center', va='center',
                       color='white', fontsize=7, fontweight='bold')

        # Layer labels
        labels = ["Input"] + [f"Hidden {i}" for i in range(1, self.L - 1)] + ["Output"]
        for i, label in enumerate(labels):
            ax.text(i, -0.8, f"{label}\n({self.layers[i]})", ha='center', color=vis.COLORS["text"],
                   fontsize=10, fontweight='bold')

        ax.axis('off')
        plt.tight_layout()
        return VisHelper.save_figure(fig, f"neural_net_{int(self.time*1000)}.png", output_dir)

    def explain(self):
        return (f"Neural network with architecture {self.layers}. "
                f"Activation: {self.params['activation']}. "
                f"Total weights: {self.metrics['weights_count']}. "
                f"Learning rate: {self.params['learning_rate']}.")


# =========================================
# GRADIENT DESCENT VISUALIZATION
# =========================================

class GradientDescentSim(BaseSimulation):
    SIM_TYPE = "gradient_descent"
    SIM_NAME = "Gradient Descent Optimizer"

    def __init__(self, params=None):
        defaults = {
            "function": "rosenbrock",
            "learning_rate": 0.01,
            "start_x": -1.0, "start_y": 1.0,
            "iterations": 200,
        }
        p = {**defaults, **(params or {})}
        super().__init__(p)
        self._init_state()

    def _init_state(self):
        self.x = self.params["start_x"]
        self.y = self.params["start_y"]
        self.path = [(self.x, self.y)]
        self.lr = self.params["learning_rate"]

    def _func(self, x, y):
        f = self.params["function"]
        if f == "rosenbrock":
            return (1 - x)**2 + 100 * (y - x**2)**2
        elif f == "sphere":
            return x**2 + y**2
        elif f == "rastrigin":
            return 20 + x**2 - 10*math.cos(2*math.pi*x) + y**2 - 10*math.cos(2*math.pi*y)
        elif f == "beale":
            return (1.5 - x + x*y)**2 + (2.25 - x + x*y**2)**2 + (2.625 - x + x*y**3)**2
        return x**2 + y**2

    def _grad(self, x, y):
        f = self.params["function"]
        eps = 1e-6
        gx = (self._func(x + eps, y) - self._func(x - eps, y)) / (2 * eps)
        gy = (self._func(x, y + eps) - self._func(x, y - eps)) / (2 * eps)
        return gx, gy

    def initialize(self):
        super().initialize()
        self._init_state()
        self.metrics = {"function": self.params["function"], "iterations": 0,
                        "final_loss": self._func(self.x, self.y)}

    def step(self, dt=0.02):
        gx, gy = self._grad(self.x, self.y)
        self.x -= self.lr * gx
        self.y -= self.lr * gy
        self.path.append((self.x, self.y))
        super().step(dt)
        self.metrics["iterations"] = self.step_count
        self.metrics["final_loss"] = self._func(self.x, self.y)
        self.metrics["current_x"] = self.x
        self.metrics["current_y"] = self.y
        self._record({"x": self.x, "y": self.y, "loss": self._func(self.x, self.y),
                      "grad_x": gx, "grad_y": gy})

    def visualize(self, output_dir=None):
        if not HAS_MPL or not HAS_NUMPY:
            return "matplotlib/numpy not available"
        output_dir = output_dir or get_engine().output_dir
        fig, axes = plt.subplots(1, 2, figsize=(14, 6))
        fig.patch.set_facecolor('#0a0a0f')
        vis = VisHelper()

        # Contour plot with path
        ax = axes[0]; ax.set_facecolor('#0a0a0f')
        x_range = np.linspace(-3, 3, 200)
        y_range = np.linspace(-3, 3, 200)
        X, Y = np.meshgrid(x_range, y_range)
        Z = np.vectorize(self._func)(X, Y)
        ax.contour(X, Y, Z, levels=50, cmap='coolwarm', alpha=0.6)
        ax.contourf(X, Y, Z, levels=50, cmap='coolwarm', alpha=0.2)
        px = [p[0] for p in self.path]
        py = [p[1] for p in self.path]
        ax.plot(px, py, color=vis.COLORS["yellow"], linewidth=1.5, marker='.', markersize=3)
        ax.plot(px[0], py[0], 'o', color=vis.COLORS["green"], markersize=8, label="Start")
        ax.plot(px[-1], py[-1], '*', color=vis.COLORS["red"], markersize=12, label="End")
        ax.set_title("Gradient Descent Path", color='white', fontsize=13)
        ax.legend(fontsize=9, facecolor='#111827', edgecolor='#334155', labelcolor='white')

        # Loss vs iteration
        ax = axes[1]; ax.set_facecolor('#0a0a0f')
        losses = [d["loss"] for d in self.history]
        ax.semilogy(losses, color=vis.COLORS["cyan"], linewidth=1.5)
        ax.set_title("Loss vs Iteration", color='white', fontsize=13)
        vis.label_axes(ax, "Iteration", "Loss (log)")
        vis.add_grid(ax)

        plt.tight_layout()
        return VisHelper.save_figure(fig, f"gradient_descent_{int(self.time*1000)}.png", output_dir)


# =========================================
# K-MEANS CLUSTERING
# =========================================

class KMeansSim(BaseSimulation):
    SIM_TYPE = "kmeans"
    SIM_NAME = "K-Means Clustering"

    def __init__(self, params=None):
        defaults = {
            "k": 3, "n_points": 300, "max_iter": 50,
            "spread": 1.5,
        }
        p = {**defaults, **(params or {})}
        super().__init__(p)

    def initialize(self):
        super().initialize()
        k = self.params["k"]
        n = self.params["n_points"]
        spread = self.params["spread"]
        # Generate random clusters
        self.centers_init = [(random.uniform(-5, 5), random.uniform(-5, 5)) for _ in range(k)]
        self.points = []
        self.labels = []
        points_per = n // k
        for i in range(k):
            cx, cy = self.centers_init[i]
            for _ in range(points_per):
                x = random.gauss(cx, spread)
                y = random.gauss(cy, spread)
                self.points.append((x, y))
                self.labels.append(i)
        self.centers = list(self.centers_init)
        self.assignments = [0] * len(self.points)
        self.metrics = {"k": k, "n_points": len(self.points), "iteration": 0}

    def step(self, dt=0.02):
        super().step(dt)

    def run_iteration(self):
        """Run one iteration of K-Means."""
        k = self.params["k"]
        points = self.points
        centers = self.centers

        # Assignment step
        new_assignments = []
        for px, py in points:
            dists = [math.sqrt((px - cx)**2 + (py - cy)**2) for cx, cy in centers]
            new_assignments.append(dists.index(min(dists)))

        # Update step
        for i in range(k):
            cluster_pts = [(points[j][0], points[j][1]) for j in range(len(points)) if new_assignments[j] == i]
            if cluster_pts:
                self.centers[i] = (sum(p[0] for p in cluster_pts) / len(cluster_pts),
                                   sum(p[1] for p in cluster_pts) / len(cluster_pts))

        self.assignments = new_assignments
        self.metrics["iteration"] = self.metrics.get("iteration", 0) + 1
        # Calculate inertia
        inertia = 0
        for j, (px, py) in enumerate(points):
            cx, cy = self.centers[self.assignments[j]]
            inertia += (px - cx)**2 + (py - cy)**2
        self.metrics["inertia"] = inertia

    def visualize(self, output_dir=None):
        if not HAS_MPL:
            return "matplotlib not available"
        output_dir = output_dir or get_engine().output_dir
        fig, ax = plt.subplots(figsize=(8, 8))
        fig.patch.set_facecolor('#0a0a0f')
        vis = VisHelper()
        ax.set_facecolor('#0a0a0f')

        colors = [vis.COLORS["cyan"], vis.COLORS["orange"], vis.COLORS["green"],
                  vis.COLORS["purple"], vis.COLORS["pink"], vis.COLORS["yellow"]]
        for i in range(self.params["k"]):
            pts = [self.points[j] for j in range(len(self.points)) if self.assignments[j] == i]
            if pts:
                xs, ys = zip(*pts)
                ax.scatter(xs, ys, c=colors[i % len(colors)], s=15, alpha=0.6, label=f"Cluster {i+1}")
            cx, cy = self.centers[i]
            ax.plot(cx, cy, 'X', color=colors[i % len(colors)], markersize=15, markeredgecolor='white', markeredgewidth=2)

        ax.set_title(f"K-Means Clustering (k={self.params['k']}, iter={self.metrics['iteration']})", color='white', fontsize=13)
        ax.legend(fontsize=10, facecolor='#111827', edgecolor='#334155', labelcolor='white')
        vis.add_grid(ax)
        plt.tight_layout()
        return VisHelper.save_figure(fig, f"kmeans_{int(self.time*1000)}.png", output_dir)


# =========================================
# CLASSIFICATION BOUNDARIES
# =========================================

class ClassificationSim(BaseSimulation):
    SIM_TYPE = "classification"
    SIM_NAME = "Classification Decision Boundary"

    def __init__(self, params=None):
        defaults = {
            "n_points": 200, "n_classes": 3,
            "method": "knn", "k_neighbors": 5,
            "noise": 0.8,
        }
        p = {**defaults, **(params or {})}
        super().__init__(p)

    def initialize(self):
        super().initialize()
        n = self.params["n_points"]
        k = self.params["n_classes"]
        noise = self.params["noise"]
        self.X = []
        self.y = []
        centers = [(random.uniform(-3, 3), random.uniform(-3, 3)) for _ in range(k)]
        for i in range(n):
            c = centers[i % k]
            x = random.gauss(c[0], noise)
            y = random.gauss(c[1], noise)
            self.X.append([x, y])
            self.y.append(i % k)
        self.metrics = {"n_points": n, "n_classes": k}

    def step(self, dt=0.02):
        super().step(dt)

    def _predict(self, x, y):
        if self.params["method"] == "knn":
            k = self.params["k_neighbors"]
            dists = [(math.sqrt((x - p[0])**2 + (y - p[1])**2), self.y[i]) for i, p in enumerate(self.X)]
            dists.sort()
            neighbors = [d[1] for d in dists[:k]]
            return max(set(neighbors), key=neighbors.count)
        return 0

    def visualize(self, output_dir=None):
        if not HAS_MPL:
            return "matplotlib not available"
        output_dir = output_dir or get_engine().output_dir
        fig, ax = plt.subplots(figsize=(8, 8))
        fig.patch.set_facecolor('#0a0a0f')
        vis = VisHelper()
        ax.set_facecolor('#0a0a0f')

        # Decision boundary
        x_min = min(p[0] for p in self.X) - 1
        x_max = max(p[0] for p in self.X) + 1
        y_min = min(p[1] for p in self.X) - 1
        y_max = max(p[1] for p in self.X) + 1
        if HAS_NUMPY:
            xx, yy = np.meshgrid(np.linspace(x_min, x_max, 100), np.linspace(y_min, y_max, 100))
            Z = np.vectorize(lambda x, y: self._predict(x, y))(xx, yy)
            ax.contourf(xx, yy, Z, alpha=0.2, cmap='coolwarm')

        colors = [vis.COLORS["cyan"], vis.COLORS["orange"], vis.COLORS["green"],
                  vis.COLORS["purple"], vis.COLORS["pink"]]
        for c in range(self.params["n_classes"]):
            pts = [self.X[i] for i in range(len(self.X)) if self.y[i] == c]
            if pts:
                xs, ys = zip(*pts)
                ax.scatter(xs, ys, c=colors[c % len(colors)], s=15, alpha=0.7, label=f"Class {c}")

        ax.set_title(f"Classification ({self.params['method'].upper()})", color='white', fontsize=13)
        ax.legend(fontsize=10, facecolor='#111827', edgecolor='#334155', labelcolor='white')
        vis.add_grid(ax)
        plt.tight_layout()
        return VisHelper.save_figure(fig, f"classification_{int(self.time*1000)}.png", output_dir)


# =========================================
# REGISTER ALL AI/ML SIMS
# =========================================

def register_ai_ml_simulations(engine=None):
    engine = engine or get_engine()
    engine.register_simulation("neural_network", NeuralNetworkSim)
    engine.register_simulation("gradient_descent", GradientDescentSim)
    engine.register_simulation("kmeans", KMeansSim)
    engine.register_simulation("classification", ClassificationSim)
