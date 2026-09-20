"""
problem_parser.py — MATRIS Problem Parser

Extracts equations, variables, and domain from free-form text using SymPy
and regex heuristics. Handles algebraic equations, matrix operations,
inequalities, integrals, derivatives, and more.
"""
from __future__ import annotations

import re
from typing import Dict, Any, List, Tuple, Optional

from .mathematical_state import MathematicalState


class ProblemParser:
    """Parse free-text math problems into MathematicalState."""

    def parse(self, text: str) -> MathematicalState:
        state = MathematicalState(problem=text)
        text_lower = text.lower().strip()

        # ── Matrix input from canvas ─────────────────────────────────────
        if text_lower.startswith("matrix"):
            return self._parse_matrix_input(text, state)

        # ── Extract numbers and units ────────────────────────────────────
        self._extract_numbers(text, state)

        # ── Detect domain ────────────────────────────────────────────────
        domain = self._detect_domain(text_lower)
        state.domain = domain["domain"]
        state.subdomains = domain["subdomains"]
        state.model_type = domain["model_type"]

        # ── Extract equations ────────────────────────────────────────────
        equations = self._extract_equations(text)
        if equations:
            state.equations = equations

        # ── Extract variables ────────────────────────────────────────────
        variables = self._extract_variables(text)
        state.variables.update(variables)

        # ── Set objective from imperative verbs ──────────────────────────
        state.objective = self._extract_objective(text_lower)

        return state

    def _parse_matrix_input(self, text: str, state: MathematicalState) -> MathematicalState:
        """Parse 'matrix 3x3: [[1,2,3],[4,5,6],[7,8,9]]. find eigenvalues' style input."""
        state.domain = "Linear Algebra"
        state.subdomains = ["Linear Algebra", "Matrix Operations"]
        state.model_type = "matrix"

        # Extract dimensions
        dim_match = re.search(r'(\d+)\s*x\s*(\d+)', text)
        if dim_match:
            rows, cols = int(dim_match.group(1)), int(dim_match.group(2))
            state.variables["matrix_size"] = f"{rows}x{cols}"

        # Extract the list literal
        list_match = re.search(r'\[.*\]', text, re.DOTALL)
        if list_match:
            try:
                import ast
                matrix = ast.literal_eval(list_match.group())
                state.equations = [f"matrix = {matrix}"]
                state.given_values["matrix"] = matrix
                if isinstance(matrix, list) and matrix:
                    if isinstance(matrix[0], list):
                        state.variables["rows"] = str(len(matrix))
                        state.variables["cols"] = str(len(matrix[0]))
            except Exception:
                state.equations = [f"matrix = {list_match.group()}"]

        # Extract description — text after the matrix brackets
        desc = text
        if list_match:
            desc = text[list_match.end():].strip().lstrip(".").strip()
        if desc:
            state.given_values["description"] = desc
            state.objective = desc
        else:
            state.objective = "perform matrix operation"
        return state

    def _detect_domain(self, text: str) -> Dict[str, Any]:
        """Heuristic domain detection from keywords."""

        # Optimization / LP
        if any(w in text for w in ["profit", "product", "labor", "labour",
                                    "material", "maximize", "minimize",
                                    "produce", "resource"]):
            return {
                "domain": "Optimization",
                "subdomains": ["Optimization", "Linear Programming"],
                "model_type": "linear_programming",
            }

        # Calculus (check BEFORE differential equations — "integrate" contains "rate")
        if any(w in text for w in ["integral", "integrate", "integ",
                                    "derivative", "differentiate", "diff",
                                    "limit", "sum", "taylor", "series",
                                    "d/dx", "d/dt"]):
            return {
                "domain": "Calculus",
                "subdomains": ["Calculus", "Analysis"],
                "model_type": "calculus",
            }

        # Differential equations
        if any(w in text for w in ["rate", "growth", "decay", "cooling",
                                    "epidemic", "sir model", "differential"]):
            return {
                "domain": "Differential Equations",
                "subdomains": ["Differential Equations", "Calculus"],
                "model_type": "ordinary_differential_equation",
            }

        # ML / Data
        if any(w in text for w in ["regression", "gradient descent", "fit",
                                    "train", "dataset", "neural"]):
            return {
                "domain": "AI and Machine Learning",
                "subdomains": ["AI and Machine Learning", "Optimization"],
                "model_type": "data_driven",
            }

        # Linear Algebra / Matrix
        if any(w in text for w in ["matrix", "determinant", "eigenvalue",
                                    "eigenvector", "inverse", "transpose",
                                    "linear system", "system of equations"]):
            return {
                "domain": "Linear Algebra",
                "subdomains": ["Linear Algebra", "Matrix Operations"],
                "model_type": "matrix",
            }

        # Statistics
        if any(w in text for w in ["probability", "mean", "variance",
                                    "std", "distribution", "hypothesis",
                                    "bayes", "statistics"]):
            return {
                "domain": "Statistics",
                "subdomains": ["Statistics", "Probability"],
                "model_type": "statistical",
            }

        # Kinematics
        if any(w in text for w in ["speed", "velocity", "distance",
                                    "acceleration", "time", "travel",
                                    "journey", "trip"]):
            if self._has_speed_time(text):
                return {
                    "domain": "Kinematics & Physics",
                    "subdomains": ["Physics", "Algebra"],
                    "model_type": "algebraic",
                }

        # Default: algebraic (SymPy will try to solve)
        return {
            "domain": "General Mathematics",
            "subdomains": ["Algebra"],
            "model_type": "algebraic",
        }

    def _has_speed_time(self, text: str) -> bool:
        """Check if text contains speed and time values."""
        speed_pattern = r'\d+\.?\d*\s*(?:km/h|m/s|mph|kmh)'
        time_pattern = r'\d+\.?\d*\s*(?:h|hr|hours?|sec|seconds?|min|minutes?)'
        return bool(re.search(speed_pattern, text, re.I)) and bool(
            re.search(time_pattern, text, re.I))

    def _extract_equations(self, text: str) -> List[str]:
        """Extract mathematical equations from text."""
        equations = []

        # First: split on "and" or comma to get individual equation segments
        # but only if there are multiple = signs
        if text.count("=") > 1:
            parts = re.split(r'\s+and\s+|,\s*(?=[a-zA-Z0-9\+\-\*])', text)
            for part in parts:
                part = part.strip().strip(".,")
                # Remove natural language prefixes
                part = re.sub(r'^(solve|find|calculate|compute|determine)\s+', '', part, flags=re.I)
                eq_match = re.search(
                    r'([a-zA-Z0-9\+\-\*/\^\(\)\s\.]+)\s*=\s*([a-zA-Z0-9\+\-\*/\^\(\)\s\.]+)',
                    part
                )
                if eq_match:
                    lhs = eq_match.group(1).strip()
                    rhs = eq_match.group(2).strip()
                    equations.append(f"{lhs} = {rhs}")
            if equations:
                return equations

        # Single equation pattern
        eq_pattern = r'([a-zA-Z0-9\+\-\*/\^\(\)\s\.]+)\s*=\s*([a-zA-Z0-9\+\-\*/\^\(\)\s\.]+)'
        for m in re.finditer(eq_pattern, text):
            lhs = m.group(1).strip()
            rhs = m.group(2).strip()
            if any(c in lhs for c in '+-*/^') or any(c in rhs for c in '+-*/^'):
                equations.append(f"{lhs} = {rhs}")
            elif re.match(r'^[a-zA-Z]\s*$', lhs) and re.search(r'\d', rhs):
                equations.append(f"{lhs} = {rhs}")

        # Pattern: expressions with == or ===
        eq_pattern2 = r'([^\s]+)\s*={2,}\s*([^\s]+)'
        for m in re.finditer(eq_pattern2, text):
            equations.append(f"{m.group(1)} = {m.group(2)}")

        # Pattern: "solve X" where X contains equation-like content
        solve_match = re.search(r'solve\s+(.+)', text, re.I)
        if solve_match:
            inner = solve_match.group(1).strip()
            if '=' in inner:
                equations.insert(0, inner)
            elif re.search(r'[a-zA-Z]\s*[\+\-\*/\^]', inner):
                equations.insert(0, inner + " = 0")

        # Pattern: "integrate/derivative X"
        calc_match = re.search(r'(?:integrate|integral|derivative|differentiate)\s+(.+)', text, re.I)
        if calc_match:
            equations.insert(0, calc_match.group(1).strip())

        return equations

    def _extract_variables(self, text: str) -> Dict[str, str]:
        """Extract variable names from text."""
        variables = {}

        # Find single-letter variables (a-z, A-Z) that appear with operators
        var_pattern = r'\b([a-zA-Z])\b\s*[\+\-\*/\^=]'
        for m in re.finditer(var_pattern, text):
            var = m.group(1)
            if len(var) == 1 and var.isalpha():
                variables[var] = f"variable_{var}"

        # Common named variables
        named = {
            "speed": "v", "velocity": "v", "time": "t",
            "distance": "d", "acceleration": "a", "mass": "m",
            "force": "F", "energy": "E", "power": "P",
            "temperature": "T", "width": "w", "height": "h",
            "radius": "r", "length": "l", "price": "p",
        }
        text_lower = text.lower()
        for name, sym in named.items():
            if name in text_lower:
                variables[sym] = name

        return variables

    def _extract_objective(self, text: str) -> str:
        """Extract the objective from imperative verbs."""
        for verb, obj in [
            ("solve", "solve the equation"),
            ("find", "find the value"),
            ("calculate", "calculate the result"),
            ("compute", "compute the result"),
            ("determine", "determine the value"),
            ("evaluate", "evaluate the expression"),
            ("simplify", "simplify the expression"),
            ("factor", "factor the expression"),
            ("expand", "expand the expression"),
            ("integrate", "compute the integral"),
            ("integrate", "compute the integral"),
            ("differentiate", "compute the derivative"),
            ("derivative", "compute the derivative"),
            ("maximize", "maximize the function"),
            ("minimize", "minimize the function"),
            ("optimize", "optimize the function"),
            ("matrix", "perform matrix operation"),
            ("multiply", "perform multiplication"),
            ("add", "perform addition"),
            ("subtract", "perform subtraction"),
        ]:
            if verb in text:
                return obj
        return "solve the problem"

    def _extract_numbers(self, text: str, state: MathematicalState) -> None:
        """Extract numeric values with units."""
        matches = re.findall(r'(\d+(?:\.\d+)?)\s*([a-zA-Z/%]+)?', text)
        for val_str, unit_str in matches:
            if not val_str:
                continue
            val = float(val_str) if '.' in val_str else int(val_str)
            if unit_str:
                state.units[str(val)] = unit_str
                u = unit_str.lower()
                if u in ['km/h', 'm/s', 'mph', 'kmh']:
                    state.given_values['speed'] = val
                elif u in ['h', 'hr', 'hours', 'sec', 'seconds', 'min']:
                    state.given_values['time'] = val
                elif u in ['kg', 'g', 'lbs']:
                    state.given_values['mass'] = val
                elif u in ['m', 'km', 'miles']:
                    state.given_values['distance'] = val
            else:
                state.given_values[f'num_{val}'] = val


class ProblemClassifier:
    """Classify a problem into domains."""

    def __init__(self):
        self._parser = ProblemParser()

    def classify(self, text: str) -> Dict[str, Any]:
        state = self._parser.parse(text)
        return {
            "domain": state.domain,
            "subdomains": state.subdomains,
            "model_type": state.model_type,
            "primary_domain": state.domain,
        }
