"""
ZENITH Biology Simulation Module
Implements: SIR Model, Lotka-Volterra, Population Growth, Genetics, Enzyme Kinetics
"""

import math
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


class SIRSim(BaseSimulation):
    SIM_TYPE = "sir_model"
    SIM_NAME = "SIR Disease Model"

    def __init__(self, params=None):
        defaults = {
            "beta": 0.3, "gamma": 0.1, "population": 1000,
            "infected": 10, "recovered": 0,
        }
        p = {**defaults, **(params or {})}
        super().__init__(p)

    def initialize(self):
        super().initialize()
        N = self.params["population"]
        self.S = N - self.params["infected"] - self.params["recovered"]
        self.I = self.params["infected"]
        self.R = self.params["recovered"]
        self.beta = self.params["beta"]
        self.gamma = self.params["gamma"]
        self.metrics = {"S": self.S, "I": self.I, "R": self.R, "peak_infected": self.I}

    def step(self, dt=0.1):
        dS = -self.beta * self.S * self.I / self.params["population"]
        dI = self.beta * self.S * self.I / self.params["population"] - self.gamma * self.I
        dR = self.gamma * self.I
        self.S += dS * dt
        self.I += dI * dt
        self.R += dR * dt
        self.S = max(0, self.S)
        self.I = max(0, self.I)
        self.R = max(0, self.R)
        super().step(dt)
        self.metrics["S"] = self.S
        self.metrics["I"] = self.I
        self.metrics["R"] = self.R
        self.metrics["peak_infected"] = max(self.metrics.get("peak_infected", 0), self.I)
        self.metrics["herd_immunity_threshold"] = 1 - self.gamma / self.beta if self.beta > 0 else 0
        self._record({"S": self.S, "I": self.I, "R": self.R})

    def visualize(self, output_dir=None):
        if not HAS_MPL:
            return "matplotlib not available"
        output_dir = output_dir or get_engine().output_dir
        fig, axes = plt.subplots(1, 2, figsize=(14, 6))
        fig.patch.set_facecolor('#0a0a0f')
        vis = VisHelper()

        ts = [d["t"] for d in self.history]
        ax = axes[0]; ax.set_facecolor('#0a0a0f')
        ax.plot(ts, [d["S"] for d in self.history], color=vis.COLORS["cyan"], linewidth=1.5, label="Susceptible")
        ax.plot(ts, [d["I"] for d in self.history], color=vis.COLORS["red"], linewidth=1.5, label="Infected")
        ax.plot(ts, [d["R"] for d in self.history], color=vis.COLORS["green"], linewidth=1.5, label="Recovered")
        ax.set_title("SIR Model", color='white', fontsize=13)
        ax.legend(fontsize=10, facecolor='#111827', edgecolor='#334155', labelcolor='white')
        vis.label_axes(ax, "Time", "Population")
        vis.add_grid(ax)

        ax = axes[1]; ax.set_facecolor('#0a0a0f')
        ax.fill_between(ts, [d["S"] for d in self.history], alpha=0.3, color=vis.COLORS["cyan"])
        ax.fill_between(ts, [d["I"] for d in self.history], alpha=0.3, color=vis.COLORS["red"])
        ax.fill_between(ts, [d["R"] for d in self.history], alpha=0.3, color=vis.COLORS["green"])
        ax.set_title("Stacked Area", color='white', fontsize=13)
        vis.label_axes(ax, "Time", "Population")
        vis.add_grid(ax)

        plt.tight_layout()
        return VisHelper.save_figure(fig, f"sir_{int(self.time*1000)}.png", output_dir)

    def explain(self):
        R0 = self.beta / self.gamma if self.gamma > 0 else 0
        hit = self.metrics.get("herd_immunity_threshold", 0)
        return (f"SIR Model: beta={self.beta}, gamma={self.gamma}, R0={R0:.2f}\n"
                f"Herd immunity threshold: {hit*100:.1f}%\n"
                f"Peak infected: {self.metrics['peak_infected']:.0f}")


class LotkaVolterraSim(BaseSimulation):
    SIM_TYPE = "predator_prey"
    SIM_NAME = "Lotka-Volterra Predator-Prey"

    def __init__(self, params=None):
        defaults = {
            "prey_birth": 1.1, "predation": 0.4,
            "predator_death": 0.4, "efficiency": 0.1,
            "prey_init": 10, "predator_init": 5,
        }
        p = {**defaults, **(params or {})}
        super().__init__(p)

    def initialize(self):
        super().initialize()
        self.prey = self.params["prey_init"]
        self.pred = self.params["predator_init"]
        self.a = self.params["prey_birth"]
        self.b = self.params["predation"]
        self.c = self.params["predator_death"]
        self.d = self.params["efficiency"]
        self.metrics = {"prey": self.prey, "predator": self.pred}

    def step(self, dt=0.05):
        dx = self.a * self.prey - self.b * self.prey * self.pred
        dy = self.d * self.prey * self.pred - self.c * self.pred
        self.prey += dx * dt
        self.pred += dy * dt
        self.prey = max(0, self.prey)
        self.pred = max(0, self.pred)
        super().step(dt)
        self.metrics["prey"] = self.prey
        self.metrics["predator"] = self.pred
        self._record({"prey": self.prey, "pred": self.pred})

    def visualize(self, output_dir=None):
        if not HAS_MPL:
            return "matplotlib not available"
        output_dir = output_dir or get_engine().output_dir
        fig, axes = plt.subplots(1, 2, figsize=(14, 6))
        fig.patch.set_facecolor('#0a0a0f')
        vis = VisHelper()

        ts = [d["t"] for d in self.history]
        ax = axes[0]; ax.set_facecolor('#0a0a0f')
        ax.plot(ts, [d["prey"] for d in self.history], color=vis.COLORS["green"], linewidth=1.5, label="Prey")
        ax.plot(ts, [d["pred"] for d in self.history], color=vis.COLORS["red"], linewidth=1.5, label="Predator")
        ax.set_title("Population Over Time", color='white', fontsize=13)
        ax.legend(fontsize=10, facecolor='#111827', edgecolor='#334155', labelcolor='white')
        vis.label_axes(ax, "Time", "Population")
        vis.add_grid(ax)

        ax = axes[1]; ax.set_facecolor('#0a0a0f')
        ax.plot([d["prey"] for d in self.history], [d["pred"] for d in self.history],
                color=vis.COLORS["purple"], linewidth=1)
        ax.set_title("Phase Portrait", color='white', fontsize=13)
        vis.label_axes(ax, "Prey", "Predator")
        vis.add_grid(ax)

        plt.tight_layout()
        return VisHelper.save_figure(fig, f"lotka_{int(self.time*1000)}.png", output_dir)


class PopulationGrowthSim(BaseSimulation):
    SIM_TYPE = "population_growth"
    SIM_NAME = "Population Growth Model"

    def __init__(self, params=None):
        defaults = {
            "growth_rate": 0.5, "carrying_capacity": 1000,
            "initial_pop": 10, "model": "logistic",
        }
        p = {**defaults, **(params or {})}
        super().__init__(p)

    def initialize(self):
        super().initialize()
        self.pop = self.params["initial_pop"]
        self.K = self.params["carrying_capacity"]
        self.r = self.params["growth_rate"]
        self.metrics = {"population": self.pop, "carrying_capacity": self.K}

    def step(self, dt=0.1):
        if self.params["model"] == "logistic":
            dP = self.r * self.pop * (1 - self.pop / self.K)
        else:
            dP = self.r * self.pop
        self.pop += dP * dt
        self.pop = max(0, self.pop)
        super().step(dt)
        self.metrics["population"] = self.pop
        self.metrics["growth_rate_current"] = dP
        self._record({"pop": self.pop})

    def visualize(self, output_dir=None):
        if not HAS_MPL:
            return "matplotlib not available"
        output_dir = output_dir or get_engine().output_dir
        fig, ax = plt.subplots(figsize=(10, 6))
        fig.patch.set_facecolor('#0a0a0f')
        vis = VisHelper()
        ax.set_facecolor('#0a0a0f')

        ts = [d["t"] for d in self.history]
        ax.plot(ts, [d["pop"] for d in self.history], color=vis.COLORS["cyan"], linewidth=2)
        ax.axhline(y=self.K, color=vis.COLORS["yellow"], linestyle='--', alpha=0.5, label=f"K={self.K}")
        ax.set_title(f"Population Growth ({self.params['model']})", color='white', fontsize=13)
        ax.legend(fontsize=10, facecolor='#111827', edgecolor='#334155', labelcolor='white')
        vis.label_axes(ax, "Time", "Population")
        vis.add_grid(ax)
        plt.tight_layout()
        return VisHelper.save_figure(fig, f"pop_growth_{int(self.time*1000)}.png", output_dir)


class EnzymeKineticsSim(BaseSimulation):
    SIM_TYPE = "enzyme_kinetics"
    SIM_NAME = "Michaelis-Menten Enzyme Kinetics"

    def __init__(self, params=None):
        defaults = {"Vmax": 10.0, "Km": 2.0, "substrate_range": 20}
        p = {**defaults, **(params or {})}
        super().__init__(p)

    def initialize(self):
        super().initialize()
        if HAS_NUMPY:
            self.s_conc = np.linspace(0, self.params["substrate_range"], 200)
            self.v_rates = (self.params["Vmax"] * self.s_conc) / (self.params["Km"] + self.s_conc)
            self.metrics["Vmax"] = self.params["Vmax"]
            self.metrics["Km"] = self.params["Km"]

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
        ax.plot(self.s_conc, self.v_rates, color=vis.COLORS["cyan"], linewidth=2)
        ax.axhline(y=self.params["Vmax"], color=vis.COLORS["yellow"], linestyle='--', alpha=0.5, label=f"Vmax={self.params['Vmax']}")
        ax.axvline(x=self.params["Km"], color=vis.COLORS["orange"], linestyle=':', alpha=0.5, label=f"Km={self.params['Km']}")
        ax.set_title("Michaelis-Menten Curve", color='white', fontsize=13)
        ax.legend(fontsize=10, facecolor='#111827', edgecolor='#334155', labelcolor='white')
        vis.label_axes(ax, "[S] (substrate)", "V (rate)")
        vis.add_grid(ax)

        ax = axes[1]; ax.set_facecolor('#0a0a0f')
        lineweaver = 1 / self.v_rates[1:]
        rec_s = 1 / self.s_conc[1:]
        ax.plot(rec_s, lineweaver, color=vis.COLORS["green"], linewidth=1.5)
        ax.set_title("Lineweaver-Burk Plot", color='white', fontsize=13)
        vis.label_axes(ax, "1/[S]", "1/V")
        vis.add_grid(ax)

        plt.tight_layout()
        return VisHelper.save_figure(fig, f"enzyme_{int(self.time*1000)}.png", output_dir)


def register_biology_simulations(engine=None):
    engine = engine or get_engine()
    engine.register_simulation("sir_model", SIRSim)
    engine.register_simulation("predator_prey", LotkaVolterraSim)
    engine.register_simulation("population_growth", PopulationGrowthSim)
    engine.register_simulation("enzyme_kinetics", EnzymeKineticsSim)
