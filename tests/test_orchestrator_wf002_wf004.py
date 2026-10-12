"""Integration and end-to-end pipeline tests for WF002, WF003, and WF004."""

import json
from pathlib import Path
import pytest

from app.agent.provider import FakeLLMProvider
from app.agent.router import LLMWorkflowRouter
from app.orchestrator import WorkflowOrchestrator


def test_orchestrator_wf002_full_pipeline():
    """End-to-end execution of WF002 — Product Price Validation via WorkflowOrchestrator."""
    fake_json = json.dumps({
        "workflow_id": "WF002",
        "confidence": 0.95,
        "reasoning": "Matches Product Price Validation trigger.",
        "extracted_inputs": {},
        "requires_clarification": False,
    })
    router = LLMWorkflowRouter(provider=FakeLLMProvider(default_response=fake_json))
    orchestrator = WorkflowOrchestrator(router=router)

    report = orchestrator.run(
        "Find products where vendor price differs by more than 10%.",
        internal_csv_path="data/sample_internal_prices.csv",
        vendor_csv_path="data/sample_vendor_prices.csv",
    )

    assert report.status == "success"
    assert report.selected_workflow_id == "WF002"
    assert report.selected_workflow_name == "Product Price Validation"
    assert len(report.steps) == 5

    # Check all 5 steps succeeded
    expected_steps = [
        "Load product prices",
        "match products by SKU",
        "compare internal and vendor prices",
        "calculate percentage difference",
        "flag exceptions",
    ]
    for step_rep, exp_name in zip(report.steps, expected_steps):
        assert step_rep.step_name == exp_name
        assert step_rep.status == "completed"
        assert step_rep.error is None

    # Check final output
    final = report.final_output
    assert isinstance(final, dict)
    assert final["total_matched"] == 7
    assert final["exception_count"] == 3
    assert len(final["exceptions"]) == 3
    exception_skus = [e["sku"] for e in final["exceptions"]]
    assert "SKU-002" in exception_skus  # +15%
    assert "SKU-004" in exception_skus  # -15%
    assert "SKU-006" in exception_skus  # +25%

    # Boundary item (exact 10%) must NOT be in exceptions
    assert "SKU-003" not in exception_skus
    assert "SKU-007" not in exception_skus


def test_orchestrator_wf003_full_pipeline():
    """End-to-end execution of WF003 — Vendor File Processing via WorkflowOrchestrator."""
    fake_json = json.dumps({
        "workflow_id": "WF003",
        "confidence": 0.95,
        "reasoning": "Matches Vendor File Processing trigger.",
        "extracted_inputs": {},
        "requires_clarification": False,
    })
    router = LLMWorkflowRouter(provider=FakeLLMProvider(default_response=fake_json))
    orchestrator = WorkflowOrchestrator(router=router)

    report = orchestrator.run(
        "Process this vendor spreadsheet and show invalid rows.",
        file_path="data/sample_vendor_catalog.csv",
    )

    assert report.status == "success"
    assert report.selected_workflow_id == "WF003"
    assert report.selected_workflow_name == "Vendor File Processing"
    assert len(report.steps) == 6

    # Check all 6 steps completed
    expected_steps = [
        "Read file",
        "detect columns",
        "normalize column names",
        "validate required fields",
        "identify invalid rows",
        "produce cleaned dataset",
    ]
    for step_rep, exp_name in zip(report.steps, expected_steps):
        assert step_rep.step_name == exp_name
        assert step_rep.status == "completed"

    final = report.final_output
    assert isinstance(final, dict)
    assert final["total_processed"] == 8
    assert final["valid_count"] == 4
    assert final["invalid_count"] == 4
    assert len(final["cleaned_records"]) == 4
    assert len(final["invalid_records"]) == 4


def test_orchestrator_wf004_full_pipeline():
    """End-to-end execution of WF004 — Product Description Generator via WorkflowOrchestrator."""
    fake_json = json.dumps({
        "workflow_id": "WF004",
        "confidence": 0.95,
        "reasoning": "Matches Product Description Generator trigger.",
        "extracted_inputs": {
            "product_name": "Premium Noise-Canceling Headphones",
            "category": "Audio Equipment",
            "material": "Brushed Aluminum and Memory Foam",
            "color": "Matte Silver",
            "target_audience": "Audiophiles and Travelers",
        },
        "requires_clarification": False,
    })
    router = LLMWorkflowRouter(provider=FakeLLMProvider(default_response=fake_json))
    orchestrator = WorkflowOrchestrator(router=router)

    report = orchestrator.run("Generate SEO content for this product.")

    assert report.status == "success"
    assert report.selected_workflow_id == "WF004"
    assert report.selected_workflow_name == "Product Description Generator"
    assert len(report.steps) == 5

    # Check all 5 steps completed
    expected_steps = [
        "Validate required attributes",
        "create product description",
        "generate short description",
        "generate SEO title",
        "generate meta description",
    ]
    for step_rep, exp_name in zip(report.steps, expected_steps):
        assert step_rep.step_name == exp_name
        assert step_rep.status == "completed"

    final = report.final_output
    assert isinstance(final, dict)
    assert final["product_name"] == "Premium Noise-Canceling Headphones"
    assert "product_description" in final
    assert "short_description" in final
    assert "seo_title" in final
    assert "meta_description" in final
    assert final["is_simulated"] is True


def test_orchestrator_wf004_missing_product_name_fails():
    """Verify that WF004 fails accurately when required product_name is absent."""
    fake_json = json.dumps({
        "workflow_id": "WF004",
        "confidence": 0.90,
        "reasoning": "Product content request.",
        "extracted_inputs": {},  # No product_name provided!
        "requires_clarification": False,
    })
    router = LLMWorkflowRouter(provider=FakeLLMProvider(default_response=fake_json))
    orchestrator = WorkflowOrchestrator(router=router)

    # Calling without product_name should fail on step 1
    report = orchestrator.run("Generate SEO content for my item.")

    assert report.status in ("failed", "partial_failure")
    assert len(report.errors) > 0
    assert "required attribute 'product_name' is missing" in report.errors[0].lower()


def test_cli_mock_route_wf002(monkeypatch, capsys):
    """Test CLI --mock-route WF002."""
    from app.main import main

    monkeypatch.setattr(
        "sys.argv",
        ["app.main", "--mock-route", "WF002", "Find products where vendor price differs by more than 10%."],
    )
    main()

    captured = capsys.readouterr()
    assert "SUCCESS" in captured.out
    assert "WF002 (Product Price Validation)" in captured.out
    assert "SKU-002" in captured.out
    assert "EXCEPTION (>10%)" in captured.out
    assert "COMPLIANT" in captured.out


def test_cli_mock_route_wf003(monkeypatch, capsys):
    """Test CLI --mock-route WF003."""
    from app.main import main

    monkeypatch.setattr(
        "sys.argv",
        ["app.main", "--mock-route", "WF003", "Process this vendor spreadsheet and show invalid rows."],
    )
    main()

    captured = capsys.readouterr()
    assert "SUCCESS" in captured.out
    assert "WF003 (Vendor File Processing)" in captured.out
    assert "Valid Records Cleaned: 4" in captured.out
    assert "Invalid Rows Flagged:  4" in captured.out


def test_cli_mock_route_wf004(monkeypatch, capsys):
    """Test CLI --mock-route WF004."""
    from app.main import main

    monkeypatch.setattr(
        "sys.argv",
        ["app.main", "--mock-route", "WF004", "Generate SEO content for this product."],
    )
    main()

    captured = capsys.readouterr()
    assert "SUCCESS" in captured.out
    assert "WF004 (Product Description Generator)" in captured.out
    assert "Ergonomic Desk Chair" in captured.out
    assert "SEO Title:" in captured.out
    assert "Meta Description:" in captured.out
    assert "simulated" in captured.out.lower()


def test_wf001_regression_remains_intact():
    """Ensure WF001 full pipeline continues to execute and succeed with all 5 steps."""
    fake_json = json.dumps({
        "workflow_id": "WF001",
        "confidence": 0.95,
        "reasoning": "Restock check.",
        "extracted_inputs": {},
        "requires_clarification": False,
    })
    router = LLMWorkflowRouter(provider=FakeLLMProvider(default_response=fake_json))
    orchestrator = WorkflowOrchestrator(router=router)

    report = orchestrator.run("Which products need restocking?")

    assert report.status == "success"
    assert report.selected_workflow_id == "WF001"
    assert len(report.steps) == 5
    assert report.final_output["restock_required_count"] == 4
