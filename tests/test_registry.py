"""Tests for WorkflowRegistry and generic registration interface."""

from pathlib import Path
import pytest

from app.models.workflow import WorkflowDefinition
from app.registry.exceptions import DuplicateWorkflowIDError, WorkflowNotFoundError
from app.registry.registry import WorkflowRegistry


def test_registry_from_excel(assessment_workbook_path: Path):
    """Test loading and managing workflows via WorkflowRegistry.from_excel."""
    registry = WorkflowRegistry.from_excel(assessment_workbook_path)

    assert len(registry) == 10
    assert len(registry.list_all()) == 10
    assert len(registry.list_ids()) == 10

    # Test retrieval
    wf = registry.get("WF001")
    assert wf.workflow_id == "WF001"
    assert wf.workflow_name == "Inventory Restock Check"

    # Test membership
    assert "WF001" in registry
    assert registry.contains("WF010")
    assert not registry.contains("WF999")


def test_registry_get_nonexistent_workflow():
    """Verify registry raises WorkflowNotFoundError for unknown IDs."""
    registry = WorkflowRegistry()
    with pytest.raises(WorkflowNotFoundError) as exc_info:
        registry.get("WF999")

    assert "WF999" in str(exc_info.value)
    assert isinstance(exc_info.value, KeyError)


def test_preliminary_generic_registration_interface():
    """Test 7: Preliminary test of the generic registration interface.

    Demonstrates that a new workflow (e.g. WF011) can be defined and registered
    dynamically without any modifications to router branches or execution engine.
    """
    registry = WorkflowRegistry()

    # Define a new workflow programmatically
    wf011 = WorkflowDefinition(
        Workflow_ID="WF011",
        Workflow_Name="Customer Return Authorization",
        Trigger="Customer requests an RMA return authorization",
        Inputs="Order ID; return reason; product condition; photos",
        Steps="Validate order → check return window → inspect condition → generate RMA label",
        Decision_Logic="If return is within 30 days and item unused, approve return",
        Tools_Required="Order database; RMA generator; email notifier",
        Expected_Output="RMA authorization code, shipping label, and customer instructions",
    )

    # Register into the generic registry
    registry.register(wf011)

    assert len(registry) == 1
    assert "WF011" in registry
    retrieved = registry.get("WF011")
    assert retrieved.workflow_name == "Customer Return Authorization"
    assert retrieved.parsed_steps == [
        "Validate order",
        "check return window",
        "inspect condition",
        "generate RMA label",
    ]
    assert retrieved.parsed_tools == [
        "Order database",
        "RMA generator",
        "email notifier",
    ]

    # Attempting to re-register the same ID without overwrite should raise DuplicateWorkflowIDError
    with pytest.raises(DuplicateWorkflowIDError) as exc_info:
        registry.register(wf011)

    assert "WF011" in str(exc_info.value)

    # Register with allow_overwrite=True
    updated_wf011 = WorkflowDefinition(
        Workflow_ID="WF011",
        Workflow_Name="Customer Return Authorization (Updated)",
        Trigger="Customer requests an RMA return authorization",
        Inputs="Order ID; return reason",
        Steps="Validate order → generate RMA",
        Decision_Logic="If within 30 days, approve",
        Tools_Required="Order database",
        Expected_Output="RMA authorization code",
    )
    registry.register(updated_wf011, allow_overwrite=True)
    assert registry.get("WF011").workflow_name == "Customer Return Authorization (Updated)"
