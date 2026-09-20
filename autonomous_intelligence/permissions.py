"""
Permission and safety system for autonomous research.
"""
import os
import re
from enum import IntEnum
from typing import List, Optional


class PermissionLevel(IntEnum):
    NO_ACCESS = 0
    READ_LOCAL = 1
    WEB_RESEARCH = 2
    EXECUTE_APPS = 3
    WRITE_WORKSPACE = 4
    SYSTEM_COMMANDS = 5
    ADMIN = 6


class PermissionManager:
    """Enforces permission boundaries for autonomous research."""

    def __init__(self, level: PermissionLevel = PermissionLevel.WEB_RESEARCH):
        self.level = level
        self._action_log: List[dict] = []

        # Default exclusions for sensitive paths
        self.sensitive_patterns = [
            r"\.ssh",
            r"\.env",
            r"password",
            r"secret",
            r"token",
            r"credential",
            r"\.key$",
            r"\.pem$",
            r"browser.*data",
            r"cookies",
            r"login.*data",
        ]

    def can_access_web(self) -> bool:
        return self.level >= PermissionLevel.WEB_RESEARCH

    def can_read_local(self) -> bool:
        return self.level >= PermissionLevel.READ_LOCAL

    def can_write(self) -> bool:
        return self.level >= PermissionLevel.WRITE_WORKSPACE

    def can_execute(self) -> bool:
        return self.level >= PermissionLevel.EXECUTE_APPS

    def check_file_access(self, path: str) -> bool:
        """Check if a file path is allowed."""
        if not self.can_read_local():
            return False

        path_lower = path.lower().replace("\\", "/")

        # Check sensitive patterns
        for pattern in self.sensitive_patterns:
            if re.search(pattern, path_lower):
                self._log("BLOCKED", path, f"Matches sensitive pattern: {pattern}")
                return False

        # Check excluded paths from config
        excluded = [
            "~/.ssh", "~/.env", "~/AppData", "~/.git",
            "node_modules", "__pycache__", ".git",
        ]
        for exc in excluded:
            exc_expanded = os.path.expanduser(exc).lower().replace("\\", "/")
            if path_lower.startswith(exc_expanded):
                self._log("BLOCKED", path, f"In excluded path: {exc}")
                return False

        self._log("ALLOWED", path, "File access granted")
        return True

    def check_url_access(self, url: str) -> bool:
        """Check if a URL is allowed."""
        if not self.can_access_web():
            return False

        blocked = [
            "facebook.com/login", "instagram.com/login",
            "twitter.com/login", "x.com/login",
            "linkedin.com/login",
        ]
        url_lower = url.lower()
        for b in blocked:
            if b in url_lower:
                self._log("BLOCKED", url, "Login page blocked")
                return False

        self._log("ALLOWED", url, "URL access granted")
        return True

    def redact_secrets(self, text: str) -> str:
        """Remove potential secrets from text before sending to external APIs."""
        if not self.level >= PermissionLevel.WEB_RESEARCH:
            return text

        # Redact common secret patterns
        patterns = [
            (r'(api[_-]?key["\s:=]+)\S+', r'\1[REDACTED]'),
            (r'(secret["\s:=]+)\S+', r'\1[REDACTED]'),
            (r'(password["\s:=]+)\S+', r'\1[REDACTED]'),
            (r'(token["\s:=]+)\S+', r'\1[REDACTED]'),
            (r'(sk-[a-zA-Z0-9]{20,})', '[REDACTED_KEY]'),
            (r'(ghp_[a-zA-Z0-9]{36})', '[REDACTED_TOKEN]'),
            (r'([a-zA-Z0-9]{32,})', lambda m: m.group(0) if len(m.group(0)) < 40 else '[REDACTED]'),
        ]

        redacted = text
        for pattern, replacement in patterns:
            redacted = re.sub(pattern, replacement, redacted, flags=re.IGNORECASE)

        return redacted

    def validate_action(self, action: str, target: str) -> bool:
        """Validate an action before execution."""
        if action in ("read_file", "read_code", "list_dir"):
            return self.check_file_access(target)
        elif action in ("web_search", "open_url", "scrape_page"):
            return self.check_url_access(target)
        elif action in ("write_file", "create_file"):
            return self.can_write()
        elif action in ("run_command", "execute"):
            return self.can_execute()
        return True

    def _log(self, status: str, target: str, reason: str):
        self._action_log.append({
            "status": status,
            "target": target[:200],
            "reason": reason,
        })

    def get_log(self, limit: int = 50) -> List[dict]:
        return self._action_log[-limit:]
