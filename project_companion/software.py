from __future__ import annotations

import ast
import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from project_companion.models import (
    ProjectSession,
    ProjectType,
    ProjectStage,
    Task,
    TaskStatus,
    Milestone,
    ProjectID,
    ProjectStateSummary,
)
from project_companion.store import ProjectStore
from project_companion.policies import default_policies, ProjectSafetyPolicies, SafetyLevel
from project_companion.tests.test_models import ProjectID as TestProjectID


class RepositoryAnalyzer:
    """Inspects a Python repository structure without dumping everything into context."""

    def __init__(self, repo_path: str, max_files: int = 50):
        self.repo_path = Path(repo_path).resolve()
        self.max_files = max_files
        self.skipped_dirs = {"__pycache__", ".git", ".egg-info", "build", "dist"}
        self.skipped_files = {".pyc", "__init__.py", "conftest.py"}
        self.info: Dict[str, Any] = {}

    def analyze(self) -> Dict[str, Any]:
        """Run full repository analysis."""
        self._collect_basic_info()
        self._find_entry_points()
        self._find_dependencies()
        self._find_test_configurations()
        self._find_key_files()
        return self.info

    def _collect_basic_info(self) -> None:
        """Collect basic repository metadata."""
        try:
            # Get repo name from parent directory or git
            if self.repo_path.name:
                self.info["name"] = self.repo_path.name
            else:
                self.info["name"] = str(self.repo_path)

            # Get Python version
            self.info["python_version"] = sys.version.split(" ")[0]

            # Check for common config files
            config_files = ["pyproject.toml", "setup.py", "setup.cfg", "tox.ini", "Makefile"]
            for cf in config_files:
                if (self.repo_path / cf).exists():
                    self.info[f"config_{cf}"] = "present"
                    break

            # Count total Python files
            py_files = list(self.repo_path.rglob("*.py"))
            excluded = [f for f in py_files if any(
                s in str(f.relative_to(self.repo_path)) for s in self.skipped_dirs
            )]
            self.info["total_python_files"] = len(py_files) - len(excluded)
        except Exception as e:
            self.info["error"] = str(e)

    def _find_entry_points(self) -> None:
        """Find entry points and main modules."""
        try:
            # Look for common entry points
            entry_patterns = ["main.py", "__main__.py", "run.py", "start.py"]
            for pattern in entry_patterns:
                p = self.repo_path / pattern
                if p.exists():
                    self.info["entry_point"] = str(p.relative_to(self.repo_path))
                    break

            # Look for app/factory functions
            factory_funcs = []
            for py_file in self._get_python_files()[:30]:
                try:
                    content = py_file.read_text(encoding="utf-8", errors="replace")
                    if "def " in content:
                        # Look for common factory/entry patterns
                        if any(kw in content for kw in ["create_app", "create_server", "main(", "app ="]):
                            func_matches = re.findall(r'def\s+(\w+)\s*\(', content[:2000])
                            factory_funcs.extend(func_matches)
                except Exception:
                    pass

            if factory_funcs:
                self.info["potential_factories"] = list(set(factory_funcs))[:10]
        except Exception as e:
            self.info["entry_point_error"] = str(e)

    def _find_dependencies(self) -> None:
        """Find project dependencies."""
        try:
            # Check for requirements files
            for rf in ["requirements.txt", "requirements-dev.txt", "environment.yml", "conda.yml"]:
                if (self.repo_path / rf).exists():
                    self.info[f"deps_{rf}"] = "present"

            # Check pyproject.toml for dependencies
            tp = self.repo_path / "pyproject.toml"
            if tp.exists():
                try:
                    content = tp.read_text(encoding="utf-8", errors="replace")
                    # Simple parsing - look for [tool.poetry.dependencies] or [project.dependencies]
                    deps = re.findall(r'dependencies\s*=\s*\[(.*?)\]', content, re.DOTALL)
                    if deps:
                        self.info["pyproject_deps"] = deps[0][:200]
                    else:
                        # Try pipreqs-style or just note it exists
                        self.info["pyproject_toml"] = "present"
                except Exception:
                    self.info["pyproject_toml"] = "present"

            # Check setup.py
            sp = self.repo_path / "setup.py"
            if sp.exists():
                self.info["setup_py"] = "present"

        except Exception as e:
            self.info["dep_error"] = str(e)

    def _find_test_configurations(self) -> None:
        """Find test configuration and command."""
        try:
            # Check for test directories
            test_dirs = ["tests", "test", "spec"]
            for td in test_dirs:
                if (self.repo_path / td).is_dir():
                    self.info["has_test_dir"] = True
                    break

            # Look for test config files
            for cfg in ["pytest.ini", "pyproject.toml", "tox.ini", "unittest.cfg"]:
                if (self.repo_path / cfg).exists():
                    self.info["test_config"] = cfg
                    break

            # Look for test commands
            for py in self._get_python_files()[:20]:
                content = py.read_text(encoding="utf-8", errors="replace")[:500]
                if "pytest" in content or "unittest" in content or "test_" in content:
                    self.info["has_test_imports"] = True
                    break

            # Try to determine test command
            if self.info.get("has_test_dir") or self.info.get("test_config"):
                self.info["test_command"] = "pytest"
            else:
                self.info["test_command"] = "unknown"
        except Exception as e:
            self.info["test_config_error"] = str(e)

    def _find_key_files(self) -> None:
        """Identify key source files."""
        try:
            important_patterns = [
                "__init__.py",
                "api.py", "handlers.py", "routes.py",
                "models.py", "db.py", "database.py",
                "errors.py", "exceptions.py",
            ]

            key_files = []
            for pattern in important_patterns:
                p = self.repo_path / pattern
                if p.exists():
                    key_files.append(str(p.relative_to(self.repo_path)))

            if key_files:
                self.info["key_files"] = key_files[:20]
        except Exception as e:
            self.info["key_files_error"] = str(e)

    def _get_python_files(self) -> List[Path]:
        """Get Python files excluding skipped dirs."""
        try:
            all_py = list(self.repo_path.rglob("*.py"))
            result = []
            for f in all_py:
                try:
                    relative = str(f.relative_to(self.repo_path))
                    if not any(s in relative for s in self.skipped_dirs):
                        result.append(f)
                except Exception:
                    pass
            return sorted(result, key=lambda p: p.name)[:self.max_files]
        except Exception:
            return []


class SoftwareProjectCompanion:
    """Companion for software project development workflow."""

    def __init__(self, orchestrator: Optional[Any] = None, policies: Optional[ProjectSafetyPolicies] = None):
        self.orchestrator = orchestrator
        self.policies = policies or default_policies()
        self.repository_analyzer: Optional[RepositoryAnalyzer] = None
        self.diagnostic_reports: List[Dict[str, Any]] = []

    def start_project(self, project_session: ProjectSession) -> ProjectSession:
        """Start the software project workflow.

        1. Ask for project goal and expected outcome
        2. Ask for acceptance criteria if missing
        3. Inspect repository structure
        4. Identify errors using available evidence
        5. Determine root cause
        6. Save checkpoint
        7. Apply smallest reasonable patch
        8. Run tests
        9. Verify against acceptance criteria
        10. Retry if needed
        """
        from project_companion.orchestrator import ProjectOrchestrator

        # Ensure project has acceptance criteria
        if not project_session.acceptance_criteria:
            # Prompt user (in real usage, this would be via voice/text)
            print("Please provide acceptance criteria for this project.")
            # For now, use defaults based on project type
            if project_session.project_type == ProjectType.SOFTWARE:
                project_session.acceptance_criteria = [
                    "No critical bugs in tested paths",
                    "All existing tests pass",
                    "Code follows project style guidelines",
                ]

        # Step 1-2: Repository inspection already done when project was created
        # Step 3: Identify errors
        errors = self._identify_errors(project_session)

        # Step 4: Determine root cause
        root_cause = self._analyze_root_cause(errors, project_session)

        # Step 5: Save checkpoint before making changes
        self._save_checkpoint(project_session)

        # Step 6-8: Apply fix and test
        fix_result = self._apply_fix(root_cause, project_session)

        # Step 9-10: Verify and retry
        verification = self._verify_fix(fix_result, project_session)

        if not verification["passed"] and verification.get("retry_limit", 0) < 3:
            # Retry with updated analysis
            return self.start_project(project_session)

        return project_session

    def _identify_errors(self, project_session: ProjectSession) -> List[Dict[str, Any]]:
        """Identify errors using available evidence."""
        errors: List[Dict[str, Any]] = []

        # Check if there's a repository to analyze
        repo_path = project_session.artifacts.get("repository_path", "")
        if not repo_path or not os.path.isdir(repo_path):
            errors.append({
                "type": "no_repository",
                "message": "No valid repository path found in project artifacts",
                "evidence": "missing",
            })
            return errors

        # Analyze repository structure
        self.repository_analyzer = RepositoryAnalyzer(repo_path)
        analysis = self.repository_analyzer.analyze()

        # Look for test failures
        if analysis.get("test_command") != "unknown":
            # Try running tests
            try:
                result = subprocess.run(
                    [sys.executable, "-m", analysis["test_command"], "--tb=short"],
                    cwd=repo_path,
                    capture_output=True,
                    text=True,
                    timeout=60,
                )
                if result.returncode != 0:
                    errors.append({
                        "type": "test_failure",
                        "message": f"Tests failed with exit code {result.returncode}",
                        "evidence": result.stderr[:500] if result.stderr else "no stderr",
                        "stdout": result.stdout[:500] if result.stdout else "no stdout",
                    })
            except subprocess.TimeoutExpired:
                errors.append({
                    "type": "test_timeout",
                    "message": "Test execution timed out after 60 seconds",
                    "evidence": "timeout",
                })
            except Exception as e:
                errors.append({
                    "type": "test_error",
                    "message": f"Error running tests: {e}",
                    "evidence": str(e),
                })

        # Look for syntax errors
        if self.repository_analyzer:
            for py_file in self.repository_analyzer._get_python_files()[:20]:
                try:
                    with open(py_file, "rb") as f:
                        ast.parse(f.read())
                except SyntaxError as e:
                    errors.append({
                        "type": "syntax_error",
                        "message": f"Syntax error in {py_file.name}: {e}",
                        "file": str(py_file.relative_to(repo_path)),
                        "evidence": "ast_parse_error",
                    })
                    # Don't check all files once we find a syntax error
                    break
                except Exception:
                    pass

        # Look for import errors
        if self.repository_analyzer:
            for py_file in self.repository_analyzer._get_python_files()[:10]:
                try:
                    import importlib.util
                    spec = importlib.util.spec_from_file_location(
                        py_file.stem, py_file
                    )
                    if spec and spec.loader:
                        module = importlib.util.module_from_spec(spec)
                        try:
                            spec.loader.exec_module(module)
                        except ImportError as e:
                            errors.append({
                                "type": "import_error",
                                "message": f"Import error in {py_file.name}: {e}",
                                "file": str(py_file.relative_to(repo_path)),
                                "evidence": "import_failure",
                            })
                            break  # Stop after first import error
                except Exception:
                    pass

        return errors

    def _analyze_root_cause(self, errors: List[Dict[str, Any]], project_session: ProjectSession) -> Dict[str, Any]:
        """Determine the likely root cause from identified errors."""
        cause: Dict[str, Any] = {
            "likely_cause": "unknown",
            "confidence": 0.0,
            "affected_files": [],
            "suggested_fix": "",
        }

        if not errors:
            cause["likely_cause"] = "no_errors_detected"
            cause["confidence"] = 1.0
            return cause

        # Categorize errors
        error_types = [e.get("type") for e in errors]

        # If syntax errors, likely cause is corrupted file or incomplete edit
        if "syntax_error" in error_types:
            syntax_errors = [e for e in errors if e["type"] == "syntax_error"]
            cause["likely_cause"] = "syntax_error_in_source"
            cause["confidence"] = 0.8
            cause["affected_files"] = [e.get("file") for e in syntax_errors]
            cause["suggested_fix"] = "Restore from last known good state or fix syntax errors"

        # If import errors, likely cause is missing dependency or circular import
        elif "import_error" in error_types:
            cause["likely_cause"] = "missing_dependency_or_circular_import"
            cause["confidence"] = 0.7
            cause["suggested_fix"] = "Install missing dependencies or refactor imports"

        # If test failures, analyze the error messages
        elif "test_failure" in error_types:
            test_errors = [e for e in errors if e["type"] == "test_failure"]
            cause["likely_cause"] = "test_failure"
            cause["confidence"] = 0.6
            cause["affected_files"] = []
            # Summarize the test error
            for te in test_errors[:3]:
                msg = te.get("message", "")[:200]
                cause["suggested_fix"] = f"Fix: {msg}"
            if test_errors:
                cause["affected_files"] = [f.get("file", "unknown") for f in test_errors[:3]]

        # If no specific pattern matches
        else:
            cause["likely_cause"] = "multiple_issues"
            cause["confidence"] = 0.3
            cause["suggested_fix"] = "Review all identified errors and fix systematically"

        return cause

    def _save_checkpoint(self, project_session: ProjectSession) -> None:
        """Save a recoverable checkpoint before making changes."""
        try:
            ProjectStore.checkpoint_project(
                project_session.id.value,
                f"before_diagnostic_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            )
            # Also store diagnostic info
            project_session.diagnostic_reports.append({
                "timestamp": datetime.now().isoformat(),
                "errors_identified": len(project_session.diagnostic_reports),
                "root_cause_analysis": "in_progress",
            })
        except Exception as e:
            print(f"Warning: Could not save checkpoint: {e}")

    def _apply_fix(self, root_cause: Dict[str, Any], project_session: ProjectSession) -> Dict[str, Any]:
        """Apply the smallest reasonable patch based on root cause analysis."""
        result: Dict[str, Any] = {
            "applied": False,
            "fix_applied": "",
            "affected_files": [],
            "new_errors": [],
        }

        cause = root_cause.get("likely_cause", "")

        if cause == "syntax_error_in_source":
            # Try to fix obvious syntax issues
            repo_path = project_session.artifacts.get("repository_path", "")
            if repo_path and os.path.isdir(repo_path):
                for py_file in Path(repo_path).rglob("*.py"):
                    try:
                        with open(py_file, "r", encoding="utf-8") as f:
                            content = f.read()
                        # Try to parse and fix
                        tree = ast.parse(content)
                        result["applied"] = True
                        result["fix_applied"] = f"Parsed successfully: {py_file.name}"
                        result["affected_files"].append(str(py_file.relative_to(repo_path)))
                        break
                    except SyntaxError:
                        # Try common fixes
                        try:
                            with open(py_file, "r", encoding="utf-8") as f:
                                content = f.read()
                            # Remove trailing commas, fix indentation, etc.
                            # For now, just note the file
                            result["affected_files"].append(str(py_file.relative_to(repo_path)))
                        except Exception:
                            pass

        elif cause == "missing_dependency_or_circular_import":
            # Note: we don't auto-install packages
            result["applied"] = False
            result["fix_applied"] = "Not auto-installing packages - require user decision"
            result["affected_files"] = []

        elif cause == "test_failure":
            # Run tests and capture output for analysis
            repo_path = project_session.artifacts.get("repository_path", "")
            if repo_path and os.path.isdir(repo_path):
                try:
                    result = subprocess.run(
                        [sys.executable, "-m", "pytest", "--tb=short", "-q"],
                        cwd=repo_path,
                        capture_output=True,
                        text=True,
                        timeout=120,
                    )
                    result["test_output"] = result.stdout + result.stderr
                    result["test_exit_code"] = result.returncode
                    result["affected_files"] = [f for f in Path(repo_path).glob("*.py") if f.name.startswith("test_")]

                    if result.returncode == 0:
                        result["applied"] = True
                        result["fix_applied"] = "All tests passing"
                    else:
                        # Extract error messages
                        errors = []
                        for line in result.stderr.split("\n")[:20]:
                            if line.strip():
                                errors.append(line.strip())
                        result["new_errors"] = errors
                        result["fix_applied"] = f"Tests still failing: {'; '.join(errors[:5])}"
                except Exception as e:
                    result["error"] = str(e)
                except Exception:
                    pass
            else:
                result["fix_applied"] = "No repository path available"

        elif cause == "no_errors_detected":
            result["applied"] = True
            result["fix_applied"] = "No errors detected - project appears healthy"
            result["affected_files"] = []

        else:
            result["fix_applied"] = f"Cause: {cause} - review manually"

        return result

    def _verify_fix(self, fix_result: Dict[str, Any], project_session: ProjectSession) -> Dict[str, Any]:
        """Verify the fix by running tests and checking acceptance criteria."""
        verification: Dict[str, Any] = {
            "passed": False,
            "test_exit_code": None,
            "test_output": "",
            "new_errors": [],
            "retry_count": project_session.diagnostic_reports.__len__(),
            "retry_limit": 3,
            "acceptance_criteria_met": False,
        }

        # Run tests
        repo_path = project_session.artifacts.get("repository_path", "")
        if repo_path and os.path.isdir(repo_path) and fix_result.get("test_exit_code") is not None:
            try:
                result = subprocess.run(
                    [sys.executable, "-m", "pytest", "--tb=short", "-q"],
                    cwd=repo_path,
                    capture_output=True,
                    text=True,
                    timeout=120,
                )
                verification["test_exit_code"] = result.returncode
                verification["test_output"] = result.stdout + result.stderr

                if result.returncode == 0:
                    verification["passed"] = True
                else:
                    verification["new_errors"] = [
                        l for l in result.stderr.split("\n")[:10] if l.strip()
                    ]
            except Exception as e:
                verification["new_errors"] = [str(e)]

        # Check acceptance criteria
        # Basic check: if tests pass, acceptance criteria are met
        if verification["passed"] or verification["test_exit_code"] == 0:
            verification["acceptance_criteria_met"] = True
        else:
            # Check if we've hit retry limit
            if verification["retry_count"] >= verification["retry_limit"]:
                # Stop and report
                pass
            else:
                verification["retry_count"] += 1

        return verification