from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
import json

@dataclass
class MathematicalState:
    problem: str = ''
    domain: str = 'General Mathematics'
    subdomains: List[str] = field(default_factory=list)
    given_values: Dict[str, Any] = field(default_factory=dict)
    variables: Dict[str, str] = field(default_factory=dict)
    constants: Dict[str, Any] = field(default_factory=dict)
    units: Dict[str, str] = field(default_factory=dict)
    assumptions: List[str] = field(default_factory=list)
    constraints: List[str] = field(default_factory=list)
    objective: str = ''
    equations: List[str] = field(default_factory=list)
    inequalities: List[str] = field(default_factory=list)
    model_type: str = 'algebraic'
    selected_method: str = 'symbolic'
    derivation_steps: List[Dict[str, str]] = field(default_factory=list)
    intermediate_results: Dict[str, Any] = field(default_factory=dict)
    solution: Dict[str, Any] = field(default_factory=dict)
    alternative_solutions: List[Any] = field(default_factory=list)
    validation: Dict[str, Any] = field(default_factory=dict)
    errors: List[Dict[str, str]] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    visualizations: List[Dict[str, Any]] = field(default_factory=list)
    real_world_interpretation: str = ''
    decision_insights: List[str] = field(default_factory=list)
    sensitivity_analysis: Dict[str, Any] = field(default_factory=dict)
    what_if_state: Dict[str, Any] = field(default_factory=dict)
    explanation_context: Dict[str, str] = field(default_factory=dict)
    confidence: float = 1.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            'problem': self.problem,
            'domain': self.domain,
            'subdomains': self.subdomains,
            'given_values': self.given_values,
            'variables': self.variables,
            'constants': self.constants,
            'units': self.units,
            'assumptions': self.assumptions,
            'constraints': self.constraints,
            'objective': self.objective,
            'equations': self.equations,
            'inequalities': self.inequalities,
            'model_type': self.model_type,
            'selected_method': self.selected_method,
            'derivation_steps': self.derivation_steps,
            'intermediate_results': self.intermediate_results,
            'solution': self.solution,
            'alternative_solutions': self.alternative_solutions,
            'validation': self.validation,
            'errors': self.errors,
            'warnings': self.warnings,
            'visualizations': self.visualizations,
            'real_world_interpretation': self.real_world_interpretation,
            'decision_insights': self.decision_insights,
            'sensitivity_analysis': self.sensitivity_analysis,
            'what_if_state': self.what_if_state,
            'explanation_context': self.explanation_context,
            'confidence': self.confidence
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2, default=str)
