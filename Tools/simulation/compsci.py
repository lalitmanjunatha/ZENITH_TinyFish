"""
ZENITH Computer Science Simulation Module
Implements: Sorting Visualizer, Graph Algorithms, Data Structures, CPU Scheduling, Memory Allocation
"""

import math
import heapq
import random
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

try:
    import numpy as _np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False


class SortingSim(BaseSimulation):
    SIM_TYPE = "sorting_algorithms"
    SIM_NAME = "Sorting Algorithm Visualizer"

    def __init__(self, params=None):
        defaults = {
            "algorithm": "quick",
            "size": 30,
            "max_value": 100,
            "delay": 0.02,
        }
        p = {**defaults, **(params or {})}
        super().__init__(p)

    def initialize(self):
        super().initialize()
        n = self.params["size"]
        self.array = [random.randint(1, self.params["max_value"]) for _ in range(n)]
        self.original = list(self.array)
        self.comparisons = 0
        self.swaps = 0
        self.sorted_indices = set()
        self._sort_steps = []
        self._generate_steps()
        self.step_index = 0
        self.metrics = {"comparisons": 0, "swaps": 0, "total_steps": len(self._sort_steps)}

    def _generate_steps(self):
        arr = list(self.array)
        algo = self.params["algorithm"]
        if algo == "bubble":
            self._bubble_sort(arr)
        elif algo == "selection":
            self._selection_sort(arr)
        elif algo == "insertion":
            self._insertion_sort(arr)
        elif algo == "merge":
            self._merge_sort(arr, 0, len(arr) - 1)
        elif algo == "quick":
            self._quick_sort(arr, 0, len(arr) - 1)
        elif algo == "heap":
            self._heap_sort(arr)

    def _bubble_sort(self, arr):
        n = len(arr)
        for i in range(n):
            for j in range(0, n - i - 1):
                self._sort_steps.append({"action": "compare", "indices": [j, j + 1], "array": list(arr)})
                if arr[j] > arr[j + 1]:
                    arr[j], arr[j + 1] = arr[j + 1], arr[j]
                    self._sort_steps.append({"action": "swap", "indices": [j, j + 1], "array": list(arr)})

    def _selection_sort(self, arr):
        n = len(arr)
        for i in range(n):
            min_idx = i
            for j in range(i + 1, n):
                self._sort_steps.append({"action": "compare", "indices": [min_idx, j], "array": list(arr)})
                if arr[j] < arr[min_idx]:
                    min_idx = j
            if min_idx != i:
                arr[i], arr[min_idx] = arr[min_idx], arr[i]
                self._sort_steps.append({"action": "swap", "indices": [i, min_idx], "array": list(arr)})

    def _insertion_sort(self, arr):
        for i in range(1, len(arr)):
            key = arr[i]
            j = i - 1
            while j >= 0 and arr[j] > key:
                self._sort_steps.append({"action": "compare", "indices": [j, j + 1], "array": list(arr)})
                arr[j + 1] = arr[j]
                self._sort_steps.append({"action": "swap", "indices": [j, j + 1], "array": list(arr)})
                j -= 1
            arr[j + 1] = key

    def _merge_sort(self, arr, l, r):
        if l < r:
            m = (l + r) // 2
            self._merge_sort(arr, l, m)
            self._merge_sort(arr, m + 1, r)
            self._merge(arr, l, m, r)

    def _merge(self, arr, l, m, r):
        left = arr[l:m + 1]
        right = arr[m + 1:r + 1]
        i = j = 0; k = l
        while i < len(left) and j < len(right):
            self._sort_steps.append({"action": "compare", "indices": [l + i, m + 1 + j], "array": list(arr)})
            if left[i] <= right[j]:
                arr[k] = left[i]; i += 1
            else:
                arr[k] = right[j]; j += 1
            self._sort_steps.append({"action": "place", "indices": [k], "array": list(arr)})
            k += 1
        while i < len(left):
            arr[k] = left[i]; i += 1; k += 1
        while j < len(right):
            arr[k] = right[j]; j += 1; k += 1

    def _quick_sort(self, arr, low, high):
        if low < high:
            pi = self._partition(arr, low, high)
            self._quick_sort(arr, low, pi - 1)
            self._quick_sort(arr, pi + 1, high)

    def _partition(self, arr, low, high):
        pivot = arr[high]
        i = low - 1
        for j in range(low, high):
            self._sort_steps.append({"action": "compare", "indices": [j, high], "array": list(arr)})
            if arr[j] < pivot:
                i += 1
                arr[i], arr[j] = arr[j], arr[i]
                self._sort_steps.append({"action": "swap", "indices": [i, j], "array": list(arr)})
        arr[i + 1], arr[high] = arr[high], arr[i + 1]
        self._sort_steps.append({"action": "swap", "indices": [i + 1, high], "array": list(arr)})
        return i + 1

    def _heap_sort(self, arr):
        n = len(arr)
        for i in range(n // 2 - 1, -1, -1):
            self._heapify(arr, n, i)
        for i in range(n - 1, 0, -1):
            arr[0], arr[i] = arr[i], arr[0]
            self._sort_steps.append({"action": "swap", "indices": [0, i], "array": list(arr)})
            self._heapify(arr, i, 0)

    def _heapify(self, arr, n, i):
        largest = i; l = 2 * i + 1; r = 2 * i + 2
        if l < n:
            self._sort_steps.append({"action": "compare", "indices": [l, largest], "array": list(arr)})
            if arr[l] > arr[largest]: largest = l
        if r < n:
            self._sort_steps.append({"action": "compare", "indices": [r, largest], "array": list(arr)})
            if arr[r] > arr[largest]: largest = r
        if largest != i:
            arr[i], arr[largest] = arr[largest], arr[i]
            self._sort_steps.append({"action": "swap", "indices": [i, largest], "array": list(arr)})
            self._heapify(arr, n, largest)

    def step(self, dt=0.02):
        if self.step_index < len(self._sort_steps):
            step = self._sort_steps[self.step_index]
            self.array = step["array"]
            self.comparisons += 1 if step["action"] == "compare" else 0
            self.swaps += 1 if step["action"] in ("swap", "place") else 0
            self.step_index += 1
        super().step(dt)
        self.metrics["comparisons"] = self.comparisons
        self.metrics["swaps"] = self.swaps
        self.metrics["progress"] = self.step_index / max(1, len(self._sort_steps))

    def visualize(self, output_dir=None):
        if not HAS_MPL:
            return "matplotlib not available"
        output_dir = output_dir or get_engine().output_dir
        fig, axes = plt.subplots(2, 1, figsize=(12, 8))
        fig.patch.set_facecolor('#0a0a0f')
        vis = VisHelper()

        ax = axes[0]; ax.set_facecolor('#0a0a0f')
        colors = [vis.COLORS["cyan"]] * len(self.array)
        if self.step_index < len(self._sort_steps):
            step = self._sort_steps[self.step_index]
            for idx in step["indices"]:
                if idx < len(colors):
                    colors[idx] = vis.COLORS["red"]
        ax.bar(range(len(self.array)), self.array, color=colors, width=0.8)
        ax.set_title(f"{self.params['algorithm'].title()} Sort - Step {self.step_index}/{len(self._sort_steps)}", color='white', fontsize=13)
        vis.label_axes(ax, "Index", "Value")
        vis.add_grid(ax)

        # Progress
        ax = axes[1]; ax.set_facecolor('#0a0a0f')
        progress = self.step_index / max(1, len(self._sort_steps)) * 100
        ax.barh([0], [progress], color=vis.COLORS["green"], height=0.5)
        ax.barh([0], [100 - progress], left=[progress], color='#1e293b', height=0.5)
        ax.set_xlim(0, 100); ax.set_ylim(-0.5, 0.5)
        ax.set_title(f"Progress: {progress:.0f}% | Comparisons: {self.comparisons} | Swaps: {self.swaps}", color='white', fontsize=11)
        ax.set_yticks([]); vis.add_grid(ax)

        plt.tight_layout()
        return VisHelper.save_figure(fig, f"sort_{self.params['algorithm']}_{int(self.time*1000)}.png", output_dir)


class CPUSchedulingSim(BaseSimulation):
    SIM_TYPE = "cpu_scheduling"
    SIM_NAME = "CPU Scheduling Algorithms"

    def __init__(self, params=None):
        defaults = {
            "algorithm": "round_robin",
            "time_quantum": 2,
            "processes": [
                {"name": "P1", "arrival": 0, "burst": 5},
                {"name": "P2", "arrival": 1, "burst": 3},
                {"name": "P3", "arrival": 2, "burst": 8},
                {"name": "P4", "arrival": 3, "burst": 2},
                {"name": "P5", "arrival": 4, "burst": 4},
            ],
        }
        p = {**defaults, **(params or {})}
        super().__init__(p)

    def initialize(self):
        super().initialize()
        self.processes = [dict(p) for p in self.params["processes"]]
        self.gantt = []
        self.schedule()
        self.metrics = {"total_time": len(self.gantt)}

    def schedule(self):
        algo = self.params["algorithm"]
        procs = [dict(p) for p in self.processes]
        remaining = {p["name"]: p["burst"] for p in procs}
        arrived = []
        time = 0
        gantt = []
        done = set()

        if algo == "fcfs":
            procs.sort(key=lambda x: x["arrival"])
            for p in procs:
                if time < p["arrival"]:
                    time = p["arrival"]
                for _ in range(p["burst"]):
                    gantt.append({"time": time, "process": p["name"]})
                    time += 1
                done.add(p["name"])

        elif algo == "sjf":
            pq = []
            idx = 0
            procs.sort(key=lambda x: x["arrival"])
            while len(done) < len(procs):
                while idx < len(procs) and procs[idx]["arrival"] <= time:
                    heapq.heappush(pq, (procs[idx]["burst"], procs[idx]["name"]))
                    idx += 1
                if pq:
                    burst, name = heapq.heappop(pq)
                    for _ in range(burst):
                        gantt.append({"time": time, "process": name})
                        time += 1
                    done.add(name)
                else:
                    gantt.append({"time": time, "process": "idle"})
                    time += 1

        elif algo == "round_robin":
            tq = self.params["time_quantum"]
            queue = []
            idx = 0
            procs.sort(key=lambda x: x["arrival"])
            time = procs[0]["arrival"] if procs else 0
            while idx < len(procs) and procs[idx]["arrival"] <= time:
                queue.append(procs[idx]); idx += 1
            while queue or idx < len(procs):
                if not queue:
                    time = procs[idx]["arrival"]
                    while idx < len(procs) and procs[idx]["arrival"] <= time:
                        queue.append(procs[idx]); idx += 1
                p = queue.pop(0)
                exec_t = min(tq, remaining[p["name"]])
                for _ in range(exec_t):
                    gantt.append({"time": time, "process": p["name"]})
                    time += 1
                remaining[p["name"]] -= exec_t
                while idx < len(procs) and procs[idx]["arrival"] <= time:
                    queue.append(procs[idx]); idx += 1
                if remaining[p["name"]] > 0:
                    queue.append(p)
                else:
                    done.add(p["name"])

        elif algo == "priority":
            pq = []
            idx = 0
            procs.sort(key=lambda x: x["arrival"])
            priorities = {p["name"]: p.get("priority", 5) for p in procs}
            while len(done) < len(procs):
                while idx < len(procs) and procs[idx]["arrival"] <= time:
                    heapq.heappush(pq, (priorities[procs[idx]["name"]], procs[idx]["name"], procs[idx]["burst"]))
                    idx += 1
                if pq:
                    pri, name, burst = heapq.heappop(pq)
                    for _ in range(burst):
                        gantt.append({"time": time, "process": name})
                        time += 1
                    done.add(name)
                else:
                    gantt.append({"time": time, "process": "idle"})
                    time += 1

        self.gantt = gantt

    def step(self, dt=0.02):
        super().step(dt)

    def visualize(self, output_dir=None):
        if not HAS_MPL:
            return "matplotlib not available"
        output_dir = output_dir or get_engine().output_dir
        fig, ax = plt.subplots(figsize=(14, 4))
        fig.patch.set_facecolor('#0a0a0f')
        vis = VisHelper()
        ax.set_facecolor('#0a0a0f')

        colors = [vis.COLORS["cyan"], vis.COLORS["orange"], vis.COLORS["green"],
                  vis.COLORS["purple"], vis.COLORS["yellow"], vis.COLORS["red"]]
        proc_names = list(set(d["process"] for d in self.gantt if d["process"] != "idle"))
        color_map = {name: colors[i % len(colors)] for i, name in enumerate(proc_names)}

        for entry in self.gantt:
            if entry["process"] == "idle":
                color = '#1e293b'
            else:
                color = color_map.get(entry["process"], vis.COLORS["cyan"])
            ax.barh(0, 1, left=entry["time"], color=color, height=0.5, edgecolor='#0a0a0f')
            ax.text(entry["time"] + 0.5, 0, entry["process"], ha='center', va='center',
                    color='white', fontsize=7, fontweight='bold')

        ax.set_xlim(-0.5, len(self.gantt) + 0.5)
        ax.set_ylim(-0.5, 0.5)
        ax.set_yticks([])
        ax.set_title(f"CPU Scheduling: {self.params['algorithm'].replace('_', ' ').title()} | Total Time: {len(self.gantt)}", color='white', fontsize=13)
        vis.label_axes(ax, "Time", "")
        vis.add_grid(ax)

        legend_elements = [patches.Patch(facecolor=color_map[n], label=n) for n in proc_names]
        ax.legend(handles=legend_elements, fontsize=9, facecolor='#111827', edgecolor='#334155', labelcolor='white')
        plt.tight_layout()
        return VisHelper.save_figure(fig, f"cpu_{self.params['algorithm']}_{int(self.time*1000)}.png", output_dir)


class BinarySearchTreeSim(BaseSimulation):
    SIM_TYPE = "binary_search_tree"
    SIM_NAME = "Binary Search Tree"

    def __init__(self, params=None):
        defaults = {
            "values": [50, 30, 70, 20, 40, 60, 80, 10, 25, 35, 45],
        }
        p = {**defaults, **(params or {})}
        super().__init__(p)

    def initialize(self):
        super().initialize()
        self.root = None
        self.nodes = []
        for v in self.params["values"]:
            self.insert(v)
        self.metrics = {"node_count": len(self.nodes)}

    def insert(self, val):
        self.root = self._insert(self.root, val, 0, 0)

    def _insert(self, node, val, x, depth):
        if node is None:
            n = {"val": val, "x": x, "y": -depth, "left": None, "right": None}
            self.nodes.append(n)
            return n
        if val < node["val"]:
            node["left"] = self._insert(node["left"], val, x - 1 / (2 ** (depth + 1)), depth + 1)
        elif val > node["val"]:
            node["right"] = self._insert(node["right"], val, x + 1 / (2 ** (depth + 1)), depth + 1)
        return node

    def step(self, dt=0.02):
        super().step(dt)

    def visualize(self, output_dir=None):
        if not HAS_MPL:
            return "matplotlib not available"
        output_dir = output_dir or get_engine().output_dir
        fig, ax = plt.subplots(figsize=(12, 8))
        fig.patch.set_facecolor('#0a0a0f')
        vis = VisHelper()
        ax.set_facecolor('#0a0a0f')
        ax.set_xlim(-1.5, 1.5)
        ax.set_ylim(-5, 1)
        ax.set_aspect('equal')

        def draw_node(n):
            if n is None:
                return
            circle = plt.Circle((n["x"], n["y"], ), 0.08, color=vis.COLORS["cyan"], fill=True, zorder=5)
            ax.add_patch(circle)
            ax.text(n["x"], n["y"], str(n["val"]), ha='center', va='center',
                    color='white', fontsize=8, fontweight='bold', zorder=6)
            if n["left"]:
                ax.plot([n["x"], n["left"]["x"]], [n["y"], n["left"]["y"]],
                        color=vis.COLORS["purple"], linewidth=1.5, zorder=2)
                draw_node(n["left"])
            if n["right"]:
                ax.plot([n["x"], n["right"]["x"]], [n["y"], n["right"]["y"]],
                        color=vis.COLORS["purple"], linewidth=1.5, zorder=2)
                draw_node(n["right"])

        draw_node(self.root)
        ax.set_title(f"Binary Search Tree ({len(self.nodes)} nodes)", color='white', fontsize=13)
        plt.tight_layout()
        return VisHelper.save_figure(fig, f"bst_{int(self.time*1000)}.png", output_dir)


class LinkedListSim(BaseSimulation):
    SIM_TYPE = "linked_list"
    SIM_NAME = "Linked List Visualizer"

    def __init__(self, params=None):
        defaults = {"values": [10, 20, 30, 40, 50]}
        p = {**defaults, **(params or {})}
        super().__init__(p)

    def initialize(self):
        super().initialize()
        self.values = list(self.params["values"])
        self.metrics = {"length": len(self.values)}

    def step(self, dt=0.02):
        super().step(dt)

    def visualize(self, output_dir=None):
        if not HAS_MPL:
            return "matplotlib not available"
        output_dir = output_dir or get_engine().output_dir
        fig, ax = plt.subplots(figsize=(14, 3))
        fig.patch.set_facecolor('#0a0a0f')
        vis = VisHelper()
        ax.set_facecolor('#0a0a0f')
        ax.set_xlim(-1, len(self.values) * 2 + 1)
        ax.set_ylim(-1, 2)

        for i, val in enumerate(self.values):
            x = i * 2
            rect = patches.FancyBboxPatch((x - 0.4, 0.2), 0.8, 0.6, boxstyle="round,pad=0.05",
                                           facecolor=vis.COLORS["cyan"], edgecolor='white', linewidth=2, zorder=5)
            ax.add_patch(rect)
            ax.text(x, 0.5, str(val), ha='center', va='center', color='white', fontsize=12, fontweight='bold', zorder=6)
            if i < len(self.values) - 1:
                ax.annotate('', xy=(x + 1, 0.5), xytext=(x + 0.5, 0.5),
                            arrowprops=dict(arrowstyle='->', color=vis.COLORS["orange"], lw=2))
            ax.text(x, 1.3, f"Node {i}", ha='center', va='center', color=vis.COLORS["purple"], fontsize=8)

        ax.text(-0.5, -0.5, "HEAD", color=vis.COLORS["green"], fontsize=9, fontweight='bold')
        ax.text(len(self.values) * 2 - 1, -0.5, "NULL", color=vis.COLORS["red"], fontsize=9, fontweight='bold')

        ax.set_title(f"Linked List ({len(self.values)} nodes)", color='white', fontsize=13)
        ax.set_yticks([]); ax.set_xticks([])
        plt.tight_layout()
        return VisHelper.save_figure(fig, f"linked_list_{int(self.time*1000)}.png", output_dir)


def register_compsci_simulations(engine=None):
    engine = engine or get_engine()
    engine.register_simulation("sorting_algorithms", SortingSim)
    engine.register_simulation("cpu_scheduling", CPUSchedulingSim)
    engine.register_simulation("binary_search_tree", BinarySearchTreeSim)
    engine.register_simulation("linked_list", LinkedListSim)
