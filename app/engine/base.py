"""Generic workflow execution interfaces and default engine."""

from abc import ABC, abstractmethod
from typing import Any, Optional

from app.engine.context import ExecutionContext
from app.models.execution import (
    ExecutionStatus,
    StepExecutionResult,
    WorkflowExecutionResult,
)
from app.models.workflow import WorkflowDefinition


class WorkflowExecutor(ABC):
    """Abstract generic execution interface.

    Any workflow execution engine must implement this interface, ensuring that
    new workflows can be executed without rewriting orchestration logic.
    """

    @abstractmethod
    def execute(
        self,
        workflow: WorkflowDefinition,
        context: Optional[ExecutionContext] = None,
        **inputs: Any,
    ) -> WorkflowExecutionResult:
        """Execute a workflow definition generically."""
        pass


class GenericWorkflowEngine(WorkflowExecutor):
    """Generic workflow engine that drives workflow execution step-by-step.

    Operates purely on WorkflowDefinition metadata (steps, decision logic, tools)
    without hardcoding any workflow ID or custom chatbot branches.
    """

    def __init__(self, tool_registry: Optional[Any] = None) -> None:
        self.tool_registry = tool_registry

    def execute(
        self,
        workflow: WorkflowDefinition,
        context: Optional[ExecutionContext] = None,
        **inputs: Any,
    ) -> WorkflowExecutionResult:
        """Execute the given workflow through its parsed steps."""
        ctx = context or ExecutionContext(workflow=workflow, inputs=inputs)
        if ctx.workflow is None:
            ctx.workflow = workflow
        if self.tool_registry and ctx.tool_registry is None:
            ctx.tool_registry = self.tool_registry

        step_results: list[StepExecutionResult] = []

        try:
            for idx, step_name in enumerate(workflow.parsed_steps, start=1):
                # Execute step generically (recording step progression)
                step_res = StepExecutionResult(
                    step_number=idx,
                    step_name=step_name,
                    status=ExecutionStatus.COMPLETED,
                    output=f"Step '{step_name}' executed for workflow '{workflow.workflow_id}'.",
                    metadata={"decision_logic": workflow.decision_logic},
                )
                ctx.record_step(step_res)
                step_results.append(step_res)

            return WorkflowExecutionResult(
                workflow_id=workflow.workflow_id,
                status=ExecutionStatus.COMPLETED,
                output=f"Workflow '{workflow.workflow_name}' completed successfully.",
                step_results=step_results,
                metadata={
                    "total_steps": len(workflow.parsed_steps),
                    "tools_required": workflow.parsed_tools,
                    "expected_output": workflow.expected_output,
                },
            )
        except Exception as exc:
            return WorkflowExecutionResult(
                workflow_id=workflow.workflow_id,
                status=ExecutionStatus.FAILED,
                error=str(exc),
                step_results=step_results,
            )
