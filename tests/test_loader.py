"""Tests for Excel workflow and evaluation request loader."""

from pathlib import Path
import pytest

from app.registry.exceptions import (
    DuplicateWorkflowIDError,
    InvalidWorkbookError,
    MissingColumnError,
    MissingSheetError,
    WorkbookNotFoundError,
    WorkflowValidationError,
)
from app.registry.loader import (
    TEST_QUESTION_REQUIRED_COLUMNS,
    WORKFLOW_REQUIRED_COLUMNS,
    load_evaluation_requests_from_excel,
    load_workbook_bundle,
    load_workflows_from_excel,
)


def test_load_all_ten_workflows_from_official_workbook(assessment_workbook_path: Path):
    """Test 1: Verify successful loading and integrity of all ten workflows from the assessment workbook."""
    workflows = load_workflows_from_excel(assessment_workbook_path)

    assert len(workflows) == 10

    expected_ids = [f"WF{i:03d}" for i in range(1, 11)]
    loaded_ids = [wf.workflow_id for wf in workflows]
    assert loaded_ids == expected_ids

    # Verify each workflow preserves its required fields
    for wf in workflows:
        assert wf.workflow_id.startswith("WF")
        assert len(wf.workflow_name) > 0
        assert len(wf.trigger) > 0
        assert len(wf.inputs) > 0
        assert len(wf.steps) > 0
        assert len(wf.decision_logic) > 0
        assert len(wf.tools_required) > 0
        assert len(wf.expected_output) > 0
        # Verify helper properties
        assert len(wf.parsed_steps) > 0
        assert len(wf.parsed_tools) > 0

    # Specifically check WF001 values
    wf001 = workflows[0]
    assert wf001.workflow_id == "WF001"
    assert wf001.workflow_name == "Inventory Restock Check"
    assert "restocking" in wf001.trigger.lower()
    assert "If current_stock < minimum_stock" in wf001.decision_logic
    assert "calculator" in wf001.tools_required


def test_load_all_ten_evaluation_requests(assessment_workbook_path: Path):
    """Test 2: Verify successful loading of all ten evaluation requests from Test_Questions."""
    eval_requests = load_evaluation_requests_from_excel(assessment_workbook_path)

    assert len(eval_requests) == 10

    expected_ids = [f"WF{i:03d}" for i in range(1, 11)]
    loaded_ids = [req.workflow_id for req in eval_requests]
    assert loaded_ids == expected_ids

    for req in eval_requests:
        assert req.workflow_id.startswith("WF")
        assert len(req.test_request) > 0
        assert len(req.what_to_check) > 0

    req001 = eval_requests[0]
    assert req001.workflow_id == "WF001"
    assert "restocking" in req001.test_request.lower()


def test_load_workbook_bundle(assessment_workbook_path: Path):
    """Verify loading both workflows and evaluation requests in a single call."""
    workflows, eval_requests = load_workbook_bundle(assessment_workbook_path)
    assert len(workflows) == 10
    assert len(eval_requests) == 10


def test_duplicate_workflow_id_detection(make_excel_file):
    """Test 3: Verify detection of duplicate workflow IDs with clear error message."""
    row1 = [
        "WF001", "Inventory Check", "Trigger 1", "Inputs 1",
        "Step 1 -> Step 2", "Logic 1", "Tool 1", "Output 1",
    ]
    # Duplicate WF001 in another row
    row2 = [
        "WF001", "Different Name", "Trigger 2", "Inputs 2",
        "Step A -> Step B", "Logic 2", "Tool 2", "Output 2",
    ]

    temp_path = make_excel_file({
        "Workflows": [WORKFLOW_REQUIRED_COLUMNS, row1, row2],
    })

    with pytest.raises(DuplicateWorkflowIDError) as exc_info:
        load_workflows_from_excel(temp_path)

    assert "WF001" in str(exc_info.value)
    assert "duplicate" in str(exc_info.value).lower()


def test_missing_required_column_detection(make_excel_file):
    """Test 4: Verify detection of missing required columns."""
    # Omit 'Decision_Logic' from headers
    bad_headers = [
        "Workflow_ID", "Workflow_Name", "Trigger", "Inputs",
        "Steps", "Tools_Required", "Expected_Output",
    ]
    temp_path = make_excel_file({
        "Workflows": [bad_headers],
    })

    with pytest.raises(MissingColumnError) as exc_info:
        load_workflows_from_excel(temp_path)

    assert "Decision_Logic" in str(exc_info.value)

    # Test missing column in Test_Questions sheet
    bad_tq_headers = ["Workflow_ID", "What_To_Check"]  # Missing 'Test_Request'
    temp_path_tq = make_excel_file({
        "Test_Questions": [bad_tq_headers],
    })

    with pytest.raises(MissingColumnError) as exc_info_tq:
        load_evaluation_requests_from_excel(temp_path_tq)

    assert "Test_Request" in str(exc_info_tq.value)


def test_missing_workflow_id_detection(make_excel_file):
    """Test 5: Verify detection of rows missing a workflow ID."""
    empty_id_row = [
        "", "No ID Workflow", "Trigger", "Inputs",
        "Step 1 -> Step 2", "Logic", "Tools", "Output",
    ]
    temp_path = make_excel_file({
        "Workflows": [WORKFLOW_REQUIRED_COLUMNS, empty_id_row],
    })

    with pytest.raises(WorkflowValidationError) as exc_info:
        load_workflows_from_excel(temp_path)

    assert "Workflow_ID" in str(exc_info.value)

    # In Test_Questions sheet:
    empty_tq_row = ["", "Some request", "Check something"]
    temp_path_tq = make_excel_file({
        "Test_Questions": [TEST_QUESTION_REQUIRED_COLUMNS, empty_tq_row],
    })

    with pytest.raises(WorkflowValidationError) as exc_info_tq:
        load_evaluation_requests_from_excel(temp_path_tq)

    assert "Workflow_ID" in str(exc_info_tq.value)


def test_missing_workbook_file_handling(tmp_path: Path):
    """Test 6a: Clear handling of a non-existent workbook file."""
    non_existent = tmp_path / "does_not_exist.xlsx"

    with pytest.raises(WorkbookNotFoundError) as exc_info:
        load_workflows_from_excel(non_existent)

    assert "not found" in str(exc_info.value).lower()
    # Confirm it is also a FileNotFoundError
    assert isinstance(exc_info.value, FileNotFoundError)


def test_corrupted_or_invalid_workbook_handling(tmp_path: Path):
    """Test 6b: Clear handling of a corrupted or unreadable workbook file."""
    corrupt_file = tmp_path / "corrupt.xlsx"
    corrupt_file.write_text("This is not a valid zip / Excel file!")

    with pytest.raises(InvalidWorkbookError) as exc_info:
        load_workflows_from_excel(corrupt_file)

    assert "Failed to read Excel workbook" in str(exc_info.value)


def test_missing_sheet_handling(make_excel_file):
    """Test 6c: Clear handling when a required sheet is missing."""
    temp_path = make_excel_file({
        "SomeOtherSheet": [["A", "B"]],
    })

    with pytest.raises(MissingSheetError) as exc_info:
        load_workflows_from_excel(temp_path)

    assert "Workflows" in str(exc_info.value)


def test_empty_rows_are_skipped(make_excel_file):
    """Ensure that completely blank rows do not cause validation failures."""
    valid_row = [
        "WF001", "Inventory Check", "Trigger", "Inputs",
        "Step 1 -> Step 2", "Logic", "Tools", "Output",
    ]
    blank_row = [None, None, None, None, None, None, None, None]
    whitespace_row = ["   ", "", None, "  ", None, None, None, None]

    temp_path = make_excel_file({
        "Workflows": [WORKFLOW_REQUIRED_COLUMNS, blank_row, valid_row, whitespace_row],
    })

    workflows = load_workflows_from_excel(temp_path)
    assert len(workflows) == 1
    assert workflows[0].workflow_id == "WF001"
