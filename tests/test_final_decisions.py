"""Tests for the final business decisions.

1. WF009: only employees with every required skill are assigned; qualified candidates rank by
   available capacity; no qualified available candidate -> escalation (never a partial match).
2. WF003: three outputs (cleaned CSV, invalid-row CSV, validation-summary JSON); input preserved;
   formula injection neutralised; empty, existing, and blocked output paths handled.
3. WF004 and WF009: missing required inputs -> needs_clarification with clarification_required=true,
   checked through the orchestrator, the CLI exit code (4), and CLI JSON output.
"""

import csv
import hashlib
import json
from pathlib import Path

import pytest

from app.agent.provider import FakeLLMProvider
from app.agent.router import LLMWorkflowRouter
from app.main import EXIT_NEEDS_CLARIFICATION, EXIT_SUCCESS
from app.orchestrator import WorkflowOrchestrator

SAMPLE_VENDOR = Path("data/sample_vendor_catalog.csv").resolve()
EMP_HEADER = "employee_id,name,role,skills,current_workload_hours,max_capacity_hours,active_tasks_count\n"
VENDOR_HEADER = "Item_SKU,Item_Title,Category,Unit_Price,Quantity_Available\n"


def _orch(workflow_id: str) -> WorkflowOrchestrator:
    payload = json.dumps({
        "workflow_id": workflow_id,
        "confidence": 0.95,
        "reasoning": "fixture routing decision",
        "extracted_inputs": {},
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


def _employees(tmp_path: Path, rows) -> str:
    path = tmp_path / "employees.csv"
    path.write_text(EMP_HEADER + "".join(rows), encoding="utf-8")
    return str(path)


def _assign(tmp_path, rows, *, skills="python, fastapi, postgresql", priority="Urgent"):
    return _orch("WF009").run(
        "Assign task",
        task_description="Build REST API endpoint",
        required_skills=skills,
        priority=priority,
        deadline="2026-10-20",
        employee_file_path=_employees(tmp_path, rows),
    )


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _vendor_input(tmp_path: Path, body: str, name: str = "vendor_input.csv") -> Path:
    path = tmp_path / name
    path.write_text(body, encoding="utf-8")
    return path


# =============================================================== 1. WF009 qualification
def test_fully_qualified_employee_can_be_selected(tmp_path):
    report = _assign(tmp_path, ["EMP-A,Alpha,Backend,\"python, fastapi, postgresql\",10,40,1\n"])
    assert report.status == "success"
    assert report.final_output["escalation_required"] is False
    assert report.final_output["assigned_employee"]["employee_id"] == "EMP-A"


@pytest.mark.parametrize("priority", ["Urgent", "High", "Medium", "Low"])
def test_partially_qualified_never_assigned_regardless_of_capacity_or_priority(tmp_path, priority):
    # Partial match (2 of 3 skills) with completely free capacity must still escalate.
    rows = ["EMP-P,Partial,Fullstack,\"python, postgresql\",0,40,0\n"]
    report = _assign(tmp_path, rows, priority=priority)
    assert report.status == "success"
    assert report.final_output["escalation_required"] is True
    assert report.final_output["assigned_employee"] is None


def test_full_match_without_capacity_still_does_not_admit_partial_match(tmp_path):
    rows = [
        "EMP-A,Alpha,Backend,\"python, fastapi, postgresql\",40,40,6\n",
        "EMP-P,Partial,Fullstack,\"python, postgresql\",0,40,0\n",
    ]
    report = _assign(tmp_path, rows)
    assert report.final_output["escalation_required"] is True
    assert report.final_output["assigned_employee"] is None


def test_escalates_when_no_employee_has_all_required_skills(monkeypatch):
    report = _orch("WF009").run(
        "Assign mainframe task",
        task_description="Maintain legacy mainframe banking routines",
        required_skills="cobol, mainframe, fortran",
        priority="High",
        deadline="2026-10-20",
        employee_file_path="data/sample_employees.csv",
    )
    assert report.status == "success"
    assert report.final_output["escalation_required"] is True
    assert report.final_output["assigned_employee"] is None
    assert "every required skill" in report.final_output["escalation_reason"]


def test_qualified_candidates_ranked_by_available_capacity(tmp_path):
    rows = [
        "EMP-A,Alpha,Backend,\"python, fastapi, postgresql\",30,40,3\n",  # 10h available
        "EMP-B,Bravo,Backend,\"python, fastapi, postgresql\",10,40,1\n",  # 30h available
    ]
    report = _assign(tmp_path, rows)
    fo = report.final_output
    assert [c["name"] for c in fo["top_candidates"]] == ["Bravo", "Alpha"]
    assert fo["assigned_employee"]["employee_id"] == "EMP-B"


# =============================================================== 2. WF004 / WF009 clarification
def test_wf009_missing_task_description_requests_clarification(tmp_path):
    report = _orch("WF009").run(
        "Assign task",
        required_skills="python",
        employee_file_path=_employees(tmp_path, ["EMP-A,Alpha,Backend,\"python\",0,40,0\n"]),
    )
    assert report.status == "needs_clarification"
    assert report.clarification_required is True
    assert report.final_output is None
    assert "task_description" in report.errors[0]


def test_wf009_missing_required_skills_requests_clarification_and_fabricates_nothing(tmp_path):
    report = _orch("WF009").run(
        "Assign this urgent task to the best available developer.",
        task_description="Build a service",
        employee_file_path=_employees(tmp_path, ["EMP-A,Alpha,Backend,\"python\",0,40,0\n"]),
    )
    assert report.status == "needs_clarification"
    assert report.clarification_required is True
    assert report.final_output is None
    assert "required_skills" in report.errors[0]
    assert "general software engineering" not in json.dumps(report.model_dump())


def test_wf004_missing_product_name_requests_clarification():
    report = _orch("WF004").run("Generate SEO content for this product.")
    assert report.status == "needs_clarification"
    assert report.clarification_required is True
    assert report.final_output is None
    assert "Required attribute 'product_name' is missing or empty." in report.errors[0]


def test_cli_wf009_missing_inputs_exit_4_with_valid_json(monkeypatch, capsys):
    code, out, _ = _run_cli(
        monkeypatch, capsys,
        ["--mock-route", "WF009", "--json", "Assign this urgent task to the best available developer."],
    )
    assert code == EXIT_NEEDS_CLARIFICATION
    report = json.loads(out)
    assert report["status"] == "needs_clarification"
    assert report["clarification_required"] is True
    assert report["errors"]


def test_cli_wf004_missing_product_exit_4_with_valid_json(monkeypatch, capsys):
    code, out, _ = _run_cli(
        monkeypatch, capsys,
        ["--mock-route", "WF004", "--json", "Generate SEO content for this product."],
    )
    assert code == EXIT_NEEDS_CLARIFICATION
    report = json.loads(out)
    assert report["status"] == "needs_clarification"
    assert report["clarification_required"] is True
    assert "product_name" in report["errors"][0]


def test_cli_wf004_missing_product_text_report_is_readable(monkeypatch, capsys):
    code, out, _ = _run_cli(monkeypatch, capsys, ["--mock-route", "WF004", "Generate SEO content for this product."])
    assert code == EXIT_NEEDS_CLARIFICATION
    assert "NEEDS_CLARIFICATION" in out
    assert "CLARIFICATION REQUIRED" in out


# =============================================================== 3. WF003 three outputs
def test_wf003_writes_three_outputs_and_summary_format(tmp_path):
    report = _orch("WF003").run(
        "Process this vendor spreadsheet and show invalid rows.",
        file_path=str(SAMPLE_VENDOR),
        output_dir=str(tmp_path),
    )
    assert report.status == "success"
    stem = SAMPLE_VENDOR.stem
    assert (tmp_path / f"cleaned_{stem}.csv").exists()
    assert (tmp_path / f"invalid_rows_{stem}.csv").exists()
    summary_path = tmp_path / f"validation_summary_{stem}.json"
    assert summary_path.exists()

    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert set(summary) == {"source_file", "processed_rows", "valid_rows", "invalid_rows", "output_files"}
    assert summary["source_file"] == SAMPLE_VENDOR.name
    assert summary["processed_rows"] == 8
    assert summary["valid_rows"] == 4
    assert summary["invalid_rows"] == 4
    assert summary["processed_rows"] == summary["valid_rows"] + summary["invalid_rows"]
    assert summary["output_files"] == {
        "cleaned_csv": f"cleaned_{stem}.csv",
        "invalid_rows_csv": f"invalid_rows_{stem}.csv",
        "validation_summary_json": f"validation_summary_{stem}.json",
    }


def test_wf003_cleaned_csv_schema_and_contents(tmp_path):
    _orch("WF003").run("Process vendor file.", file_path=str(SAMPLE_VENDOR), output_dir=str(tmp_path))
    with (tmp_path / f"cleaned_{SAMPLE_VENDOR.stem}.csv").open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    assert [r["sku"] for r in rows] == ["VND-101", "VND-104", "VND-106", "VND-108"]
    assert list(rows[0].keys()) == ["sku", "product_name", "price", "category", "stock"]


def test_wf003_invalid_rows_csv_contains_every_invalid_row(tmp_path):
    _orch("WF003").run("Process vendor file.", file_path=str(SAMPLE_VENDOR), output_dir=str(tmp_path))
    with (tmp_path / f"invalid_rows_{SAMPLE_VENDOR.stem}.csv").open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        assert reader.fieldnames == ["row_number", "sku", "product_name", "price", "category", "stock", "errors"]
        rows = list(reader)
    assert len(rows) == 4
    assert all(r["errors"] for r in rows)
    assert any("price must be non-negative" in r["errors"] for r in rows)


def test_wf003_preserves_original_input(tmp_path):
    before = _sha(SAMPLE_VENDOR)
    _orch("WF003").run("Process vendor file.", file_path=str(SAMPLE_VENDOR), output_dir=str(tmp_path))
    assert _sha(SAMPLE_VENDOR) == before


def test_wf003_empty_input_with_header_only_produces_empty_outputs(tmp_path):
    src = _vendor_input(tmp_path, VENDOR_HEADER, "header_only.csv")
    out = tmp_path / "out"
    report = _orch("WF003").run("Process vendor file.", file_path=str(src), output_dir=str(out))
    assert report.status == "success"
    summary = json.loads((out / "validation_summary_header_only.json").read_text(encoding="utf-8"))
    assert (summary["processed_rows"], summary["valid_rows"], summary["invalid_rows"]) == (0, 0, 0)
    assert (out / "cleaned_header_only.csv").read_text(encoding="utf-8").strip() == "sku,product_name,price,category,stock"
    assert (out / "invalid_rows_header_only.csv").read_text(encoding="utf-8").strip().startswith("row_number,")


def test_wf003_zero_byte_input_fails_without_writing_outputs(tmp_path):
    src = _vendor_input(tmp_path, "", "zero.csv")
    out = tmp_path / "out"
    report = _orch("WF003").run("Process vendor file.", file_path=str(src), output_dir=str(out))
    assert report.status == "failed"
    assert not out.exists() or not any(out.iterdir())
    assert _sha(src) == hashlib.sha256(b"").hexdigest()


def test_wf003_existing_outputs_are_replaced_and_input_preserved(tmp_path):
    out = tmp_path / "out"
    out.mkdir()
    stale = out / f"cleaned_{SAMPLE_VENDOR.stem}.csv"
    stale.write_text("STALE CONTENT\n", encoding="utf-8")
    before = _sha(SAMPLE_VENDOR)
    report = _orch("WF003").run("Process vendor file.", file_path=str(SAMPLE_VENDOR), output_dir=str(out))
    assert report.status == "success"
    assert "STALE CONTENT" not in stale.read_text(encoding="utf-8")
    assert _sha(SAMPLE_VENDOR) == before


def test_wf003_output_path_blocked_by_directory_fails_cleanly(tmp_path):
    out = tmp_path / "out"
    (out / f"cleaned_{SAMPLE_VENDOR.stem}.csv").mkdir(parents=True)
    before = _sha(SAMPLE_VENDOR)
    report = _orch("WF003").run("Process vendor file.", file_path=str(SAMPLE_VENDOR), output_dir=str(out))
    # The read and clean steps succeed; writing the output fails, so the run is a partial failure.
    assert report.status == "partial_failure"
    assert "is a directory" in report.errors[0]
    assert _sha(SAMPLE_VENDOR) == before


def test_wf003_neutralises_formula_injection_in_both_csvs(tmp_path):
    # Valid row with formula-like SKU and product name (quoted: the SKU contains commas).
    # Invalid row (missing name) with a formula-like SKU.
    src = _vendor_input(
        tmp_path,
        VENDOR_HEADER
        + '"=HYPERLINK(""http://evil.example"",""x"")",=SUM(1+1),Audio,10.00,5\n'
        + '=cmd|calc,,Audio,10.00,5\n',
        "inject.csv",
    )
    out = tmp_path / "out"
    report = _orch("WF003").run("Process vendor file.", file_path=str(src), output_dir=str(out))
    assert report.status == "success"
    with (out / "cleaned_inject.csv").open(newline="", encoding="utf-8") as f:
        cleaned = list(csv.DictReader(f))
    with (out / "invalid_rows_inject.csv").open(newline="", encoding="utf-8") as f:
        invalid = list(csv.DictReader(f))
    assert cleaned[0]["sku"].startswith("'=")
    assert cleaned[0]["product_name"] == "'=SUM(1+1)"
    assert invalid[0]["sku"] == "'=cmd|calc"


def test_cli_wf003_three_outputs_and_exit_zero(monkeypatch, capsys, tmp_path):
    code, out, _ = _run_cli(
        monkeypatch, capsys,
        ["--mock-route", "WF003", "--vendor-file", str(SAMPLE_VENDOR), "--output-dir", str(tmp_path),
         "--json", "Process this vendor spreadsheet and show invalid rows."],
    )
    assert code == EXIT_SUCCESS
    files = json.loads(out)["final_output"]["output_files"]
    assert set(files) == {"cleaned_csv", "invalid_rows_csv", "validation_summary_json"}
    assert all(Path(p).exists() for p in files.values())


def test_cli_help_documents_wf003_default_output_directory(monkeypatch, capsys):
    code, out, _ = _run_cli(monkeypatch, capsys, ["--help"])
    assert code in (0, None)
    assert "outputs" in out
