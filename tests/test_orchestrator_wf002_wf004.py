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


def test_orchestrator_wf004_missing_product_name_requests_clarification():
    """Decision 3: a missing required product_name returns needs_clarification (was: failed)."""
    fake_json = json.dumps({
        "workflow_id": "WF004",
        "confidence": 0.95,
        "reasoning": "Matches Product Description Generator trigger.",
        "extracted_inputs": {},
        "requires_clarification": False,
    })
    router = LLMWorkflowRouter(provider=FakeLLMProvider(default_response=fake_json))
    report = WorkflowOrchestrator(router=router).run("Generate SEO content for this product.")

    assert report.status == "needs_clarification"
    assert report.clarification_required is True
    assert report.final_output is None
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
    assert "SKU-008" in captured.out
    assert "SKU-099" in captured.out
    assert "Unmatched Vendor SKUs: 1 record(s)" in captured.out
    assert "Unmatched Internal SKUs: 1 record(s)" in captured.out


def test_cli_mock_route_wf003(monkeypatch, capsys, tmp_path):
    """Test CLI --mock-route WF003."""
    from app.main import main

    monkeypatch.setattr(
        "sys.argv",
        ["app.main", "--mock-route", "WF003", "--output-dir", str(tmp_path), "Process this vendor spreadsheet and show invalid rows."],
    )
    main()

    captured = capsys.readouterr()
    assert "SUCCESS" in captured.out
    assert "WF003 (Vendor File Processing)" in captured.out
    assert "Valid Records Cleaned: 4" in captured.out
    assert "Invalid Rows Flagged:  4" in captured.out


def test_cli_mock_route_wf004_without_product_does_not_fabricate(monkeypatch, capsys):
    """WF004 must NOT invent product attributes. Missing product_name requests clarification (exit 4).

    Corrected expectation: the earlier version asserted fabricated defaults and SUCCESS.
    """
    from app.main import main

    monkeypatch.setattr(
        "sys.argv",
        ["app.main", "--mock-route", "WF004", "Generate SEO content for this product."],
    )
    with pytest.raises(SystemExit) as exc:
        main()
    assert exc.value.code == 4

    captured = capsys.readouterr()
    assert "Ergonomic Desk Chair" not in captured.out
    assert "Breathable Mesh" not in captured.out
    assert "product_name" in captured.out



def test_cli_mock_route_wf004_with_explicit_product_succeeds(monkeypatch, capsys):
    """Explicitly supplied product input still produces a description."""
    from app.main import main

    monkeypatch.setattr(
        "sys.argv",
        [
            "app.main", "--mock-route", "WF004",
            "--product-name", "Ergonomic Desk Chair",
            "Generate SEO content for this product.",
        ],
    )
    main()

    captured = capsys.readouterr()
    assert "SUCCESS" in captured.out
    assert "WF004 (Product Description Generator)" in captured.out
    assert "Ergonomic Desk Chair" in captured.out
    assert "SEO Title:" in captured.out


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


def test_orchestrator_wf002_exact_boundary_and_precision_e2e(tmp_path: Path):
    """E2E test with custom CSVs verifying exact boundary and precision preservation."""
    int_csv = tmp_path / "internal_boundary.csv"
    int_csv.write_text(
        "sku,product_name,internal_price,currency\n"
        "SKU-B1,Boundary 3.30,3.30,USD\n"
        "SKU-B2,Precision 100,100.00,USD\n"
    )
    ven_csv = tmp_path / "vendor_boundary.csv"
    ven_csv.write_text(
        "sku,vendor_name,vendor_price,currency\n"
        "SKU-B1,Vendor Alpha,3.63,USD\n"
        "SKU-B2,Vendor Alpha,110.004,USD\n"
    )

    fake_json = json.dumps({
        "workflow_id": "WF002",
        "confidence": 0.95,
        "reasoning": "Price validation",
        "extracted_inputs": {},
        "requires_clarification": False,
    })
    router = LLMWorkflowRouter(provider=FakeLLMProvider(default_response=fake_json))
    orchestrator = WorkflowOrchestrator(router=router)

    report = orchestrator.run(
        "Validate prices",
        internal_csv_path=str(int_csv),
        vendor_csv_path=str(ven_csv),
    )

    assert report.status == "success"
    assert len(report.steps) == 5
    final = report.final_output
    assert final["total_matched"] == 2
    assert final["exception_count"] == 1

    by_sku = {item["sku"]: item for item in final["matched_products"]}
    # 3.30 vs 3.63: exactly 10.0%, NOT an exception
    assert by_sku["SKU-B1"]["is_exception"] is False
    assert by_sku["SKU-B1"]["validation_status"] == "COMPLIANT"
    assert by_sku["SKU-B1"]["percentage_difference"] == 10.0

    # 100.00 vs 110.004: raw difference > 10.0%, IS an exception, display rounded to 10.0%
    assert by_sku["SKU-B2"]["is_exception"] is True
    assert by_sku["SKU-B2"]["validation_status"] == "EXCEPTION_EXCEEDS_10_PERCENT"
    assert by_sku["SKU-B2"]["percentage_difference"] == 10.0

    # Ensure no internal raw keys leaked
    for item in final["matched_products"]:
        assert "_raw_percentage_difference" not in item


def test_orchestrator_wf002_malformed_unquoted_csv_aborts(tmp_path: Path):
    """WF002 aborts immediately when unquoted commas corrupt CSV column structure."""
    bad_int = tmp_path / "bad_internal.csv"
    bad_int.write_text(
        "sku,product_name,internal_price,currency\n"
        "SKU-01,Camera,$1,200.00,USD\n"
    )
    ven = tmp_path / "ven.csv"
    ven.write_text("sku,vendor_name,vendor_price,currency\nSKU-01,Ven,1200.00,USD\n")

    fake_json = json.dumps({
        "workflow_id": "WF002",
        "confidence": 0.95,
        "reasoning": "Price validation",
        "extracted_inputs": {},
        "requires_clarification": False,
    })
    router = LLMWorkflowRouter(provider=FakeLLMProvider(default_response=fake_json))
    orchestrator = WorkflowOrchestrator(router=router)

    report = orchestrator.run(
        "Validate prices",
        internal_csv_path=str(bad_int),
        vendor_csv_path=str(ven),
    )

    assert report.status in ("failed", "partial_failure")
    assert any("line 2 has 5 columns, expected 4" in err for err in report.errors)
    assert any("Unquoted commas" in err for err in report.errors)


def test_orchestrator_wf002_duplicate_sku_aborts(tmp_path: Path):
    """WF002 aborts on step 1 when duplicate SKU appears in internal catalog."""
    dup_int = tmp_path / "dup_internal.csv"
    dup_int.write_text(
        "sku,product_name,internal_price,currency\n"
        "SKU-01,Widget A,10.00,USD\n"
        "sku-01,Widget B,12.00,USD\n"
    )
    ven = tmp_path / "ven.csv"
    ven.write_text("sku,vendor_name,vendor_price,currency\nSKU-01,Ven,10.00,USD\n")

    fake_json = json.dumps({
        "workflow_id": "WF002",
        "confidence": 0.95,
        "reasoning": "Price validation",
        "extracted_inputs": {},
        "requires_clarification": False,
    })
    router = LLMWorkflowRouter(provider=FakeLLMProvider(default_response=fake_json))
    orchestrator = WorkflowOrchestrator(router=router)

    report = orchestrator.run(
        "Validate prices",
        internal_csv_path=str(dup_int),
        vendor_csv_path=str(ven),
    )

    assert report.status in ("failed", "partial_failure")
    assert any("Duplicate internal SKU" in err for err in report.errors)


def test_orchestrator_wf002_currency_mismatch_aborts(tmp_path: Path):
    """WF002 aborts on step 2 when matched SKU has mismatched currencies."""
    int_csv = tmp_path / "int.csv"
    int_csv.write_text(
        "sku,product_name,internal_price,currency\n"
        "SKU-01,Widget,10.00,USD\n"
    )
    ven_csv = tmp_path / "ven.csv"
    ven_csv.write_text(
        "sku,vendor_name,vendor_price,currency\n"
        "SKU-01,Ven,10.00,EUR\n"
    )

    fake_json = json.dumps({
        "workflow_id": "WF002",
        "confidence": 0.95,
        "reasoning": "Price validation",
        "extracted_inputs": {},
        "requires_clarification": False,
    })
    router = LLMWorkflowRouter(provider=FakeLLMProvider(default_response=fake_json))
    orchestrator = WorkflowOrchestrator(router=router)

    report = orchestrator.run(
        "Validate prices",
        internal_csv_path=str(int_csv),
        vendor_csv_path=str(ven_csv),
    )

    assert report.status in ("failed", "partial_failure")
    assert any("Currency mismatch" in err for err in report.errors)


def test_orchestrator_wf002_blank_currency_aborts(tmp_path: Path):
    """WF002 aborts when a row with currency column has a blank currency value."""
    int_csv = tmp_path / "int.csv"
    int_csv.write_text(
        "sku,product_name,internal_price,currency\n"
        "SKU-01,Widget,10.00,   \n"
    )
    ven_csv = tmp_path / "ven.csv"
    ven_csv.write_text(
        "sku,vendor_name,vendor_price,currency\n"
        "SKU-01,Ven,10.00,USD\n"
    )

    fake_json = json.dumps({
        "workflow_id": "WF002",
        "confidence": 0.95,
        "reasoning": "Price validation",
        "extracted_inputs": {},
        "requires_clarification": False,
    })
    router = LLMWorkflowRouter(provider=FakeLLMProvider(default_response=fake_json))
    orchestrator = WorkflowOrchestrator(router=router)

    report = orchestrator.run(
        "Validate prices",
        internal_csv_path=str(int_csv),
        vendor_csv_path=str(ven_csv),
    )

    assert report.status in ("failed", "partial_failure")
    assert any("Missing or blank currency" in err for err in report.errors)


def test_orchestrator_wf002_threshold_cannot_be_overridden_to_15_percent(tmp_path: Path):
    """WF002 enforces the official fixed 10% threshold; router/user 15% cannot change policy."""
    from decimal import Decimal

    int_csv = tmp_path / "int_12pct.csv"
    int_csv.write_text(
        "sku,product_name,internal_price,currency\n"
        "SKU-12,Product 12% Diff,100.00,USD\n"
    )
    ven_csv = tmp_path / "ven_12pct.csv"
    ven_csv.write_text(
        "sku,vendor_name,vendor_price,currency\n"
        "SKU-12,Vendor Alpha,112.00,USD\n"
    )

    # Simulated router returning WF002 with extracted threshold argument
    fake_json = json.dumps({
        "workflow_id": "WF002",
        "confidence": 0.95,
        "reasoning": "Price validation with custom threshold requested",
        "extracted_inputs": {"threshold": 15.0},
        "requires_clarification": False,
    })
    router = LLMWorkflowRouter(provider=FakeLLMProvider(default_response=fake_json))
    orchestrator = WorkflowOrchestrator(router=router)

    # Explicitly pass threshold=15.0 as runtime input
    report = orchestrator.run(
        "Find products where vendor price differs by more than 15%.",
        internal_csv_path=str(int_csv),
        vendor_csv_path=str(ven_csv),
        threshold=15.0,
    )

    assert report.status == "success"
    final = report.final_output
    # 112.00 vs 100.00 is 12.0% difference:
    # Under fixed 10% policy, it MUST be flagged as an exception!
    assert final["exception_count"] == 1
    assert len(final["exceptions"]) == 1
    exc_item = final["exceptions"][0]
    assert exc_item["sku"] == "SKU-12"
    assert exc_item["is_exception"] is True
    assert exc_item["validation_status"] == "EXCEPTION_EXCEEDS_10_PERCENT"
    assert "10.0% threshold" in final["summary"]


def test_orchestrator_wf002_end_to_end_precision_preservation_from_csv(tmp_path: Path):
    """True E2E test using CSV input proving precision is preserved across all models and serialization."""
    from decimal import Decimal

    int_csv = tmp_path / "int_prec.csv"
    int_csv.write_text(
        "sku,product_name,internal_price,currency\n"
        "SKU-P1,Micro-Calibration Sensor,100.0000,USD\n"
    )
    ven_csv = tmp_path / "ven_prec.csv"
    ven_csv.write_text(
        "sku,vendor_name,vendor_price,currency\n"
        "SKU-P1,Precision Dynamics,110.0040,USD\n"
    )

    fake_json = json.dumps({
        "workflow_id": "WF002",
        "confidence": 0.95,
        "reasoning": "Price validation",
        "extracted_inputs": {},
        "requires_clarification": False,
    })
    router = LLMWorkflowRouter(provider=FakeLLMProvider(default_response=fake_json))
    orchestrator = WorkflowOrchestrator(router=router)

    report = orchestrator.run(
        "Validate high precision pricing.",
        internal_csv_path=str(int_csv),
        vendor_csv_path=str(ven_csv),
    )

    assert report.status == "success"
    final = report.final_output
    assert final["total_matched"] == 1
    assert final["exception_count"] == 1

    matched = final["matched_products"][0]
    # Check that exact Decimal types are preserved end-to-end
    assert isinstance(matched["internal_price"], Decimal)
    assert isinstance(matched["vendor_price"], Decimal)
    assert matched["internal_price"] == Decimal("100.0000")
    assert matched["vendor_price"] == Decimal("110.0040")
    assert str(matched["vendor_price"]) == "110.0040"

    # Check authoritative comparison flagged 110.0040 > 110.0000
    assert matched["is_exception"] is True
    assert matched["validation_status"] == "EXCEPTION_EXCEEDS_10_PERCENT"
    assert matched["percentage_difference"] == 10.0

    # Verify report is cleanly serializable via model_dump_json()
    json_repr = report.model_dump_json()
    assert "110.0040" in json_repr
    assert "EXCEPTION_EXCEEDS_10_PERCENT" in json_repr
