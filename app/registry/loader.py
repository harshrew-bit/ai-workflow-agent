"""Excel workbook loader for workflows and evaluation requests."""

from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple, Union
import openpyxl

from app.models.evaluation import EvaluationRequest
from app.models.workflow import WorkflowDefinition
from app.registry.exceptions import (
    DuplicateWorkflowIDError,
    InvalidWorkbookError,
    MissingColumnError,
    MissingSheetError,
    WorkbookNotFoundError,
    WorkflowValidationError,
)

WORKFLOWS_SHEET_NAME = "Workflows"
TEST_QUESTIONS_SHEET_NAME = "Test_Questions"

WORKFLOW_REQUIRED_COLUMNS: Sequence[str] = (
    "Workflow_ID",
    "Workflow_Name",
    "Trigger",
    "Inputs",
    "Steps",
    "Decision_Logic",
    "Tools_Required",
    "Expected_Output",
)

TEST_QUESTION_REQUIRED_COLUMNS: Sequence[str] = (
    "Workflow_ID",
    "Test_Request",
    "What_To_Check",
)


def _open_workbook(filepath: Union[str, Path]) -> openpyxl.Workbook:
    """Safely open an Excel workbook with validation and clear error handling."""
    path = Path(filepath)
    if not path.is_file():
        raise WorkbookNotFoundError(
            f"Workbook not found at '{path.resolve()}'. Please verify the file path exists."
        )

    try:
        return openpyxl.load_workbook(str(path), data_only=True, read_only=True)
    except Exception as exc:
        raise InvalidWorkbookError(
            f"Failed to read Excel workbook at '{path.resolve()}': {exc}"
        ) from exc


def _extract_sheet_rows(
    wb: openpyxl.Workbook,
    sheet_name: str,
    required_columns: Sequence[str],
) -> Tuple[List[str], Dict[str, int], List[Sequence[Any]]]:
    """Validate sheet presence and headers, returning header metadata and data rows."""
    if sheet_name not in wb.sheetnames:
        raise MissingSheetError(
            f"Required sheet '{sheet_name}' was not found in workbook. "
            f"Available sheets: {list(wb.sheetnames)}."
        )

    sheet = wb[sheet_name]
    rows = list(sheet.iter_rows(values_only=True))
    if not rows:
        raise InvalidWorkbookError(f"Sheet '{sheet_name}' is empty.")

    raw_headers = rows[0]
    if not raw_headers or not any(raw_headers):
        raise MissingColumnError(
            f"Sheet '{sheet_name}' has no column headers in row 1."
        )

    headers = [str(h).strip() if h is not None else "" for h in raw_headers]
    missing_columns = [col for col in required_columns if col not in headers]
    if missing_columns:
        found_columns = [h for h in headers if h]
        raise MissingColumnError(
            f"Sheet '{sheet_name}' is missing required column(s): {missing_columns}. "
            f"Found columns: {found_columns}."
        )

    col_indices = {col: headers.index(col) for col in required_columns}
    data_rows = rows[1:]
    return headers, col_indices, data_rows


def _is_empty_row(row: Sequence[Any]) -> bool:
    """Return True if row has no cells or only contains None and whitespace."""
    if not row:
        return True
    return not any(
        cell is not None and str(cell).strip() != ""
        for cell in row
    )


def load_workflows_from_excel(filepath: Union[str, Path]) -> List[WorkflowDefinition]:
    """Load and validate all workflow definitions from the Workflows sheet.

    Validates schema, detects duplicate workflow IDs, ensures non-empty IDs,
    and preserves all workflow definition fields dynamically.
    """
    wb = _open_workbook(filepath)
    try:
        _, col_indices, data_rows = _extract_sheet_rows(
            wb, WORKFLOWS_SHEET_NAME, WORKFLOW_REQUIRED_COLUMNS
        )

        workflows: List[WorkflowDefinition] = []
        seen_ids: set[str] = set()

        for row_idx, row in enumerate(data_rows, start=2):
            if _is_empty_row(row):
                continue

            row_data: Dict[str, Any] = {}
            for col_name, col_idx in col_indices.items():
                val = row[col_idx] if col_idx < len(row) else None
                row_data[col_name] = str(val).strip() if val is not None else ""

            workflow_id = row_data.get("Workflow_ID", "")
            if not workflow_id:
                raise WorkflowValidationError(
                    f"Row {row_idx} in sheet '{WORKFLOWS_SHEET_NAME}' has an empty or missing 'Workflow_ID'."
                )

            if workflow_id in seen_ids:
                raise DuplicateWorkflowIDError(
                    f"Duplicate Workflow_ID '{workflow_id}' detected at row {row_idx} in sheet '{WORKFLOWS_SHEET_NAME}'."
                )
            seen_ids.add(workflow_id)

            try:
                workflow = WorkflowDefinition.model_validate(row_data)
                workflows.append(workflow)
            except Exception as exc:
                raise WorkflowValidationError(
                    f"Validation failed for row {row_idx} in sheet '{WORKFLOWS_SHEET_NAME}' "
                    f"(Workflow_ID='{workflow_id}'): {exc}"
                ) from exc

        return workflows
    finally:
        wb.close()


def load_evaluation_requests_from_excel(
    filepath: Union[str, Path],
) -> List[EvaluationRequest]:
    """Load and validate all evaluation requests from the Test_Questions sheet."""
    wb = _open_workbook(filepath)
    try:
        _, col_indices, data_rows = _extract_sheet_rows(
            wb, TEST_QUESTIONS_SHEET_NAME, TEST_QUESTION_REQUIRED_COLUMNS
        )

        eval_requests: List[EvaluationRequest] = []

        for row_idx, row in enumerate(data_rows, start=2):
            if _is_empty_row(row):
                continue

            row_data: Dict[str, Any] = {}
            for col_name, col_idx in col_indices.items():
                val = row[col_idx] if col_idx < len(row) else None
                row_data[col_name] = str(val).strip() if val is not None else ""

            workflow_id = row_data.get("Workflow_ID", "")
            if not workflow_id:
                raise WorkflowValidationError(
                    f"Row {row_idx} in sheet '{TEST_QUESTIONS_SHEET_NAME}' has an empty or missing 'Workflow_ID'."
                )

            try:
                eval_request = EvaluationRequest.model_validate(row_data)
                eval_requests.append(eval_request)
            except Exception as exc:
                raise WorkflowValidationError(
                    f"Validation failed for row {row_idx} in sheet '{TEST_QUESTIONS_SHEET_NAME}' "
                    f"(Workflow_ID='{workflow_id}'): {exc}"
                ) from exc

        return eval_requests
    finally:
        wb.close()


def load_workbook_bundle(
    filepath: Union[str, Path],
) -> Tuple[List[WorkflowDefinition], List[EvaluationRequest]]:
    """Load both workflow definitions and evaluation requests from a workbook."""
    workflows = load_workflows_from_excel(filepath)
    test_questions = load_evaluation_requests_from_excel(filepath)
    return workflows, test_questions


# Convenient aliases
load_workflows = load_workflows_from_excel
load_evaluation_requests = load_evaluation_requests_from_excel
