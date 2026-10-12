"""Unit tests for Pydantic data models."""

import pytest
from pydantic import ValidationError

from app.models.evaluation import EvaluationRequest
from app.models.execution import (
    ExecutionStatus,
    StepExecutionResult,
    WorkflowExecutionResult,
)
from app.models.workflow import WorkflowDefinition


def test_workflow_definition_valid():
    """Verify valid workflow creation and property aliases."""
    wf = WorkflowDefinition(
        Workflow_ID="WF001",
        Workflow_Name="Inventory Restock Check",
        Trigger="User asks which products need restocking",
        Inputs="Product inventory CSV; minimum stock threshold",
        Steps="Load inventory → compare stock → generate restock list",
        Decision_Logic="If current_stock < minimum_stock, mark product",
        Tools_Required="CSV reader; calculator",
        Expected_Output="List of products requiring restock",
    )

    assert wf.id == "WF001"
    assert wf.name == "Inventory Restock Check"
    assert wf.parsed_steps == ["Load inventory", "compare stock", "generate restock list"]
    assert wf.parsed_tools == ["CSV reader", "calculator"]
    assert wf.parsed_inputs == ["Product inventory CSV", "minimum stock threshold"]


def test_workflow_definition_empty_fields_rejected():
    """Verify empty or whitespace-only fields are rejected by validation."""
    with pytest.raises(ValidationError):
        WorkflowDefinition(
            Workflow_ID="WF001",
            Workflow_Name="",
            Trigger="Valid trigger",
            Inputs="Valid inputs",
            Steps="Valid steps",
            Decision_Logic="Valid logic",
            Tools_Required="Valid tools",
            Expected_Output="Valid output",
        )


def test_evaluation_request_valid():
    """Verify evaluation request creation and property aliases."""
    req = EvaluationRequest(
        Workflow_ID="WF001",
        Test_Request="Which products need restocking?",
        What_To_Check="Tests workflow selection and threshold logic",
    )

    assert req.id == "WF001"
    assert req.request == "Which products need restocking?"
    assert req.what_to_check == "Tests workflow selection and threshold logic"


def test_evaluation_request_empty_fields_rejected():
    """Verify empty strings in evaluation request are rejected."""
    with pytest.raises(ValidationError):
        EvaluationRequest(
            Workflow_ID="WF001",
            Test_Request="   ",
            What_To_Check="Tests something",
        )


def test_execution_models():
    """Verify execution result model contracts."""
    step = StepExecutionResult(
        step_number=1,
        step_name="Load inventory",
        status=ExecutionStatus.COMPLETED,
        output="Loaded 42 rows",
    )
    assert step.status == ExecutionStatus.COMPLETED

    wf_result = WorkflowExecutionResult(
        workflow_id="WF001",
        status=ExecutionStatus.COMPLETED,
        output="All done",
        step_results=[step],
    )
    assert wf_result.workflow_id == "WF001"
    assert len(wf_result.step_results) == 1
