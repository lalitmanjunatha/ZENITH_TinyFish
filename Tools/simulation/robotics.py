"""
ZENITH Robotics Simulation Module
Implements: PID Controller, Robot Arm, Mobile Robot, Path Planning (A*), Inverted Pendulum
"""

import math
import heapq
import numpy as np
from typing import Any, Dict, List, Tuple
from .core import BaseSimulation, VisHelper, get_engine

try:
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches
    from matplotlib.figure import Figure
    HAS_MPL = True
except ImportError:
    HAS_MPL = False

try:
    import numpy as _np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False


class PIDControllerSim(BaseSimulation):
    SIM_TYPE = "pid_controller"
    SIM_NAME = "PID Controller"

    def __init__(self, params=None):
        defaults = {
            "Kp": 2.0, "Ki": 0.5, "Kd": 0.1,
            "setpoint": 10.0, "process_gain": 1.0,
            "time_constant": 1.0, "dead_time": 0.0,
        }
        p = {**defaults, **(params or {})}
        super().__init__(p)

    def initialize(self):
        super().initialize()
        self.output = 0.0
        self.process_var = 0.0
        self.integral = 0.0
        self.prev_error = 0.0
        self.setpoint = self.params["setpoint"]
        self.Kp = self.params["Kp"]
        self.Ki = self.params["Ki"]
        self.Kd = self.params["Kd"]
        self.metrics = {"setpoint": self.setpoint, "overshoot": 0, "settling_time": None}

    def step(self, dt=0.01):
        error = self.setpoint - self.process_var
        self.integral += error * dt
        derivative = (error - self.prev_error) / dt if dt > 0 else 0

        self.output = self.Kp * error + self.Ki * self.integral + self.Kd * derivative

        # Simple first-order process
        KG = self.params["process_gain"]
        TC = self.params["time_constant"]
        dpv = (KG * self.output - self.process_var) / TC * dt
        self.process_var += dpv

        self.prev_error = error
        super().step(dt)

        overshoot = max(0, (self.process_var - self.setpoint) / self.setpoint * 100) if self.setpoint > 0 else 0
        self.metrics["process_var"] = self.process_var
        self.metrics["output"] = self.output
        self.metrics["error"] = error
        self.metrics["overshoot"] = max(self.metrics.get("overshoot", 0), overshoot)
        self._record({"pv": self.process_var, "out": self.output, "err": error})

    def visualize(self, output_dir=None):
        if not HAS_MPL:
            return "matplotlib not available"
        output_dir = output_dir or get_engine().output_dir
        fig, axes = plt.subplots(1, 2, figsize=(14, 6))
        fig.patch.set_facecolor('#0a0a0f')
        vis = VisHelper()

        ts = [d["t"] for d in self.history]
        ax = axes[0]; ax.set_facecolor('#0a0a0f')
        ax.plot(ts, [d["pv"] for d in self.history], color=vis.COLORS["cyan"], linewidth=2, label="Process Variable")
        ax.axhline(y=self.setpoint, color=vis.COLORS["yellow"], linestyle='--', label=f"Setpoint={self.setpoint}")
        ax.set_title("PID Response", color='white', fontsize=13)
        ax.legend(fontsize=10, facecolor='#111827', edgecolor='#334155', labelcolor='white')
        vis.label_axes(ax, "Time (s)", "Value")
        vis.add_grid(ax)

        ax = axes[1]; ax.set_facecolor('#0a0a0f')
        ax.plot(ts, [d["out"] for d in self.history], color=vis.COLORS["orange"], linewidth=1.5, label="Controller Output")
        ax.plot(ts, [d["err"] for d in self.history], color=vis.COLORS["red"], linewidth=1, label="Error")
        ax.set_title("Control Signals", color='white', fontsize=13)
        ax.legend(fontsize=10, facecolor='#111827', edgecolor='#334155', labelcolor='white')
        vis.label_axes(ax, "Time (s)", "Value")
        vis.add_grid(ax)

        plt.tight_layout()
        return VisHelper.save_figure(fig, f"pid_{int(self.time*1000)}.png", output_dir)


class RobotArmSim(BaseSimulation):
    SIM_TYPE = "robot_arm"
    SIM_NAME = "Robot Arm (Forward Kinematics)"

    def __init__(self, params=None):
        defaults = {
            "lengths": [2.0, 1.5, 1.0],
            "angles": [0.5, 0.8, -0.3],
            "joint_mode": "forward",
        }
        p = {**defaults, **(params or {})}
        super().__init__(p)

    def initialize(self):
        super().initialize()
        self.lengths = self.params["lengths"]
        self.angles = list(self.params["angles"])
        self._compute_fk()

    def _compute_fk(self):
        self.joints = [(0, 0)]
        x, y = 0, 0
        cumulative_angle = 0
        for i, (L, theta) in enumerate(zip(self.lengths, self.angles)):
            cumulative_angle += theta
            x += L * math.cos(cumulative_angle)
            y += L * math.sin(cumulative_angle)
            self.joints.append((x, y))
        self.end_effector = self.joints[-1]
        self.metrics["end_x"] = self.end_effector[0]
        self.metrics["end_y"] = self.end_effector[1]

    def step(self, dt=0.02):
        super().step(dt)
        # Slowly oscillate joints for animation
        for i in range(len(self.angles)):
            self.angles[i] += 0.02 * math.sin(self.time + i)
        self._compute_fk()
        self._record({"x": self.end_effector[0], "y": self.end_effector[1],
                      "angles": list(self.angles)})

    def visualize(self, output_dir=None):
        if not HAS_MPL:
            return "matplotlib not available"
        output_dir = output_dir or get_engine().output_dir
        fig, ax = plt.subplots(figsize=(8, 8))
        fig.patch.set_facecolor('#0a0a0f')
        vis = VisHelper()
        ax.set_facecolor('#0a0a0f')
        ax.set_xlim(-5, 5); ax.set_ylim(-3, 5)
        ax.set_aspect('equal')

        colors = [vis.COLORS["cyan"], vis.COLORS["orange"], vis.COLORS["green"]]
        for i in range(len(self.joints) - 1):
            x1, y1 = self.joints[i]
            x2, y2 = self.joints[i + 1]
            ax.plot([x1, x2], [y1, y2], color=colors[i % len(colors)], linewidth=4, solid_capstyle='round')
            ax.plot(x1, y1, 'o', color='white', markersize=8, zorder=5)

        ex, ey = self.end_effector
        ax.plot(ex, ey, '*', color=vis.COLORS["yellow"], markersize=15, zorder=6)
        ax.set_title("Robot Arm - Forward Kinematics", color='white', fontsize=13)
        vis.add_grid(ax)
        plt.tight_layout()
        return VisHelper.save_figure(fig, f"robot_arm_{int(self.time*1000)}.png", output_dir)


class AStarSim(BaseSimulation):
    SIM_TYPE = "astar"
    SIM_NAME = "A* Pathfinding"

    def __init__(self, params=None):
        defaults = {
            "grid_size": 20,
            "obstacle_density": 0.25,
            "start": [0, 0],
            "goal": [19, 19],
        }
        p = {**defaults, **(params or {})}
        super().__init__(p)

    def initialize(self):
        super().initialize()
        import random
        n = self.params["grid_size"]
        self.grid = [[0] * n for _ in range(n)]
        # Place obstacles
        for i in range(n):
            for j in range(n):
                if random.random() < self.params["obstacle_density"]:
                    if [i, j] != self.params["start"] and [i, j] != self.params["goal"]:
                        self.grid[i][j] = 1
        self.start_pos = tuple(self.params["start"])
        self.goal_pos = tuple(self.params["goal"])
        self.path = []
        self.explored = []
        self._run_astar()
        self.metrics["path_length"] = len(self.path)
        self.metrics["explored_count"] = len(self.explored)

    def _heuristic(self, a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def _run_astar(self):
        n = self.params["grid_size"]
        open_set = [(0, self.start_pos)]
        came_from = {}
        g_score = {self.start_pos: 0}
        explored_order = []

        while open_set:
            _, current = heapq.heappop(open_set)
            explored_order.append(current)

            if current == self.goal_pos:
                # Reconstruct path
                path = [current]
                while current in came_from:
                    current = came_from[current]
                    path.append(current)
                self.path = path[::-1]
                self.explored = explored_order
                return

            for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                neighbor = (current[0] + dx, current[1] + dy)
                if 0 <= neighbor[0] < n and 0 <= neighbor[1] < n:
                    if self.grid[neighbor[0]][neighbor[1]] == 1:
                        continue
                    tentative_g = g_score[current] + 1
                    if tentative_g < g_score.get(neighbor, float('inf')):
                        came_from[neighbor] = current
                        g_score[neighbor] = tentative_g
                        f = tentative_g + self._heuristic(neighbor, self.goal_pos)
                        heapq.heappush(open_set, (f, neighbor))

        self.path = []
        self.explored = explored_order

    def step(self, dt=0.02):
        super().step(dt)

    def visualize(self, output_dir=None):
        if not HAS_MPL:
            return "matplotlib not available"
        output_dir = output_dir or get_engine().output_dir
        n = self.params["grid_size"]
        fig, ax = plt.subplots(figsize=(8, 8))
        fig.patch.set_facecolor('#0a0a0f')
        vis = VisHelper()
        ax.set_facecolor('#0a0a0f')
        ax.set_xlim(-0.5, n - 0.5); ax.set_ylim(-0.5, n - 0.5)
        ax.set_aspect('equal')

        # Draw grid
        for i in range(n):
            for j in range(n):
                if self.grid[i][j] == 1:
                    rect = patches.Rectangle((j - 0.5, n - i - 0.5), 1, 1, facecolor='#334155', edgecolor='#1e293b')
                    ax.add_patch(rect)

        # Draw explored
        for e in self.explored:
            ax.plot(e[1], n - e[0], 's', color=vis.COLORS["blue"], markersize=3, alpha=0.3)

        # Draw path
        if self.path:
            px = [p[1] for p in self.path]
            py = [n - p[0] for p in self.path]
            ax.plot(px, py, color=vis.COLORS["cyan"], linewidth=2, marker='o', markersize=4)

        # Start and goal
        ax.plot(self.start_pos[1], n - self.start_pos[0], 'o', color=vis.COLORS["green"], markersize=12, label="Start")
        ax.plot(self.goal_pos[1], n - self.goal_pos[0], '*', color=vis.COLORS["red"], markersize=15, label="Goal")

        ax.set_title(f"A* Pathfinding (explored={len(self.explored)}, path={len(self.path)})", color='white', fontsize=13)
        ax.legend(fontsize=10, facecolor='#111827', edgecolor='#334155', labelcolor='white')
        plt.tight_layout()
        return VisHelper.save_figure(fig, f"astar_{int(self.time*1000)}.png", output_dir)


class InvertedPendulumSim(BaseSimulation):
    SIM_TYPE = "inverted_pendulum"
    SIM_NAME = "Inverted Pendulum on Cart (PID Balance)"

    def __init__(self, params=None):
        defaults = {
            "cart_mass": 1.0, "pendulum_mass": 0.1,
            "pendulum_length": 1.0, "gravity": 9.81,
            "Kp": 50.0, "Ki": 0.1, "Kd": 10.0,
        }
        p = {**defaults, **(params or {})}
        super().__init__(p)

    def initialize(self):
        super().initialize()
        self.x = 0.0
        self.theta = 0.1  # slight perturbation
        self.x_dot = 0.0
        self.theta_dot = 0.0
        self.cart_v = 0.0
        self.integral = 0.0
        self.metrics = {"x": 0, "theta_deg": math.degrees(0.1)}

    def step(self, dt=0.01):
        M = self.params["cart_mass"]
        m = self.params["pendulum_mass"]
        L = self.params["pendulum_length"]
        g = self.params["gravity"]

        # PID on theta
        error = self.theta
        self.integral += error * dt
        derivative = (error - getattr(self, '_prev_theta', 0)) / dt
        self._prev_theta = error

        F = -self.params["Kp"] * error - self.params["Ki"] * self.integral - self.params["Kd"] * derivative

        # Physics
        sin_t = math.sin(self.theta)
        cos_t = math.cos(self.theta)
        denom = M + m - m * cos_t**2

        x_ddot = (F + m * L * self.theta_dot**2 * sin_t - m * g * sin_t * cos_t) / denom
        theta_ddot = (g * sin_t * cos_t - x_ddot * cos_t) / L

        self.x_dot += x_ddot * dt
        self.theta_dot += theta_ddot * dt
        self.x += self.x_dot * dt
        self.theta += self.theta_dot * dt

        super().step(dt)
        self.metrics["x"] = self.x
        self.metrics["theta"] = self.theta
        self.metrics["theta_deg"] = math.degrees(self.theta)
        self._record({"x": self.x, "theta": self.theta, "F": F})

    def visualize(self, output_dir=None):
        if not HAS_MPL:
            return "matplotlib not available"
        output_dir = output_dir or get_engine().output_dir
        fig, axes = plt.subplots(1, 2, figsize=(14, 6))
        fig.patch.set_facecolor('#0a0a0f')
        vis = VisHelper()

        ts = [d["t"] for d in self.history]
        ax = axes[0]; ax.set_facecolor('#0a0a0f')
        ax.plot(ts, [math.degrees(d["theta"]) for d in self.history], color=vis.COLORS["cyan"], linewidth=1.5, label="theta")
        ax.axhline(y=0, color=vis.COLORS["yellow"], linestyle='--', alpha=0.5)
        ax.set_title("Pendulum Angle", color='white', fontsize=13)
        ax.legend(fontsize=10, facecolor='#111827', edgecolor='#334155', labelcolor='white')
        vis.label_axes(ax, "Time (s)", "Angle (deg)")
        vis.add_grid(ax)

        ax = axes[1]; ax.set_facecolor('#0a0a0f')
        ax.plot(ts, [d["x"] for d in self.history], color=vis.COLORS["orange"], linewidth=1.5, label="cart position")
        ax.set_title("Cart Position", color='white', fontsize=13)
        ax.legend(fontsize=10, facecolor='#111827', edgecolor='#334155', labelcolor='white')
        vis.label_axes(ax, "Time (s)", "x (m)")
        vis.add_grid(ax)

        plt.tight_layout()
        return VisHelper.save_figure(fig, f"inverted_pendulum_{int(self.time*1000)}.png", output_dir)


def register_robotics_simulations(engine=None):
    engine = engine or get_engine()
    engine.register_simulation("pid_controller", PIDControllerSim)
    engine.register_simulation("robot_arm", RobotArmSim)
    engine.register_simulation("astar", AStarSim)
    engine.register_simulation("inverted_pendulum", InvertedPendulumSim)
