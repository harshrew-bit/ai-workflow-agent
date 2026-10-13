"""Tests for forced routing indicator and better-match warnings in mock-route mode."""

import json
from app.main import format_report_for_display
from app.models.report import ExecutionReport, StepReport


def test_text_report_displays_forced_routing_line():
    report = ExecutionReport(
        request="Check inventory",
        selected_workflow_id="WF001",
        selected_workflow_name="Inventory Restock Check",
        routing_confidence=0.95,
        routing_reasoning="Simulated routing selection for WF001",
        status="success",
        routing_mode="forced",
        steps=[],
    )
    text = format_report_for_display(report)
    assert "Routing Mode:          FORCED (--mock-route; this is not a routing decision)" in text


def test_text_report_displays_better_match_warning():
    warning = "[WARNING] Forced route selected WF003, but request appears to match WF001 (Inventory Restock Check)."
    report = ExecutionReport(
        request="Check today's inventory and identify products that need restocking.",
        selected_workflow_id="WF003",
        selected_workflow_name="Vendor File Processing",
        routing_confidence=0.95,
        routing_reasoning="Simulated routing selection for WF003",
        status="success",
        routing_mode="forced",
        warnings=[warning],
        steps=[],
    )
    text = format_report_for_display(report)
    assert "Routing Mode:          FORCED (--mock-route; this is not a routing decision)" in text
    assert warning in text


def test_json_report_includes_forced_routing_mode_and_warnings():
    warning = "[WARNING] Forced route selected WF003, but request appears to match WF001 (Inventory Restock Check)."
    report = ExecutionReport(
        request="Check today's inventory and identify products that need restocking.",
        selected_workflow_id="WF003",
        selected_workflow_name="Vendor File Processing",
        routing_confidence=0.95,
        routing_reasoning="Simulated routing selection for WF003",
        status="success",
        routing_mode="forced",
        warnings=[warning],
        steps=[],
    )
    raw_json = report.model_dump_json()
    data = json.loads(raw_json)
    assert data["routing_mode"] == "forced"
    assert data["warnings"] == [warning]


def test_offline_scorer_identifies_better_match_for_mismatched_forced_route():
    from app.agent.offline_router import OfflineWorkflowRouter
    from app.registry.registry import WorkflowRegistry

    registry = WorkflowRegistry.from_excel("data/workflows.xlsx")
    workflows = registry.list_all()

    scorer = OfflineWorkflowRouter()
    ranked = scorer.score_workflows(
        "Check today's inventory and identify products that need restocking.",
        workflows,
    )

    top_wf, top_score, _ = ranked[0]
    assert top_wf.workflow_id == "WF001"

    # Forced WF003 score should be lower than WF001
    forced_score = next(s for wf, s, _ in ranked if wf.workflow_id == "WF003")
    assert top_score > forced_score
