"""Regression tests for the QA audit findings (H1, H2, H4, H5).

Each test is written to FAIL on the pre-fix code and PASS after the fix.
"""

import json

import pytest

from app.agent.provider import FakeLLMProvider
from app.agent.router import LLMWorkflowRouter
from app.orchestrator import WorkflowOrchestrator
from app.registry.registry import WorkflowRegistry


def _orchestrator_for(workflow_id: str, extracted_inputs=None) -> WorkflowOrchestrator:
    payload = json.dumps({
        "workflow_id": workflow_id,
        "confidence": 0.95,
        "reasoning": "fixture routing decision",
        "extracted_inputs": extracted_inputs or {},
        "requires_clarification": False,
    })
    router = LLMWorkflowRouter(provider=FakeLLMProvider(default_response=payload))
    return WorkflowOrchestrator(router=router)


def _run_cli(monkeypatch, capsys, argv):
    from app.main import main

    monkeypatch.setattr("sys.argv", ["app.main", *argv])
    exit_code = 0
    try:
        main()
    except SystemExit as exc:
        exit_code = exc.code
    return exit_code, capsys.readouterr().out


# ---------------------------------------------------------------- H1
@pytest.mark.parametrize(
    "workflow_id, request_text, fabricated_marker, expected_exit",
    [
        # Workbook: WF007 must request missing goal/dates -> needs clarification (exit 4).
        ("WF007", "Create a campaign brief for the new collection.", "Launch New Sustainable", 4),
        # Decision 3: missing required WF009 inputs request clarification (exit 4).
        ("WF009", "Assign this urgent task to the best available developer.", "Build secure REST API", 4),
    ],
)
def test_mock_route_does_not_fabricate_missing_inputs(monkeypatch, capsys, workflow_id, request_text, fabricated_marker, expected_exit):
    code, out = _run_cli(monkeypatch, capsys, ["--mock-route", workflow_id, request_text])
    assert code == expected_exit, f"{workflow_id}: expected exit {expected_exit}, got {code}"
    assert fabricated_marker not in out



def test_mock_route_wf005_extracts_order_id_from_request(monkeypatch, capsys):
    code, out = _run_cli(
        monkeypatch, capsys,
        ["--mock-route", "WF005", "--json", "Where is order ORD-1001?"],
    )
    assert code == 0
    report = json.loads(out)
    final = report["final_output"]
    assert final["order_found"] is True
    assert [o["order_id"] for o in final["orders"]] == ["ORD-1001"]


def test_mock_route_wf005_explicit_flag_wins_over_extraction(monkeypatch, capsys):
    code, out = _run_cli(
        monkeypatch, capsys,
        ["--mock-route", "WF005", "--json", "--order-id", "ORD-1002", "Where is order ORD-1001?"],
    )
    assert code == 0
    final = json.loads(out)["final_output"]
    assert [o["order_id"] for o in final["orders"]] == ["ORD-1002"]


# ---------------------------------------------------------------- H4
@pytest.mark.parametrize("literal", ["NaN", "Infinity", "-Infinity"])
def test_router_rejects_non_finite_confidence(literal):
    """Fail closed: a non-finite confidence must not clear the gate or execute anything."""
    raw = '{"workflow_id": "WF001", "confidence": %s, "reasoning": "r", "extracted_inputs": {}}' % literal
    registry = WorkflowRegistry.from_excel("data/workflows.xlsx")
    decision = LLMWorkflowRouter(provider=FakeLLMProvider(default_response=raw)).route(
        "Which products need restocking?", registry.list_all()
    )
    assert decision.confidence == 0.0
    assert decision.requires_clarification is True

    report = WorkflowOrchestrator(router=LLMWorkflowRouter(provider=FakeLLMProvider(default_response=raw))).run(
        "Which products need restocking?"
    )
    assert report.status == "needs_clarification"
    assert report.steps == []


def test_router_still_accepts_valid_confidence_at_threshold():
    raw = '{"workflow_id": "WF001", "confidence": 0.70, "reasoning": "r", "extracted_inputs": {}}'
    registry = WorkflowRegistry.from_excel("data/workflows.xlsx")
    decision = LLMWorkflowRouter(provider=FakeLLMProvider(default_response=raw)).route(
        "Which products need restocking?", registry.list_all()
    )
    assert decision.workflow_id == "WF001"
    assert decision.requires_clarification is False


# ---------------------------------------------------------------- H5
def _outside_vendor_csv(tmp_path):
    path = tmp_path / "outside_vendor.csv"
    path.write_text("sku,vendor_name,vendor_price\nOUT-1,Outside Vendor,12.00\n", encoding="utf-8")
    return str(path)


def test_router_extracted_path_is_ignored_and_outside_file_not_read(tmp_path):
    outside = _outside_vendor_csv(tmp_path)
    report = _orchestrator_for("WF002", {"vendor_csv_path": outside}).run(
        "Find products where vendor price differs by more than 10%."
    )
    assert report.status == "success"
    unmatched = [r["sku"] for r in report.final_output["unmatched_vendor_records"]]
    assert "OUT-1" not in unmatched, "LLM-supplied path must not be read"
    assert "Ignored router-supplied file path input(s): vendor_csv_path" in report.routing_reasoning


def test_explicit_runtime_path_still_honored(tmp_path):
    outside = _outside_vendor_csv(tmp_path)
    report = _orchestrator_for("WF002").run(
        "Find products where vendor price differs by more than 10%.",
        vendor_csv_path=outside,
    )
    assert report.status == "success"
    unmatched = [r["sku"] for r in report.final_output["unmatched_vendor_records"]]
    assert "OUT-1" in unmatched, "explicit CLI/runtime paths must keep working"


def test_non_path_extracted_inputs_are_still_merged():
    report = _orchestrator_for("WF005", {"order_id": "ORD-1001"}).run("Where is order ORD-1001?")
    assert report.status == "success"
    assert report.final_output["order_found"] is True
    assert "Ignored router-supplied" not in report.routing_reasoning
