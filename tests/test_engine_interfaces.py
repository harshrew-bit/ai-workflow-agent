"""Tests for execution engine, context, and tool registry interfaces."""

import pytest

from app.engine.base import GenericWorkflowEngine
from app.engine.context import ExecutionContext
from app.models.execution import ExecutionStatus
from app.models.workflow import WorkflowDefinition
from app.tools.base import BaseTool, ToolMetadata
from app.tools.registry import ToolRegistry


class DummyCalculatorTool(BaseTool):
    """Dummy calculator tool for interface testing."""

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="calculator",
            description="Performs numeric arithmetic calculations",
        )

    def execute(self, a: int, b: int) -> int:
        return a + b


def test_execution_context_state_management():
    """Verify execution context correctly stores and retrieves variables."""
    ctx = ExecutionContext()
    ctx.set("threshold", 10)
    ctx.inputs["catalog"] = "products.csv"

    assert ctx.get("threshold") == 10
    assert ctx.get("catalog") == "products.csv"
    assert ctx.get("unknown", "default") == "default"


def test_tool_registry():
    """Verify tool registration and lookup."""
    registry = ToolRegistry()
    calc = DummyCalculatorTool()

    registry.register(calc)
    assert len(registry) == 1
    assert registry.has_tool("calculator")
    assert registry.get("CALCULATOR") is calc

    # Duplicate registration without overwrite should fail
    with pytest.raises(ValueError):
        registry.register(calc)


def test_generic_engine_executes_without_hardcoded_workflow_ids():
    """Verify that GenericWorkflowEngine executes any workflow definition dynamically."""
    engine = GenericWorkflowEngine()

    # Generic arbitrary workflow (could be WF001, WF010, or an arbitrary future WF999)
    custom_wf = WorkflowDefinition(
        Workflow_ID="WF999",
        Workflow_Name="Automated Sanity Verification",
        Trigger="System startup check",
        Inputs="System configuration",
        Steps="Read configuration → Ping services → Report health",
        Decision_Logic="All services must respond with 200 OK",
        Tools_Required="HTTP client; health analyzer",
        Expected_Output="Status report",
    )

    result = engine.execute(custom_wf)

    assert result.status == ExecutionStatus.COMPLETED
    assert result.workflow_id == "WF999"
    assert len(result.step_results) == 3
    assert result.step_results[0].step_name == "Read configuration"
    assert result.step_results[1].step_name == "Ping services"
    assert result.step_results[2].step_name == "Report health"
