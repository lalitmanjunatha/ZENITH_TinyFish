from __future__ import annotations
import json
import asyncio
import inspect
from pathlib import Path
from livekit.agents import function_tool

TOOL = {
    "name": "multi_task",
    "description": "Execute multiple tool operations sequentially in a single request. Use when the user wants to perform several tasks at once without waiting for each to complete individually.",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "tasks": {
                "type": "ARRAY",
                "description": "List of task dictionaries (or JSON string), each with 'tool_name' and 'params' keys",
                "items": {"type": "OBJECT"}
            }
        },
        "required": ["tasks"]
    },
    "handler": "execute_multi_task",
}

@function_tool()
async def execute_multi_task(tasks: list[dict] | str) -> str:
    """
    Executes multiple registered tools sequentially as per user request.

    Args:
        tasks: A list of dictionaries or JSON string, each containing:
            - 'tool_name': Name of the tool (string)
            - 'params': Dictionary of parameters for that tool
    """
    if isinstance(tasks, str):
        try:
            tasks = json.loads(tasks)
        except Exception as e:
            return f"❌ Failed to parse tasks JSON: {e}"

    if not isinstance(tasks, list):
        return "❌ 'tasks' must be a list of task dictionaries."

    from core.action_loader import discover_actions
    registry = discover_actions(Path(__file__).resolve().parent, logger=lambda msg: None)

    results = []

    for idx, task in enumerate(tasks, start=1):
        if not isinstance(task, dict):
            results.append(f"⚠️ Task {idx}: Invalid format (expected dictionary).")
            continue

        tool_name = task.get("tool_name") or task.get("name") or task.get("tool")
        params = task.get("params") or task.get("parameters") or {}

        if not tool_name:
            results.append(f"⚠️ Task {idx}: 'tool_name' missing.")
            continue

        if not registry.has(tool_name):
            results.append(f"⚠️ Task {idx}: Tool '{tool_name}' not found in action registry.")
            continue

        try:
            # Execute tool through action registry
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, lambda tn=tool_name, tp=params: registry.run(tn, tp))
            results.append(f"✅ Task {idx} ({tool_name}): {result}")
        except Exception as e:
            results.append(f"❌ Task {idx} ({tool_name}) failed: {str(e)}")

    return "🔹 Multi-Task Execution Complete:\n" + "\n".join(results)

