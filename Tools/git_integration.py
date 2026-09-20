"""
ZENITH Git Integration Tool
Provides: git status, commit, push, pull, log, branch
"""

import subprocess
from typing import Optional
from livekit.agents import function_tool

TOOL = {
    "name": "git_integration",
    "description": "Perform Git operations: status, commit, push, pull, log, branch, diff, and clone. Use when the user wants to manage a Git repository.",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "action": {"type": "STRING", "description": "Git action: 'status', 'log', 'commit', 'push', 'pull', 'branch_list', 'diff', 'clone'"},
            "directory": {"type": "STRING", "description": "Repository directory path (default: current directory)"},
            "message": {"type": "STRING", "description": "Commit message (for commit action)"},
            "remote": {"type": "STRING", "description": "Remote name (default: 'origin')"},
            "url": {"type": "STRING", "description": "Repository URL (for clone action)"},
            "count": {"type": "INTEGER", "description": "Number of log entries to show (default: 10)"}
        },
        "required": ["action"]
    },
    "handler": "git_status",
}


def _run_git(args: list, cwd: str = None) -> dict:
    try:
        result = subprocess.run(
            ["git"] + args,
            capture_output=True, text=True, cwd=cwd, timeout=30
        )
        return {"success": result.returncode == 0, "output": result.stdout.strip(), "error": result.stderr.strip()}
    except FileNotFoundError:
        return {"success": False, "output": "", "error": "Git is not installed or not in PATH"}
    except subprocess.TimeoutExpired:
        return {"success": False, "output": "", "error": "Git command timed out"}
    except Exception as e:
        return {"success": False, "output": "", "error": str(e)}


@function_tool()
async def git_status(directory: str = ".") -> str:
    """Show the working tree status of a git repository."""
    result = _run_git(["status"], cwd=directory)
    if result["success"]:
        return f"Git Status:\n{result['output']}"
    return f"Git Error: {result['error']}"


@function_tool()
async def git_log(directory: str = ".", count: int = 10) -> str:
    """Show recent commit logs."""
    result = _run_git(["log", f"--oneline", f"-{count}"], cwd=directory)
    if result["success"]:
        return f"Recent Commits:\n{result['output']}"
    return f"Git Error: {result['error']}"


@function_tool()
async def git_commit(message: str, directory: str = ".") -> str:
    """Stage all changes and commit with a message."""
    _run_git(["add", "."], cwd=directory)
    result = _run_git(["commit", "-m", message], cwd=directory)
    if result["success"]:
        return f"Committed:\n{result['output']}"
    return f"Git Error: {result['error']}"


@function_tool()
async def git_push(remote: str = "origin", directory: str = ".") -> str:
    """Push commits to remote repository."""
    result = _run_git(["push", remote], cwd=directory)
    if result["success"]:
        return f"Pushed:\n{result['output']}"
    return f"Git Error: {result['error']}"


@function_tool()
async def git_pull(remote: str = "origin", directory: str = ".") -> str:
    """Pull latest changes from remote repository."""
    result = _run_git(["pull", remote], cwd=directory)
    if result["success"]:
        return f"Pulled:\n{result['output']}"
    return f"Git Error: {result['error']}"


@function_tool()
async def git_branch_list(directory: str = ".") -> str:
    """List all git branches."""
    result = _run_git(["branch", "-a"], cwd=directory)
    if result["success"]:
        return f"Branches:\n{result['output']}"
    return f"Git Error: {result['error']}"


@function_tool()
async def git_diff(directory: str = ".") -> str:
    """Show unstaged changes in the working directory."""
    result = _run_git(["diff"], cwd=directory)
    if result["success"]:
        return f"Changes:\n{result['output']}" if result["output"] else "No unstaged changes."
    return f"Git Error: {result['error']}"


@function_tool()
async def git_clone(url: str, directory: str = ".") -> str:
    """Clone a repository from a URL."""
    result = _run_git(["clone", url], cwd=directory)
    if result["success"]:
        return f"Cloned:\n{result['output']}"
    return f"Git Error: {result['error']
}"
