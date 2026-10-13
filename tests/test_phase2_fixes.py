"""Regression tests for phase-2 audit decisions.

Covers: WF009 ranking (skill coverage first, then capacity), WF003 cleaned and invalid-row
CSV outputs, WF005/WF007 clarification semantics, the CLI exit-code contract, the
required-request CLI behaviour, and JSON validity of CLI output.
"""

import csv
import hashlib
import json
from pathlib import Path

import pytest

from app.agent.provider import FakeLLMProvider
from app.agent.router import LLMWorkflowRouter
from app.main import (
    EXIT_FAILED,
    EXIT_NEEDS_CLARIFICATION,
    EXIT_PARTIAL_FAILURE,
    EXIT_SUCCESS,
    EXIT_USAGE,
    exit_code_for_status,
)
from app.models.execution import ExecutionStatus
from app.orchestrator import WorkflowOrchestrator

SAMPLE_VENDOR = Path("data/sample_vendor_catalog.csv")
SAMPLE_VENDOR_ABS = SAMPLE_VENDOR.resolve()  # absolute, so tests that change cwd still work


def _orchestrator_for(workflow_id: str, extracted_inputs=None) -> WorkflowOrchestrator:
    payload = json.dumps({
        "workflow_id": workflow_id,
        "confidence": 0.95,
        "reasoning": "fixture routing decision",
        "extracted_inputs": extracted_inputs or {},
        "requires_clarification": False,
    })
    return WorkflowOrchestrator(router=LLMWorkflowRouter(provider=FakeLLMProvider(default_response=payload)))


def _run_cli(monkeypatch, capsys, argv):
    from app.main import main

    monkeypatch.setattr("sys.argv", ["app.main", *argv])
    code = 0
    try:
        main()
    except SystemExit as exc:
        code = exc.code
    captured = capsys.readouterr()
    return code, captured.out, captured.err


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


# ------------------------------------------------------------------ exit-code contract
@pytest.mark.parametrize(
    "status, expected",
    [
        ("success", EXIT_SUCCESS),
        ("failed", EXIT_FAILED),
        ("partial_failure", EXIT_PARTIAL_FAILURE),
        ("needs_clarification", EXIT_NEEDS_CLARIFICATION),
        ("something_unknown", EXIT_FAILED),
    ],
)
def test_exit_code_mapping(status, expected):
    assert exit_code_for_status(status) == expected


def test_documented_exit_code_values():
    assert (EXIT_SUCCESS, EXIT_FAILED, EXIT_USAGE, EXIT_PARTIAL_FAILURE, EXIT_NEEDS_CLARIFICATION) == (0, 1, 2, 3, 4)


def test_needs_clarification_status_exists():
    assert ExecutionStatus.NEEDS_CLARIFICATION.value == "needs_clarification"


def test_cli_success_exits_zero(monkeypatch, capsys):
    code, out, _ = _run_cli(monkeypatch, capsys, ["--mock-route", "WF001", "Which products need restocking?"])
    assert code == EXIT_SUCCESS
    assert "Status:                SUCCESS" in out


def test_cli_unknown_order_exits_needs_clarification_and_json_is_valid(monkeypatch, capsys):
    code, out, _ = _run_cli(
        monkeypatch, capsys,
        ["--mock-route", "WF005", "--order-id", "ORD-9999", "--json", "Where is order ORD-9999?"],
    )
    assert code == EXIT_NEEDS_CLARIFICATION
    report = json.loads(out)  # JSON output must be valid
    assert report["status"] == "needs_clarification"
    assert report["clarification_required"] is True
    assert "Please provide a valid Order ID" in report["errors"][0]


def test_cli_missing_wf007_dates_exits_needs_clarification(monkeypatch, capsys):
    code, out, _ = _run_cli(
        monkeypatch, capsys,
        ["--mock-route", "WF007", "--campaign-goal", "Launch", "--json", "Create a campaign brief."],
    )
    assert code == EXIT_NEEDS_CLARIFICATION
    report = json.loads(out)
    assert report["clarification_required"] is True
    assert "dates" in report["errors"][0]


def test_cli_missing_wf004_product_exits_needs_clarification(monkeypatch, capsys):
    """Decision 3: missing WF004 product_name is a clarification request (exit 4), not a failure."""
    code, out, _ = _run_cli(monkeypatch, capsys, ["--mock-route", "WF004", "--json", "Generate SEO content for this product."])
    assert code == EXIT_NEEDS_CLARIFICATION
    report = json.loads(out)
    assert report["status"] == "needs_clarification"
    assert report["clarification_required"] is True



# ------------------------------------------------------------------ no-argument behaviour
def test_no_arguments_is_a_usage_error_not_a_default_request(monkeypatch, capsys):
    code, out, err = _run_cli(monkeypatch, capsys, [])
    assert code == EXIT_USAGE
    assert out == ""  # no execution report; no silent default request
    assert "request" in err


def test_mock_route_without_request_is_usage_error(monkeypatch, capsys):
    code, out, err = _run_cli(monkeypatch, capsys, ["--mock-route", "WF001"])
    assert code == EXIT_USAGE
    assert out == ""
    assert "request" in err


# ------------------------------------------------------------------ WF005 / WF007 semantics
def test_wf005_found_order_still_succeeds():
    report = _orchestrator_for("WF005", {"order_id": "ORD-1001"}).run("Where is order ORD-1001?")
    assert report.status == "success"
    assert report.clarification_required is False


def test_wf005_unknown_order_has_no_final_output_and_no_success():
    report = _orchestrator_for("WF005", {"order_id": "ORD-9999"}).run("Where is order ORD-9999?")
    assert report.status == "needs_clarification"
    assert report.clarification_required is True
    assert report.final_output is None
    assert report.steps[-1].status == "needs_clarification"


def test_wf007_complete_inputs_succeed():
    report = _orchestrator_for("WF007").run(
        "Create a brief.",
        campaign_goal="Launch collection",
        dates="2026-11-01 to 2026-11-30",
        product_list=["Desk Organizer"],
    )
    assert report.status == "success"


def test_wf007_missing_goal_requests_clarification():
    report = _orchestrator_for("WF007").run("Create a brief.", dates="2026-11-01 to 2026-11-30")
    assert report.status == "needs_clarification"
    assert "campaign_goal" in report.errors[0]


# ------------------------------------------------------------------ WF009 ranking
def _employee_csv(tmp_path: Path, rows) -> str:
    path = tmp_path / "employees.csv"
    header = "employee_id,name,role,skills,current_workload_hours,max_capacity_hours,active_tasks_count\n"
    path.write_text(header + "".join(rows), encoding="utf-8")
    return str(path)


def _assign(tmp_path, rows, skills="python, fastapi, postgresql"):
    return _orchestrator_for("WF009").run(
        "Assign task",
        task_description="Build REST API endpoint",
        required_skills=skills,
        priority="Urgent",
        deadline="2026-10-20",
        employee_file_path=_employee_csv(tmp_path, rows),
    )


def test_fully_qualified_available_candidate_ranks_above_partial(tmp_path):
    # Fully qualified (3/3 skills, 10h free) vs partially qualified (2/3 skills, 35h free).
    # Under the old 50/50 composite the partial candidate won; skill coverage must come first.
    rows = [
        "EMP-A,Full Match,Backend,\"python, fastapi, postgresql\",30,40,3\n",
        "EMP-B,Partial Match,Fullstack,\"python, postgresql\",5,40,1\n",
    ]
    report = _assign(tmp_path, rows)
    assert report.status == "success"
    fo = report.final_output
    ranked_names = [c["name"] for c in fo["top_candidates"]]
    assert ranked_names.index("Full Match") < ranked_names.index("Partial Match")
    assert fo["assigned_employee"]["employee_id"] == "EMP-A"


def test_partial_candidate_never_assigned_even_with_capacity(tmp_path):
    """Decision 1: a partially qualified employee is never assigned, even with ample capacity."""
    rows = [
        "EMP-A,Full Match No Capacity,Backend,\"python, fastapi, postgresql\",40,40,6\n",
        "EMP-B,Partial Match,Fullstack,\"python, postgresql\",5,40,1\n",
    ]
    report = _assign(tmp_path, rows)
    assert report.status == "success"
    assert report.final_output["escalation_required"] is True
    assert report.final_output["assigned_employee"] is None



def test_sample_employees_assign_fully_qualified_alice():
    report = _orchestrator_for("WF009").run(
        "Assign task",
        task_description="Build secure REST API endpoint for user profile export in FastAPI with PostgreSQL",
        required_skills="python, fastapi, postgresql",
        priority="Urgent",
        deadline="2026-10-20",
        employee_file_path="data/sample_employees.csv",
    )
    assert report.status == "success"
    assert report.final_output["assigned_employee"]["employee_id"] == "EMP-101"


def test_ranking_explanation_states_skill_first_rule(tmp_path):
    rows = ["EMP-A,Full,Backend,\"python, fastapi, postgresql\",30,40,3\n"]
    report = _assign(tmp_path, rows)
    explanation = report.final_output["assigned_employee"]["ranking_explanation"]
    assert "all required skills first" in explanation


# ------------------------------------------------------------------ WF003 outputs
def test_wf003_writes_cleaned_and_invalid_csv_and_preserves_input(tmp_path):
    before = _sha256(SAMPLE_VENDOR_ABS)
    report = _orchestrator_for("WF003").run(
        "Process this vendor spreadsheet and show invalid rows.",
        file_path=str(SAMPLE_VENDOR_ABS),
        output_dir=str(tmp_path),
    )
    assert report.status == "success"
    assert _sha256(SAMPLE_VENDOR_ABS) == before, "source file must never be modified"

    cleaned = tmp_path / "cleaned_sample_vendor_catalog.csv"
    invalid = tmp_path / "invalid_rows_sample_vendor_catalog.csv"
    assert cleaned.exists() and invalid.exists()

    with cleaned.open(newline="", encoding="utf-8") as f:
        cleaned_rows = list(csv.DictReader(f))
    assert list(cleaned_rows[0].keys()) == ["sku", "product_name", "price", "category", "stock"]
    assert [r["sku"] for r in cleaned_rows] == ["VND-101", "VND-104", "VND-106", "VND-108"]

    with invalid.open(newline="", encoding="utf-8") as f:
        invalid_rows = list(csv.DictReader(f))
    assert len(invalid_rows) == 4
    assert all(r["errors"] for r in invalid_rows)
    assert "row_number" in invalid_rows[0]

    assert report.final_output["output_files"]["cleaned_csv"] == str(cleaned)
    assert report.final_output["output_files"]["invalid_rows_csv"] == str(invalid)


def test_wf003_without_output_dir_writes_nothing(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    report = _orchestrator_for("WF003").run(
        "Process this vendor spreadsheet and show invalid rows.",
        file_path=str(SAMPLE_VENDOR_ABS),
    )
    assert report.status == "success"
    assert report.final_output["output_files"] == {}
    assert list(tmp_path.iterdir()) == []


def test_wf003_neutralises_spreadsheet_formula_injection(tmp_path):
    source = tmp_path / "inject.csv"
    source.write_text(
        "Item_SKU,Item_Title,Category,Unit_Price,Quantity_Available\n"
        'VND-900,"=HYPERLINK(""http://evil.example"",""x"")",Audio,10.00,5\n',
        encoding="utf-8",
    )
    out = tmp_path / "out"
    report = _orchestrator_for("WF003").run(
        "Process this vendor spreadsheet and show invalid rows.",
        file_path=str(source),
        output_dir=str(out),
    )
    assert report.status == "success"
    with (out / "cleaned_inject.csv").open(newline="", encoding="utf-8") as f:
        row = next(csv.DictReader(f))
    assert row["product_name"].startswith("'=")


def test_cli_wf003_writes_outputs_to_output_dir(monkeypatch, capsys, tmp_path):
    code, out, _ = _run_cli(
        monkeypatch, capsys,
        ["--mock-route", "WF003", "--vendor-file", str(SAMPLE_VENDOR), "--output-dir", str(tmp_path),
         "--json", "Process this vendor spreadsheet and show invalid rows."],
    )
    assert code == EXIT_SUCCESS
    assert json.loads(out)["final_output"]["valid_count"] == 4
    assert (tmp_path / "cleaned_sample_vendor_catalog.csv").exists()
    assert (tmp_path / "invalid_rows_sample_vendor_catalog.csv").exists()
