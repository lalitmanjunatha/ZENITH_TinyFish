"""
ZENITH Simulation Voice API
Natural language interface for all simulations. These are the function_tools
registered with the LiveKit agent.
"""

import math
import json
from typing import List, Dict, Optional
from pathlib import Path
from livekit.agents import function_tool

from .core import get_engine
from .physics import (
    PendulumSim, ProjectileSim, SpringMassSim, WaveSim,
    CollisionSim, DoublePendulumSim, register_physics_simulations,
)
from .mathematics import (
    FunctionGraph2D, DerivativeSim, IntegralSim, FractalSim,
    VectorSim, ProbabilitySim, register_math_simulations,
)
from .ai_ml import (
    NeuralNetworkSim, GradientDescentSim, KMeansSim, ClassificationSim,
    register_ai_ml_simulations,
)
from .electronics import (
    RCSim, FullWaveRectifierSim, DigitalLogicSim,
    register_electronics_simulations,
)
from .biology import (
    SIRSim, LotkaVolterraSim, PopulationGrowthSim, EnzymeKineticsSim,
    register_biology_simulations,
)
from .robotics import (
    PIDControllerSim, RobotArmSim, AStarSim, InvertedPendulumSim,
    register_robotics_simulations,
)
from .compsci import (
    SortingSim, CPUSchedulingSim, BinarySearchTreeSim, LinkedListSim,
    register_compsci_simulations,
)
from .visualization_3d import (
    SurfacePlot3DSim, ParametricCurve3DSim, VectorField3DSim,
    register_3d_simulations,
)
from .signal import (
    FourierTransformSim, ConvolutionSim, FilterDesignSim, SamplingTheoremSim,
    register_signal_simulations,
)

# Register all simulations on import
engine = get_engine()
register_physics_simulations(engine)
register_math_simulations(engine)
register_ai_ml_simulations(engine)
register_electronics_simulations(engine)
register_biology_simulations(engine)
register_robotics_simulations(engine)
register_compsci_simulations(engine)
register_3d_simulations(engine)
register_signal_simulations(engine)


# =========================================
# MASTER SIMULATION CONTROL
# =========================================

@function_tool()
async def sim_create(
    sim_type: str,
    param_string: str = "{}"
) -> str:
    """
    Create a new simulation. Use this for any simulation request.

    Supported sim_type values:
    PHYSICS: pendulum, projectile, spring_mass, wave, collision, double_pendulum
    MATH: function_graph_2d, derivative, integral, fractal, vectors, probability
    AI/ML: neural_network, gradient_descent, kmeans, classification
    ELECTRONICS: rc_circuit, full_wave_rectifier, digital_logic
    BIOLOGY: sir_model, predator_prey, population_growth, enzyme_kinetics
    ROBOTICS: pid_controller, robot_arm, astar, inverted_pendulum
    CS: sorting_algorithms, cpu_scheduling, binary_search_tree, linked_list
    3D: surface_3d, parametric_3d, vector_field_3d
    SIGNALS: fourier_transform, convolution, filter_design, sampling_theorem

    param_string: JSON string of parameters, e.g. '{"length": 2, "angle": 1.0}'
    """
    try:
        params = json.loads(param_string)
    except json.JSONDecodeError:
        params = {}

    result = engine.create(sim_type, params)
    return result


@function_tool()
async def sim_run(
    duration: float = 3.0,
    dt: float = 0.02
) -> str:
    """Run the current active simulation for a duration (seconds)."""
    return engine.run(duration, dt)


@function_tool()
async def sim_step(
    n_steps: int = 100
) -> str:
    """Advance the current simulation by N steps."""
    return engine.step(n_steps)


@function_tool()
async def sim_pause() -> str:
    """Pause the current simulation."""
    return engine.pause()


@function_tool()
async def sim_resume() -> str:
    """Resume the current simulation."""
    return engine.resume()


@function_tool()
async def sim_stop() -> str:
    """Stop the current simulation."""
    return engine.stop()


@function_tool()
async def sim_reset() -> str:
    """Reset the current simulation."""
    return engine.reset()


@function_tool()
async def sim_set_param(
    name: str,
    value: str
) -> str:
    """
    Change a parameter of the current simulation.
    value is passed as string - will be converted to number if possible.
    """
    try:
        v = float(value)
        if v == int(v):
            v = int(v)
    except ValueError:
        v = value
    return engine.set_param(name, v)


@function_tool()
async def sim_visualize() -> str:
    """Generate visualization (plot/image) of the current simulation."""
    return engine.visualize()


@function_tool()
async def sim_explain() -> str:
    """Explain what the current simulation is doing and its key metrics."""
    return engine.explain()


@function_tool()
async def sim_save(name: str = "") -> str:
    """Save the current simulation state and results."""
    return engine.save(name or None)


@function_tool()
async def sim_list() -> str:
    """List all available simulation types."""
    types = engine.get_available()
    categories = {
        "Physics": ["pendulum", "projectile", "spring_mass", "wave", "collision", "double_pendulum"],
        "Mathematics": ["function_graph_2d", "derivative", "integral", "fractal", "vectors", "probability"],
        "AI/ML": ["neural_network", "gradient_descent", "kmeans", "classification"],
        "Electronics": ["rc_circuit", "full_wave_rectifier", "digital_logic"],
        "Biology": ["sir_model", "predator_prey", "population_growth", "enzyme_kinetics"],
        "Robotics": ["pid_controller", "robot_arm", "astar", "inverted_pendulum"],
        "Computer Science": ["sorting_algorithms", "cpu_scheduling", "binary_search_tree", "linked_list"],
        "3D Visualization": ["surface_3d", "parametric_3d", "vector_field_3d"],
        "Signal Processing": ["fourier_transform", "convolution", "filter_design", "sampling_theorem"],
    }
    lines = ["Available simulations:"]
    for cat, sims in categories.items():
        available = [s for s in sims if s in types]
        if available:
            lines.append(f"  {cat}: {', '.join(available)}")
    return "\n".join(lines)


@function_tool()
async def sim_status() -> str:
    """Get the status of the current active simulation."""
    state = engine.get_state()
    if "status" in state and state["status"] == "no active simulation":
        return "No active simulation."
    lines = [
        f"Type: {state.get('type', '?')}",
        f"State: {state.get('state', '?')}",
        f"Time: {state.get('time', 0):.3f}s",
        f"Steps: {state.get('step_count', 0)}",
    ]
    metrics = state.get("metrics", {})
    if metrics:
        lines.append("Key metrics:")
        for k, v in list(metrics.items())[:10]:
            if isinstance(v, float):
                lines.append(f"  {k}: {v:.4f}")
            else:
                lines.append(f"  {k}: {v}")
    return "\n".join(lines)


@function_tool()
async def sim_run_n_times(n: int = 10, duration: float = 2.0) -> str:
    """Run the simulation N times and collect statistics."""
    return engine.run_n_times(n, duration)


@function_tool()
async def sim_get_state() -> str:
    """Get detailed simulation state as JSON."""
    state = engine.get_state()
    return json.dumps(state, indent=2, default=str)


# =========================================
# QUICK SIMULATION COMMANDS
# =========================================

@function_tool()
async def sim_pendulum(
    length: float = 2.0,
    angle_deg: float = 45.0,
    gravity: float = 9.81,
    damping: float = 0.0,
    run_seconds: float = 5.0
) -> str:
    """Quick pendulum simulation. angle_deg is in degrees."""
    angle_rad = math.radians(angle_deg)
    engine.create("pendulum", {
        "length": length, "angle": angle_rad,
        "gravity": gravity, "damping": damping,
    })
    engine.run(run_seconds)
    viz = engine.visualize()
    explain = engine.explain()
    return f"{explain}\nVisualization: {viz}"


@function_tool()
async def sim_projectile(
    velocity: float = 20.0,
    angle_deg: float = 45.0,
    gravity: float = 9.81,
    height: float = 0.0,
    air_resistance: float = 0.0,
    run_seconds: float = 5.0
) -> str:
    """Quick projectile motion simulation."""
    engine.create("projectile", {
        "v0": velocity, "angle": angle_deg,
        "gravity": gravity, "height": height,
        "air_resistance": air_resistance,
    })
    engine.run(run_seconds)
    viz = engine.visualize()
    state = engine.get_state()
    return f"Range: {state.get('metrics', {}).get('range', 0):.1f}m\nMax Height: {state.get('metrics', {}).get('max_height', 0):.1f}m\nVisualization: {viz}"


@function_tool()
async def sim_graph_function(
    expression: str = "sin(x)",
    x_min: float = -10,
    x_max: float = 10,
    second_function: str = ""
) -> str:
    """Graph a 2D function. Example: expression='x**2 - 4'"""
    params = {
        "expression": expression,
        "x_min": x_min, "x_max": x_max,
    }
    if second_function:
        params["second_function"] = second_function
    engine.create("function_graph_2d", params)
    viz = engine.visualize()
    return f"Graph of y = {expression}\nVisualization: {viz}"


@function_tool()
async def sim_show_derivative(
    expression: str = "x**2",
    point: float = 1.0
) -> str:
    """Visualize the derivative of a function at a point."""
    engine.create("derivative", {"expression": expression, "tangent_x": point})
    viz = engine.visualize()
    state = engine.get_state()
    deriv = state.get("metrics", {}).get("derivative_at_point", 0)
    return f"f(x) = {expression}\nf'({point}) = {deriv:.4f}\nVisualization: {viz}"


@function_tool()
async def sim_show_integral(
    expression: str = "sin(x)",
    a: float = 0,
    b: float = 3.14159
) -> str:
    """Visualize the integral (area under curve) of a function."""
    engine.create("integral", {"expression": expression, "a": a, "b": b})
    viz = engine.visualize()
    state = engine.get_state()
    area = state.get("metrics", {}).get("area", 0)
    return f"Integral of {expression} from {a:.2f} to {b:.2f}\nArea = {area:.4f}\nVisualization: {viz}"


@function_tool()
async def sim_fractal(
    fractal_type: str = "mandelbrot",
    resolution: int = 300
) -> str:
    """Generate a fractal (mandelbrot or julia)."""
    engine.create("fractal", {"fractal_type": fractal_type, "resolution": resolution})
    viz = engine.visualize()
    return f"{fractal_type.title()} fractal generated\nVisualization: {viz}"


@function_tool()
async def sim_neural_network(
    layers: str = "[2,4,3,1]",
    activation: str = "sigmoid",
    epochs: int = 50
) -> str:
    """Create and visualize a neural network. layers is JSON array like '[2,4,1]'."""
    try:
        layer_list = json.loads(layers)
    except:
        layer_list = [2, 4, 1]
    engine.create("neural_network", {"layers": layer_list, "activation": activation})
    viz = engine.visualize()
    state = engine.get_state()
    metrics = state.get("metrics", {})
    return f"Neural Network: {layer_list}\nWeights: {metrics.get('weights_count', 0)}\nVisualization: {viz}"


@function_tool()
async def sim_gradient_descent(
    function: str = "rosenbrock",
    learning_rate: float = 0.01,
    iterations: int = 200
) -> str:
    """Run gradient descent on a function and visualize the path."""
    engine.create("gradient_descent", {
        "function": function, "learning_rate": learning_rate,
        "start_x": -1.0, "start_y": 1.0,
    })
    engine.run(iterations * 0.02)
    viz = engine.visualize()
    state = engine.get_state()
    m = state.get("metrics", {})
    return f"Gradient Descent on {function}\nFinal loss: {m.get('final_loss', 0):.6f}\nIterations: {m.get('iterations', 0)}\nVisualization: {viz}"


@function_tool()
async def sim_kmeans(
    k: int = 3,
    n_points: int = 300,
    iterations: int = 20
) -> str:
    """Run K-Means clustering and visualize."""
    engine.create("kmeans", {"k": k, "n_points": n_points})
    sim = engine.active_simulation
    for _ in range(iterations):
        sim.run_iteration()
    viz = engine.visualize()
    state = engine.get_state()
    m = state.get("metrics", {})
    return f"K-Means (k={k}, {m.get('iteration', 0)} iterations)\nInertia: {m.get('inertia', 0):.1f}\nVisualization: {viz}"


@function_tool()
async def sim_rc_circuit(
    voltage: float = 5.0,
    resistance: float = 1000.0,
    capacitance: float = 0.001,
    mode: str = "charge",
    run_seconds: float = 5.0
) -> str:
    """Simulate an RC circuit charging or discharging."""
    engine.create("rc_circuit", {
        "voltage": voltage, "resistance": resistance,
        "capacitance": capacitance, "mode": mode,
    })
    engine.run(run_seconds)
    viz = engine.visualize()
    state = engine.get_state()
    m = state.get("metrics", {})
    return f"RC Circuit ({mode})\nTau = {m.get('tau', 0):.3f}s\nFinal V_cap = {m.get('v_capacitor', 0):.3f}V ({m.get('percent', 0):.1f}%)\nVisualization: {viz}"


@function_tool()
async def sim_rectifier(
    amplitude: float = 5.0,
    frequency: float = 50.0
) -> str:
    """Simulate a full-wave bridge rectifier."""
    engine.create("full_wave_rectifier", {"amplitude": amplitude, "frequency": frequency})
    engine.run(0.1)
    viz = engine.visualize()
    return f"Full-Wave Rectifier (Vpk={amplitude}V, f={frequency}Hz)\nVisualization: {viz}"


@function_tool()
async def sim_logic_gate(
    gate: str = "AND",
    input_a: str = "[0,0,1,1]",
    input_b: str = "[0,1,0,1]"
) -> str:
    """Simulate a digital logic gate. gate: AND, OR, XOR, NAND, NOR."""
    try:
        a = json.loads(input_a)
        b = json.loads(input_b)
    except:
        a, b = [0, 0, 1, 1], [0, 1, 0, 1]
    engine.create("digital_logic", {"gate": gate, "input_a": a, "input_b": b})
    viz = engine.visualize()
    state = engine.get_state()
    tt = state.get("metrics", {}).get("truth_table", {})
    return f"{gate.upper()} Gate\nOutput: {tt.get('Output', [])}\nVisualization: {viz}"


@function_tool()
async def sim_probability(
    distribution: str = "normal",
    n_samples: int = 10000
) -> str:
    """Show a probability distribution (normal, uniform, exponential, poisson)."""
    engine.create("probability", {"distribution": distribution, "n_samples": n_samples})
    viz = engine.visualize()
    state = engine.get_state()
    m = state.get("metrics", {})
    return f"{distribution.title()} Distribution (n={n_samples})\nMean={m.get('mean', 0):.4f}, Std={m.get('std', 0):.4f}\nVisualization: {viz}"


# =========================================
# BIOLOGY SIMULATIONS
# =========================================

@function_tool()
async def sim_sir_model(
    beta: float = 0.3,
    gamma: float = 0.1,
    population: int = 1000,
    infected: int = 10,
    run_seconds: float = 50.0
) -> str:
    """Simulate SIR disease spread model."""
    engine.create("sir_model", {
        "beta": beta, "gamma": gamma,
        "population": population, "infected": infected,
    })
    engine.run(run_seconds)
    viz = engine.visualize()
    state = engine.get_state()
    m = state.get("metrics", {})
    return (f"SIR Model: beta={beta}, gamma={gamma}\n"
            f"Peak infected: {m.get('peak_infected', 0):.0f}\n"
            f"Herd immunity: {m.get('herd_immunity_threshold', 0)*100:.1f}%\n"
            f"Visualization: {viz}")


@function_tool()
async def sim_predator_prey(
    prey_birth: float = 1.1,
    predation: float = 0.4,
    predator_death: float = 0.4,
    prey_init: int = 10,
    predator_init: int = 5,
    run_seconds: float = 30.0
) -> str:
    """Simulate Lotka-Volterra predator-prey dynamics."""
    engine.create("predator_prey", {
        "prey_birth": prey_birth, "predation": predation,
        "predator_death": predator_death,
        "prey_init": prey_init, "predator_init": predator_init,
    })
    engine.run(run_seconds)
    viz = engine.visualize()
    state = engine.get_state()
    m = state.get("metrics", {})
    return (f"Predator-Prey: Prey={m.get('prey', 0):.0f}, Predator={m.get('predator', 0):.0f}\n"
            f"Visualization: {viz}")


@function_tool()
async def sim_population_growth(
    growth_rate: float = 0.5,
    carrying_capacity: int = 1000,
    initial_pop: int = 10,
    model: str = "logistic",
    run_seconds: float = 50.0
) -> str:
    """Simulate population growth (exponential or logistic)."""
    engine.create("population_growth", {
        "growth_rate": growth_rate, "carrying_capacity": carrying_capacity,
        "initial_pop": initial_pop, "model": model,
    })
    engine.run(run_seconds)
    viz = engine.visualize()
    state = engine.get_state()
    m = state.get("metrics", {})
    return (f"Population Growth ({model})\n"
            f"Final population: {m.get('population', 0):.0f}\n"
            f"Carrying capacity: {carrying_capacity}\n"
            f"Visualization: {viz}")


@function_tool()
async def sim_enzyme_kinetics(
    Vmax: float = 10.0,
    Km: float = 2.0,
    substrate_range: float = 20.0
) -> str:
    """Simulate Michaelis-Menten enzyme kinetics."""
    engine.create("enzyme_kinetics", {
        "Vmax": Vmax, "Km": Km, "substrate_range": substrate_range,
    })
    engine.run(1.0)
    viz = engine.visualize()
    return (f"Enzyme Kinetics: Vmax={Vmax}, Km={Km}\n"
            f"Visualization: {viz}")


# =========================================
# ROBOTICS SIMULATIONS
# =========================================

@function_tool()
async def sim_pid_controller(
    Kp: float = 2.0,
    Ki: float = 0.5,
    Kd: float = 0.1,
    setpoint: float = 10.0,
    run_seconds: float = 10.0
) -> str:
    """Simulate a PID controller response."""
    engine.create("pid_controller", {
        "Kp": Kp, "Ki": Ki, "Kd": Kd, "setpoint": setpoint,
    })
    engine.run(run_seconds)
    viz = engine.visualize()
    state = engine.get_state()
    m = state.get("metrics", {})
    return (f"PID Controller: Kp={Kp}, Ki={Ki}, Kd={Kd}\n"
            f"Overshoot: {m.get('overshoot', 0):.1f}%\n"
            f"Visualization: {viz}")


@function_tool()
async def sim_robot_arm(
    lengths: str = "[2.0, 1.5, 1.0]",
    angles: str = "[0.5, 0.8, -0.3]"
) -> str:
    """Simulate a robot arm with forward kinematics."""
    try:
        l_list = json.loads(lengths)
        a_list = json.loads(angles)
    except:
        l_list = [2.0, 1.5, 1.0]
        a_list = [0.5, 0.8, -0.3]
    engine.create("robot_arm", {"lengths": l_list, "angles": a_list})
    engine.run(3.0)
    viz = engine.visualize()
    state = engine.get_state()
    m = state.get("metrics", {})
    return (f"Robot Arm: End effector at ({m.get('end_x', 0):.2f}, {m.get('end_y', 0):.2f})\n"
            f"Visualization: {viz}")


@function_tool()
async def sim_astar(
    grid_size: int = 20,
    obstacle_density: float = 0.25,
    start_x: int = 0, start_y: int = 0,
    goal_x: int = 19, goal_y: int = 19
) -> str:
    """Simulate A* pathfinding on a grid."""
    engine.create("astar", {
        "grid_size": grid_size, "obstacle_density": obstacle_density,
        "start": [start_x, start_y], "goal": [goal_x, goal_y],
    })
    engine.run(0.1)
    viz = engine.visualize()
    state = engine.get_state()
    m = state.get("metrics", {})
    return (f"A* Pathfinding: {m.get('path_length', 0)} steps, {m.get('explored_count', 0)} explored\n"
            f"Visualization: {viz}")


@function_tool()
async def sim_inverted_pendulum(
    Kp: float = 50.0,
    Ki: float = 0.1,
    Kd: float = 10.0,
    run_seconds: float = 10.0
) -> str:
    """Simulate inverted pendulum on cart with PID balance."""
    engine.create("inverted_pendulum", {
        "Kp": Kp, "Ki": Ki, "Kd": Kd,
    })
    engine.run(run_seconds)
    viz = engine.visualize()
    state = engine.get_state()
    m = state.get("metrics", {})
    return (f"Inverted Pendulum: angle={m.get('theta_deg', 0):.1f} deg\n"
            f"Cart position: {m.get('x', 0):.2f}\n"
            f"Visualization: {viz}")


# =========================================
# COMPUTER SCIENCE SIMULATIONS
# =========================================

@function_tool()
async def sim_sorting(
    algorithm: str = "quick",
    size: int = 30,
    max_value: int = 100
) -> str:
    """Visualize sorting algorithm step-by-step."""
    engine.create("sorting_algorithms", {
        "algorithm": algorithm, "size": size, "max_value": max_value,
    })
    engine.run(1.0)
    viz = engine.visualize()
    state = engine.get_state()
    m = state.get("metrics", {})
    return (f"{algorithm.title()} Sort: {size} elements\n"
            f"Comparisons: {m.get('comparisons', 0)}, Swaps: {m.get('swaps', 0)}\n"
            f"Visualization: {viz}")


@function_tool()
async def sim_cpu_scheduling(
    algorithm: str = "round_robin",
    time_quantum: int = 2,
    processes: str = ""
) -> str:
    """Simulate CPU scheduling algorithm."""
    params = {"algorithm": algorithm, "time_quantum": time_quantum}
    if processes:
        try:
            params["processes"] = json.loads(processes)
        except:
            pass
    engine.create("cpu_scheduling", params)
    engine.run(0.1)
    viz = engine.visualize()
    state = engine.get_state()
    m = state.get("metrics", {})
    return (f"CPU Scheduling: {algorithm}\n"
            f"Total time: {m.get('total_time', 0)}\n"
            f"Visualization: {viz}")


@function_tool()
async def sim_bst(
    values: str = "[50, 30, 70, 20, 40, 60, 80]"
) -> str:
    """Visualize a Binary Search Tree."""
    try:
        v_list = json.loads(values)
    except:
        v_list = [50, 30, 70, 20, 40, 60, 80]
    engine.create("binary_search_tree", {"values": v_list})
    engine.run(0.1)
    viz = engine.visualize()
    state = engine.get_state()
    m = state.get("metrics", {})
    return f"Binary Search Tree ({m.get('node_count', 0)} nodes)\nVisualization: {viz}"


@function_tool()
async def sim_linked_list(
    values: str = "[10, 20, 30, 40, 50]"
) -> str:
    """Visualize a linked list."""
    try:
        v_list = json.loads(values)
    except:
        v_list = [10, 20, 30, 40, 50]
    engine.create("linked_list", {"values": v_list})
    engine.run(0.1)
    viz = engine.visualize()
    state = engine.get_state()
    m = state.get("metrics", {})
    return f"Linked List ({m.get('length', 0)} nodes)\nVisualization: {viz}"


# =========================================
# 3D VISUALIZATION
# =========================================

@function_tool()
async def sim_surface_3d(
    function: str = "sin(sqrt(x**2 + y**2))",
    x_min: float = -5, x_max: float = 5,
    y_min: float = -5, y_max: float = 5,
    colormap: str = "cool"
) -> str:
    """Create a 3D surface plot of a function."""
    engine.create("surface_3d", {
        "function": function,
        "x_range": [x_min, x_max], "y_range": [y_min, y_max],
        "colormap": colormap,
    })
    engine.run(0.1)
    viz = engine.visualize()
    return f"3D Surface: {function}\nVisualization: {viz}"


@function_tool()
async def sim_parametric_3d(
    curve_type: str = "helix",
    t_max: float = 6.28
) -> str:
    """Create a 3D parametric curve."""
    engine.create("parametric_3d", {
        "curve_type": curve_type, "t_range": [0, t_max],
    })
    engine.run(0.1)
    viz = engine.visualize()
    return f"3D Parametric: {curve_type}\nVisualization: {viz}"


@function_tool()
async def sim_vector_field_3d(
    field_type: str = "vortex",
    grid_size: int = 10
) -> str:
    """Visualize a 3D vector field."""
    engine.create("vector_field_3d", {
        "field": field_type, "grid_size": grid_size,
    })
    engine.run(0.1)
    viz = engine.visualize()
    return f"3D Vector Field: {field_type}\nVisualization: {viz}"


# =========================================
# SIGNAL PROCESSING
# =========================================

@function_tool()
async def sim_fourier(
    frequencies: str = "[5, 15, 30]",
    amplitudes: str = "[1.0, 0.5, 0.3]",
    duration: float = 1.0,
    sample_rate: int = 500
) -> str:
    """Perform Fourier transform on a composite signal."""
    try:
        freq_list = json.loads(frequencies)
        amp_list = json.loads(amplitudes)
    except:
        freq_list = [5, 15, 30]
        amp_list = [1.0, 0.5, 0.3]
    engine.create("fourier_transform", {
        "frequencies": freq_list, "amplitudes": amp_list,
        "duration": duration, "sample_rate": sample_rate,
    })
    engine.run(0.1)
    viz = engine.visualize()
    state = engine.get_state()
    m = state.get("metrics", {})
    return (f"Fourier Transform: {len(freq_list)} frequency components\n"
            f"Frequencies: {freq_list} Hz\n"
            f"Visualization: {viz}")


@function_tool()
async def sim_convolution(
    signal: str = "[0,0,1,1,1,0,0,0,2,2,0,0]",
    kernel: str = "[1,2,1]"
) -> str:
    """Perform convolution on a signal."""
    try:
        sig = json.loads(signal)
        ker = json.loads(kernel)
    except:
        sig = [0, 0, 1, 1, 1, 0, 0, 0, 2, 2, 0, 0]
        ker = [1, 2, 1]
    engine.create("convolution", {"signal": sig, "kernel": ker})
    engine.run(0.1)
    viz = engine.visualize()
    return f"Convolution: signal({len(sig)}) * kernel({len(ker)})\nVisualization: {viz}"


@function_tool()
async def sim_filter_design(
    filter_type: str = "low_pass",
    cutoff: float = 50.0,
    sample_rate: int = 500,
    order: int = 5
) -> str:
    """Design and visualize a digital filter."""
    engine.create("filter_design", {
        "filter_type": filter_type, "cutoff": cutoff,
        "sample_rate": sample_rate, "order": order,
    })
    engine.run(0.1)
    viz = engine.visualize()
    return f"{filter_type.replace('_', ' ').title()} Filter (cutoff={cutoff}Hz, order={order})\nVisualization: {viz}"


@function_tool()
async def sim_sampling(
    signal_freq: float = 10.0,
    sampling_rate: float = 30.0,
    duration: float = 1.0
) -> str:
    """Demonstrate Nyquist sampling theorem."""
    engine.create("sampling_theorem", {
        "original_freq": signal_freq, "sampling_rate": sampling_rate,
        "duration": duration,
    })
    engine.run(0.1)
    viz = engine.visualize()
    state = engine.get_state()
    m = state.get("metrics", {})
    aliasing = "YES (Aliasing!)" if m.get("undersampled") else "NO"
    return (f"Sampling Theorem: Signal={signal_freq}Hz, Sample Rate={sampling_rate}Hz\n"
            f"Nyquist Rate: {m.get('nyquist_rate', 0)}Hz\n"
            f"Aliasing: {aliasing}\n"
            f"Visualization: {viz}")
