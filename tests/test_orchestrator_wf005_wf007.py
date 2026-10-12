"""Integration and end-to-end pipeline tests for WF005, WF006, and WF007."""

import json
from pathlib import Path
import pytest

from app.agent.provider import FakeLLMProvider
from app.agent.router import LLMWorkflowRouter
from app.orchestrator import WorkflowOrchestrator


def test_orchestrator_wf005_full_pipeline_known_order_with_shipment():
    """End-to-end execution of WF005 — Customer Order Status with known order and shipment."""
    fake_json = json.dumps({
        "workflow_id": "WF005",
        "confidence": 0.95,
        "reasoning": "Matches Customer Order Status trigger.",
        "extracted_inputs": {
            "order_id": "ORD-1001",
        },
        "requires_clarification": False,
    })
    router = LLMWorkflowRouter(provider=FakeLLMProvider(default_response=fake_json))
    orchestrator = WorkflowOrchestrator(router=router)

    report = orchestrator.run("What is the status of order ORD-1001?")

    assert report.status == "success"
    assert report.selected_workflow_id == "WF005"
    assert report.selected_workflow_name == "Customer Order Status"
    assert len(report.steps) == 5

    expected_steps = [
        "Validate identifier",
        "search order data",
        "retrieve order status",
        "retrieve shipment information",
        "summarize current status",
    ]
    for step_rep, exp_name in zip(report.steps, expected_steps):
        assert step_rep.step_name == exp_name
        assert step_rep.status == "completed"
        assert step_rep.error is None

    final = report.final_output
    assert isinstance(final, dict)
    assert final["order_found"] is True
    assert final["order_id"] == "ORD-1001"
    assert len(final["orders"]) == 1
    order_item = final["orders"][0]
    assert order_item["order_id"] == "ORD-1001"
    assert order_item["order_status"] == "SHIPPED"
    assert order_item["has_shipment"] is True
    assert order_item["tracking_number"] == "TRK-987654321"
    assert order_item["carrier"] == "FastShip Express"
    assert final["request_another_identifier"] is False
    assert final["is_simulated"] is True


def test_orchestrator_wf005_unknown_order_asks_for_another_identifier():
    """Verify that WF005 asks for another identifier when order cannot be located."""
    fake_json = json.dumps({
        "workflow_id": "WF005",
        "confidence": 0.95,
        "reasoning": "Matches Customer Order Status trigger.",
        "extracted_inputs": {
            "order_id": "UNKNOWN-9999",
        },
        "requires_clarification": False,
    })
    router = LLMWorkflowRouter(provider=FakeLLMProvider(default_response=fake_json))
    orchestrator = WorkflowOrchestrator(router=router)

    report = orchestrator.run("Status for order UNKNOWN-9999 please.")

    assert report.status == "success"
    assert report.selected_workflow_id == "WF005"
    assert len(report.steps) == 5

    final = report.final_output
    assert isinstance(final, dict)
    assert final["order_found"] is False
    assert final["request_another_identifier"] is True
    assert "no order found" in final["summary"].lower()
    assert "please provide a valid order id" in final["summary"].lower()


def test_orchestrator_wf006_full_pipeline():
    """End-to-end execution of WF006 — Duplicate Product Detection via WorkflowOrchestrator."""
    fake_json = json.dumps({
        "workflow_id": "WF006",
        "confidence": 0.95,
        "reasoning": "Matches Duplicate Product Detection trigger.",
        "extracted_inputs": {
            "catalog_csv_path": "data/sample_products_catalog.csv",
        },
        "requires_clarification": False,
    })
    router = LLMWorkflowRouter(provider=FakeLLMProvider(default_response=fake_json))
    orchestrator = WorkflowOrchestrator(router=router)

    report = orchestrator.run("Identify duplicate products in our catalog.")

    assert report.status == "success"
    assert report.selected_workflow_id == "WF006"
    assert report.selected_workflow_name == "Duplicate Product Detection"
    assert len(report.steps) == 6

    expected_steps = [
        "Load products",
        "normalize names/SKUs",
        "compare identifiers",
        "compare product attributes",
        "group likely duplicates",
        "assign confidence",
    ]
    for step_rep, exp_name in zip(report.steps, expected_steps):
        assert step_rep.step_name == exp_name
        assert step_rep.status == "completed"

    final = report.final_output
    assert isinstance(final, dict)
    assert final["definite_duplicates_count"] == 1
    assert final["likely_duplicates_count"] >= 1
    assert len(final["duplicate_candidates"]) >= 2

    # Verify exact SKU candidate
    exact_candidates = [c for c in final["duplicate_candidates"] if c["match_type"] == "exact_sku_match"]
    assert len(exact_candidates) == 1
    assert exact_candidates[0]["confidence"] == "definite"
    assert exact_candidates[0]["primary_sku"] == "SKU-1001"
    assert exact_candidates[0]["duplicate_sku"] == "SKU-1001"

    # Verify limitations note is present
    assert "limitations" in final
    assert len(final["limitations"]) > 0


def test_orchestrator_wf007_full_pipeline():
    """End-to-end execution of WF007 — Marketing Campaign Brief via WorkflowOrchestrator."""
    fake_json = json.dumps({
        "workflow_id": "WF007",
        "confidence": 0.95,
        "reasoning": "Matches Marketing Campaign Brief trigger.",
        "extracted_inputs": {
            "campaign_goal": "Drive 25% increase in autumn boot sales",
            "target_audience": "Outdoor enthusiasts and urban commuters",
            "dates": "October 1 - October 31",
            "promotion": "15% off with code AUTUMN15",
            "products": ["Waterproof Trail Boots", "Urban Leather Chelsea"],
        },
        "requires_clarification": False,
    })
    router = LLMWorkflowRouter(provider=FakeLLMProvider(default_response=fake_json))
    orchestrator = WorkflowOrchestrator(router=router)

    report = orchestrator.run("Generate a marketing campaign brief for autumn boots.")

    assert report.status == "success"
    assert report.selected_workflow_id == "WF007"
    assert report.selected_workflow_name == "Marketing Campaign Brief"
    assert len(report.steps) == 6

    expected_steps = [
        "Validate inputs",
        "identify campaign objective",
        "summarize products",
        "create messaging",
        "create channel recommendations",
        "create campaign checklist",
    ]
    for step_rep, exp_name in zip(report.steps, expected_steps):
        assert step_rep.step_name == exp_name
        assert step_rep.status == "completed"

    final = report.final_output
    assert isinstance(final, dict)
    assert final["campaign_goal"] == "Drive 25% increase in autumn boot sales"
    assert final["timeline"] == "October 1 - October 31"
    assert "objectives" in final
    assert "messaging" in final
    assert "channels" in final
    assert "execution_checklist" in final
    assert final["is_simulated"] is True


def test_orchestrator_wf007_missing_dates_fails():
    """Verify that WF007 halts safely when required dates are not provided."""
    fake_json = json.dumps({
        "workflow_id": "WF007",
        "confidence": 0.90,
        "reasoning": "Campaign brief request.",
        "extracted_inputs": {
            "campaign_goal": "Boost brand awareness",
            # dates omitted!
        },
        "requires_clarification": False,
    })
    router = LLMWorkflowRouter(provider=FakeLLMProvider(default_response=fake_json))
    orchestrator = WorkflowOrchestrator(router=router)

    report = orchestrator.run("Create a marketing brief.")

    assert report.status in ("failed", "partial_failure")
    assert len(report.errors) > 0
    assert "dates" in report.errors[0].lower()


def test_cli_mock_route_wf005(monkeypatch, capsys):
    """Test CLI --mock-route WF005."""
    from app.main import main

    monkeypatch.setattr(
        "sys.argv",
        [
            "app.main",
            "--mock-route",
            "WF005",
            "--order-id",
            "ORD-1001",
            "What is the status of order ORD-1001?",
        ],
    )
    main()

    captured = capsys.readouterr()
    assert "SUCCESS" in captured.out
    assert "WF005 (Customer Order Status)" in captured.out
    assert "ORD-1001" in captured.out
    assert "SHIPPED" in captured.out
    assert "TRK-987654321" in captured.out
    assert "SIMULATED" in captured.out


def test_cli_mock_route_wf006(monkeypatch, capsys):
    """Test CLI --mock-route WF006."""
    from app.main import main

    monkeypatch.setattr(
        "sys.argv",
        [
            "app.main",
            "--mock-route",
            "WF006",
            "Find duplicates in product catalog",
        ],
    )
    main()

    captured = capsys.readouterr()
    assert "SUCCESS" in captured.out
    assert "WF006 (Duplicate Product Detection)" in captured.out
    assert "SKU-1001" in captured.out
    assert "DEFINITE" in captured.out
    assert "LIMITATIONS & METHODOLOGY" in captured.out


def test_cli_mock_route_wf007(monkeypatch, capsys):
    """Test CLI --mock-route WF007."""
    from app.main import main

    monkeypatch.setattr(
        "sys.argv",
        [
            "app.main",
            "--mock-route",
            "WF007",
            "--campaign-goal",
            "Q4 Holiday Gift Guide Campaign",
            "--dates",
            "Nov 15 - Dec 24",
            "--promotion",
            "20% off all bundles with HOLIDAY20",
            "Generate holiday campaign brief",
        ],
    )
    main()

    captured = capsys.readouterr()
    assert "SUCCESS" in captured.out
    assert "WF007 (Marketing Campaign Brief)" in captured.out
    assert "Q4 Holiday Gift Guide Campaign" in captured.out
    assert "Nov 15 - Dec 24" in captured.out
    assert "Execution Checklist:" in captured.out
    assert "SIMULATED" in captured.out


def test_all_workflows_regression_wf001_through_wf004():
    """Verify that WF001 through WF004 continue to execute and succeed."""
    # WF001
    r1 = LLMWorkflowRouter(provider=FakeLLMProvider(default_response=json.dumps({
        "workflow_id": "WF001", "confidence": 0.95, "reasoning": "R", "extracted_inputs": {}, "requires_clarification": False
    })))
    rep1 = WorkflowOrchestrator(router=r1).run("Restock check")
    assert rep1.status == "success"
    assert rep1.final_output["restock_required_count"] == 4

    # WF002
    r2 = LLMWorkflowRouter(provider=FakeLLMProvider(default_response=json.dumps({
        "workflow_id": "WF002", "confidence": 0.95, "reasoning": "R", "extracted_inputs": {}, "requires_clarification": False
    })))
    rep2 = WorkflowOrchestrator(router=r2).run(
        "Price check",
        internal_csv_path="data/sample_internal_prices.csv",
        vendor_csv_path="data/sample_vendor_prices.csv",
    )
    assert rep2.status == "success"
    assert rep2.final_output["exception_count"] == 3

    # WF003
    r3 = LLMWorkflowRouter(provider=FakeLLMProvider(default_response=json.dumps({
        "workflow_id": "WF003", "confidence": 0.95, "reasoning": "R", "extracted_inputs": {}, "requires_clarification": False
    })))
    rep3 = WorkflowOrchestrator(router=r3).run("Vendor file", file_path="data/sample_vendor_catalog.csv")
    assert rep3.status == "success"
    assert rep3.final_output["valid_count"] == 4

    # WF004
    r4 = LLMWorkflowRouter(provider=FakeLLMProvider(default_response=json.dumps({
        "workflow_id": "WF004", "confidence": 0.95, "reasoning": "R",
        "extracted_inputs": {"product_name": "Test Wireless Mouse"}, "requires_clarification": False
    })))
    rep4 = WorkflowOrchestrator(router=r4).run("SEO description")
    assert rep4.status == "success"
    assert rep4.final_output["product_name"] == "Test Wireless Mouse"
