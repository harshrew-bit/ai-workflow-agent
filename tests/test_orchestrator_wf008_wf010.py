"""Integration and end-to-end pipeline tests for WF008, WF009, and WF010."""

import json
from pathlib import Path
import pytest

from app.agent.provider import FakeLLMProvider
from app.agent.router import LLMWorkflowRouter
from app.orchestrator import WorkflowOrchestrator


def test_orchestrator_wf008_full_pipeline():
    """End-to-end execution of WF008 — SEO Keyword Classification via WorkflowOrchestrator."""
    fake_json = json.dumps({
        "workflow_id": "WF008",
        "confidence": 0.95,
        "reasoning": "Matches SEO Keyword Classification trigger.",
        "extracted_inputs": {
            "keyword_file_path": "data/sample_keywords.csv",
        },
        "requires_clarification": False,
    })
    router = LLMWorkflowRouter(provider=FakeLLMProvider(default_response=fake_json))
    orchestrator = WorkflowOrchestrator(router=router)

    report = orchestrator.run("Classify these keywords and map them to pages.")

    assert report.status == "success"
    assert report.selected_workflow_id == "WF008"
    assert report.selected_workflow_name == "SEO Keyword Classification"
    assert len(report.steps) == 6

    expected_steps = [
        "Read keywords",
        "remove duplicates",
        "classify search intent",
        "map keywords to categories",
        "identify high-priority keywords",
        "export results",
    ]
    for step_rep, exp_name in zip(report.steps, expected_steps):
        assert step_rep.step_name == exp_name
        assert step_rep.status == "completed"
        assert step_rep.error is None

    final = report.final_output
    assert isinstance(final, dict)
    assert final["total_keywords"] >= 10
    assert final["high_priority_count"] >= 1
    assert "intent_counts" in final
    assert "category_counts" in final
    assert final["is_simulated"] is True


def test_orchestrator_wf009_full_pipeline_assigned():
    """End-to-end execution of WF009 — Employee Task Assignment with successful assignment."""
    fake_json = json.dumps({
        "workflow_id": "WF009",
        "confidence": 0.95,
        "reasoning": "Matches Employee Task Assignment trigger.",
        "extracted_inputs": {
            "task_description": "Build high-throughput REST service in FastAPI with PostgreSQL backend",
            "required_skills": "fastapi, python, postgresql",
            "priority": "Urgent",
        },
        "requires_clarification": False,
    })
    router = LLMWorkflowRouter(provider=FakeLLMProvider(default_response=fake_json))
    orchestrator = WorkflowOrchestrator(router=router)

    report = orchestrator.run("Assign this urgent task to the best available developer.")

    assert report.status == "success"
    assert report.selected_workflow_id == "WF009"
    assert report.selected_workflow_name == "Employee Task Assignment"
    assert len(report.steps) == 6

    expected_steps = [
        "Understand task requirements",
        "compare employee skills",
        "check current workload",
        "rank candidates",
        "select employee",
        "generate assignment summary",
    ]
    for step_rep, exp_name in zip(report.steps, expected_steps):
        assert step_rep.step_name == exp_name
        assert step_rep.status == "completed"

    final = report.final_output
    assert isinstance(final, dict)
    assert final["assignment_status"] == "ASSIGNED"
    assert final["escalation_required"] is False
    assert final["assigned_employee"] is not None
    assert final["assigned_employee"]["name"] in ["Alice Chen", "Carlos Rivera"]
    assert final["is_simulated"] is True


def test_orchestrator_wf009_escalation_when_no_skills():
    """Verify that WF009 triggers escalation when nobody has required skills."""
    fake_json = json.dumps({
        "workflow_id": "WF009",
        "confidence": 0.95,
        "reasoning": "Matches Employee Task Assignment trigger.",
        "extracted_inputs": {
            "task_description": "Maintain legacy mainframe banking COBOL routines",
            "required_skills": "cobol, mainframe, fortran",
            "priority": "High",
        },
        "requires_clarification": False,
    })
    router = LLMWorkflowRouter(provider=FakeLLMProvider(default_response=fake_json))
    orchestrator = WorkflowOrchestrator(router=router)

    report = orchestrator.run("Assign mainframe task.")

    assert report.status == "success"
    assert report.selected_workflow_id == "WF009"

    final = report.final_output
    assert isinstance(final, dict)
    assert final["assignment_status"] == "ESCALATED"
    assert final["escalation_required"] is True
    assert final["assigned_employee"] is None
    assert "No employee possesses the required skills" in final["escalation_reason"]


def test_orchestrator_wf010_full_pipeline():
    """End-to-end execution of WF010 — Workflow Performance Report via WorkflowOrchestrator."""
    fake_json = json.dumps({
        "workflow_id": "WF010",
        "confidence": 0.95,
        "reasoning": "Matches Workflow Performance Report trigger.",
        "extracted_inputs": {
            "log_file_path": "data/sample_workflow_logs.csv",
        },
        "requires_clarification": False,
    })
    router = LLMWorkflowRouter(provider=FakeLLMProvider(default_response=fake_json))
    orchestrator = WorkflowOrchestrator(router=router)

    report = orchestrator.run("Which workflows are failing most often?")

    assert report.status == "success"
    assert report.selected_workflow_id == "WF010"
    assert report.selected_workflow_name == "Workflow Performance Report"
    assert len(report.steps) == 6

    expected_steps = [
        "Load execution logs",
        "calculate success/failure rate",
        "calculate average execution time",
        "identify frequent errors",
        "identify slow steps",
        "generate recommendations",
    ]
    for step_rep, exp_name in zip(report.steps, expected_steps):
        assert step_rep.step_name == exp_name
        assert step_rep.status == "completed"

    final = report.final_output
    assert isinstance(final, dict)
    assert "overall_metrics" in final
    assert "workflow_performance" in final
    assert "flagged_high_failure_workflows" in final
    # WF003 has 25% failure rate in sample logs, which exceeds 10%
    assert "WF003" in final["flagged_high_failure_workflows"]
    # WF003 has 6.4s avg execution time, which exceeds 5.0s
    assert "WF003" in final["flagged_slow_workflows"]
    assert len(final["recommendations"]) > 0
    assert final["is_simulated"] is True


def test_cli_mock_route_wf008(monkeypatch, capsys):
    """Test CLI --mock-route WF008."""
    from app.main import main

    monkeypatch.setattr(
        "sys.argv",
        [
            "app.main",
            "--mock-route",
            "WF008",
            "Classify these keywords and map them to pages.",
        ],
    )
    main()

    captured = capsys.readouterr()
    assert "SUCCESS" in captured.out
    assert "WF008 (SEO Keyword Classification)" in captured.out
    assert "how to clean mechanical keyboard" in captured.out.lower()
    assert "INFORMATIONAL" in captured.out
    assert "SIMULATED" in captured.out


def test_cli_mock_route_wf009(monkeypatch, capsys):
    """Test CLI --mock-route WF009."""
    from app.main import main

    monkeypatch.setattr(
        "sys.argv",
        [
            "app.main",
            "--mock-route",
            "WF009",
            "--task-desc",
            "Build secure FastAPI endpoints with PostgreSQL",
            "--skills",
            "fastapi, python, postgresql",
            "Assign this urgent task to the best available developer.",
        ],
    )
    main()

    captured = capsys.readouterr()
    assert "SUCCESS" in captured.out
    assert "WF009 (Employee Task Assignment)" in captured.out
    assert "ASSIGNED" in captured.out
    assert "Alice Chen" in captured.out or "Carlos Rivera" in captured.out
    assert "SIMULATED" in captured.out


def test_cli_mock_route_wf010(monkeypatch, capsys):
    """Test CLI --mock-route WF010."""
    from app.main import main

    monkeypatch.setattr(
        "sys.argv",
        [
            "app.main",
            "--mock-route",
            "WF010",
            "Which workflows are failing most often?",
        ],
    )
    main()

    captured = capsys.readouterr()
    assert "SUCCESS" in captured.out
    assert "WF010 (Workflow Performance Report)" in captured.out
    assert "WF003" in captured.out
    assert "CRITICAL" in captured.out or "HIGH FAILURE" in captured.out
    assert "SIMULATED" in captured.out


def test_all_workflows_regression_wf001_through_wf007():
    """Verify that WF001 through WF007 continue to execute cleanly."""
    workflows_to_test = [
        ("WF001", "Which products need restocking?", {"csv_path": "data/sample_inventory.csv"}),
        ("WF002", "Check price differences", {"internal_csv_path": "data/sample_internal_prices.csv", "vendor_csv_path": "data/sample_vendor_prices.csv"}),
        ("WF003", "Process vendor catalog", {"file_path": "data/sample_vendor_catalog.csv"}),
        ("WF004", "Generate SEO description", {"product_name": "Premium Keyboard", "category": "Electronics"}),
        ("WF005", "Where is my order?", {"order_id": "ORD-1001"}),
        ("WF006", "Find duplicates", {"catalog_csv_path": "data/sample_products_catalog.csv"}),
        ("WF007", "Campaign brief", {"campaign_goal": "Summer Sale", "dates": "July 1-15"}),
    ]

    for wid, req_text, inputs in workflows_to_test:
        r = LLMWorkflowRouter(provider=FakeLLMProvider(default_response=json.dumps({
            "workflow_id": wid, "confidence": 0.95, "reasoning": "R", "extracted_inputs": inputs, "requires_clarification": False
        })))
        rep = WorkflowOrchestrator(router=r).run(req_text, **inputs)
        assert rep.status == "success", f"Regression failure in {wid}: {rep.errors}"
        assert rep.selected_workflow_id == wid
