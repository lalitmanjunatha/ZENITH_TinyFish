"""
ZENITH Electronics Simulation Module
Implements: RC/RL/RLC circuits, Rectifiers, Digital Logic Gates, Basic Components
"""

import math
import numpy as np
from typing import Any, Dict, List
from .core import BaseSimulation, VisHelper, get_engine

try:
    import matplotlib.pyplot as plt
    from matplotlib.figure import Figure
    HAS_MPL = True
except ImportError:
    HAS_MPL = False


class RCSim(BaseSimulation):
    SIM_TYPE = "rc_circuit"
    SIM_NAME = "RC Circuit (Charging/Discharging)"

    def __init__(self, params=None):
        defaults = {
            "voltage": 5.0, "resistance": 1000.0, "capacitance": 0.001,
            "mode": "charge",
        }
        p = {**defaults, **(params or {})}
        super().__init__(p)

    def initialize(self):
        super().initialize()
        V = self.params["voltage"]
        R = self.params["resistance"]
        C = self.params["capacitance"]
        self.tau = R * C
        self.v_cap = 0.0 if self.params["mode"] == "charge" else V
        self.metrics = {"tau": self.tau, "voltage_source": V, "resistance": R, "capacitance": C}

    def step(self, dt=0.02):
        V = self.params["voltage"]
        tau = self.tau
        super().step(dt)
        if self.params["mode"] == "charge":
            self.v_cap = V * (1 - math.exp(-self.time / tau))
        else:
            self.v_cap = V * math.exp(-self.time / tau)

        i = (V - self.v_cap) / self.params["resistance"] if self.params["mode"] == "charge" else -self.v_cap / self.params["resistance"]
        self.metrics["v_capacitor"] = self.v_cap
        self.metrics["current"] = i
        self.metrics["v_resistor"] = V - self.v_cap if self.params["mode"] == "charge" else self.v_cap
        self.metrics["percent"] = (self.v_cap / V * 100) if V > 0 else 0
        self._record({"vc": self.v_cap, "i": i, "vr": self.metrics["v_resistor"]})

    def visualize(self, output_dir=None):
        if not HAS_MPL:
            return "matplotlib not available"
        output_dir = output_dir or get_engine().output_dir
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))
        fig.patch.set_facecolor('#0a0a0f')
        vis = VisHelper()

        ts = [d["t"] for d in self.history]
        vcs = [d["vc"] for d in self.history]

        ax = axes[0]; ax.set_facecolor('#0a0a0f')
        ax.plot(ts, vcs, color=vis.COLORS["cyan"], linewidth=2, label="V_capacitor")
        ax.axhline(y=self.params["voltage"], color=vis.COLORS["yellow"], linestyle='--', alpha=0.5, label="V_source")
        ax.axhline(y=self.params["voltage"] * 0.632, color=vis.COLORS["orange"], linestyle=':', alpha=0.5, label="63.2% (1 tau)")
        ax.set_title(f"RC Circuit ({self.params['mode']})", color='white', fontsize=13)
        ax.legend(fontsize=9, facecolor='#111827', edgecolor='#334155', labelcolor='white')
        vis.label_axes(ax, "Time (s)", "Voltage (V)")
        vis.add_grid(ax)

        ax = axes[1]; ax.set_facecolor('#0a0a0f')
        currents = [d["i"] * 1000 for d in self.history]  # mA
        ax.plot(ts, currents, color=vis.COLORS["green"], linewidth=1.5, label="Current")
        ax.set_title("Current", color='white', fontsize=13)
        ax.legend(fontsize=9, facecolor='#111827', edgecolor='#334155', labelcolor='white')
        vis.label_axes(ax, "Time (s)", "Current (mA)")
        vis.add_grid(ax)

        plt.tight_layout()
        return VisHelper.save_figure(fig, f"rc_circuit_{int(self.time*1000)}.png", output_dir)


class FullWaveRectifierSim(BaseSimulation):
    SIM_TYPE = "full_wave_rectifier"
    SIM_NAME = "Full-Wave Bridge Rectifier"

    def __init__(self, params=None):
        defaults = {"amplitude": 5.0, "frequency": 50.0, "diode_drop": 0.7}
        p = {**defaults, **(params or {})}
        super().__init__(p)

    def initialize(self):
        super().initialize()
        self.metrics = {"amplitude": self.params["amplitude"], "frequency": self.params["frequency"]}

    def step(self, dt=0.001):
        super().step(dt)
        V = self.params["amplitude"]
        f = self.params["frequency"]
        Vd = self.params["diode_drop"]
        v_in = V * math.sin(2 * math.pi * f * self.time)
        v_out = abs(v_in) - 2 * Vd
        v_out = max(0, v_out)
        self.metrics["v_in"] = v_in
        self.metrics["v_out"] = v_out
        self._record({"vin": v_in, "vout": v_out})

    def visualize(self, output_dir=None):
        if not HAS_MPL:
            return "matplotlib not available"
        output_dir = output_dir or get_engine().output_dir
        fig, ax = plt.subplots(figsize=(12, 5))
        fig.patch.set_facecolor('#0a0a0f')
        vis = VisHelper()
        ax.set_facecolor('#0a0a0f')

        ts = [d["t"] * 1000 for d in self.history]
        vins = [d["vin"] for d in self.history]
        vouts = [d["vout"] for d in self.history]
        ax.plot(ts, vins, color=vis.COLORS["cyan"], linewidth=1, alpha=0.5, label="Input (AC)")
        ax.plot(ts, vouts, color=vis.COLORS["orange"], linewidth=1.5, label="Output (DC)")
        ax.set_title("Full-Wave Bridge Rectifier", color='white', fontsize=13)
        ax.legend(fontsize=10, facecolor='#111827', edgecolor='#334155', labelcolor='white')
        vis.label_axes(ax, "Time (ms)", "Voltage (V)")
        vis.add_grid(ax)
        plt.tight_layout()
        return VisHelper.save_figure(fig, f"rectifier_{int(self.time*1000)}.png", output_dir)


class DigitalLogicSim(BaseSimulation):
    SIM_TYPE = "digital_logic"
    SIM_NAME = "Digital Logic Gates"

    def __init__(self, params=None):
        defaults = {"gate": "AND", "input_a": [0,0,1,1], "input_b": [0,1,0,1]}
        p = {**defaults, **(params or {})}
        super().__init__(p)

    def initialize(self):
        super().initialize()
        a = self.params["input_a"]
        b = self.params["input_b"]
        gate = self.params["gate"].upper()
        output = []
        for i in range(len(a)):
            if gate == "AND":
                output.append(a[i] & b[i])
            elif gate == "OR":
                output.append(a[i] | b[i])
            elif gate == "XOR":
                output.append(a[i] ^ b[i])
            elif gate == "NAND":
                output.append(1 - (a[i] & b[i]))
            elif gate == "NOR":
                output.append(1 - (a[i] | b[i]))
            elif gate == "NOT":
                output.append(1 - a[i])
            else:
                output.append(a[i] & b[i])
        self.output = output
        self.metrics = {"gate": gate, "truth_table": {"A": a, "B": b, "Output": output}}

    def step(self, dt=0.02):
        super().step(dt)

    def visualize(self, output_dir=None):
        if not HAS_MPL:
            return "matplotlib not available"
        output_dir = output_dir or get_engine().output_dir
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))
        fig.patch.set_facecolor('#0a0a0f')
        vis = VisHelper()

        # Truth table
        ax = axes[0]; ax.set_facecolor('#0a0a0f')
        ax.axis('off')
        ax.set_title(f"{self.params['gate']} Gate - Truth Table", color='white', fontsize=13, pad=15)
        a = self.params["input_a"]
        b = self.params["input_b"]
        table_data = [["A", "B", "Output"]] + [[a[i], b[i], self.output[i]] for i in range(len(a))]
        table = ax.table(cellText=table_data, loc='center', cellLoc='center')
        table.auto_set_font_size(False)
        table.set_fontsize(12)
        for (row, col), cell in table.get_celld().items():
            cell.set_edgecolor('#334155')
            if row == 0:
                cell.set_facecolor('#1e40af')
                cell.set_text_props(color='white', fontweight='bold')
            else:
                cell.set_facecolor('#111827')
                cell.set_text_props(color='white')
            cell.set_height(0.15)

        # Digital waveform
        ax = axes[1]; ax.set_facecolor('#0a0a0f')
        n = len(a)
        t_a, t_b, t_out = [], [], []
        for i in range(n):
            t_a.extend([i, i+0.9, i+0.9, i+1])
            t_b.extend([i, i+0.9, i+0.9, i+1])
            t_out.extend([i, i+0.9, i+0.9, i+1])
            v_a = [a[i], a[i], a[i], a[i]]
            v_b = [b[i]+1.5, b[i]+1.5, b[i]+1.5, b[i]+1.5]
            v_o = [self.output[i]+3, self.output[i]+3, self.output[i]+3, self.output[i]+3]
            ax.fill_between(t_a[-4:], [0]*4, v_a, step='mid', alpha=0.4, color=vis.COLORS["cyan"])
            ax.fill_between(t_b[-4:], [1.5]*4, v_b, step='mid', alpha=0.4, color=vis.COLORS["green"])
            ax.fill_between(t_out[-4:], [3]*4, v_o, step='mid', alpha=0.4, color=vis.COLORS["orange"])

        ax.set_xlim(0, n)
        ax.set_ylim(-0.5, 5)
        ax.set_yticks([0.5, 2, 3.5])
        ax.set_yticklabels(["A", "B", "Out"])
        ax.set_title("Waveform", color='white', fontsize=13)
        vis.add_grid(ax)
        plt.tight_layout()
        return VisHelper.save_figure(fig, f"digital_{self.params['gate']}_{int(self.time*1000)}.png", output_dir)


def register_electronics_simulations(engine=None):
    engine = engine or get_engine()
    engine.register_simulation("rc_circuit", RCSim)
    engine.register_simulation("full_wave_rectifier", FullWaveRectifierSim)
    engine.register_simulation("digital_logic", DigitalLogicSim)
