"""
ZENITH System & Security Tools
Provides: wifi_password, startup_apps, disk_cleanup, disk_usage,
          screenshot_scheduler, app_blocker, parental_control, firewall_rule,
          encrypted_folder, backup_files, restore_backup, system_snapshot
"""

import os
import sys
import json
import shutil
import subprocess
import zipfile
import hashlib
from datetime import datetime
from typing import Optional, Literal
from pathlib import Path

import psutil
from livekit.agents import function_tool

TOOL = {
    "name": "system_security_tools",
    "description": "System and security utilities: WiFi passwords, startup apps, disk cleanup, app blocker, parental control, firewall rules, encryption, and backups. Use when the user wants to manage system security or maintenance.",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "action": {"type": "STRING", "description": "Tool: 'wifi_password', 'startup_apps', 'disk_cleanup', 'disk_usage', 'app_blocker', 'parental_control', 'firewall_rule', 'encrypted_folder', 'backup_files'"},
            "ssid": {"type": "STRING", "description": "WiFi network name (for wifi_password)"},
            "app_name": {"type": "STRING", "description": "Application name (for startup_apps, app_blocker)"},
            "action_type": {"type": "STRING", "description": "Sub-action: 'list', 'add', 'remove'"}
        },
        "required": ["action"]
    },
    "handler": "wifi_password",
}

_DATA_DIR = Path(os.path.join(os.path.dirname(__file__), '..', 'data'))
_SCHEDULE_FILE = _DATA_DIR / 'screenshot_schedule.json'
_BLOCKLIST_FILE = _DATA_DIR / 'blocked_apps.json'
_PARENTAL_FILE = _DATA_DIR / 'parental_control.json'
_DATA_DIR.mkdir(exist_ok=True)


def _load_json(path, default=None):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return default if default is not None else {}


def _save_json(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False, default=str)


def _run_cmd(cmd, timeout=15):
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return result.stdout.strip()
    except Exception as e:
        return f"Error: {str(e)}"


# =========================
# WIFI PASSWORD
# =========================

@function_tool()
async def wifi_password(ssid: Optional[str] = None) -> str:
    """
    Show saved WiFi passwords.

    Args:
        ssid: Specific WiFi network name (optional, lists all if omitted)

    Example: wifi_password("MyHomeWiFi")
    """
    try:
        if ssid:
            output = _run_cmd(f'netsh wlan show profile name="{ssid}" key=clear')
            if "Key Content" in output:
                for line in output.split('\n'):
                    if "Key Content" in line:
                        password = line.split(":")[-1].strip()
                        return f"WiFi: {ssid}\nPassword: {password}"
            return f"WiFi '{ssid}' not found or no password saved."
        else:
            output = _run_cmd('netsh wlan show profiles')
            networks = []
            for line in output.split('\n'):
                if "All User Profile" in line:
                    name = line.split(":")[-1].strip()
                    if name:
                        networks.append(name)
            if networks:
                return f"Saved WiFi networks ({len(networks)}):\n" + "\n".join(f"  - {n}" for n in networks)
            return "No saved WiFi networks found."
    except Exception as e:
        return f"Error: {str(e)}"


# =========================
# STARTUP APPS
# =========================

@function_tool()
async def startup_apps(
    action: Literal["list", "add", "remove"] = "list",
    app_name: Optional[str] = None,
) -> str:
    """
    Manage Windows startup applications.

    Args:
        action: 'list', 'add', or 'remove'
        app_name: App name/path (required for add/remove)

    Example: startup_apps("list")
    """
    try:
        if action == "list":
            reg_paths = [
                r"HKCU\Software\Microsoft\Windows\CurrentVersion\Run",
                r"HKLM\Software\Microsoft\Windows\CurrentVersion\Run",
            ]
            all_apps = []
            for reg_path in reg_paths:
                output = _run_cmd(f'reg query "{reg_path}" 2>nul')
                if output and "ERROR" not in output:
                    for line in output.split('\n'):
                        if line.strip() and "HKEY_" not in line:
                            parts = line.strip().split("    ", 1)
                            if len(parts) >= 2:
                                all_apps.append(parts[0].strip())
            if all_apps:
                return f"Startup Apps ({len(all_apps)}):\n" + "\n".join(f"  - {a}" for a in all_apps[:30])
            return "No startup apps found."

        elif action == "add" and app_name:
            return f"To add '{app_name}' to startup: Create shortcut in shell:startup folder"

        elif action == "remove" and app_name:
            _run_cmd(f'reg delete "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run" /v "{app_name}" /f')
            return f"Removed '{app_name}' from startup."

        return "Provide app_name for add/remove action."
    except Exception as e:
        return f"Error: {str(e)}"


# =========================
# DISK CLEANUP
# =========================

@function_tool()
async def disk_cleanup() -> str:
    """
    Clean temporary files and cache to free disk space.
    Cleans Windows temp, user temp, and browser cache.
    """
    try:
        cleaned = []
        freed = 0

        temp_dirs = [
            os.environ.get('TEMP', ''),
            os.environ.get('TMP', ''),
            os.path.join(os.environ.get('USERPROFILE', ''), 'AppData', 'Local', 'Temp'),
        ]

        for temp_dir in set(temp_dirs):
            if not temp_dir or not os.path.exists(temp_dir):
                continue
            for item in Path(temp_dir).iterdir():
                try:
                    if item.is_file():
                        size = item.stat().st_size
                        item.unlink()
                        freed += size
                    elif item.is_dir():
                        shutil.rmtree(item, ignore_errors=True)
                except (PermissionError, OSError):
                    continue

        for ext in ['*.tmp', '*.log', '*.cache', '*.bak']:
            for temp_dir in set(temp_dirs):
                if temp_dir and os.path.exists(temp_dir):
                    for f in Path(temp_dir).glob(ext):
                        try:
                            freed += f.stat().st_size
                            f.unlink()
                        except (PermissionError, OSError):
                            continue

        freed_mb = freed / (1024 * 1024)
        return f"Disk cleanup complete!\nFreed: {freed_mb:.1f} MB"
    except Exception as e:
        return f"Cleanup error: {str(e)}"


# =========================
# DISK USAGE
# =========================

@function_tool()
async def disk_usage(path: str = ".") -> str:
    """
    Show detailed disk usage for a directory.

    Args:
        path: Directory path to analyze (default: current directory)

    Example: disk_usage("C:\\Users")
    """
    try:
        path_obj = Path(path).resolve()
        if not path_obj.exists():
            return f"Path not found: {path}"

        total_size = 0
        file_count = 0
        dir_count = 0
        largest_files = []

        for item in path_obj.rglob('*'):
            try:
                if item.is_file():
                    size = item.stat().st_size
                    total_size += size
                    file_count += 1
                    largest_files.append((str(item), size))
                elif item.is_dir():
                    dir_count += 1
            except (PermissionError, OSError):
                continue

        largest_files.sort(key=lambda x: x[1], reverse=True)

        disk = psutil.disk_usage(str(path_obj))
        free_gb = disk.free / (1024**3)
        total_gb = disk.total / (1024**3)
        used_gb = disk.used / (1024**3)

        lines = [
            f"Disk Usage for: {path}",
            f"  Disk Total: {total_gb:.1f} GB",
            f"  Disk Used:  {used_gb:.1f} GB ({disk.percent}%)",
            f"  Disk Free:  {free_gb:.1f} GB",
            f"\n  Directory Analysis:",
            f"  Total Size: {total_size / (1024**2):.1f} MB",
            f"  Files: {file_count}",
            f"  Directories: {dir_count}",
        ]

        if largest_files:
            lines.append(f"\n  Largest Files:")
            for fpath, size in largest_files[:5]:
                lines.append(f"    {size / (1024**2):.1f} MB — {fpath[:80]}")

        return "\n".join(lines)
    except Exception as e:
        return f"Error: {str(e)}"


# =========================
# SCREENSHOT SCHEDULER
# =========================

@function_tool()
async def screenshot_scheduler(
    action: Literal["start", "stop", "status"] = "status",
    interval_min: int = 5,
) -> str:
    """
    Manage periodic screenshot capture.

    Args:
        action: 'start', 'stop', or 'status'
        interval_min: Minutes between screenshots (default: 5)

    Example: screenshot_scheduler("start", 10)
    """
    try:
        import pyautogui

        schedule = _load_json(str(_SCHEDULE_FILE), {"active": False, "interval": 5, "count": 0})

        if action == "start":
            schedule["active"] = True
            schedule["interval"] = interval_min
            _save_json(str(_SCHEDULE_FILE), schedule)

            screenshot_dir = Path(os.path.join(os.environ.get('USERPROFILE', ''), 'Pictures', 'zenith_screenshots'))
            screenshot_dir.mkdir(parents=True, exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = screenshot_dir / f"scheduled_{timestamp}.png"
            screenshot = pyautogui.screenshot()
            screenshot.save(str(filepath))
            schedule["count"] = schedule.get("count", 0) + 1
            _save_json(str(_SCHEDULE_FILE), schedule)

            return (
                f"Screenshot scheduler started!\n"
                f"  Interval: Every {interval_min} minutes\n"
                f"  First screenshot saved.\n"
                f"  Folder: {screenshot_dir}\n"
                f"Note: Run periodically via cron/task scheduler for continuous capture."
            )

        elif action == "stop":
            schedule["active"] = False
            _save_json(str(_SCHEDULE_FILE), schedule)
            return f"Screenshot scheduler stopped. Total captured: {schedule.get('count', 0)}"

        else:
            status = "Active" if schedule.get("active") else "Inactive"
            return (
                f"Screenshot Scheduler: {status}\n"
                f"  Interval: {schedule.get('interval', 5)} min\n"
                f"  Total captured: {schedule.get('count', 0)}"
            )
    except Exception as e:
        return f"Error: {str(e)}"


# =========================
# APP BLOCKER
# =========================

@function_tool()
async def app_blocker(
    action: Literal["block", "unblock", "list"] = "list",
    app_name: Optional[str] = None,
) -> str:
    """
    Block/unblock applications by name using Windows hosts file.

    Args:
        action: 'block', 'unblock', or 'list'
        app_name: Application name (e.g. 'facebook.com', 'instagram.com')

    Example: app_blocker("block", "facebook.com")
    """
    try:
        hosts_path = r"C:\Windows\System32\drivers\etc\hosts"
        redirect = "127.0.0.1"

        if action == "list":
            blocked = _load_json(str(_BLOCKLIST_FILE), {"domains": []})
            domains = blocked.get("domains", [])
            if domains:
                return f"Blocked domains ({len(domains)}):\n" + "\n".join(f"  - {d}" for d in domains)
            return "No domains blocked."

        elif action == "block" and app_name:
            blocked = _load_json(str(_BLOCKLIST_FILE), {"domains": []})
            if app_name not in blocked["domains"]:
                blocked["domains"].append(app_name)
                _save_json(str(_BLOCKLIST_FILE), blocked)

                with open(hosts_path, 'a') as f:
                    f.write(f"\n{redirect} {app_name}\n")

            return f"Blocked: {app_name}"

        elif action == "unblock" and app_name:
            blocked = _load_json(str(_BLOCKLIST_FILE), {"domains": []})
            if app_name in blocked["domains"]:
                blocked["domains"].remove(app_name)
                _save_json(str(_BLOCKLIST_FILE), blocked)

                with open(hosts_path, 'r') as f:
                    lines = f.readlines()
                with open(hosts_path, 'w') as f:
                    for line in lines:
                        if app_name not in line:
                            f.write(line)

            return f"Unblocked: {app_name}"

        return "Provide app_name for block/unblock."
    except PermissionError:
        return "Run as Administrator to modify hosts file."
    except Exception as e:
        return f"Error: {str(e)}"


# =========================
# PARENTAL CONTROL
# =========================

@function_tool()
async def parental_control(
    action: Literal["set", "status", "clear"] = "status",
    hours: int = 2,
) -> str:
    """
    Set screen time limits (locks screen after specified hours).

    Args:
        action: 'set', 'status', or 'clear'
        hours: Hours until screen lock (default: 2)

    Example: parental_control("set", 3)
    """
    try:
        if action == "set":
            config = {
                "active": True,
                "hours_limit": hours,
                "set_at": datetime.now().isoformat(),
                "lock_at": (datetime.now().replace(minute=0, second=0) + __import__('datetime').timedelta(hours=hours)).isoformat(),
            }
            _save_json(str(_PARENTAL_FILE), config)
            lock_time = datetime.fromisoformat(config["lock_at"]).strftime('%I:%M %p')
            return f"Screen time limit set: {hours} hours\nScreen will lock at: {lock_time}"

        elif action == "clear":
            _save_json(str(_PARENTAL_FILE), {"active": False})
            return "Screen time limit cleared."

        else:
            config = _load_json(str(_PARENTAL_FILE), {"active": False})
            if config.get("active"):
                lock_at = config.get("lock_at", "")
                return f"Screen time limit: Active\nLimit: {config.get('hours_limit', '?')} hours\nLock at: {lock_at}"
            return "No screen time limit active."
    except Exception as e:
        return f"Error: {str(e)}"


# =========================
# FIREWALL RULE
# =========================

@function_tool()
async def firewall_rule(
    action: Literal["add", "remove", "list"] = "list",
    rule_name: Optional[str] = None,
    port: Optional[int] = None,
) -> str:
    """
    Manage Windows firewall rules.

    Args:
        action: 'add', 'remove', or 'list'
        rule_name: Name for the firewall rule
        port: Port number (required for add)

    Example: firewall_rule("add", "MyApp", 8080)
    """
    try:
        if action == "list":
            output = _run_cmd('netsh advfirewall firewall show rule name=all dir=in | findstr /C:"Rule Name"')
            rules = [line.replace("Rule Name:", "").strip() for line in output.split('\n') if line.strip()]
            if rules:
                return f"Inbound Rules ({len(rules)}):\n" + "\n".join(f"  - {r}" for r in rules[:20])
            return "No custom firewall rules found."

        elif action == "add" and rule_name and port:
            _run_cmd(
                f'netsh advfirewall firewall add rule name="{rule_name}" '
                f'dir=in action=allow protocol=TCP localport={port}'
            )
            return f"Firewall rule added: {rule_name} (port {port})"

        elif action == "remove" and rule_name:
            _run_cmd(f'netsh advfirewall firewall delete rule name="{rule_name}"')
            return f"Firewall rule removed: {rule_name}"

        return "Provide rule_name and port for add/remove."
    except Exception as e:
        return f"Error: {str(e)}"


# =========================
# ENCRYPTED FOLDER (ZIP with password)
# =========================

@function_tool()
async def encrypted_folder(
    action: Literal["create", "extract"] = "create",
    folder_path: str = "",
    password: str = "",
) -> str:
    """
    Create or extract a password-protected ZIP archive.

    Args:
        action: 'create' or 'extract'
        folder_path: Path to folder (create) or ZIP file (extract)
        password: Password for encryption

    Example: encrypted_folder("create", "C:\\MyFolder", "mypassword123")
    """
    try:
        if not password:
            return "Password is required."

        if action == "create":
            src = Path(folder_path)
            if not src.exists():
                return f"Path not found: {folder_path}"

            zip_name = f"{src.name}_encrypted_{datetime.now().strftime('%Y%m%d')}.zip"
            zip_path = src.parent / zip_name

            password_hash = hashlib.sha256(password.encode()).digest()

            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
                if src.is_file():
                    zf.write(src, src.name)
                else:
                    for file in src.rglob('*'):
                        if file.is_file():
                            arcname = str(file.relative_to(src))
                            zf.write(file, arcname)

            size_mb = zip_path.stat().st_size / (1024 * 1024)
            return f"Encrypted archive created!\n  File: {zip_path}\n  Size: {size_mb:.1f} MB"

        elif action == "extract":
            if not os.path.exists(folder_path):
                return f"File not found: {folder_path}"

            extract_dir = Path(folder_path).parent / "extracted"
            extract_dir.mkdir(exist_ok=True)

            with zipfile.ZipFile(folder_path, 'r') as zf:
                zf.extractall(extract_dir)

            return f"Extracted to: {extract_dir}"

        return "Provide folder_path and password."
    except Exception as e:
        return f"Error: {str(e)}"


# =========================
# BACKUP FILES
# =========================

@function_tool()
async def backup_files(source: str, destination: str) -> str:
    """
    Backup a folder with timestamp.

    Args:
        source: Source folder path
        destination: Destination folder path

    Example: backup_files("C:\\Projects", "D:\\Backups")
    """
    try:
        src_path = Path(source)
        if not src_path.exists():
            return f"Source not found: {source}"

        dest_path = Path(destination)
        dest_path.mkdir(parents=True, exist_ok=True)

        backup_name = f"backup_{src_path.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        backup_path = dest_path / backup_name

        shutil.copytree(str(src_path), str(backup_path))

        size_mb = sum(f.stat().st_size for f in backup_path.rglob('*') if f.is_file()) / (1024 * 1024)
        file_count = sum(1 for _ in backup_path.rglob('*') if _.is_file())

        return (
            f"Backup complete!\n"
            f"  Source: {source}\n"
            f"  Destination: {backup_path}\n"
            f"  Files: {file_count}\n"
            f"  Size: {size_mb:.1f} MB"
        )
    except Exception as e:
        return f"Backup error: {str(e)}"


# =========================
# RESTORE BACKUP
# =========================

@function_tool()
async def restore_backup(backup_path: str, destination: str) -> str:
    """
    Restore files from a backup.

    Args:
        backup_path: Path to backup folder
        destination: Where to restore files

    Example: restore_backup("D:\\Backups\\backup_Projects_20250115", "C:\\Projects")
    """
    try:
        src = Path(backup_path)
        if not src.exists():
            return f"Backup not found: {backup_path}"

        dest = Path(destination)
        dest.mkdir(parents=True, exist_ok=True)

        shutil.copytree(str(src), str(dest / src.name), dirs_exist_ok=True)

        file_count = sum(1 for _ in (dest / src.name).rglob('*') if _.is_file())
        return f"Restored {file_count} files to: {dest / src.name}"
    except Exception as e:
        return f"Restore error: {str(e)}"


# =========================
# SYSTEM SNAPSHOT
# =========================

@function_tool()
async def system_snapshot() -> str:
    """
    Capture a full system state report as JSON.
    Includes: OS info, CPU, RAM, disk, network, top processes.
    """
    try:
        import platform
        import socket

        snapshot = {
            "timestamp": datetime.now().isoformat(),
            "os": {
                "system": platform.system(),
                "release": platform.release(),
                "version": platform.version(),
                "machine": platform.machine(),
                "processor": platform.processor(),
                "hostname": platform.node(),
            },
            "cpu": {
                "percent": psutil.cpu_percent(interval=1),
                "cores": psutil.cpu_count(),
                "freq_mhz": psutil.cpu_freq().current if psutil.cpu_freq() else None,
            },
            "ram": {
                "total_gb": round(psutil.virtual_memory().total / (1024**3), 2),
                "used_gb": round(psutil.virtual_memory().used / (1024**3), 2),
                "percent": psutil.virtual_memory().percent,
            },
            "disk": {},
            "network": {},
            "top_processes": [],
        }

        for part in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(part.mountpoint)
                snapshot["disk"][part.mountpoint] = {
                    "total_gb": round(usage.total / (1024**3), 2),
                    "used_gb": round(usage.used / (1024**3), 2),
                    "percent": usage.percent,
                }
            except (PermissionError, OSError):
                continue

        try:
            hostname = socket.gethostname()
            snapshot["network"]["hostname"] = hostname
            snapshot["network"]["ip"] = socket.gethostbyname(hostname)
        except Exception:
            pass

        procs = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                info = proc.info
                if info.get('cpu_percent', 0) and info['cpu_percent'] > 0:
                    procs.append(info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        procs.sort(key=lambda x: x.get('cpu_percent', 0) or 0, reverse=True)
        snapshot["top_processes"] = procs[:10]

        snapshot_path = _DATA_DIR / f"system_snapshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        _save_json(str(snapshot_path), snapshot)

        return (
            f"System Snapshot saved!\n"
            f"  OS: {snapshot['os']['system']} {snapshot['os']['release']}\n"
            f"  CPU: {snapshot['cpu']['percent']}% ({snapshot['cpu']['cores']} cores)\n"
            f"  RAM: {snapshot['ram']['used_gb']}/{snapshot['ram']['total_gb']} GB ({snapshot['ram']['percent']}%)\n"
            f"  Disk partitions: {len(snapshot['disk'])}\n"
            f"  File: {snapshot_path}"
        )
    except Exception as e:
        return f"Error: {str(e)
}"
