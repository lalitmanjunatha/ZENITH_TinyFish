import asyncio
import math
import time
from datetime import datetime
from typing import Optional, List, Dict, Any, Tuple
from pathlib import Path

import numpy as np

TOOL = {
    "name": "simulation_engine",
    "description": "Run physics simulations and create visualizations: pendulum, projectile, wave, spring, and orbit simulations. Use when the user wants to see a physics simulation or scientific visualization.",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "simulation": {"type": "STRING", "description": "Simulation type: 'pendulum', 'projectile', 'wave', 'spring', 'orbit'"},
            "length": {"type": "NUMBER", "description": "Length parameter (e.g. pendulum length in meters)"},
            "initial_angle": {"type": "NUMBER", "description": "Initial angle in radians"},
            "gravity": {"type": "NUMBER", "description": "Gravity value (default: 9.81)"},
            "duration": {"type": "NUMBER", "description": "Simulation duration in seconds (default: 10)"},
            "velocity": {"type": "NUMBER", "description": "Initial velocity for projectile/orbit"},
            "mass": {"type": "NUMBER", "description": "Mass for spring simulation"}
        },
        "required": ["simulation"]
    },
    "handler": "handle_simulation_engine",
}

try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches
    from matplotlib.figure import Figure
    import matplotlib.animation as animation
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

try:
    from PIL import Image, ImageDraw
    PILLOW_AVAILABLE = True
except ImportError:
    PILLOW_AVAILABLE = False

from livekit.agents import function_tool


class SimulationEngine:
    """Engine for physics simulations, charts, and visualizations."""

    def __init__(self):
        self.output_dir = Path.home() / "Downloads" / "zenith_simulations"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _create_figure(self, figsize=(10, 7)):
        """Create a matplotlib figure with dark theme."""
        fig, ax = plt.subplots(figsize=figsize)
        fig.patch.set_facecolor('#0f1116')
        ax.set_facecolor('#0f1116')
        ax.tick_params(colors='white')
        for spine in ax.spines.values():
            spine.set_color('#334155')
        return fig, ax

    def _save_figure(self, fig, filename: str) -> str:
        """Save figure to file and return path."""
        filepath = self.output_dir / filename
        fig.savefig(str(filepath), dpi=150, bbox_inches='tight', facecolor='#0f1116')
        plt.close(fig)
        return str(filepath)

    # =========================
    # PHYSICS SIMULATIONS
    # =========================

    def simulate_pendulum(
        self,
        length: float = 1.0,
        initial_angle: float = math.pi / 4,
        gravity: float = 9.81,
        duration: float = 10.0,
        dt: float = 0.02
    ) -> Dict[str, List[float]]:
        """
        Simulate simple pendulum motion.
        Returns time, angle, angular_velocity, x, y coordinates.
        """
        t = 0
        theta = initial_angle
        omega = 0.0
        
        times = []
        angles = []
        angular_vels = []
        x_positions = []
        y_positions = []
        
        while t <= duration:
            alpha = -(gravity / length) * math.sin(theta)
            omega += alpha * dt
            theta += omega * dt
            
            x = length * math.sin(theta)
            y = -length * math.cos(theta)
            
            times.append(t)
            angles.append(theta)
            angular_vels.append(omega)
            x_positions.append(x)
            y_positions.append(y)
            
            t += dt
        
        return {
            "time": times,
            "angle": angles,
            "angular_velocity": angular_vels,
            "x": x_positions,
            "y": y_positions,
            "length": length,
            "gravity": gravity
        }

    def simulate_projectile(
        self,
        v0: float = 20.0,
        angle: float = math.pi / 4,
        gravity: float = 9.81,
        height: float = 0.0,
        dt: float = 0.02
    ) -> Dict[str, List[float]]:
        """Simulate projectile motion with air resistance option."""
        vx = v0 * math.cos(angle)
        vy = v0 * math.sin(angle)
        x = 0.0
        y = height
        t = 0.0
        
        times = []
        x_positions = []
        y_positions = []
        vx_vals = []
        vy_vals = []
        
        while y >= 0 and t < 30:
            times.append(t)
            x_positions.append(x)
            y_positions.append(y)
            vx_vals.append(vx)
            vy_vals.append(vy)
            
            x += vx * dt
            y += vy * dt
            vy -= gravity * dt
            t += dt
        
        return {
            "time": times,
            "x": x_positions,
            "y": y_positions,
            "vx": vx_vals,
            "vy": vy_vals,
            "range": x_positions[-1] if x_positions else 0,
            "max_height": max(y_positions) if y_positions else 0,
            "flight_time": times[-1] if times else 0
        }

    def simulate_spring_mass(
        self,
        mass: float = 1.0,
        spring_constant: float = 10.0,
        damping: float = 0.1,
        initial_displacement: float = 1.0,
        duration: float = 20.0,
        dt: float = 0.02
    ) -> Dict[str, List[float]]:
        """Simulate damped spring-mass system."""
        x = initial_displacement
        v = 0.0
        t = 0.0
        
        times = []
        positions = []
        velocities = []
        energies = []
        
        while t <= duration:
            a = -(spring_constant / mass) * x - (damping / mass) * v
            v += a * dt
            x += v * dt
            
            kinetic = 0.5 * mass * v**2
            potential = 0.5 * spring_constant * x**2
            total = kinetic + potential
            
            times.append(t)
            positions.append(x)
            velocities.append(v)
            energies.append(total)
            
            t += dt
        
        return {
            "time": times,
            "position": positions,
            "velocity": velocities,
            "energy": energies,
            "period": 2 * math.pi * math.sqrt(mass / spring_constant) if spring_constant > 0 else 0
        }

    def simulate_wave(
        self,
        length: float = 10.0,
        wave_number: int = 2,
        amplitude: float = 1.0,
        frequency: float = 1.0,
        duration: float = 5.0,
        dt: float = 0.05
    ) -> Dict[str, List]:
        """Simulate standing wave."""
        x = np.linspace(0, length, 200)
        t_vals = np.arange(0, duration, dt)
        frames = []
        
        for t in t_vals:
            y = amplitude * np.sin(wave_number * math.pi * x / length) * np.cos(2 * math.pi * frequency * t)
            frames.append(y.tolist())
        
        return {
            "x": x.tolist(),
            "frames": frames,
            "times": t_vals.tolist(),
            "length": length,
            "wave_number": wave_number,
            "frequency": frequency
        }

    # =========================
    # VISUALIZATIONS
    # =========================

    def plot_pendulum(self, sim_data: Dict, save: bool = True) -> str:
        """Create pendulum visualization."""
        if not MATPLOTLIB_AVAILABLE:
            return "❌ matplotlib not available"

        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        fig.patch.set_facecolor('#0f1116')
        
        # Phase space
        ax = axes[0, 0]
        ax.plot(sim_data["angle"], sim_data["angular_velocity"], '#4ecdc4', linewidth=1)
        ax.set_xlabel('Angle (rad)', color='white')
        ax.set_ylabel('Angular Velocity (rad/s)', color='white')
        ax.set_title('Phase Space', color='white')
        ax.tick_params(colors='white')
        ax.set_facecolor('#0f1116')
        
        # Angle vs time
        ax = axes[0, 1]
        ax.plot(sim_data["time"], sim_data["angle"], '#ff6b6b', linewidth=1)
        ax.set_xlabel('Time (s)', color='white')
        ax.set_ylabel('Angle (rad)', color='white')
        ax.set_title('Angle vs Time', color='white')
        ax.tick_params(colors='white')
        ax.set_facecolor('#0f1116')
        
        # Trajectory
        ax = axes[1, 0]
        ax.plot(sim_data["x"], sim_data["y"], '#45b7d1', linewidth=1)
        ax.scatter([0], [0], color='#ff6b6b', s=100, zorder=5)
        ax.set_xlabel('X (m)', color='white')
        ax.set_ylabel('Y (m)', color='white')
        ax.set_title('Trajectory', color='white')
        ax.tick_params(colors='white')
        ax.set_facecolor('#0f1116')
        ax.axis('equal')
        
        # Energy
        ax = axes[1, 1]
        ax.set_title('Energy (Constant)', color='white')
        ax.tick_params(colors='white')
        ax.set_facecolor('#0f1116')
        
        plt.tight_layout()
        
        if save:
            filename = f"pendulum_{datetime.now().strftime('%H%M%S')}.png"
            return self._save_figure(fig, filename)
        return "Plot created"

    def plot_projectile(self, sim_data: Dict, save: bool = True) -> str:
        """Create projectile motion visualization."""
        if not MATPLOTLIB_AVAILABLE:
            return "❌ matplotlib not available"

        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        fig.patch.set_facecolor('#0f1116')
        
        # Trajectory
        ax = axes[0, 0]
        ax.plot(sim_data["x"], sim_data["y"], '#ff6b6b', linewidth=2)
        ax.fill_between(sim_data["x"], 0, sim_data["y"], alpha=0.3, color='#ff6b6b')
        ax.set_xlabel('Distance (m)', color='white')
        ax.set_ylabel('Height (m)', color='white')
        ax.set_title(f'Trajectory (Range: {sim_data["range"]:.1f}m)', color='white')
        ax.tick_params(colors='white')
        ax.set_facecolor('#0f1116')
        ax.grid(True, alpha=0.3)
        
        # Height vs time
        ax = axes[0, 1]
        ax.plot(sim_data["time"], sim_data["y"], '#4ecdc4', linewidth=1)
        ax.set_xlabel('Time (s)', color='white')
        ax.set_ylabel('Height (m)', color='white')
        ax.set_title('Height vs Time', color='white')
        ax.tick_params(colors='white')
        ax.set_facecolor('#0f1116')
        
        # Velocity components
        ax = axes[1, 0]
        ax.plot(sim_data["time"], sim_data["vx"], '#45b7d1', label='Vx', linewidth=1)
        ax.plot(sim_data["time"], sim_data["vy"], '#f9c80e', label='Vy', linewidth=1)
        ax.set_xlabel('Time (s)', color='white')
        ax.set_ylabel('Velocity (m/s)', color='white')
        ax.set_title('Velocity Components', color='white')
        ax.legend()
        ax.tick_params(colors='white')
        ax.set_facecolor('#0f1116')
        
        # Speed vs time
        ax = axes[1, 1]
        speed = [math.sqrt(vx**2 + vy**2) for vx, vy in zip(sim_data["vx"], sim_data["vy"])]
        ax.plot(sim_data["time"], speed, '#ff6b6b', linewidth=1)
        ax.set_xlabel('Time (s)', color='white')
        ax.set_ylabel('Speed (m/s)', color='white')
        ax.set_title('Speed vs Time', color='white')
        ax.tick_params(colors='white')
        ax.set_facecolor('#0f1116')
        
        plt.tight_layout()
        
        if save:
            filename = f"projectile_{datetime.now().strftime('%H%M%S')}.png"
            return self._save_figure(fig, filename)
        return "Plot created"

    def plot_spring_mass(self, sim_data: Dict, save: bool = True) -> str:
        """Create spring-mass visualization."""
        if not MATPLOTLIB_AVAILABLE:
            return "❌ matplotlib not available"

        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        fig.patch.set_facecolor('#0f1116')
        
        # Position vs time
        ax = axes[0, 0]
        ax.plot(sim_data["time"], sim_data["position"], '#4ecdc4', linewidth=1)
        ax.set_xlabel('Time (s)', color='white')
        ax.set_ylabel('Displacement (m)', color='white')
        ax.set_title('Damped Oscillation', color='white')
        ax.tick_params(colors='white')
        ax.set_facecolor('#0f1116')
        
        # Phase space
        ax = axes[0, 1]
        ax.plot(sim_data["position"], sim_data["velocity"], '#ff6b6b', linewidth=1)
        ax.set_xlabel('Position (m)', color='white')
        ax.set_ylabel('Velocity (m/s)', color='white')
        ax.set_title('Phase Space', color='white')
        ax.tick_params(colors='white')
        ax.set_facecolor('#0f1116')
        
        # Energy
        ax = axes[1, 0]
        ax.plot(sim_data["time"], sim_data["energy"], '#f9c80e', linewidth=1)
        ax.set_xlabel('Time (s)', color='white')
        ax.set_ylabel('Total Energy (J)', color='white')
        ax.set_title('Energy Decay', color='white')
        ax.tick_params(colors='white')
        ax.set_facecolor('#0f1116')
        
        # Position histogram
        ax = axes[1, 1]
        ax.hist(sim_data["position"], bins=50, color='#45b7d1', alpha=0.7, edgecolor='white')
        ax.set_xlabel('Position (m)', color='white')
        ax.set_ylabel('Frequency', color='white')
        ax.set_title('Position Distribution', color='white')
        ax.tick_params(colors='white')
        ax.set_facecolor('#0f1116')
        
        plt.tight_layout()
        
        if save:
            filename = f"spring_{datetime.now().strftime('%H%M%S')}.png"
            return self._save_figure(fig, filename)
        return "Plot created"

    # =========================
    # CHART CREATIONS
    # =========================

    def create_bar_chart(
        self,
        labels: List[str],
        values: List[float],
        title: str = "Bar Chart",
        colors: Optional[List[str]] = None,
        horizontal: bool = False
    ) -> str:
        """Create a styled bar chart."""
        if not MATPLOTLIB_AVAILABLE:
            return "❌ matplotlib not available"

        fig, ax = self._create_figure(figsize=(10, 6))
        
        if colors is None:
            colors = ['#ff6b6b', '#4ecdc4', '#45b7d1', '#f9c80e', '#f86624', 
                     '#ea3546', '#662e9b', '#c5d86d', '#0cce6b', '#5f0f40']
        
        if horizontal:
            bars = ax.barh(range(len(labels)), values, color=colors[:len(labels)], height=0.6)
            ax.set_yticks(range(len(labels)))
            ax.set_yticklabels(labels, color='white')
            ax.set_xlabel('Value', color='white')
        else:
            bars = ax.bar(range(len(labels)), values, color=colors[:len(labels)], width=0.6)
            ax.set_xticks(range(len(labels)))
            ax.set_xticklabels(labels, color='white', rotation=45, ha='right')
            ax.set_ylabel('Value', color='white')
        
        # Add value labels
        for bar, val in zip(bars, values):
            if horizontal:
                ax.text(bar.get_width() + max(values)*0.01, bar.get_y() + bar.get_height()/2,
                       f'{val:.1f}', va='center', color='white', fontsize=10)
            else:
                ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(values)*0.01,
                       f'{val:.1f}', ha='center', va='bottom', color='white', fontsize=10)
        
        ax.set_title(title, color='white', fontsize=16, pad=20)
        ax.grid(True, alpha=0.3, axis='x' if horizontal else 'y')
        
        filename = f"barchart_{datetime.now().strftime('%H%M%S')}.png"
        return self._save_figure(fig, filename)

    def create_pie_chart(
        self,
        labels: List[str],
        values: List[float],
        title: str = "Pie Chart"
    ) -> str:
        """Create a styled pie chart."""
        if not MATPLOTLIB_AVAILABLE:
            return "❌ matplotlib not available"

        fig, ax = self._create_figure(figsize=(8, 8))
        
        colors = ['#ff6b6b', '#4ecdc4', '#45b7d1', '#f9c80e', '#f86624', 
                 '#ea3546', '#662e9b', '#c5d86d', '#0cce6b', '#5f0f40']
        
        wedges, texts, autotexts = ax.pie(
            values, labels=labels, autopct='%1.1f%%',
            colors=colors[:len(values)], startangle=90,
            textprops={'color': 'white', 'fontsize': 11}
        )
        
        for autotext in autotexts:
            autotext.set_fontweight('bold')
        
        ax.set_title(title, color='white', fontsize=16, pad=20)
        
        filename = f"piechart_{datetime.now().strftime('%H%M%S')}.png"
        return self._save_figure(fig, filename)

    def create_line_chart(
        self,
        x_data: List[float],
        y_data: List[List[float]],
        labels: List[str],
        title: str = "Line Chart",
        x_label: str = "X",
        y_label: str = "Y"
    ) -> str:
        """Create multi-line chart."""
        if not MATPLOTLIB_AVAILABLE:
            return "❌ matplotlib not available"

        fig, ax = self._create_figure(figsize=(10, 6))
        
        colors = ['#ff6b6b', '#4ecdc4', '#45b7d1', '#f9c80e', '#f86624', '#ea3546']
        
        for i, (y_vals, label) in enumerate(zip(y_data, labels)):
            ax.plot(x_data, y_vals, color=colors[i % len(colors)], 
                   linewidth=2, label=label, marker='o', markersize=4)
        
        ax.set_xlabel(x_label, color='white')
        ax.set_ylabel(y_label, color='white')
        ax.set_title(title, color='white', fontsize=16, pad=20)
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        filename = f"linechart_{datetime.now().strftime('%H%M%S')}.png"
        return self._save_figure(fig, filename)

    def create_scatter_plot(
        self,
        x_data: List[float],
        y_data: List[float],
        title: str = "Scatter Plot",
        x_label: str = "X",
        y_label: str = "Y",
        colors: Optional[List[str]] = None
    ) -> str:
        """Create scatter plot."""
        if not MATPLOTLIB_AVAILABLE:
            return "❌ matplotlib not available"

        fig, ax = self._create_figure(figsize=(10, 6))
        
        if colors:
            ax.scatter(x_data, y_data, c=colors, s=50, alpha=0.7, edgecolors='white')
        else:
            ax.scatter(x_data, y_data, c='#4ecdc4', s=50, alpha=0.7, edgecolors='white')
        
        ax.set_xlabel(x_label, color='white')
        ax.set_ylabel(y_label, color='white')
        ax.set_title(title, color='white', fontsize=16, pad=20)
        ax.grid(True, alpha=0.3)
        
        filename = f"scatter_{datetime.now().strftime('%H%M%S')}.png"
        return self._save_figure(fig, filename)

    # =========================
    # ARCHITECTURE DIAGRAMS
    # =========================

    def create_flowchart(
        self,
        nodes: List[Dict],
        edges: List[Tuple[int, int]],
        title: str = "System Architecture"
    ) -> str:
        """
        Create a flowchart/architecture diagram.
        nodes: [{"id": 0, "label": "API", "type": "service"}, ...]
        edges: [(0, 1), (1, 2), ...]
        """
        if not MATPLOTLIB_AVAILABLE:
            return "❌ matplotlib not available"

        fig, ax = self._create_figure(figsize=(12, 8))
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 10)
        ax.axis('off')
        ax.set_title(title, color='white', fontsize=18, pad=20)

        # Node colors by type
        type_colors = {
            'input': '#ff6b6b',
            'process': '#4ecdc4',
            'output': '#45b7d1',
            'database': '#f9c80e',
            'service': '#662e9b',
            'external': '#ea3546',
            'default': '#94a3b8'
        }

        # Simple layout - arrange in layers
        layers = {}
        for node in nodes:
            layer = node.get('layer', 0)
            if layer not in layers:
                layers[layer] = []
            layers[layer].append(node)

        positions = {}
        max_layer = max(layers.keys()) if layers else 0
        for layer, layer_nodes in layers.items():
            y = 8 - layer * 2.5
            x_start = 1
            x_spacing = 8 / (len(layer_nodes) + 1)
            for i, node in enumerate(layer_nodes):
                x = x_start + (i + 1) * x_spacing
                positions[node['id']] = (x, y)

        # Draw edges
        for src, dst in edges:
            if src in positions and dst in positions:
                x1, y1 = positions[src]
                x2, y2 = positions[dst]
                ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                           arrowprops=dict(arrowstyle='->', color='#94a3b8', lw=2))

        # Draw nodes
        for node in nodes:
            if node['id'] in positions:
                x, y = positions[node['id']]
                ntype = node.get('type', 'default')
                color = type_colors.get(ntype, type_colors['default'])
                
                rect = patches.FancyBboxPatch(
                    (x - 1.2, y - 0.5), 2.4, 1.0,
                    boxstyle="round,pad=0.1",
                    facecolor=color,
                    edgecolor='white',
                    linewidth=2
                )
                ax.add_patch(rect)
                ax.text(x, y, node['label'], ha='center', va='center',
                       color='white', fontsize=10, fontweight='bold')

        filename = f"flowchart_{datetime.now().strftime('%H%M%S')}.png"
        return self._save_figure(fig, filename)

    def create_network_topology(
        self,
        nodes: List[Dict],
        connections: List[Tuple[int, int, float]],
        title: str = "Network Topology"
    ) -> str:
        """Create network graph visualization."""
        if not MATPLOTLIB_AVAILABLE:
            return "❌ matplotlib not available"

        fig, ax = self._create_figure(figsize=(10, 10))
        ax.set_xlim(-1.5, 1.5)
        ax.set_ylim(-1.5, 1.5)
        ax.axis('off')
        ax.set_title(title, color='white', fontsize=18, pad=20)

        n = len(nodes)
        positions = {}
        for i, node in enumerate(nodes):
            angle = 2 * math.pi * i / n
            x = math.cos(angle)
            y = math.sin(angle)
            positions[node['id']] = (x, y)

        # Draw connections with width proportional to weight
        for src, dst, weight in connections:
            if src in positions and dst in positions:
                x1, y1 = positions[src]
                x2, y2 = positions[dst]
                ax.plot([x1, x2], [y1, y2], color='#94a3b8', 
                       alpha=0.5, linewidth=weight*2)

        # Draw nodes
        for node in nodes:
            if node['id'] in positions:
                x, y = positions[node['id']]
                circle = plt.Circle((x, y), 0.1, color='#4ecdc4', ec='white', lw=2, zorder=5)
                ax.add_patch(circle)
                ax.text(x, y, node['label'], ha='center', va='center',
                       color='white', fontsize=9, fontweight='bold', zorder=10)

        filename = f"network_{datetime.now().strftime('%H%M%S')}.png"
        return self._save_figure(fig, filename)

    # =========================
    # MASTER SIMULATION RUNNER
    # =========================

    def run_simulation(self, sim_type: str, **params) -> Dict[str, Any]:
        """Master function to run any simulation by type."""
        sim_type = sim_type.lower()
        
        if sim_type in ['pendulum', 'simple pendulum']:
            data = self.simulate_pendulum(**params)
            plot_path = self.plot_pendulum(data)
            return {"type": "pendulum", "data": data, "plot": plot_path}
        
        elif sim_type in ['projectile', 'projectile motion']:
            data = self.simulate_projectile(**params)
            plot_path = self.plot_projectile(data)
            return {"type": "projectile", "data": data, "plot": plot_path}
        
        elif sim_type in ['spring', 'spring mass', 'mass spring']:
            data = self.simulate_spring_mass(**params)
            plot_path = self.plot_spring_mass(data)
            return {"type": "spring", "data": data, "plot": plot_path}
        
        elif sim_type in ['wave', 'standing wave']:
            data = self.simulate_wave(**params)
            return {"type": "wave", "data": data}
        
        elif sim_type in ['bar chart', 'barchart']:
            plot_path = self.create_bar_chart(**params)
            return {"type": "bar_chart", "plot": plot_path}
        
        elif sim_type in ['pie chart', 'piechart']:
            plot_path = self.create_pie_chart(**params)
            return {"type": "pie_chart", "plot": plot_path}
        
        elif sim_type in ['line chart', 'linechart']:
            plot_path = self.create_line_chart(**params)
            return {"type": "line_chart", "plot": plot_path}
        
        elif sim_type in ['scatter', 'scatter plot']:
            plot_path = self.create_scatter_plot(**params)
            return {"type": "scatter", "plot": plot_path}
        
        elif sim_type in ['flowchart', 'architecture', 'system diagram']:
            plot_path = self.create_flowchart(**params)
            return {"type": "flowchart", "plot": plot_path}
        
        elif sim_type in ['network', 'network topology']:
            plot_path = self.create_network_topology(**params)
            return {"type": "network", "plot": plot_path}
        
        else:
            return {"error": f"Unknown simulation type: {sim_type}"}


# Global instance
_simulation = SimulationEngine()


@function_tool()
async def run_simulation(
    sim_type: str,
    length: float = 1.0,
    initial_angle: float = 0.785,
    gravity: float = 9.81,
    duration: float = 10.0,
    v0: float = 20.0,
    angle: float = 0.785,
    height: float = 0.0,
    mass: float = 1.0,
    spring_constant: float = 10.0,
    damping: float = 0.1,
    initial_displacement: float = 1.0,
    labels: List[str] = None,
    values: List[float] = None,
    title: str = "Chart",
    x_data: List[float] = None,
    y_data: List[List[float]] = None,
    line_labels: List[str] = None,
    nodes: List[Dict] = None,
    edges: List[List[int]] = None
) -> str:
    """
    Run a simulation or create a visualization.
    
    Simulation types:
    - pendulum: Simple pendulum (length, initial_angle, gravity, duration)
    - projectile: Projectile motion (v0, angle, gravity, height)
    - spring: Damped spring-mass (mass, spring_constant, damping, initial_displacement)
    - wave: Standing wave (length, wave_number, amplitude, frequency)
    - bar_chart: Bar chart (labels, values, title)
    - pie_chart: Pie chart (labels, values, title)
    - line_chart: Multi-line chart (x_data, y_data, labels, title)
    - scatter: Scatter plot (x_data, y_data, title)
    - flowchart: Architecture diagram (nodes, edges)
    - network: Network topology (nodes, connections)
    """
    params = {k: v for k, v in locals().items() 
              if k not in ['sim_type', 'params'] and v is not None}
    result = _simulation.run_simulation(sim_type, **params)
    
    if "error" in result:
        return f"❌ {result['error']}"
    
    output = f"✅ Simulation complete: {result['type']}\n"
    if "plot" in result:
        output += f"📊 Visualization saved: {result['plot']}\n"
    if "data" in result:
        data = result["data"]
        if "range" in data:
            output += f"📏 Range: {data['range']:.1f}m\n"
        if "max_height" in data:
            output += f"📐 Max Height: {data['max_height']:.1f}m\n"
        if "flight_time" in data:
            output += f"⏱️ Flight Time: {data['flight_time']:.1f}s\n"
        if "period" in data:
            output += f"🔄 Period: {data['period']:.2f}s\n"
    
    return output


@function_tool()
async def create_chart(
    chart_type: str,
    labels: List[str] = None,
    values: List[float] = None,
    title: str = "Chart",
    x_data: List[float] = None,
    y_data: List[List[float]] = None,
    line_labels: List[str] = None
) -> str:
    """Quick chart creation tool."""
    chart_type = chart_type.lower()
    
    if chart_type in ['bar', 'bar_chart']:
        return _simulation.create_bar_chart(labels, values, title)
    elif chart_type in ['pie', 'pie_chart']:
        return _simulation.create_pie_chart(labels, values, title)
    elif chart_type in ['line', 'line_chart']:
        return _simulation.create_line_chart(x_data, y_data, line_labels, title)
    elif chart_type in ['scatter']:
        return _simulation.create_scatter_plot(x_data or [], y_data or [], title)
    else:
        return f"❌ Unknown chart type: {chart_type}"


@function_tool()
async def create_diagram(
    diagram_type: str,
    nodes: List[Dict],
    edges: List[List[int]] = None,
    connections: List[List[float]] = None,
    title: str = "Diagram"
) -> str:
    """Create architecture/network diagrams."""
    diagram_type = diagram_type.lower()
    
    if diagram_type in ['flowchart', 'architecture', 'system']:
        return _simulation.create_flowchart(nodes, edges or [], title)
    elif diagram_type in ['network', 'topology']:
        return _simulation.create_network_topology(nodes, connections or [], title)
    else:
        return f"❌ Unknown diagram type: {diagram_type
}"


@function_tool()
async def list_simulation_types() -> str:
    """List all available simulation types."""
    return """🔬 Available Simulations:

Physics:
• pendulum - Simple pendulum motion
• projectile - Projectile trajectory
• spring - Damped spring-mass system
• wave - Standing wave simulation

Charts:
• bar_chart - Bar chart (labels, values)
• pie_chart - Pie chart (labels, values)
• line_chart - Multi-line chart (x_data, y_data, labels)
• scatter - Scatter plot (x_data, y_data)

Diagrams:
• flowchart - System architecture (nodes, edges)
• network - Network topology (nodes, connections)

Usage: "Run simulation of pendulum with length 2 meters"
       "Create bar chart of quarterly sales"
       "Draw flowchart of ZENITH architecture"
"""


def handle_simulation_engine(parameters: dict) -> str:
    """Module-level handler for the action loader — runs simulation synchronously."""
    import asyncio
    sim_type = parameters.get("simulation", "")
    if not sim_type:
        return "❌ 'simulation' parameter is required."
    try:
        # Build kwargs from parameters, excluding 'simulation'
        kwargs = {k: v for k, v in parameters.items() if k != "simulation" and v is not None}
        # Map TOOL parameter names to run_simulation's expected names
        if "velocity" in kwargs:
            kwargs.setdefault("v0", kwargs.pop("velocity"))
        result = _simulation.run_simulation(sim_type, **kwargs)
        if "error" in result:
            return f"❌ {result['error']}"
        output = f"✅ Simulation complete: {result['type']}\n"
        if "plot" in result:
            output += f"📊 Visualization saved: {result['plot']}\n"
        if "data" in result:
            data = result["data"]
            if "range" in data:
                output += f"📏 Range: {data['range']:.1f}m\n"
            if "max_height" in data:
                output += f"📐 Max Height: {data['max_height']:.1f}m\n"
            if "flight_time" in data:
                output += f"⏱️ Flight Time: {data['flight_time']:.1f}s\n"
            if "period" in data:
                output += f"🔄 Period: {data['period']:.2f}s\n"
        return output
    except Exception as e:
        return f"❌ Simulation engine error: {e}"