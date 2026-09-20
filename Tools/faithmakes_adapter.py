"""
Tools Adapter for ZENITH LiveKit Agent.
Provides @function_tool decorated wrappers for flight_finder, game_updater, background_monitor, and dev_agent.
"""

from livekit.agents import function_tool
from typing import Optional, Literal

TOOL = {
    "name": "faithmakes_adapter",
    "description": "Adapter for external tools: flight search, game updates, topic monitoring, and dev agent. Use when the user wants to search flights, manage game updates, monitor topics, or run autonomous coding tasks.",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "action": {"type": "STRING", "description": "Tool: 'find_flights', 'check_games', 'manage_monitor', 'run_dev_agent'"},
            "origin": {"type": "STRING", "description": "Departure city/airport for flight search"},
            "destination": {"type": "STRING", "description": "Arrival city/airport for flight search"},
            "date": {"type": "STRING", "description": "Departure date"},
            "instruction": {"type": "STRING", "description": "Instruction for dev agent"}
        },
        "required": ["action"]
    },
    "handler": "find_flights",
}

@function_tool()
async def find_flights(origin: str, destination: str, date: str, return_date: str = "", passengers: int = 1, cabin: str = "economy", save: bool = False) -> str:
    """
    Searches Google Flights for flight options, prices, and availability.

    Args:
        origin (str): Departure city or airport code (e.g. "DEL", "London")
        destination (str): Arrival city or airport code (e.g. "BOM", "New York")
        date (str): Departure date (e.g. "tomorrow", "2026-10-15")
        return_date (str): Optional return date for round trips
        passengers (int): Number of passengers
        cabin (str): Cabin class ("economy", "premium", "business", "first")
        save (bool): Whether to save search report to Desktop
    """
    try:
        from Tools.flight_finder import flight_finder
        res = flight_finder({
            "origin": origin,
            "destination": destination,
            "date": date,
            "return_date": return_date,
            "passengers": passengers,
            "cabin": cabin,
            "save": save
        })
        return str(res)
    except Exception as e:
        return f"Flight search failed: {e}"


@function_tool()
async def check_game_updates(action: str = "update", platform: str = "both", game_name: str = "", app_id: str = "") -> str:
    """
    Checks and manages Steam and Epic Games updates, installations, and downloads.

    Args:
        action (str): "update" | "install" | "list" | "download_status"
        platform (str): "steam" | "epic" | "both"
        game_name (str): Optional game name for filtering
        app_id (str): Optional Steam AppID
    """
    try:
        from Tools.game_updater import game_updater
        res = game_updater({
            "action": action,
            "platform": platform,
            "game_name": game_name,
            "app_id": app_id
        })
        return str(res)
    except Exception as e:
        return f"Game updater error: {e}"


@function_tool()
async def manage_topic_monitor(action: Literal["add", "remove", "list"], topic: str = "") -> str:
    """
    Add, remove, or list background monitoring topics. Checks daily for news developments.

    Args:
        action: "add" | "remove" | "list"
        topic: Topic string (e.g. "AI news", "space exploration")
    """
    try:
        from Tools.background_monitor import add_monitor, remove_monitor, list_monitors
        if action == "add":
            return add_monitor(topic)
        elif action == "remove":
            return remove_monitor(topic)
        else:
            return list_monitors()
    except Exception as e:
        return f"Topic monitor error: {e}"


@function_tool()
async def run_dev_agent(instruction: str, project_dir: str = "") -> str:
    """
    Autonomous software developer agent for complex coding tasks.

    Args:
        instruction (str): Coding goal or refactoring request
        project_dir (str): Optional target project directory
    """
    try:
        from Tools.dev_agent import run_dev_task
        res = run_dev_task(instruction, project_dir)
        return str(res)
    except Exception as e:
        return f"Dev agent error: {e
}"
