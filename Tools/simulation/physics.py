"""
ZENITH Physics Simulation Module
Implements: Pendulum, Projectile, Spring-Mass, Collision, Wave, Double Pendulum, Air Resistance
"""

import math
import numpy as np
from typing import Any, Dict, List
from .core import BaseSimulation, VisHelper, get_engine

try:
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches
    from matplotlib.figure import Figure
    HAS_MPL = True
except ImportError:
    HAS_MPL = False


# =========================================
# PENDULUM
# =========================================

class PendulumSim(BaseSimulation):
    SIM_TYPE = "pendulum"
    SIM_NAME = "Simple Pendulum"

    def __init__(self, params=None):
        defaults = {
            "length": 2.0,
            "angle": math.pi / 4,
            "angular_velocity": 0.0,
            "gravity": 9.81,
            "damping": 0.0,
            "mass": 1.0,
        }
        p = {**defaults, **(params or {})}
        super().__init__(p)
        self.theta = p["angle"]
        self.omega = p["angular_velocity"]
        self.length = p["length"]
        self.g = p["gravity"]
        self.damping = p["damping"]
        self.mass = p["mass"]

    def initialize(self):
        super().initialize()
        self.theta = self.params["angle"]
        self.omega = self.params["angular_velocity"]
        self.length = self.params["length"]
        self.g = self.params["gravity"]
        self.damping = self.params["damping"]
        self.metrics = {
            "max_angle": abs(self.theta),
            "energy": 0.5 * self.mass * (self.length * self.omega)**2 + self.mass * self.g * self.length * (1 - math.cos(self.theta)),
        }

    def step(self, dt=0.02):
        # RK4 integration for accuracy
        def derivs(theta, omega):
            alpha = -(self.g / self.length) * math.sin(theta) - self.damping * omega
            return omega, alpha

        k1_t, k1_o = derivs(self.theta, self.omega)
        k2_t, k2_o = derivs(self.theta + 0.5*dt*k1_t, self.omega + 0.5*dt*k1_o)
        k3_t, k3_o = derivs(self.theta + 0.5*dt*k2_t, self.omega + 0.5*dt*k2_o)
        k4_t, k4_o = derivs(self.theta + dt*k3_t, self.omega + dt*k3_o)

        self.theta += (dt/6) * (k1_t + 2*k2_t + 2*k3_t + k4_t)
        self.omega += (dt/6) * (k1_o + 2*k2_o + 2*k3_o + k4_o)

        super().step(dt)

        # Track metrics
        self.metrics["current_angle"] = self.theta
        self.metrics["angular_velocity"] = self.omega
        self.metrics["max_angle"] = max(self.metrics.get("max_angle", 0), abs(self.theta))
        ke = 0.5 * self.mass * (self.length * self.omega)**2
        pe = self.mass * self.g * self.length * (1 - math.cos(self.theta))
        self.metrics["kinetic_energy"] = ke
        self.metrics["potential_energy"] = pe
        self.metrics["total_energy"] = ke + pe

        x = self.length * math.sin(self.theta)
        y = -self.length * math.cos(self.theta)
        self._record({"x": x, "y": y, "theta": self.theta, "omega": self.omega,
                      "ke": ke, "pe": pe, "te": ke + pe})

    def get_state(self):
        s = super().get_state()
        x = self.length * math.sin(self.theta)
        y = -self.length * math.cos(self.theta)
        s["bob_position"] = {"x": x, "y": y}
        s["angle_deg"] = math.degrees(self.theta)
        s["period"] = 2 * math.pi * math.sqrt(self.length / self.g)
        return s

    def visualize(self, output_dir=None):
        if not HAS_MPL:
            return "matplotlib not available"
        output_dir = output_dir or get_engine().output_dir

        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        fig.patch.set_facecolor('#0a0a0f')
        vis = VisHelper()

        # Trajectory (top-left)
        ax = axes[0, 0]
        ax.set_facecolor('#0a0a0f')
        xs = [d["x"] for d in self.history]
        ys = [d["y"] for d in self.history]
        ax.plot(xs, ys, color=vis.COLORS["cyan"], linewidth=0.8, alpha=0.7)
        ax.set_title("Bob Trajectory", color='white', fontsize=12)
        vis.label_axes(ax, "X (m)", "Y (m)")
        vis.add_grid(ax)
        ax.set_aspect('equal')

        # Angle vs time (top-right)
        ax = axes[0, 1]
        ax.set_facecolor('#0a0a0f')
        ts = [d["t"] for d in self.history]
        thetas = [d["theta"] for d in self.history]
        ax.plot(ts, thetas, color=vis.COLORS["orange"], linewidth=1)
        ax.set_title("Angle vs Time", color='white', fontsize=12)
        vis.label_axes(ax, "Time (s)", "Angle (rad)")
        vis.add_grid(ax)

        # Energy (bottom-left)
        ax = axes[1, 0]
        ax.set_facecolor('#0a0a0f')
        kes = [d["ke"] for d in self.history]
        pes = [d["pe"] for d in self.history]
        tes = [d["te"] for d in self.history]
        ax.plot(ts, kes, color=vis.COLORS["red"], linewidth=1, label="Kinetic")
        ax.plot(ts, pes, color=vis.COLORS["blue"], linewidth=1, label="Potential")
        ax.plot(ts, tes, color=vis.COLORS["yellow"], linewidth=1.5, label="Total", linestyle='--')
        ax.set_title("Energy", color='white', fontsize=12)
        ax.legend(fontsize=9, facecolor='#111827', edgecolor='#334155', labelcolor='white')
        vis.label_axes(ax, "Time (s)", "Energy (J)")
        vis.add_grid(ax)

        # Phase space (bottom-right)
        ax = axes[1, 1]
        ax.set_facecolor('#0a0a0f')
        omegas = [d["omega"] for d in self.history]
        ax.plot(thetas, omegas, color=vis.COLORS["purple"], linewidth=0.8)
        ax.set_title("Phase Space", color='white', fontsize=12)
        vis.label_axes(ax, "Angle (rad)", "Angular Velocity (rad/s)")
        vis.add_grid(ax)

        plt.tight_layout()
        return VisHelper.save_figure(fig, f"pendulum_{int(self.time*1000)}.png", output_dir)

    def explain(self):
        period = 2 * math.pi * math.sqrt(self.length / self.g)
        return (f"A pendulum of length {self.length:.1f}m swings under gravity {self.g:.1f} m/s2. "
                f"Theoretical period: {period:.3f}s. "
                f"Current angle: {math.degrees(self.theta):.1f} degrees. "
                f"Total energy: {self.metrics.get('total_energy', 0):.4f} J.")


# =========================================
# PROJECTILE MOTION
# =========================================

class ProjectileSim(BaseSimulation):
    SIM_TYPE = "projectile"
    SIM_NAME = "Projectile Motion"

    def __init__(self, params=None):
        defaults = {
            "v0": 20.0, "angle": 45.0, "gravity": 9.81,
            "height": 0.0, "mass": 1.0, "air_resistance": 0.0,
            "wind_x": 0.0, "wind_y": 0.0,
        }
        p = {**defaults, **(params or {})}
        super().__init__(p)
        self._init_state()

    def _init_state(self):
        angle_rad = math.radians(self.params["angle"])
        self.vx = self.params["v0"] * math.cos(angle_rad)
        self.vy = self.params["v0"] * math.sin(angle_rad)
        self.x = 0.0
        self.y = self.params["height"]
        self.g = self.params["gravity"]
        self.k = self.params.get("air_resistance", 0.0)
        self.wind_x = self.params.get("wind_x", 0.0)

    def initialize(self):
        super().initialize()
        self._init_state()

    def step(self, dt=0.02):
        speed = math.sqrt(self.vx**2 + self.vy**2)
        # Air resistance force (proportional to v^2)
        drag_x = -self.k * speed * self.vx if self.k else 0
        drag_y = -self.k * speed * self.vy if self.k else 0

        ax = drag_x / self.params["mass"] + self.wind_x
        ay = -self.g + drag_y / self.params["mass"]

        self.vx += ax * dt
        self.vy += ay * dt
        self.x += self.vx * dt
        self.y += self.vy * dt

        super().step(dt)

        speed_now = math.sqrt(self.vx**2 + self.vy**2)
        self.metrics["range"] = self.x
        self.metrics["max_height"] = max(self.metrics.get("max_height", 0), self.y)
        self.metrics["speed"] = speed_now
        self.metrics["current_height"] = self.y

        self._record({"x": self.x, "y": max(self.y, 0), "vx": self.vx, "vy": self.vy,
                      "speed": speed_now, "h": max(self.y, 0)})

    def get_state(self):
        s = super().get_state()
        s["range"] = self.x
        s["height"] = self.y
        s["speed"] = math.sqrt(self.vx**2 + self.vy**2)
        s["impact_time"] = self.time if self.y <= 0 and self.step_count > 1 else None
        return s

    def visualize(self, output_dir=None):
        if not HAS_MPL:
            return "matplotlib not available"
        output_dir = output_dir or get_engine().output_dir
        fig, axes = plt.subplots(1, 2, figsize=(14, 6))
        fig.patch.set_facecolor('#0a0a0f')
        vis = VisHelper()

        xs = [d["x"] for d in self.history]
        ys = [d["y"] for d in self.history]

        ax = axes[0]
        ax.set_facecolor('#0a0a0f')
        ax.plot(xs, ys, color=vis.COLORS["orange"], linewidth=2)
        ax.fill_between(xs, 0, ys, alpha=0.15, color=vis.COLORS["orange"])
        ax.set_title("Trajectory", color='white', fontsize=13)
        vis.label_axes(ax, "Distance (m)", "Height (m)")
        vis.add_grid(ax)

        ax = axes[1]
        ax.set_facecolor('#0a0a0f')
        ts = [d["t"] for d in self.history]
        speeds = [d["speed"] for d in self.history]
        ax.plot(ts, speeds, color=vis.COLORS["cyan"], linewidth=1.5, label="Speed")
        ax.plot(ts, [d["vy"] for d in self.history], color=vis.COLORS["red"], linewidth=1, label="Vy")
        ax.set_title("Speed Profile", color='white', fontsize=13)
        ax.legend(fontsize=9, facecolor='#111827', edgecolor='#334155', labelcolor='white')
        vis.label_axes(ax, "Time (s)", "Speed (m/s)")
        vis.add_grid(ax)

        plt.tight_layout()
        return VisHelper.save_figure(fig, f"projectile_{int(self.time*1000)}.png", output_dir)


# =========================================
# SPRING-MASS SYSTEM
# =========================================

class SpringMassSim(BaseSimulation):
    SIM_TYPE = "spring_mass"
    SIM_NAME = "Spring-Mass Oscillator"

    def __init__(self, params=None):
        defaults = {
            "mass": 1.0, "spring_k": 10.0, "damping": 0.1,
            "initial_displacement": 1.0, "initial_velocity": 0.0,
        }
        p = {**defaults, **(params or {})}
        super().__init__(p)
        self._init_state()

    def _init_state(self):
        self.x = self.params["initial_displacement"]
        self.v = self.params["initial_velocity"]
        self.k = self.params["spring_k"]
        self.m = self.params["mass"]
        self.c = self.params["damping"]
        self.omega_n = math.sqrt(self.k / self.m) if self.m > 0 else 0
        self.zeta = self.c / (2 * math.sqrt(self.k * self.m)) if (self.k * self.m) > 0 else 0

    def initialize(self):
        super().initialize()
        self._init_state()
        self.metrics = {"period": 2*math.pi/self.omega_n if self.omega_n > 0 else 0,
                        "frequency": self.omega_n / (2*math.pi) if self.omega_n > 0 else 0,
                        "damping_ratio": self.zeta}

    def step(self, dt=0.02):
        a = -(self.k / self.m) * self.x - (self.c / self.m) * self.v
        self.v += a * dt
        self.x += self.v * dt
        super().step(dt)

        ke = 0.5 * self.m * self.v**2
        pe = 0.5 * self.k * self.x**2
        self.metrics["displacement"] = self.x
        self.metrics["velocity"] = self.v
        self.metrics["kinetic_energy"] = ke
        self.metrics["potential_energy"] = pe
        self.metrics["total_energy"] = ke + pe
        self.metrics["max_displacement"] = max(self.metrics.get("max_displacement", 0), abs(self.x))
        self._record({"x": self.x, "v": self.v, "ke": ke, "pe": pe, "te": ke + pe})

    def visualize(self, output_dir=None):
        if not HAS_MPL:
            return "matplotlib not available"
        output_dir = output_dir or get_engine().output_dir
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        fig.patch.set_facecolor('#0a0a0f')
        vis = VisHelper()

        ts = [d["t"] for d in self.history]
        xs = [d["x"] for d in self.history]
        vs = [d["v"] for d in self.history]

        ax = axes[0, 0]; ax.set_facecolor('#0a0a0f')
        ax.plot(ts, xs, color=vis.COLORS["cyan"], linewidth=1.2)
        ax.set_title("Displacement vs Time", color='white', fontsize=11)
        vis.label_axes(ax, "Time (s)", "x (m)")
        vis.add_grid(ax)

        ax = axes[0, 1]; ax.set_facecolor('#0a0a0f')
        ax.plot(xs, vs, color=vis.COLORS["purple"], linewidth=0.8)
        ax.set_title("Phase Space", color='white', fontsize=11)
        vis.label_axes(ax, "x (m)", "v (m/s)")
        vis.add_grid(ax)

        ax = axes[1, 0]; ax.set_facecolor('#0a0a0f')
        kes = [d["ke"] for d in self.history]
        pes = [d["pe"] for d in self.history]
        tes = [d["te"] for d in self.history]
        ax.plot(ts, kes, color=vis.COLORS["red"], linewidth=1, label="KE")
        ax.plot(ts, pes, color=vis.COLORS["blue"], linewidth=1, label="PE")
        ax.plot(ts, tes, color=vis.COLORS["yellow"], linewidth=1.5, label="Total", linestyle='--')
        ax.set_title("Energy", color='white', fontsize=11)
        ax.legend(fontsize=9, facecolor='#111827', edgecolor='#334155', labelcolor='white')
        vis.label_axes(ax, "Time (s)", "Energy (J)")
        vis.add_grid(ax)

        ax = axes[1, 1]; ax.set_facecolor('#0a0a0f')
        ax.hist(xs, bins=40, color=vis.COLORS["green"], alpha=0.7, edgecolor='white', linewidth=0.3)
        ax.set_title("Position Distribution", color='white', fontsize=11)
        vis.label_axes(ax, "x (m)", "Frequency")
        vis.add_grid(ax)

        plt.tight_layout()
        return VisHelper.save_figure(fig, f"spring_{int(self.time*1000)}.png", output_dir)


# =========================================
# WAVE SIMULATION
# =========================================

class WaveSim(BaseSimulation):
    SIM_TYPE = "wave"
    SIM_NAME = "Wave Simulation"

    def __init__(self, params=None):
        defaults = {
            "length": 10.0, "wave_number": 2, "amplitude": 1.0,
            "frequency": 1.0, "damping": 0.0,
        }
        p = {**defaults, **(params or {})}
        super().__init__(p)
        self.x_grid = np.linspace(0, self.params["length"], 300) if HAS_NUMPY else []

    def initialize(self):
        super().initialize()
        self.x_grid = np.linspace(0, self.params["length"], 300) if HAS_NUMPY else []

    def step(self, dt=0.02):
        super().step(dt)
        k = self.params["wave_number"]
        A = self.params["amplitude"]
        f = self.params["frequency"]
        L = self.params["length"]
        damp = self.params.get("damping", 0)
        if HAS_NUMPY:
            y = A * np.sin(k * np.pi * self.x_grid / L) * np.cos(2 * np.pi * f * self.time) * np.exp(-damp * self.time)
            self._record({"wave_data": y.tolist(), "x_data": self.x_grid.tolist()})
        self.metrics["current_time"] = self.time

    def visualize(self, output_dir=None):
        if not HAS_MPL or not HAS_NUMPY:
            return "matplotlib/numpy not available"
        output_dir = output_dir or get_engine().output_dir
        fig, ax = plt.subplots(figsize=(12, 5))
        fig.patch.set_facecolor('#0a0a0f')
        vis = VisHelper()
        ax.set_facecolor('#0a0a0f')

        if self.history:
            last = self.history[-1]
            ax.plot(last["x_data"], last["wave_data"], color=vis.COLORS["cyan"], linewidth=1.5)
            ax.fill_between(last["x_data"], 0, last["wave_data"], alpha=0.15, color=vis.COLORS["cyan"])

        ax.set_title(f"Standing Wave  (n={self.params['wave_number']}, f={self.params['frequency']}Hz)", color='white', fontsize=13)
        vis.label_axes(ax, "Position (m)", "Amplitude (m)")
        vis.add_grid(ax)
        plt.tight_layout()
        return VisHelper.save_figure(fig, f"wave_{int(self.time*1000)}.png", output_dir)


# =========================================
# COLLISION SIMULATION
# =========================================

class CollisionSim(BaseSimulation):
    SIM_TYPE = "collision"
    SIM_NAME = "Elastic/Inelastic Collision"

    def __init__(self, params=None):
        defaults = {
            "mass_a": 1.0, "mass_b": 2.0,
            "vel_a": 5.0, "vel_b": -3.0,
            "elasticity": 1.0, "size_a": 0.5, "size_b": 0.8,
        }
        p = {**defaults, **(params or {})}
        super().__init__(p)
        self._init_state()

    def _init_state(self):
        self.pos_a = -3.0
        self.pos_b = 3.0
        self.vel_a = self.params["vel_a"]
        self.vel_b = self.params["vel_b"]
        self.collided = False

    def initialize(self):
        super().initialize()
        self._init_state()
        self.collided = False
        self.metrics = {"collisions": 0, "vel_a": self.vel_a, "vel_b": self.vel_b}

    def step(self, dt=0.02):
        self.pos_a += self.vel_a * dt
        self.pos_b += self.vel_b * dt

        # Check collision
        min_dist = self.params["size_a"] + self.params["size_b"]
        if not self.collided and abs(self.pos_a - self.pos_b) <= min_dist:
            self.collided = True
            e = self.params["elasticity"]
            m1, m2 = self.params["mass_a"], self.params["mass_b"]
            v1, v2 = self.vel_a, self.vel_b
            self.vel_a = ((m1 - e*m2)*v1 + (1+e)*m2*v2) / (m1 + m2)
            self.vel_b = ((m2 - e*m1)*v2 + (1+e)*m1*v1) / (m1 + m2)
            self.metrics["collisions"] += 1
            self._log_event("collision")

        # Wall bouncing
        if self.pos_a < -5: self.vel_a = abs(self.vel_a)
        if self.pos_a > 5: self.vel_a = -abs(self.vel_a)
        if self.pos_b < -5: self.vel_b = abs(self.vel_b)
        if self.pos_b > 5: self.vel_b = -abs(self.vel_b)

        super().step(dt)
        ke_a = 0.5 * self.params["mass_a"] * self.vel_a**2
        ke_b = 0.5 * self.params["mass_b"] * self.vel_b**2
        self.metrics["vel_a"] = self.vel_a
        self.metrics["vel_b"] = self.vel_b
        self.metrics["total_ke"] = ke_a + ke_b
        self._record({"pos_a": self.pos_a, "pos_b": self.pos_b,
                      "vel_a": self.vel_a, "vel_b": self.vel_b, "ke": ke_a + ke_b})

    def visualize(self, output_dir=None):
        if not HAS_MPL:
            return "matplotlib not available"
        output_dir = output_dir or get_engine().output_dir
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))
        fig.patch.set_facecolor('#0a0a0f')
        vis = VisHelper()

        ts = [d["t"] for d in self.history]

        ax = axes[0]; ax.set_facecolor('#0a0a0f')
        ax.plot(ts, [d["pos_a"] for d in self.history], color=vis.COLORS["cyan"], linewidth=1.5, label="Object A")
        ax.plot(ts, [d["pos_b"] for d in self.history], color=vis.COLORS["orange"], linewidth=1.5, label="Object B")
        ax.set_title("Position vs Time", color='white', fontsize=12)
        ax.legend(fontsize=9, facecolor='#111827', edgecolor='#334155', labelcolor='white')
        vis.label_axes(ax, "Time (s)", "Position (m)")
        vis.add_grid(ax)

        ax = axes[1]; ax.set_facecolor('#0a0a0f')
        ax.plot(ts, [d["vel_a"] for d in self.history], color=vis.COLORS["cyan"], linewidth=1.5, label="v_A")
        ax.plot(ts, [d["vel_b"] for d in self.history], color=vis.COLORS["orange"], linewidth=1.5, label="v_B")
        ax.set_title("Velocity vs Time", color='white', fontsize=12)
        ax.legend(fontsize=9, facecolor='#111827', edgecolor='#334155', labelcolor='white')
        vis.label_axes(ax, "Time (s)", "Velocity (m/s)")
        vis.add_grid(ax)

        plt.tight_layout()
        return VisHelper.save_figure(fig, f"collision_{int(self.time*1000)}.png", output_dir)


# =========================================
# DOUBLE PENDULUM
# =========================================

class DoublePendulumSim(BaseSimulation):
    SIM_TYPE = "double_pendulum"
    SIM_NAME = "Double Pendulum (Chaotic)"

    def __init__(self, params=None):
        defaults = {
            "length1": 1.0, "length2": 1.0,
            "mass1": 1.0, "mass2": 1.0,
            "angle1": math.pi / 2, "angle2": math.pi / 4,
            "gravity": 9.81,
        }
        p = {**defaults, **(params or {})}
        super().__init__(p)
        self._init_state()

    def _init_state(self):
        self.theta1 = self.params["angle1"]
        self.theta2 = self.params["angle2"]
        self.omega1 = 0.0
        self.omega2 = 0.0
        self.g = self.params["gravity"]
        self.L1 = self.params["length1"]
        self.L2 = self.params["length2"]
        self.m1 = self.params["mass1"]
        self.m2 = self.params["mass2"]

    def initialize(self):
        super().initialize()
        self._init_state()

    def step(self, dt=0.01):
        t1, t2, w1, w2 = self.theta1, self.theta2, self.omega1, self.omega2
        g, L1, L2, m1, m2 = self.g, self.L1, self.L2, self.m1, self.m2

        delta = t1 - t2
        den1 = (m1 + m2) * L1 - m2 * L1 * math.cos(delta)**2
        den2 = (L2 / L1) * den1

        dw1 = (m2 * L1 * w1**2 * math.sin(delta) * math.cos(delta)
               + m2 * g * math.sin(t2) * math.cos(delta)
               + m2 * L2 * w2**2 * math.sin(delta)
               - (m1 + m2) * g * math.sin(t1)) / den1

        dw2 = (-m2 * L2 * w2**2 * math.sin(delta) * math.cos(delta)
               + (m1 + m2) * g * math.sin(t1) * math.cos(delta)
               - (m1 + m2) * L1 * w1**2 * math.sin(delta)
               - (m1 + m2) * g * math.sin(t2)) / den2

        self.omega1 += dw1 * dt
        self.omega2 += dw2 * dt
        self.theta1 += self.omega1 * dt
        self.theta2 += self.omega2 * dt
        super().step(dt)

        x1 = L1 * math.sin(self.theta1)
        y1 = -L1 * math.cos(self.theta1)
        x2 = x1 + L2 * math.sin(self.theta2)
        y2 = y1 - L2 * math.cos(self.theta2)

        self.metrics["x_tip"] = x2
        self.metrics["y_tip"] = y2
        self._record({"x1": x1, "y1": y1, "x2": x2, "y2": y2,
                      "t1": self.theta1, "t2": self.theta2})

    def visualize(self, output_dir=None):
        if not HAS_MPL:
            return "matplotlib not available"
        output_dir = output_dir or get_engine().output_dir
        fig, ax = plt.subplots(figsize=(8, 8))
        fig.patch.set_facecolor('#0a0a0f')
        vis = VisHelper()
        ax.set_facecolor('#0a0a0f')
        ax.set_xlim(-3, 3); ax.set_ylim(-3, 3)
        ax.set_aspect('equal')
        ax.set_title("Double Pendulum Trace", color='white', fontsize=14)

        xs = [d["x2"] for d in self.history]
        ys = [d["y2"] for d in self.history]
        points = ax.plot(xs, ys, color=vis.COLORS["purple"], linewidth=0.3, alpha=0.8)
        vis.add_grid(ax)

        return VisHelper.save_figure(fig, f"double_pendulum_{int(self.time*1000)}.png", output_dir)

    def explain(self):
        return ("A double pendulum exhibits chaotic motion — tiny changes in initial conditions "
                "lead to vastly different trajectories. This is a classic example of deterministic chaos.")


# =========================================
# REGISTER ALL PHYSICS SIMS
# =========================================

def register_physics_simulations(engine=None):
    engine = engine or get_engine()
    engine.register_simulation("pendulum", PendulumSim)
    engine.register_simulation("projectile", ProjectileSim)
    engine.register_simulation("spring_mass", SpringMassSim)
    engine.register_simulation("wave", WaveSim)
    engine.register_simulation("collision", CollisionSim)
    engine.register_simulation("double_pendulum", DoublePendulumSim)
