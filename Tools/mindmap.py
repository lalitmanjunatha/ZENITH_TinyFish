"""
ZENITH Mind Map Creator Tool
Provides: create_mindmap
"""

import os
import math
from typing import Optional, List
from livekit.agents import function_tool

TOOL = {
    "name": "mindmap",
    "description": "Create visual mind maps from a central topic and branches. Use when the user wants to visualize ideas, concepts, or brainstorm topics in a mind map format.",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "central_topic": {"type": "STRING", "description": "The main central topic for the mind map"},
            "branches": {"type": "STRING", "description": "Comma-separated topics, can use 'topic:sub1,sub2' format for sub-branches"}
        },
        "required": ["central_topic", "branches"]
    },
    "handler": "create_mindmap",
}


@function_tool()
async def create_mindmap(central_topic: str, branches: str) -> str:
    """Create a visual mind map. branches: comma-separated topics, can use 'topic:sub1,sub2' format."""
    try:
        import matplotlib.pyplot as plt
        import matplotlib.patches as patches
    except ImportError:
        return "matplotlib not installed."

    try:
        output_path = os.path.join(os.path.dirname(__file__), '..', 'zenith_mindmap.png')
        branch_list = [b.strip() for b in branches.split(',')]

        fig, ax = plt.subplots(figsize=(14, 10))
        fig.patch.set_facecolor('#0a0a0f')
        ax.set_facecolor('#0a0a0f')
        ax.set_xlim(-10, 10)
        ax.set_ylim(-8, 8)
        ax.set_aspect('equal')
        ax.axis('off')

        colors = ['#00d4ff', '#ff6b35', '#10b981', '#8b5cf6', '#f59e0b', '#ef4444', '#06b6d4', '#ec4899']

        # Central topic
        central_box = patches.FancyBboxPatch((-2, -0.7), 4, 1.4, boxstyle="round,pad=0.2",
                                              facecolor='#1e293b', edgecolor='#00d4ff', linewidth=3, zorder=10)
        ax.add_patch(central_box)
        ax.text(0, 0, central_topic, ha='center', va='center', color='white', fontsize=14, fontweight='bold', zorder=11)

        num_branches = len(branch_list)
        for i, branch in enumerate(branch_list):
            angle = (2 * math.pi * i / num_branches) - math.pi / 2
            color = colors[i % len(colors)]

            bx = 4 * math.cos(angle)
            by = 4 * math.sin(angle)

            ax.plot([0, bx], [0, by], color=color, linewidth=2.5, zorder=5)

            box_w = max(2.5, len(branch) * 0.18)
            branch_box = patches.FancyBboxPatch((bx - box_w / 2, by - 0.4), box_w, 0.8,
                                                boxstyle="round,pad=0.15",
                                                facecolor=color, edgecolor='white', linewidth=1.5, alpha=0.85, zorder=8)
            ax.add_patch(branch_box)
            ax.text(bx, by, branch, ha='center', va='center', color='white', fontsize=11, fontweight='bold', zorder=9)

        ax.set_title(f"Mind Map: {central_topic}", color='white', fontsize=16, pad=20)
        plt.tight_layout()
        plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='#0a0a0f')
        plt.close(fig)

        return f"Mind map created for '{central_topic}' with {num_branches} branches -> {output_path}"
    except Exception as e:
        return f"Error: {str(e)
}"
