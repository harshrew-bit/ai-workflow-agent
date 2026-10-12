"""Step-to-tool resolution interfaces and configuration."""

from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, Optional, Sequence, Union
from pydantic import BaseModel, Field

from app.engine.context import ExecutionContext
from app.models.workflow import WorkflowDefinition
from app.tools.registry import ToolRegistry


class StepResolutionError(Exception):
    """Base exception for step resolution failures."""

    pass


class UnresolvedStepError(StepResolutionError):
    """Raised when a workflow step cannot be mapped to any registered tool."""

    pass


class StepBinding(BaseModel):
    """Explicit binding configuration connecting a workflow step to an executable tool."""

    model_config = {"arbitrary_types_allowed": True}

    tool_name: str = Field(..., min_length=1, description="Name of the registered tool")
    step_name: Optional[str] = Field(default=None, description="Step name or pattern to bind")
    workflow_id: Optional[str] = Field(default=None, description="Optional workflow ID scope")
    input_mapper: Optional[
        Union[Callable[[ExecutionContext], Dict[str, Any]], Dict[str, Any]]
    ] = Field(default=None, description="Callable or dict mapping context variables to tool inputs")
    output_key: Optional[str] = Field(
        default=None, description="Context variable name to store the tool output in"
    )


class StepResolver(ABC):
    """Abstract interface for resolving human-readable workflow steps to executable tools."""

    @abstractmethod
    def resolve(
        self,
        step_name: str,
        workflow: WorkflowDefinition,
        context: ExecutionContext,
        tool_registry: ToolRegistry,
    ) -> Optional[StepBinding]:
        """Resolve a workflow step to an executable StepBinding, or None if unresolvable."""
        pass


class ConfigurableStepResolver(StepResolver):
    """Extensible step-to-tool resolver.

    Provides a clean, generic mechanism to map human-readable workflow steps
    to concrete tools without embedding workflow-specific code inside the engine.

    Resolution order:
    1. Workflow-scoped explicit binding (workflow_id + step_name)
    2. Global explicit binding (step_name)
    3. Direct tool name match (tool_registry has a tool with the step_name)
    4. Registered tool name match (normalized case-insensitive match against registered tools)
    """

    def __init__(self) -> None:
        self._workflow_bindings: Dict[tuple[str, str], StepBinding] = {}
        self._global_bindings: Dict[str, StepBinding] = {}

    def bind(
        self,
        step_name: str,
        tool_name: str,
        workflow_id: Optional[str] = None,
        input_mapper: Optional[
            Union[Callable[[ExecutionContext], Dict[str, Any]], Dict[str, Any]]
        ] = None,
        output_key: Optional[str] = None,
    ) -> "ConfigurableStepResolver":
        """Register an explicit binding between a step name and a tool."""
        binding = StepBinding(
            tool_name=tool_name,
            step_name=step_name,
            workflow_id=workflow_id,
            input_mapper=input_mapper,
            output_key=output_key,
        )
        return self.register_binding(binding)

    def register_binding(self, binding: StepBinding) -> "ConfigurableStepResolver":
        """Register a StepBinding instance."""
        norm_step = (binding.step_name or "").strip().lower()
        if binding.workflow_id:
            self._workflow_bindings[(binding.workflow_id, norm_step)] = binding
        else:
            self._global_bindings[norm_step] = binding
        return self

    def resolve(
        self,
        step_name: str,
        workflow: WorkflowDefinition,
        context: ExecutionContext,
        tool_registry: ToolRegistry,
    ) -> Optional[StepBinding]:
        """Resolve a step using workflow-scoped bindings, global bindings, or direct tool match."""
        norm_step = step_name.strip().lower()

        # 1. Workflow-specific explicit binding
        wf_key = (workflow.workflow_id, norm_step)
        if wf_key in self._workflow_bindings:
            return self._workflow_bindings[wf_key]

        # 2. Global explicit binding
        if norm_step in self._global_bindings:
            return self._global_bindings[norm_step]

        # 3. Direct match: if tool_registry has a tool named exactly like this step
        if tool_registry.has_tool(norm_step):
            tool = tool_registry.get(norm_step)
            return StepBinding(
                step_name=step_name,
                tool_name=tool.name if tool else step_name,
            )

        # 4. Registered tools case-insensitive match
        for reg_tool in tool_registry.list_tools():
            if reg_tool.name.strip().lower() == norm_step:
                return StepBinding(
                    step_name=step_name,
                    tool_name=reg_tool.name,
                )

        return None
