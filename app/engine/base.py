"""Generic workflow execution interfaces and genuine execution engine."""

from abc import ABC, abstractmethod
import inspect
from typing import Any, Dict, Optional

from app.engine.context import ExecutionContext
from app.engine.resolver import ConfigurableStepResolver, StepResolver
from app.models.execution import (
    ExecutionStatus,
    StepExecutionResult,
    WorkflowExecutionResult,
)
from app.models.workflow import WorkflowDefinition
from app.tools.base import BaseTool
from app.tools.registry import ToolRegistry


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


def _prepare_tool_kwargs(
    tool: BaseTool,
    candidate_kwargs: Dict[str, Any],
    ctx: ExecutionContext,
) -> Dict[str, Any]:
    """Prepare keyword arguments matching the tool's execute() parameter signature.

    Passes arguments from candidate variables (inputs, prior step outputs, context).
    If the tool accepts **kwargs, passes all candidate arguments.
    Otherwise, filters only parameters defined in the tool's signature.
    """
    sig = inspect.signature(tool.execute)
    has_var_keyword = any(
        param.kind == inspect.Parameter.VAR_KEYWORD
        for param in sig.parameters.values()
    )

    if has_var_keyword:
        call_kwargs = dict(candidate_kwargs)
        if "context" in sig.parameters:
            call_kwargs["context"] = ctx
        return call_kwargs

    call_kwargs: Dict[str, Any] = {}
    for param_name in sig.parameters.keys():
        if param_name == "self":
            continue
        if param_name in candidate_kwargs:
            call_kwargs[param_name] = candidate_kwargs[param_name]
        elif param_name == "context":
            call_kwargs["context"] = ctx
        elif param_name in ctx.inputs:
            call_kwargs[param_name] = ctx.inputs[param_name]
        elif param_name in ctx.variables:
            call_kwargs[param_name] = ctx.variables[param_name]
    return call_kwargs


class GenericWorkflowEngine(WorkflowExecutor):
    """Generic workflow engine that drives genuine workflow tool execution step-by-step.

    Operates purely on WorkflowDefinition metadata (steps, decision logic, tools)
    and resolves each step via an extensible StepResolver, invoking real BaseTool instances
    from ToolRegistry. Never marks a step COMPLETED without successful tool execution.
    """

    def __init__(
        self,
        tool_registry: Optional[ToolRegistry] = None,
        step_resolver: Optional[StepResolver] = None,
    ) -> None:
        self.tool_registry = (
            tool_registry if tool_registry is not None else ToolRegistry()
        )
        self.step_resolver = (
            step_resolver if step_resolver is not None else ConfigurableStepResolver()
        )

    def execute(
        self,
        workflow: WorkflowDefinition,
        context: Optional[ExecutionContext] = None,
        **inputs: Any,
    ) -> WorkflowExecutionResult:
        """Execute the given workflow through its parsed steps using registered tools.

        Fails explicitly if steps cannot be resolved, tools are missing, or a tool raises an error.
        Preserves all completed prior step outputs if a later step fails.
        """
        # Validate that workflow has executable steps
        if not workflow.parsed_steps:
            return WorkflowExecutionResult(
                workflow_id=workflow.workflow_id,
                status=ExecutionStatus.FAILED,
                error=f"Workflow '{workflow.workflow_id}' contains no executable steps.",
                step_results=[],
            )

        ctx = context or ExecutionContext(workflow=workflow, inputs=inputs)
        if ctx.workflow is None:
            ctx.workflow = workflow
        for k, v in inputs.items():
            ctx.inputs[k] = v

        active_tool_registry = (
            ctx.tool_registry
            if getattr(ctx, "tool_registry", None) is not None
            else self.tool_registry
        )

        step_results: list[StepExecutionResult] = []

        for idx, step_name in enumerate(workflow.parsed_steps, start=1):
            # 1. Resolve step to an executable StepBinding
            binding = self.step_resolver.resolve(
                step_name=step_name,
                workflow=workflow,
                context=ctx,
                tool_registry=active_tool_registry,
            )

            if binding is None:
                step_res = StepExecutionResult(
                    step_number=idx,
                    step_name=step_name,
                    status=ExecutionStatus.FAILED,
                    output=None,
                    error=(
                        f"Step '{step_name}' could not be resolved to any registered tool in ToolRegistry. "
                        "Please register a matching tool or configure a step binding."
                    ),
                    metadata={"decision_logic": workflow.decision_logic},
                )
                ctx.record_step(step_res)
                step_results.append(step_res)
                return WorkflowExecutionResult(
                    workflow_id=workflow.workflow_id,
                    status=ExecutionStatus.FAILED,
                    error=step_res.error,
                    step_results=step_results,
                )

            # 2. Retrieve tool from registry
            tool = active_tool_registry.get(binding.tool_name)
            if tool is None:
                step_res = StepExecutionResult(
                    step_number=idx,
                    step_name=step_name,
                    status=ExecutionStatus.FAILED,
                    output=None,
                    error=(
                        f"Required tool '{binding.tool_name}' for step '{step_name}' was not found in ToolRegistry."
                    ),
                    metadata={
                        "tool_name": binding.tool_name,
                        "decision_logic": workflow.decision_logic,
                    },
                )
                ctx.record_step(step_res)
                step_results.append(step_res)
                return WorkflowExecutionResult(
                    workflow_id=workflow.workflow_id,
                    status=ExecutionStatus.FAILED,
                    error=step_res.error,
                    step_results=step_results,
                )

            # 3. Prepare inputs using context and bindings
            candidate_kwargs = ctx.get_all()
            if "last_output" in ctx.variables:
                candidate_kwargs["last_output"] = ctx.variables["last_output"]
            prev_step_key = f"step_{idx - 1}_output"
            if prev_step_key in ctx.variables:
                candidate_kwargs[prev_step_key] = ctx.variables[prev_step_key]

            if binding.input_mapper is not None:
                if callable(binding.input_mapper):
                    call_kwargs = binding.input_mapper(ctx)
                elif isinstance(binding.input_mapper, dict):
                    call_kwargs = {}
                    for param_name, src in binding.input_mapper.items():
                        if isinstance(src, str) and src.startswith("$"):
                            var_name = src[1:]
                            call_kwargs[param_name] = ctx.get(var_name)
                        else:
                            call_kwargs[param_name] = src
                else:
                    call_kwargs = _prepare_tool_kwargs(tool, candidate_kwargs, ctx)
            else:
                call_kwargs = _prepare_tool_kwargs(tool, candidate_kwargs, ctx)

            # 4. Invoke tool.execute()
            try:
                actual_output = tool.execute(**call_kwargs)
            except Exception as exc:
                step_res = StepExecutionResult(
                    step_number=idx,
                    step_name=step_name,
                    status=ExecutionStatus.FAILED,
                    output=None,
                    error=f"Tool '{tool.name}' raised an exception: {exc}",
                    metadata={
                        "tool_name": tool.name,
                        "inputs_passed": {
                            k: str(v) for k, v in call_kwargs.items() if k != "context"
                        },
                        "decision_logic": workflow.decision_logic,
                    },
                )
                ctx.record_step(step_res)
                step_results.append(step_res)
                return WorkflowExecutionResult(
                    workflow_id=workflow.workflow_id,
                    status=ExecutionStatus.FAILED,
                    error=step_res.error,
                    step_results=step_results,
                )

            # 5. Tool completed successfully - update context
            ctx.set("last_output", actual_output)
            ctx.set(f"step_{idx}_output", actual_output)
            ctx.set(step_name, actual_output)
            if binding.output_key:
                ctx.set(binding.output_key, actual_output)
            if isinstance(actual_output, dict):
                for k, v in actual_output.items():
                    ctx.set(k, v)

            step_res = StepExecutionResult(
                step_number=idx,
                step_name=step_name,
                status=ExecutionStatus.COMPLETED,
                output=actual_output,
                metadata={
                    "tool_name": tool.name,
                    "inputs_passed": {
                        k: str(v) for k, v in call_kwargs.items() if k != "context"
                    },
                    "decision_logic": workflow.decision_logic,
                },
            )
            ctx.record_step(step_res)
            step_results.append(step_res)

        # Entire workflow finished successfully
        final_output = ctx.get("last_output")
        return WorkflowExecutionResult(
            workflow_id=workflow.workflow_id,
            status=ExecutionStatus.COMPLETED,
            output=final_output,
            step_results=step_results,
            metadata={
                "total_steps": len(workflow.parsed_steps),
                "tools_executed": [
                    r.metadata.get("tool_name") for r in step_results if r.metadata
                ],
                "expected_output": workflow.expected_output,
            },
        )
