"""Reliable, local Windows application launcher for ZENITH."""
from __future__ import annotations

import asyncio
import os
import shutil
import subprocess
from pathlib import Path

from livekit.agents import function_tool

TOOL = {
    "name": "open_app",
    "description": "Launch an installed Windows app by name. Prefer this for app-opening commands.",
    "parameters": {"type": "OBJECT", "properties": {
        "app_name": {"type": "STRING", "description": "App name, e.g. chrome, spotify, notepad"}},
        "required": ["app_name"]},
    "handler": "open_app",
}

_ALIASES = {
    "chrome": "chrome.exe", "google chrome": "chrome.exe", "edge": "msedge.exe",
    "microsoft edge": "msedge.exe", "firefox": "firefox.exe", "spotify": "Spotify.exe",
    "notepad": "notepad.exe", "calculator": "calc.exe", "settings": "ms-settings:",
    "vscode": "Code.exe", "visual studio code": "Code.exe", "whatsapp": "WhatsApp.exe",
}


def _candidate_paths(executable: str) -> list[Path]:
    roots = [os.getenv("LOCALAPPDATA", ""), os.getenv("PROGRAMFILES", ""), os.getenv("PROGRAMFILES(X86)", "")]
    return [Path(root) / relative for root in roots if root for relative in (
        f"Google/Chrome/Application/{executable}", f"Microsoft/Edge/Application/{executable}",
        f"Microsoft/WindowsApps/{executable}", f"Programs/Microsoft VS Code/{executable}", executable)]


def _launch(app_name: str) -> str:
    query = app_name.strip()
    if not query:
        return "I need an application name."
    executable = _ALIASES.get(query.casefold(), query if query.lower().endswith(".exe") else f"{query}.exe")
    if executable.endswith(":"):
        os.startfile(executable)
        return f"Opened {query}."
    resolved = shutil.which(executable)
    if resolved:
        subprocess.Popen([resolved], close_fds=True)
        return f"Opened {query}."
    for path in _candidate_paths(executable):
        if path.is_file():
            subprocess.Popen([str(path)], close_fds=True)
            return f"Opened {query}."
    # Isolated fallback for Store apps that have no directly launchable executable.
    import pyautogui
    pyautogui.press("win")
    pyautogui.write(query, interval=0.03)
    pyautogui.press("enter")
    return f"Asked Windows to open {query}."


@function_tool()
async def open_app(app_name: str) -> str:
    try:
        return await asyncio.to_thread(_launch, app_name)
    except Exception as exc:
        return f"Could not open '{app_name}': {exc}"
