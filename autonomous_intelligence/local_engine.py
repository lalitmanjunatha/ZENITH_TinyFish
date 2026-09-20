"""
Local Intelligence Engine for searching and analyzing local files.
"""
import os
import re
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from .models import Source, SourceType
from .events import EventBus, EventType, create_event
from .config import ResearchConfig
from .permissions import PermissionManager


class FileRecord:
    """Metadata for an indexed file."""
    def __init__(self, path: str):
        self.path = path
        self.name = os.path.basename(path)
        self.ext = os.path.splitext(path)[1].lower()
        self.size = 0
        self.modified = ""
        self.content_hash = ""
        self.content_type = "unknown"
        self.indexed = False
        self._update_metadata()

    def _update_metadata(self):
        try:
            stat = os.stat(self.path)
            self.size = stat.st_size
            self.modified = datetime.fromtimestamp(stat.st_mtime).isoformat()
            self.content_type = self._guess_type()
        except Exception:
            pass

    def _guess_type(self) -> str:
        ext_map = {
            ".py": "python", ".js": "javascript", ".ts": "typescript",
            ".java": "java", ".cpp": "cpp", ".c": "c", ".h": "c_header",
            ".html": "html", ".css": "css", ".json": "json",
            ".xml": "xml", ".yaml": "yaml", ".yml": "yaml",
            ".md": "markdown", ".txt": "text", ".csv": "csv",
            ".sql": "sql", ".log": "log", ".sh": "shell",
            ".bat": "batch", ".ps1": "powershell",
            ".dart": "dart", ".go": "go", ".rs": "rust",
            ".rb": "ruby", ".php": "php", ".swift": "swift",
            ".kt": "kotlin", ".scala": "scala",
            ".pdf": "pdf", ".docx": "docx", ".xlsx": "xlsx",
            ".pptx": "pptx", ".rtf": "rtf",
        }
        return ext_map.get(self.ext, "other")


class LocalIntelligenceEngine:
    """Handles local file search, reading, and code analysis."""

    READABLE_EXTENSIONS = {
        ".py", ".js", ".ts", ".jsx", ".tsx", ".java", ".cpp", ".c", ".h",
        ".html", ".css", ".scss", ".less", ".json", ".xml", ".yaml", ".yml",
        ".md", ".txt", ".csv", ".sql", ".log", ".sh", ".bat", ".ps1",
        ".dart", ".go", ".rs", ".rb", ".php", ".swift", ".kt", ".scala",
        ".cfg", ".ini", ".toml", ".env.example", ".gitignore",
        ".r", ".R", ".m", ".mm", ".vue", ".svelte",
    }

    def __init__(
        self,
        config: ResearchConfig,
        event_bus: EventBus,
        permissions: PermissionManager,
    ):
        self.config = config
        self.events = event_bus
        self.permissions = permissions
        self._file_index: Dict[str, FileRecord] = {}
        self._content_cache: Dict[str, str] = {}

    def build_index(self, paths: List[str] = None) -> int:
        """Build file index from configured or specified paths."""
        paths = paths or self.config.indexed_paths
        count = 0

        for base_path in paths:
            base_path = os.path.expanduser(base_path)
            if not os.path.exists(base_path):
                continue

            for root, dirs, files in os.walk(base_path):
                # Skip excluded directories
                dirs[:] = [d for d in dirs if not self._is_excluded_dir(d, root)]

                for fname in files:
                    fpath = os.path.join(root, fname)
                    if self._is_indexable(fpath):
                        if fpath not in self._file_index:
                            record = FileRecord(fpath)
                            self._file_index[fpath] = record
                            count += 1

                        if count >= self.config.max_index_files:
                            return count

        self.events.emit(create_event(
            EventType.FILE_INDEXED,
            files_indexed=count, total=len(self._file_index)
        ))
        return count

    def search(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """Search indexed files by content and name."""
        if not self.permissions.can_read_local():
            return []

        self.events.emit(create_event(
            EventType.LOCAL_SEARCH_STARTED, query=query
        ))

        results = []
        query_lower = query.lower()
        query_terms = query_lower.split()

        for path, record in self._file_index.items():
            if not self.permissions.check_file_access(path):
                continue

            score = 0
            name_lower = record.name.lower()

            # Name match
            for term in query_terms:
                if term in name_lower:
                    score += 3

            # Extension relevance
            if record.content_type in ("python", "javascript", "markdown", "text", "json"):
                score += 1

            # Content match (check cached or read)
            if score > 0 or len(results) < max_results:
                content = self._read_file_preview(path)
                if content:
                    for term in query_terms:
                        if term in content.lower():
                            score += 2

            if score > 0:
                results.append({
                    "path": path,
                    "name": record.name,
                    "type": record.content_type,
                    "size": record.size,
                    "modified": record.modified,
                    "score": score,
                    "preview": self._read_file_preview(path)[:500] if score > 2 else "",
                })

        results.sort(key=lambda x: x["score"], reverse=True)
        results = results[:max_results]

        self.events.emit(create_event(
            EventType.LOCAL_SEARCH_COMPLETED,
            query=query, results_count=len(results)
        ))

        return results

    def read_file(self, path: str, max_lines: int = 200) -> str:
        """Read a file's content."""
        if not self.permissions.check_file_access(path):
            return "[ACCESS DENIED]"

        if not os.path.exists(path):
            return "[FILE NOT FOUND]"

        ext = os.path.splitext(path)[1].lower()
        if ext not in self.READABLE_EXTENSIONS:
            return f"[UNSUPPORTED FORMAT: {ext}]"

        try:
            size = os.path.getsize(path)
            if size > self.config.max_file_size_mb * 1024 * 1024:
                return f"[FILE TOO LARGE: {size // (1024*1024)}MB]"

            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = []
                for i, line in enumerate(f):
                    if i >= max_lines:
                        lines.append(f"\n... [{max_lines} lines shown]")
                        break
                    lines.append(line.rstrip())

            content = "\n".join(lines)

            self.events.emit(create_event(
                EventType.FILE_READ,
                path=path, lines=len(lines), size=size
            ))

            return content

        except Exception as e:
            return f"[READ ERROR: {str(e)[:100]}]"

    def search_code(self, query: str, file_types: List[str] = None) -> List[Dict[str, Any]]:
        """Search for code patterns in files."""
        if not self.permissions.can_read_local():
            return []

        file_types = file_types or [".py", ".js", ".ts", ".java", ".cpp", ".c", ".h"]
        results = []

        for path, record in self._file_index.items():
            if record.ext not in file_types:
                continue
            if not self.permissions.check_file_access(path):
                continue

            try:
                with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                    for i, line in enumerate(f, 1):
                        if query.lower() in line.lower():
                            results.append({
                                "path": path,
                                "line": i,
                                "content": line.strip()[:200],
                                "type": record.content_type,
                            })
                            if len(results) >= 20:
                                return results
            except Exception:
                continue

        return results

    def analyze_codebase(self, path: str) -> Dict[str, Any]:
        """Analyze a codebase directory for structure and patterns."""
        if not os.path.exists(path):
            return {"error": "Path not found"}

        analysis = {
            "path": path,
            "total_files": 0,
            "by_type": {},
            "total_lines": 0,
            "languages": set(),
            "imports": [],
            "classes": [],
            "functions": [],
            "key_files": [],
            "dependencies": [],
            "config_files": [],
        }

        for root, dirs, files in os.walk(path):
            dirs[:] = [d for d in dirs if not self._is_excluded_dir(d, root)]

            for fname in files:
                fpath = os.path.join(root, fname)
                ext = os.path.splitext(fname)[1].lower()

                analysis["total_files"] += 1
                analysis["by_type"][ext] = analysis["by_type"].get(ext, 0) + 1

                if ext in self.READABLE_EXTENSIONS:
                    try:
                        with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            lines = content.split('\n')
                            analysis["total_lines"] += len(lines)

                            if ext == ".py":
                                analysis["languages"].add("Python")
                                for line in lines[:500]:
                                    if line.strip().startswith("import ") or line.strip().startswith("from "):
                                        analysis["imports"].append(line.strip()[:100])
                                    if line.strip().startswith("class "):
                                        analysis["classes"].append(line.strip()[:100])
                                    if line.strip().startswith("def "):
                                        analysis["functions"].append(line.strip()[:100])

                            if fname in ("requirements.txt", "package.json", "pyproject.toml"):
                                analysis["dependencies"].append(fname)

                            if fname in (".env", "config.json", "config.yaml", "settings.py"):
                                analysis["config_files"].append(fname)
                    except Exception:
                        pass

                # Track key files
                if fname in ("agent.py", "main.py", "app.py", "index.ts", "README.md"):
                    analysis["key_files"].append(fpath)

        analysis["languages"] = list(analysis["languages"])
        analysis["imports"] = analysis["imports"][:50]
        analysis["classes"] = analysis["classes"][:50]
        analysis["functions"] = analysis["functions"][:50]

        return analysis

    def list_directory(self, path: str, max_items: int = 50) -> List[Dict[str, str]]:
        """List contents of a directory."""
        if not self.permissions.check_file_access(path):
            return []

        if not os.path.exists(path):
            return []

        items = []
        try:
            for entry in os.scandir(path):
                items.append({
                    "name": entry.name,
                    "type": "dir" if entry.is_dir() else "file",
                    "path": entry.path,
                    "size": str(entry.stat().st_size) if entry.is_file() else "-",
                })
                if len(items) >= max_items:
                    break
        except PermissionError:
            pass

        return sorted(items, key=lambda x: (x["type"] != "dir", x["name"].lower()))

    def _read_file_preview(self, path: str, max_chars: int = 1000) -> str:
        """Read a small preview of a file."""
        if path in self._content_cache:
            return self._content_cache[path][:max_chars]

        try:
            ext = os.path.splitext(path)[1].lower()
            if ext not in self.READABLE_EXTENSIONS:
                return ""

            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read(max_chars * 2)

            self._content_cache[path] = content
            return content[:max_chars]
        except Exception:
            return ""

    def _is_indexable(self, path: str) -> bool:
        """Check if a file should be indexed."""
        ext = os.path.splitext(path)[1].lower()
        if ext in self.config.excluded_extensions:
            return False
        if ext not in self.READABLE_EXTENSIONS:
            return False

        try:
            size = os.path.getsize(path)
            if size > self.config.max_file_size_mb * 1024 * 1024:
                return False
        except Exception:
            return False

        return True

    def _is_excluded_dir(self, dirname: str, parent_path: str) -> bool:
        """Check if a directory should be excluded."""
        if dirname.startswith('.'):
            return True
        for excluded in self.config.excluded_paths:
            if dirname in excluded:
                return True
        return False

    def get_index_stats(self) -> Dict[str, Any]:
        """Get statistics about the file index."""
        by_type = {}
        for record in self._file_index.values():
            by_type[record.content_type] = by_type.get(record.content_type, 0) + 1

        return {
            "total_files": len(self._file_index),
            "by_type": by_type,
            "cached_content": len(self._content_cache),
        }
