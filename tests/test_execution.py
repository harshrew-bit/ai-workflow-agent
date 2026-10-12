"""Comprehensive tests for genuine tool execution and step resolution."""

from typing import Any, Dict, List
import pytest

from app.engine.base import GenericWorkflowEngine
from app.engine.context import ExecutionContext
from app.engine.resolver import ConfigurableStepResolver, StepBinding
from app.models.execution import ExecutionStatus
from app.models.workflow import WorkflowDefinition
from app.registry.registry import WorkflowRegistry
from app.tools.base import BaseTool, ToolMetadata
from app.tools.registry import ToolRegistry


# --- Deterministic Test Tools ---

class SpyTool(BaseTool):
    """Tool that records its execution calls and parameters."""

    def __init__(self, name: str = "spy_tool", return_multiplier: int = 10) -> None:
        self._name = name
        self.return_multiplier = return_multiplier
        self.call_count = 0
        self.last_kwargs: Dict[str, Any] = {}

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(name=self._name, description="Spy tool for recording calls")

    def execute(self, **kwargs: Any) -> Dict[str, Any]:
        self.call_count += 1
        self.last_kwargs = dict(kwargs)
        val = kwargs.get("val", 1)
        return {
            "processed": True,
            "received_val": val,
            "calculated": val * self.return_multiplier,
        }


class AdderTool(BaseTool):
    """Tool that adds two numbers."""

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(name="adder", description="Adds two numbers")

    def execute(self, a: int, b: int) -> int:
        return a + b


class MultiplierTool(BaseTool):
    """Tool that multiplies two numbers, with support for last_output."""

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(name="multiplier", description="Multiplies numbers")

    def execute(self, factor: int, last_output: int) -> int:
        return factor * last_output


class FailingTool(BaseTool):
    """Tool that always raises an exception."""

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(name="failing_tool", description="Intentionally fails")

    def execute(self, **kwargs: Any) -> Any:
        raise RuntimeError("Simulated failure in tool execution")


# --- Test Cases ---

def test_registered_test_tool_is_actually_invoked_and_receives_correct_inputs():
    """Requirement 1 & 2: Prove registered test tool is actually invoked with correct inputs."""
    tool_reg = ToolRegistry()
    spy = SpyTool(name="spy_tool")
    tool_reg.register(spy)

    resolver = ConfigurableStepResolver()
    resolver.bind(step_name="Execute spy action", tool_name="spy_tool")

    engine = GenericWorkflowEngine(tool_registry=tool_reg, step_resolver=resolver)

    wf = WorkflowDefinition(
        Workflow_ID="WF_TEST_01",
        Workflow_Name="Tool Invocation Test",
        Trigger="Test trigger",
        Inputs="val: int",
        Steps="Execute spy action",
        Decision_Logic="None",
        Tools_Required="spy_tool",
        Expected_Output="Processed result",
    )

    result = engine.execute(wf, val=7)

    # 1. Verify tool was actually invoked
    assert spy.call_count == 1

    # 2. Verify tool received exact validated inputs
    assert spy.last_kwargs.get("val") == 7

    # 3. Verify real return value appears in step and workflow result
    assert result.status == ExecutionStatus.COMPLETED
    expected_output = {"processed": True, "received_val": 7, "calculated": 70}
    assert result.step_results[0].output == expected_output
    assert result.output == expected_output


def test_real_return_value_in_step_and_workflow_result():
    """Requirement 3: Return value from tool appears in step and workflow result."""
    tool_reg = ToolRegistry()
    adder = AdderTool()
    tool_reg.register(adder)

    resolver = ConfigurableStepResolver()
    resolver.bind(step_name="Add numbers", tool_name="adder")

    engine = GenericWorkflowEngine(tool_registry=tool_reg, step_resolver=resolver)

    wf = WorkflowDefinition(
        Workflow_ID="WF_TEST_02",
        Workflow_Name="Calculation Test",
        Trigger="Calculate",
        Inputs="a, b",
        Steps="Add numbers",
        Decision_Logic="Sum values",
        Tools_Required="adder",
        Expected_Output="Sum of a and b",
    )

    result = engine.execute(wf, a=25, b=17)

    assert result.status == ExecutionStatus.COMPLETED
    assert result.step_results[0].status == ExecutionStatus.COMPLETED
    assert result.step_results[0].output == 42
    assert result.output == 42


def test_second_step_can_access_first_step_output():
    """Requirement 4: Verify step 2 consumes output of step 1 from context."""
    tool_reg = ToolRegistry()
    adder = AdderTool()
    multiplier = MultiplierTool()
    tool_reg.register(adder)
    tool_reg.register(multiplier)

    resolver = ConfigurableStepResolver()
    resolver.bind(step_name="Compute base sum", tool_name="adder")
    resolver.bind(step_name="Multiply sum", tool_name="multiplier")

    engine = GenericWorkflowEngine(tool_registry=tool_reg, step_resolver=resolver)

    wf = WorkflowDefinition(
        Workflow_ID="WF_TEST_03",
        Workflow_Name="Multi-Step Pipeline",
        Trigger="Run math pipeline",
        Inputs="a, b, factor",
        Steps="Compute base sum → Multiply sum",
        Decision_Logic="Step 2 requires step 1 output",
        Tools_Required="adder; multiplier",
        Expected_Output="Scaled sum",
    )

    # Initial inputs: a=4, b=6, factor=5
    # Step 1: adder(a=4, b=6) -> 10
    # Step 2: multiplier(factor=5, last_output=10) -> 50
    result = engine.execute(wf, a=4, b=6, factor=5)

    assert result.status == ExecutionStatus.COMPLETED
    assert len(result.step_results) == 2

    # Step 1 output
    assert result.step_results[0].status == ExecutionStatus.COMPLETED
    assert result.step_results[0].output == 10

    # Step 2 output (received step 1's 10 and factor 5)
    assert result.step_results[1].status == ExecutionStatus.COMPLETED
    assert result.step_results[1].output == 50

    # Overall workflow output
    assert result.output == 50


def test_explicit_input_mapping_with_context_variable_references():
    """Verify explicit input mapping resolving variables from context."""
    tool_reg = ToolRegistry()
    adder = AdderTool()
    tool_reg.register(adder)

    resolver = ConfigurableStepResolver()
    # Step 1: adder with inputs a=10, b=5 -> 15
    resolver.bind("Step One", "adder")
    # Step 2: adder where a is mapped to $step_1_output and b is fixed at 100
    resolver.bind(
        "Step Two",
        "adder",
        input_mapper={"a": "$step_1_output", "b": 100},
    )

    engine = GenericWorkflowEngine(tool_registry=tool_reg, step_resolver=resolver)

    wf = WorkflowDefinition(
        Workflow_ID="WF_TEST_MAP",
        Workflow_Name="Mapped Context Test",
        Trigger="Test mapping",
        Inputs="a, b",
        Steps="Step One → Step Two",
        Decision_Logic="Pass intermediate output",
        Tools_Required="adder",
        Expected_Output="Final mapped sum",
    )

    result = engine.execute(wf, a=10, b=5)

    assert result.status == ExecutionStatus.COMPLETED
    assert result.step_results[0].output == 15
    assert result.step_results[1].output == 115
    assert result.output == 115


def test_missing_tool_resolution_produces_accurate_failure():
    """Requirement 5a: Unresolved step produces clear failure and does not claim completion."""
    tool_reg = ToolRegistry()
    # No tools registered, no bindings
    engine = GenericWorkflowEngine(tool_registry=tool_reg)

    wf = WorkflowDefinition(
        Workflow_ID="WF_TEST_04",
        Workflow_Name="Unresolved Step Workflow",
        Trigger="Trigger",
        Inputs="None",
        Steps="Perform unknown magic action",
        Decision_Logic="Must fail",
        Tools_Required="Unknown tool",
        Expected_Output="None",
    )

    result = engine.execute(wf)

    assert result.status == ExecutionStatus.FAILED
    assert len(result.step_results) == 1
    assert result.step_results[0].status == ExecutionStatus.FAILED
    assert "could not be resolved" in result.step_results[0].error
    assert "could not be resolved" in result.error
    assert result.output is None


def test_missing_tool_in_registry_produces_accurate_failure():
    """Requirement 5b: Step binds to a tool that is not in ToolRegistry."""
    tool_reg = ToolRegistry()
    resolver = ConfigurableStepResolver()
    resolver.bind(step_name="Run missing tool", tool_name="ghost_tool")

    engine = GenericWorkflowEngine(tool_registry=tool_reg, step_resolver=resolver)

    wf = WorkflowDefinition(
        Workflow_ID="WF_TEST_05",
        Workflow_Name="Missing Tool Workflow",
        Trigger="Trigger",
        Inputs="None",
        Steps="Run missing tool",
        Decision_Logic="Must fail",
        Tools_Required="ghost_tool",
        Expected_Output="None",
    )

    result = engine.execute(wf)

    assert result.status == ExecutionStatus.FAILED
    assert result.step_results[0].status == ExecutionStatus.FAILED
    assert "not found in ToolRegistry" in result.step_results[0].error
    assert "ghost_tool" in result.step_results[0].error


def test_tool_exceptions_produce_accurate_failure_and_preserve_earlier_steps():
    """Requirement 6: Tool exception marks step and workflow as FAILED, preserving earlier successes."""
    tool_reg = ToolRegistry()
    adder = AdderTool()
    failing = FailingTool()
    tool_reg.register(adder)
    tool_reg.register(failing)

    resolver = ConfigurableStepResolver()
    resolver.bind(step_name="Good Step", tool_name="adder")
    resolver.bind(step_name="Bad Step", tool_name="failing_tool")

    engine = GenericWorkflowEngine(tool_registry=tool_reg, step_resolver=resolver)

    wf = WorkflowDefinition(
        Workflow_ID="WF_TEST_06",
        Workflow_Name="Faulty Workflow",
        Trigger="Trigger",
        Inputs="a, b",
        Steps="Good Step → Bad Step",
        Decision_Logic="Fail on step 2",
        Tools_Required="adder; failing_tool",
        Expected_Output="None",
    )

    result = engine.execute(wf, a=10, b=20)

    # Overall workflow must be FAILED
    assert result.status == ExecutionStatus.FAILED
    assert "Simulated failure in tool execution" in result.error

    # Exactly 2 steps recorded
    assert len(result.step_results) == 2

    # Step 1 succeeded and its output is preserved
    assert result.step_results[0].step_name == "Good Step"
    assert result.step_results[0].status == ExecutionStatus.COMPLETED
    assert result.step_results[0].output == 30

    # Step 2 failed with accurate error
    assert result.step_results[1].step_name == "Bad Step"
    assert result.step_results[1].status == ExecutionStatus.FAILED
    assert "Simulated failure in tool execution" in result.step_results[1].error


def test_newly_registered_workflow_executes_without_engine_code_changes():
    """Requirement 7: A new workflow (e.g. WF011) executes dynamically without altering engine code."""
    # Setup fresh registry
    registry = WorkflowRegistry()
    tool_reg = ToolRegistry()

    # Define brand new tool
    class RMAGeneratorTool(BaseTool):
        @property
        def metadata(self) -> ToolMetadata:
            return ToolMetadata(name="rma_generator", description="Generates return authorization")

        def execute(self, order_id: str, reason: str) -> Dict[str, str]:
            return {
                "rma_code": f"RMA-{order_id}-APPROVED",
                "reason": reason,
                "label_url": f"https://shipping.internal/labels/{order_id}.pdf",
            }

    tool_reg.register(RMAGeneratorTool())

    # Configure resolver mapping for new workflow
    resolver = ConfigurableStepResolver()
    resolver.bind(
        workflow_id="WF011",
        step_name="Generate RMA authorization",
        tool_name="rma_generator",
    )

    # Register workflow in registry
    wf011 = WorkflowDefinition(
        Workflow_ID="WF011",
        Workflow_Name="Customer Return Authorization",
        Trigger="Customer requests return authorization",
        Inputs="order_id; reason",
        Steps="Generate RMA authorization",
        Decision_Logic="If within return window, approve",
        Tools_Required="rma_generator",
        Expected_Output="RMA authorization code and label",
    )
    registry.register(wf011)

    # Execute on GenericWorkflowEngine WITHOUT any code modifications to engine
    engine = GenericWorkflowEngine(tool_registry=tool_reg, step_resolver=resolver)
    result = engine.execute(registry.get("WF011"), order_id="ORD-9988", reason="Wrong size")

    assert result.status == ExecutionStatus.COMPLETED
    assert result.workflow_id == "WF011"
    assert result.output["rma_code"] == "RMA-ORD-9988-APPROVED"
    assert result.output["reason"] == "Wrong size"


def test_empty_workflow_steps_handled_explicitly():
    """Requirement 8: Empty workflow steps return an explicit failed outcome rather than claiming success."""
    engine = GenericWorkflowEngine()

    # Create dummy workflow with no parsed steps
    class EmptyStepsWorkflow:
        workflow_id = "WF_EMPTY"
        workflow_name = "Empty Workflow"
        parsed_steps: List[str] = []
        expected_output = ""

    result = engine.execute(EmptyStepsWorkflow())  # type: ignore

    assert result.status == ExecutionStatus.FAILED
    assert "contains no executable steps" in result.error
    assert len(result.step_results) == 0
