"""
ZENITH Terminal Execution Tool
Provides: run_command, run_python, list_processes, kill_process
"""

import subprocess
import sys
import os
import psutil
import asyncio
from typing import Optional
from livekit.agents import function_tool

TOOL = {
    "name": "terminal_exec",
    "description": "Execute shell commands and Python code, list processes, and kill processes. Use when the user wants to run terminal commands or manage running processes.",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "action": {"type": "STRING", "description": "Action: 'run_command', 'run_python', 'list_processes', 'kill_process'"},
            "command": {"type": "STRING", "description": "Shell command to execute"},
            "code": {"type": "STRING", "description": "Python code to execute"},
            "pid": {"type": "INTEGER", "description": "Process ID to kill"},
            "name": {"type": "STRING", "description": "Process name to kill"},
            "sort_by": {"type": "STRING", "description": "Sort processes by: 'cpu' or 'memory'"},
            "timeout": {"type": "INTEGER", "description": "Command timeout in seconds (default: 30)"}
        },
        "required": ["action"]
    },
    "handler": "run_command",
}


@function_tool()
async def run_command(command: str, timeout: int = 30) -> str:
    """Execute a shell command and return output."""
    try:
        result = await asyncio.to_thread(
            subprocess.run,
            command, shell=True, capture_output=True, text=True, timeout=timeout
        )
        output = result.stdout
        if result.stderr:
            output += f"\n[STDERR]\n{result.stderr}"
        if not output.strip():
            output = "(no output)"
        return f"Command: {command}\nExit Code: {result.returncode}\nOutput:\n{output}"
    except subprocess.TimeoutExpired:
        return f"Command timed out after {timeout}s: {command}"
    except Exception as e:
        return f"Error: {str(e)}"


@function_tool()
async def run_python(code: str) -> str:
    """Execute Python code and return output."""
    try:
        result = await asyncio.to_thread(
            subprocess.run,
            [sys.executable, "-c", code],
            capture_output=True, text=True, timeout=30
        )
        output = result.stdout
        if result.stderr:
            output += f"\n[STDERR]\n{result.stderr}"
        if not output.strip():
            output = "(no output)"
        return f"Exit Code: {result.returncode}\nOutput:\n{output}"
    except subprocess.TimeoutExpired:
        return "Python code execution timed out (30s limit)"
    except Exception as e:
        return f"Error: {str(e)}"


@function_tool()
async def list_processes(sort_by: str = "cpu") -> str:
    """List running processes sorted by cpu or memory usage."""
    procs = []
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
        try:
            procs.append(proc.info)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    if sort_by == "memory":
        procs.sort(key=lambda x: x.get('memory_percent', 0) or 0, reverse=True)
    else:
        procs.sort(key=lambda x: x.get('cpu_percent', 0) or 0, reverse=True)

    lines = [f"{'PID':<8} {'CPU%':<8} {'MEM%':<8} {'NAME'}"]
    lines.append("-" * 50)
    for p in procs[:20]:
        cpu = p.get('cpu_percent', 0) or 0
        mem = p.get('memory_percent', 0) or 0
        name = (p.get('name', '?') or '?')[:30]
        lines.append(f"{p['pid']:<8} {cpu:<8.1f} {mem:<8.1f} {name}")

    return "\n".join(lines)


@function_tool()
async def kill_process(pid: int = 0, name: str = "") -> str:
    """Kill a process by PID or name."""
    if pid:
        try:
            proc = psutil.Process(pid)
            proc.terminate()
            return f"Terminated PID {pid}: {proc.name()}"
        except psutil.NoSuchProcess:
            return f"Process PID {pid} not found"
        except psutil.AccessDenied:
            return f"Access denied to PID {pid}"

    if name:
        killed = []
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                if proc.info['name'] and name.lower() in proc.info['name'].lower():
                    proc.terminate()
                    killed.append(f"{proc.info['name']} (PID {proc.info['pid']})")
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        if killed:
            return f"Terminated: {', '.join(killed)}"
        return f"No process matching '{name
}'"

    return "Provide a PID or process name"
