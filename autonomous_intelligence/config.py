"""
Configuration for the Autonomous Intelligence Engine.
"""
import os
import json
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class ResearchConfig:
    """Configuration for autonomous research sessions."""

    # Research limits
    max_runtime_minutes: int = 15
    max_search_queries: int = 20
    max_pages_visited: int = 30
    max_browser_tabs: int = 5
    max_tasks: int = 25
    max_evidence_items: int = 100
    max_retries: int = 3
    max_iterations: int = 50

    # Web research
    search_provider: str = "duckduckgo"
    allowed_domains: List[str] = field(default_factory=list)
    blocked_domains: List[str] = field(default_factory=lambda: [
        "facebook.com", "instagram.com", "tiktok.com",
        "reddit.com/login", "twitter.com/login"
    ])
    request_timeout: int = 15
    respect_robots_txt: bool = True
    rate_limit_delay: float = 1.0

    # Local intelligence
    indexed_paths: List[str] = field(default_factory=lambda: [
        os.path.expanduser("~/Desktop"),
        os.path.expanduser("~/Documents"),
    ])
    excluded_paths: List[str] = field(default_factory=lambda: [
        os.path.expanduser("~/.ssh"),
        os.path.expanduser("~/.env"),
        os.path.expanduser("~/AppData"),
        os.path.expanduser("~/.git"),
        "node_modules",
        "__pycache__",
        ".git",
    ])
    excluded_extensions: List[str] = field(default_factory=lambda: [
        ".exe", ".dll", ".so", ".dylib", ".bin",
        ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".ico",
        ".mp3", ".mp4", ".wav", ".avi", ".mov",
        ".zip", ".rar", ".7z", ".tar", ".gz",
        ".pyc", ".pyo", ".class",
    ])
    max_file_size_mb: int = 10
    max_index_files: int = 10000

    # Knowledge engine
    min_confidence_threshold: float = 0.3
    verification_searches: int = 2
    contradiction_detection: bool = True

    # Model configuration
    research_model: str = "gemini"
    temperature: float = 0.3

    # Storage
    storage_dir: str = field(
        default_factory=lambda: os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "autonomous_intelligence", "storage"
        )
    )

    # Permission level (0-6)
    permission_level: int = 2

    # Privacy
    redact_secrets: bool = True
    upload_local_files: bool = False

    def save(self, path: str = None):
        """Save config to JSON file."""
        path = path or os.path.join(self.storage_dir, "config.json")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w') as f:
            json.dump(self.__dict__, f, indent=2, default=str)

    @classmethod
    def load(cls, path: str = None) -> "ResearchConfig":
        """Load config from JSON file."""
        path = path or os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "autonomous_intelligence", "storage", "config.json"
        )
        if os.path.exists(path):
            with open(path, 'r') as f:
                data = json.load(f)
                return cls(**data)
        return cls()
