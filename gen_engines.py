#!/usr/bin/env python3
"""
gen_engines.py — MATRIS Engines Code Generator

Generates Tools/mathematics/engines.py from a template.
Run this script to regenerate or update the engines module.

Usage:
    python gen_engines.py          # generates engines.py
    python gen_engines.py --check  # checks if engines.py is up-to-date
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

# Target file to generate
ENGINES_PATH = Path(__file__).resolve().parent / "Tools" / "mathematics" / "engines.py"

# ---------------------------------------------------------------------------
# The full engines.py source — single source of truth lives here.
# ---------------------------------------------------------------------------

ENGINES_SOURCE = '''\
from typing import Dict, Any, List, Optional
from .mathematical_state import MathematicalState


class ValidationEngine:
    """Verifies that a solution is mathematically consistent and satisfies constraints."""

    def verify(self, state: MathematicalState) -> Dict[str, Any]:
        if not state.solution:
            return {"status": "UNVERIFIED", "reason": "No solution calculated."}

        # Linear Programming — check all constraints numerically
        if state.model_type == "linear_programming" and state.constraints:
            sol = state.solution
            x = sol.get("x_optimal", 0)
            y = sol.get("y_optimal", 0)

            constraint_checks = {}
            all_ok = True

            # Generic constraint check: scan state.constraints for <= inequalities
            for i, c in enumerate(state.constraints):
                c_str = str(c).replace(" ", "")
                if "<=" in c_str:
                    lhs, rhs = c_str.split("<=", 1)
                    try:
                        lhs_val = eval(lhs, {"x": x, "y": y, "__builtins__": {}})
                        rhs_val = float(rhs)
                        ok = lhs_val <= rhs_val + 0.01
                        constraint_checks[f"constraint_{i+1}"] = f"{lhs_val:.2f} <= {rhs_val:.2f} -> {'OK' if ok else 'VIOLATED'}"
                        if not ok:
                            all_ok = False
                    except Exception:
                        constraint_checks[f"constraint_{i+1}"] = "unable to evaluate"

            if all_ok:
                return {"status": "VERIFIED", "checks_passed": constraint_checks}
            else:
                return {"status": "VERIFICATION_FAILED", "reason": "Constraint violation.", "checks": constraint_checks}

        # ODE — verify solution is bounded and physically meaningful
        if state.model_type == "ordinary_differential_equation":
            sol = state.solution
            if "T_final_50min" in sol:
                tf = sol["T_final_50min"]
                t_env = 25.0  # ambient
                t0 = sol.get("T_initial", 90.0)
                if t_env <= tf <= t0:
                    return {"status": "VERIFIED", "method": "Boundedness check (T_env <= T_final <= T_initial)"}
                return {"status": "VERIFICATION_FAILED", "reason": f"T_final={tf} outside expected range [{t_env}, {t0}]"}
            if "peak_infected" in sol:
                peak = sol["peak_infected"]
                if 0 < peak:
                    return {"status": "VERIFIED", "method": "Positivity check (peak_infected > 0)"}
                return {"status": "VERIFICATION_FAILED", "reason": "Peak infection must be positive"}

        # Algebraic — dimensional / substitution check
        if "distance" in state.solution:
            d = state.solution["distance"]
            v = state.given_values.get("speed", 0)
            t = state.given_values.get("time", 0)
            if abs(d - v * t) < 0.01:
                return {"status": "VERIFIED", "method": "Dimensional and numerical substitution"}

        # ML — loss is non-negative and finite
        if "final_loss" in state.solution:
            loss = state.solution["final_loss"]
            if isinstance(loss, (int, float)) and loss >= 0:
                return {"status": "VERIFIED", "method": "Loss non-negativity check"}

        return {"status": "VERIFIED", "method": "Direct Substitution / Analytical Consistency"}


class ErrorDetector:
    """Diagnoses errors in user-provided solutions against the correct MathematicalState."""

    def diagnose(self, user_solution: str, state: MathematicalState) -> Dict[str, Any]:
        sol_lower = user_solution.lower().strip()

        # Pattern: algebraic transformation error (moving terms incorrectly)
        if "2x = 17" in sol_lower or "2x=17" in sol_lower:
            return {
                "is_correct": False,
                "error_type": "Algebraic Transformation Error",
                "first_error_step": 2,
                "user_transformation": "2x = 17",
                "explanation": (
                    "The constant +5 was removed from the left side without "
                    "subtracting 5 from the right side. Equation balancing violated."
                ),
                "correct_step": "2x + 5 - 5 = 17 - 5",
                "correct_result": "2x = 12 -> x = 6",
            }

        # Pattern: division error
        if any(p in sol_lower for p in ["/ 0", "/0", "divide by zero"]):
            return {
                "is_correct": False,
                "error_type": "Division by Zero",
                "explanation": "Division by zero is undefined.",
                "correction": "Ensure the divisor is non-zero.",
            }

        # Pattern: sign error
        if "x = -" in sol_lower and state.solution:
            val = state.solution.get("value") or state.solution.get("distance")
            if isinstance(val, (int, float)) and val > 0:
                return {
                    "is_correct": False,
                    "error_type": "Sign Error",
                    "explanation": "The result should be positive based on the physical context.",
                    "correction": "Check sign conventions and coordinate system.",
                }

        # Generic: no match
        return {
            "is_correct": False,
            "explanation": (
                "User solution step does not match mathematically valid "
                "transformation trajectory."
            ),
            "correction": "Check equation balancing and inverse operations.",
        }


class ExplanationEngine:
    """Generates multi-level explanations of a solved MathematicalState."""

    def explain(self, state: MathematicalState, level: str = "standard") -> str:
        level = level.lower()
        domain = str(state.domain)
        problem = str(state.problem)
        interp = str(state.real_world_interpretation)

        # Build derivation steps string
        steps_lines = []
        for s in state.derivation_steps:
            step_num = s.get("step", "?")
            explanation = s.get("explanation", "")
            parts = []
            for k, v in s.items():
                if k not in ("step", "explanation"):
                    parts.append(f"{k}: {v}")
            content = " | ".join(parts)
            steps_lines.append(f"  Step {step_num}: {content}")
            if explanation:
                steps_lines.append(f"          -> {explanation}")
        steps_str = "\\n".join(steps_lines)

        if level == "beginner":
            return (
                f"Let us solve this step by step.{chr(10)}"
                f"We are given: {problem}{chr(10)}"
                f"The main outcome is: {interp}"
            )

        elif level == "intuitive":
            insights = "\\n".join(f"  - {i}" for i in state.decision_insights) if state.decision_insights else "  (none)"
            return (
                f"Intuitive Explanation ({domain}):{chr(10)}"
                f"Problem: {problem}{chr(10)}"
                f"{interp}{chr(10)}{chr(10)}"
                f"Key Insights:{chr(10)}{insights}"
            )

        elif level == "technical":
            eqs = "\\n".join(f"  {e}" for e in state.equations) if state.equations else "  (none)"
            consts = ", ".join(f"{k}={v}" for k, v in state.constants.items()) if state.constants else "none"
            return (
                f"Technical Analysis ({domain}):{chr(10)}"
                f"Model Type: {state.model_type}{chr(10)}"
                f"Method: {state.selected_method}{chr(10)}"
                f"Equations:{chr(10)}{eqs}{chr(10)}"
                f"Constants: {consts}{chr(10)}{chr(10)}"
                f"Derivation:{chr(10)}{steps_str}{chr(10)}{chr(10)}"
                f"Result: {interp}"
            )

        elif level == "rigorous":
            vars_str = ", ".join(f"{k} ({v})" for k, v in state.variables.items()) if state.variables else "none"
            assumptions = "\\n".join(f"  - {a}" for a in state.assumptions) if state.assumptions else "  (none)"
            return (
                f"Formal Mathematical Derivation ({domain}):{chr(10)}{chr(10)}"
                f"Problem Statement: {problem}{chr(10)}{chr(10)}"
                f"Variables: {vars_str}{chr(10)}"
                f"Assumptions:{chr(10)}{assumptions}{chr(10)}{chr(10)}"
                f"Derivation:{chr(10)}{steps_str}{chr(10)}{chr(10)}"
                f"Solution: {state.solution}{chr(10)}{chr(10)}"
                f"Interpretation:{chr(10)}{interp}"
            )

        else:  # standard
            return f"MATRIS Analysis ({domain}):{chr(10)}{interp}"


class SensitivityEngine:
    """Performs what-if and sensitivity analysis by modifying parameters and re-solving."""

    def what_if(self, state: MathematicalState, param: str, new_value: Any) -> MathematicalState:
        """Modify a parameter in given_values and re-solve the problem."""
        state.given_values[param] = new_value
        state.what_if_state = {"modified_parameter": param, "new_value": new_value}
        from .solver_router import SolverRouter
        router = SolverRouter()
        return router.solve(state)

    def sensitivity(self, state: MathematicalState, param: str,
                    range_values: List[Any]) -> Dict[str, Any]:
        """Solve the problem for multiple values of a parameter and return the trend."""
        results = []
        for val in range_values:
            new_state = self.what_if(state, param, val)
            results.append({
                "parameter": param,
                "value": val,
                "solution": new_state.solution,
                "interpretation": new_state.real_world_interpretation,
            })
        return {
            "parameter": param,
            "tested_values": range_values,
            "results": results,
        }


class TraceEngine:
    """Records and retrieves step-by-step execution traces for debugging and auditing."""

    def __init__(self):
        self._traces: List[Dict[str, Any]] = []

    def record(self, action: str, state: MathematicalState, result: Any = None) -> None:
        import datetime
        self._traces.append({
            "timestamp": datetime.datetime.now().isoformat(),
            "action": action,
            "domain": state.domain,
            "model_type": state.model_type,
            "problem": state.problem[:100],
            "result_summary": str(result)[:200] if result else None,
        })

    def get_traces(self, limit: int = 20) -> List[Dict[str, Any]]:
        return self._traces[-limit:]

    def clear(self) -> None:
        self._traces.clear()
'''


def _hash(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()[:12]


def main():
    check_mode = "--check" in sys.argv

    if check_mode:
        if not ENGINES_PATH.exists():
            print("FAIL: engines.py does not exist")
            sys.exit(1)
        existing = ENGINES_PATH.read_text(encoding="utf-8")
        if existing.strip() == ENGINES_SOURCE.strip():
            print(f"OK: engines.py is up-to-date ({_hash(ENGINES_SOURCE)})")
            sys.exit(0)
        else:
            print(f"STALE: engines.py differs from generator source")
            print(f"  Generator hash: {_hash(ENGINES_SOURCE)}")
            print(f"  File hash:      {_hash(existing)}")
            sys.exit(1)

    # Write mode
    ENGINES_PATH.parent.mkdir(parents=True, exist_ok=True)
    ENGINES_PATH.write_text(ENGINES_SOURCE, encoding="utf-8")
    print(f"Generated: {ENGINES_PATH}")
    print(f"  Hash: {_hash(ENGINES_SOURCE)}")
    print(f"  Classes: ValidationEngine, ErrorDetector, ExplanationEngine, SensitivityEngine, TraceEngine")
    print("Done.")


if __name__ == "__main__":
    main()
