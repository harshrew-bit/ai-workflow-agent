"""Pytest fixtures and configuration."""

from pathlib import Path
from typing import Any, Callable, Dict, List, Sequence
import openpyxl
import pytest

ASSESSMENT_WORKBOOK_PATH = Path(__file__).parent.parent / "data" / "workflows.xlsx"

DEFAULT_WORKFLOW_HEADERS = [
    "Workflow_ID",
    "Workflow_Name",
    "Trigger",
    "Inputs",
    "Steps",
    "Decision_Logic",
    "Tools_Required",
    "Expected_Output",
]

DEFAULT_TEST_QUESTION_HEADERS = [
    "Workflow_ID",
    "Test_Request",
    "What_To_Check",
]


@pytest.fixture
def assessment_workbook_path() -> Path:
    """Return the absolute path to the official assessment workbook."""
    assert ASSESSMENT_WORKBOOK_PATH.exists(), f"Assessment workbook missing at {ASSESSMENT_WORKBOOK_PATH}"
    return ASSESSMENT_WORKBOOK_PATH


@pytest.fixture
def make_excel_file(tmp_path: Path) -> Callable[..., Path]:
    """Factory fixture to create temporary Excel workbooks for testing."""

    def _create_workbook(
        sheets_data: Dict[str, Sequence[Sequence[Any]]],
        filename: str = "test_workflows.xlsx",
    ) -> Path:
        file_path = tmp_path / filename
        wb = openpyxl.Workbook()
        # Remove default sheet
        wb.remove(wb.active)

        for sheet_name, rows in sheets_data.items():
            ws = wb.create_sheet(title=sheet_name)
            for row in rows:
                ws.append(list(row))

        wb.save(file_path)
        wb.close()
        return file_path

    return _create_workbook
