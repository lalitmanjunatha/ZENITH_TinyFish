import os
from typing import Dict, Any, Optional
from .mathematical_state import MathematicalState

class MathematicalModelAdapter:
    def __init__(self, backend: Optional[str] = None):
        self.backend = backend or os.environ.get('MATRIS_BACKEND', 'mock')
        self.model_path = os.environ.get('MATRIS_MODEL_PATH', '')
        self.endpoint = os.environ.get('MATRIS_MODEL_ENDPOINT', '')

    def analyze_problem(self, problem: str) -> Dict[str, Any]:
        return {
            'backend': self.backend,
            'status': 'analyzed',
            'summary': f'Analyzed formulation for: {problem[:60]}...'
        }

    def classify_problem(self, problem: str) -> Dict[str, Any]:
        prob_lower = problem.lower()
        domains = []
        if any(w in prob_lower for w in ['d/dt', 'dy/dx', 'growth', 'decay', 'rate', 'cooling', 'epidemic', 'population']):
            domains.append('Differential Equations')
        if any(w in prob_lower for w in ['maximize', 'minimize', 'profit', 'cost', 'resource', 'constraint', 'capacity', 'optimum']):
            domains.append('Optimization')
        if any(w in prob_lower for w in ['matrix', 'vector', 'eigenvalue', 'determinant', 'linear system']):
            domains.append('Linear Algebra')
        if any(w in prob_lower for w in ['probability', 'mean', 'variance', 'distribution', 'bayes', 'data']):
            domains.append('Probability & Statistics')
        if any(w in prob_lower for w in ['integral', 'derivative', 'limit', 'calculus']):
            domains.append('Calculus')

        if not domains:
            domains.append('Algebra & General Mathematics')

        return {
            'primary_domain': domains[0],
            'subdomains': domains,
            'confidence': 0.92
        }

    def formulate_model(self, state: MathematicalState) -> MathematicalState:
        prob = state.problem.lower()

        # Don't override if parser already classified as Calculus
        if state.model_type == "calculus":
            return state

        if 'maximize' in prob or 'minimize' in prob or 'profit' in prob or 'cost' in prob:
            state.domain = 'Optimization'
            state.model_type = 'linear_programming'
        elif ('rate' in prob or 'dy/dx' in prob or 'decay' in prob or 'growth' in prob) \
                and 'integra' not in prob and 'deriv' not in prob and 'calculus' not in prob:
            state.domain = 'Differential Equations'
            state.model_type = 'ordinary_differential_equation'
        elif 'matrix' in prob or 'vector' in prob or 'system' in prob:
            state.domain = 'Linear Algebra'
            state.model_type = 'matrix_equation'
        return state

    def reason(self, state: MathematicalState) -> MathematicalState:
        state.explanation_context['reasoning_summary'] = f'Selected solver strategy for domain {state.domain} using model type {state.model_type}'
        return state

    def explain(self, state: MathematicalState, target: Optional[str] = None) -> str:
        return f'MATRIS Explanation ({state.domain}): {state.real_world_interpretation}'

    def diagnose(self, user_solution: str, state: MathematicalState) -> Dict[str, Any]:
        return {
            'is_correct': False,
            'first_error_step': 1,
            'explanation': 'Transformation error in step 1.',
            'correction': 'Apply balanced subtraction on both sides of the equation.'
        }
