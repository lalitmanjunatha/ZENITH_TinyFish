from __future__ import annotations
import json
from typing import Optional
from livekit.agents import function_tool
from Tools.mathematics.problem_parser import ProblemParser, ProblemClassifier
from Tools.mathematics.solver_router import SolverRouter
from Tools.mathematics.engines import ValidationEngine, ErrorDetector, ExplanationEngine, SensitivityEngine
from Tools.mathematics.mathematical_state import MathematicalState

TOOL = {
    "name": "mathematical_reasoner",
    "description": (
        "MATRIS Mathematical Intelligence subsystem. Solves equations, matrices, "
        "calculus, optimization, ODEs, statistics, and more. "
        "Use this for ANY mathematical problem the user asks about. "
        "Default action is solve_problem — just pass the problem text. "
        "Actions: solve_problem, model_problem, classify_problem, explain_step, "
        "verify_solution, diagnose_solution, what_if, sensitivity_analysis."
    ),
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "action": {
                "type": "STRING",
                "description": "solve_problem (default) | model_problem | classify_problem | explain_step | verify_solution | diagnose_solution | what_if | sensitivity_analysis"
            },
            "problem": {
                "type": "STRING",
                "description": "Mathematical problem text (e.g. 'Solve 2x + 5 = 17', 'matrix [[1,2],[3,4]]', 'integrate x^2 dx')"
            },
            "solution_text": {
                "type": "STRING",
                "description": "User/student solution text for error diagnosis"
            },
            "parameter_name": {
                "type": "STRING",
                "description": "Parameter name for what_if analysis"
            },
            "parameter_value": {
                "type": "STRING",
                "description": "New parameter value for what_if analysis"
            },
            "explanation_level": {
                "type": "STRING",
                "description": "beginner | standard | technical | rigorous | intuitive"
            }
        },
        "required": ["action"]
    },
    "handler": "handle_mathematical_reasoner"
}

_parser = ProblemParser()
_classifier = ProblemClassifier()
_router = SolverRouter()
_validator = ValidationEngine()
_detector = ErrorDetector()
_explainer = ExplanationEngine()
_sensitizer = SensitivityEngine()
_last_state: Optional[MathematicalState] = None


def handle_mathematical_reasoner(parameters: dict) -> str:
    global _last_state
    action = parameters.get("action", "").strip().lower() or "solve_problem"
    problem_text = parameters.get("problem", "").strip()
    sol_text = parameters.get("solution_text", "").strip()
    param_name = parameters.get("parameter_name", "").strip()
    param_val = parameters.get("parameter_value", "").strip()
    level = parameters.get("explanation_level", "standard").strip()

    if not action:
        action = "solve_problem"

    try:
        if action == "solve_problem":
            prob = problem_text or ("" if not _last_state else _last_state.problem)
            if not prob:
                return "MATRIS: Please provide a mathematical problem to solve."
            st = _parser.parse(prob)
            st = _router.solve(st)
            if st is None:
                st = _parser.parse(prob)
            _last_state = st
            ver = _validator.verify(st) if st else {"status": "ERROR", "reason": "Parser returned None"}
            explanation = _explainer.explain(st, level=level) if st else "Error: could not parse problem."
            return "\n".join([
                "MATRIS Solution [" + str(st.domain) + "]",
                "  Status        : " + str(ver.get("status", "COMPLETED")),
                "  Model Type    : " + str(st.model_type),
                "  Solution      : " + str(json.dumps(st.solution, default=str)),
                "  Interpretation: " + str(st.real_world_interpretation),
                "",
                explanation
            ])

        elif action == "model_problem":
            st = _parser.parse(problem_text or "Unknown problem")
            _last_state = st
            return "\n".join([
                "MATRIS Model Formulation:",
                "  Domain      : " + str(st.domain),
                "  Variables   : " + str(st.variables),
                "  Given Values: " + str(st.given_values),
                "  Constraints : " + str(st.constraints),
                "  Equations   : " + str(st.equations),
                "  Objective   : " + str(st.objective)
            ])

        elif action == "classify_problem":
            res = _classifier.classify(problem_text or "Unknown")
            subdomains = ", ".join(res["subdomains"])
            domain = res.get("primary_domain") or res.get("domain", "Unknown")
            return "\n".join([
                "MATRIS Problem Classification:",
                "  Primary Domain: " + str(domain),
                "  Subdomains    : " + subdomains,
                "  Model Type    : " + str(res["model_type"])
            ])

        elif action == "verify_solution":
            if not _last_state:
                _last_state = _parser.parse(problem_text or "d = v * t")
                _last_state = _router.solve(_last_state)
            ver = _validator.verify(_last_state)
            return "MATRIS Verification Status: " + str(ver.get("status"))

        elif action == "diagnose_solution":
            if not _last_state:
                _last_state = _parser.parse(problem_text or "2x + 5 = 17")
            res = _detector.diagnose(sol_text or problem_text, _last_state)
            return "\n".join([
                "MATRIS Error Diagnosis:",
                "  Correct     : " + str(res.get("is_correct")),
                "  Error Type  : " + str(res.get("error_type", "None")),
                "  Explanation : " + str(res.get("explanation")),
                "  Correction  : " + str(res.get("correct_step") or res.get("correction", ""))
            ])

        elif action in ["what_if", "sensitivity_analysis"]:
            if not _last_state:
                _last_state = _parser.parse(problem_text or "A vehicle travels at 60 km/h for 2.5 hours.")
                _last_state = _router.solve(_last_state)
            try:
                val: float | str = float(param_val) if param_val else 80.0
            except ValueError:
                val = param_val
            st_new = _sensitizer.what_if(_last_state, param_name or "speed", val)
            _last_state = st_new
            return "\n".join([
                "MATRIS What-If Analysis:",
                "  Changed       : " + str(param_name or "speed") + " to " + str(val),
                "  New Solution  : " + str(json.dumps(st_new.solution, default=str)),
                "  Interpretation: " + str(st_new.real_world_interpretation)
            ])

        elif action == "explain_step":
            if not _last_state:
                return "MATRIS: No active state. Run solve_problem first."
            return _explainer.explain(_last_state, level=level)

        else:
            if not _last_state:
                _last_state = _parser.parse(problem_text or "d = v * t")
                _last_state = _router.solve(_last_state)
            return "MATRIS Result [" + action + "]: " + str(json.dumps(_last_state.solution, default=str))

    except Exception as e:
        import traceback
        return "MATRIS Error: " + str(e) + "\nTraceback:\n" + traceback.format_exc()


# ============================================================================
# @function_tool wrapper — used by agent.py's LiveKit Agent registration
# ============================================================================
@function_tool()
async def mathematical_reasoner(
    action: str,
    problem: str = "",
    solution_text: str = "",
    parameter_name: str = "",
    parameter_value: str = "",
    explanation_level: str = "standard",
) -> str:
    """
    MATRIS Mathematical Intelligence subsystem. Formulates, solves, validates,
    and explains real-world mathematical problems across Optimization,
    Differential Equations, Calculus, Linear Algebra, Statistics, Physics,
    AI/ML, Finance, and Engineering.

    Args:
        action: solve_problem | model_problem | classify_problem | explain_step
                | verify_solution | diagnose_solution | what_if | sensitivity_analysis
        problem: Mathematical problem text (e.g. "A vehicle travels at 60 km/h for 2.5 hours.")
        solution_text: User/student solution text for error diagnosis
        parameter_name: Parameter name for what_if analysis (e.g. "speed")
        parameter_value: New parameter value for what_if analysis (e.g. "80")
        explanation_level: beginner | standard | technical | rigorous | intuitive

    Returns:
        str: Formatted MATRIS response with solution, derivation, and interpretation.
    """
    return handle_mathematical_reasoner({
        "action": action,
        "problem": problem,
        "solution_text": solution_text,
        "parameter_name": parameter_name,
        "parameter_value": parameter_value,
        "explanation_level": explanation_level,
    })
