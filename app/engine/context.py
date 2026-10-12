"""Execution context for workflow executions."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from app.models.execution import StepExecutionResult
from app.models.workflow import WorkflowDefinition


@dataclass
class ExecutionContext:
    """Carries runtime state, inputs, variables, and step history during execution.

    Designed to be generic across all workflows without hardcoded properties.
    """

    workflow: Optional[WorkflowDefinition] = None
    inputs: Dict[str, Any] = field(default_factory=dict)
    variables: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    step_results: List[StepExecutionResult] = field(default_factory=list)
    tool_registry: Optional[Any] = None

    def set(self, key: str, value: Any) -> None:
        """Store an intermediate or output variable in the context."""
        self.variables[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        """Retrieve a variable from variables, inputs, or metadata."""
        if key in self.variables:
            return self.variables[key]
        if key in self.inputs:
            return self.inputs[key]
        return self.metadata.get(key, default)

    def get_all(self) -> Dict[str, Any]:
        """Return all merged inputs and variables."""
        merged = dict(self.inputs)
        merged.update(self.variables)
        return merged

    def record_step(self, step_result: StepExecutionResult) -> None:
        """Record the outcome of a step execution."""
        self.step_results.append(step_result)
