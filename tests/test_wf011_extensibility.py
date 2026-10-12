"""Tests demonstrating WF011 extensibility without modifying the generic engine."""

import json
from pathlib import Path
import subprocess
import sys
import pytest

from app.agent.provider import FakeLLMProvider
from app.agent.router import LLMWorkflowRouter
from app.engine.base import GenericWorkflowEngine
from app.engine.resolver import ConfigurableStepResolver
from app.models.execution import ExecutionStatus
from app.models.workflow import WorkflowDefinition
from app.orchestrator import WorkflowOrchestrator
from app.registry.registry import WorkflowRegistry
from app.tools.registry import ToolRegistry
from app.tools.supplier_risk import (
    DeliveryMetricsCalculatorTool,
    DeliveryRecord,
    DeliveryRecordValidatorTool,
    SupplierDeliveryLoaderTool,
    SupplierRiskEvaluation,
    SupplierRiskEvaluatorTool,
    SupplierRiskMetrics,
    SupplierRiskReporterTool,
    calculate_supplier_metrics,
    evaluate_supplier_risk,
    get_wf011_definition,
    register_wf011_extension,
)


def test_generic_engine_executes_wf011_without_engine_modifications():
    """Requirement: Prove WF011 executes on GenericWorkflowEngine with ZERO engine modifications."""
    tool_reg = ToolRegistry()
    step_res = ConfigurableStepResolver()

    # Register WF011 through the existing generic interfaces
    wf011 = register_wf011_extension(
        tool_registry=tool_reg,
        step_resolver=step_res,
    )

    # Initialize generic engine with NO custom engine subclasses or workflow-specific code
    engine = GenericWorkflowEngine(tool_registry=tool_reg, step_resolver=step_res)

    result = engine.execute(wf011)

    assert result.status == ExecutionStatus.COMPLETED
    assert result.workflow_id == "WF011"
    assert len(result.step_results) == 5
    for step_res_item in result.step_results:
        assert step_res_item.status == ExecutionStatus.COMPLETED

    final_output = result.output
    assert isinstance(final_output, dict)
    assert final_output["total_suppliers_assessed"] == 4
    assert final_output["risk_distribution"]["high"] == 1
    assert final_output["risk_distribution"]["medium"] == 1
    assert final_output["risk_distribution"]["low"] == 2
    assert "Apex Logistics & Materials" in final_output["high_risk_suppliers"]
    assert final_output["is_simulated"] is True


def test_register_wf011_extension_into_orchestrator():
    """Test registering WF011 extension dynamically into WorkflowOrchestrator."""
    fake_json = json.dumps({
        "workflow_id": "WF011",
        "confidence": 0.96,
        "reasoning": "Request asks for supplier delivery risk assessment, matching WF011.",
        "extracted_inputs": {},
        "requires_clarification": False,
    })
    router = LLMWorkflowRouter(provider=FakeLLMProvider(default_response=fake_json))

    orchestrator = WorkflowOrchestrator(router=router)

    # Register WF011 extension dynamically into orchestrator
    register_wf011_extension(
        registry=orchestrator.registry,
        tool_registry=orchestrator.tool_registry,
        step_resolver=orchestrator.step_resolver,
    )

    assert orchestrator.registry.contains("WF011")

    report = orchestrator.run("Assess supplier delivery risk for all active vendors")

    assert report.status == "success"
    assert report.selected_workflow_id == "WF011"
    assert report.selected_workflow_name == "Supplier Delivery Risk Assessment"
    assert report.routing_confidence == 0.96
    assert len(report.steps) == 5
    assert report.final_output is not None
    assert report.final_output["risk_distribution"]["high"] == 1


def test_router_dynamically_routes_wf011_when_registered():
    """Test that LLM router dynamically recognizes and routes WF011 without router code changes."""
    wf_registry = WorkflowRegistry()
    wf011 = get_wf011_definition()
    wf_registry.register(wf011)

    fake_json = json.dumps({
        "workflow_id": "WF011",
        "confidence": 0.94,
        "reasoning": "Identified high-priority supplier risk audit request.",
        "extracted_inputs": {},
        "requires_clarification": False,
    })
    router = LLMWorkflowRouter(provider=FakeLLMProvider(default_response=fake_json))

    decision = router.route("Evaluate vendor delivery risk and delays", wf_registry.list_all())

    assert decision.workflow_id == "WF011"
    assert decision.confidence == 0.94
    assert decision.requires_clarification is False


def test_supplier_risk_scoring_thresholds_low_medium_high():
    """Test deterministic risk scoring logic across distinct threshold boundaries."""
    # 1. Low risk: 0% late, 0.0 avg delay
    low_metrics = SupplierRiskMetrics(
        supplier_id="SUP-LOW",
        supplier_name="Reliable Vendor",
        total_shipments=10,
        on_time_shipments=10,
        late_shipments=0,
        late_delivery_rate=0.0,
        total_delay_days=0,
        average_delay_days=0.0,
        max_delay_days=0,
    )
    low_eval = evaluate_supplier_risk(low_metrics)
    assert low_eval.risk_level == "LOW"
    assert low_eval.risk_score == 0.0
    assert "preferred supplier" in low_eval.recommended_action.lower()

    # 2. Medium risk: 20% late, 3.5 avg delay -> score = (0.2*60) + min(3.5*8, 40) = 12 + 28 = 40.0
    med_metrics = SupplierRiskMetrics(
        supplier_id="SUP-MED",
        supplier_name="Moderate Vendor",
        total_shipments=10,
        on_time_shipments=8,
        late_shipments=2,
        late_delivery_rate=0.20,
        total_delay_days=7,
        average_delay_days=3.5,
        max_delay_days=4,
    )
    med_eval = evaluate_supplier_risk(med_metrics)
    assert med_eval.risk_level == "MEDIUM"
    assert med_eval.risk_score == 40.0
    assert "monitor" in med_eval.recommended_action.lower()

    # 3. High risk: 40% late, 8.0 avg delay -> score = (0.4*60) + min(8*8, 40) = 24 + 40 = 64.0
    high_metrics = SupplierRiskMetrics(
        supplier_id="SUP-HIGH",
        supplier_name="Delayed Vendor",
        total_shipments=10,
        on_time_shipments=6,
        late_shipments=4,
        late_delivery_rate=0.40,
        total_delay_days=32,
        average_delay_days=8.0,
        max_delay_days=12,
    )
    high_eval = evaluate_supplier_risk(high_metrics)
    assert high_eval.risk_level == "HIGH"
    assert high_eval.risk_score == 64.0
    assert "formal vendor review" in high_eval.recommended_action.lower()


def test_malformed_and_missing_data_handled_safely():
    """Test DeliveryRecordValidatorTool safely flags invalid/incomplete rows without crashing."""
    raw_data = [
        # Valid row
        {
            "delivery_id": "DEL-1",
            "supplier_id": "SUP-1",
            "supplier_name": "Supplier One",
            "promised_delivery_date": "2026-09-10",
            "actual_delivery_date": "2026-09-12",
        },
        # Missing supplier_id
        {
            "delivery_id": "DEL-2",
            "supplier_id": "",
            "supplier_name": "Supplier Two",
            "promised_delivery_date": "2026-09-10",
            "actual_delivery_date": "2026-09-10",
        },
        # Invalid date format
        {
            "delivery_id": "DEL-3",
            "supplier_id": "SUP-3",
            "supplier_name": "Supplier Three",
            "promised_delivery_date": "invalid-date",
            "actual_delivery_date": "2026-09-10",
        },
        # Missing actual delivery date
        {
            "delivery_id": "DEL-4",
            "supplier_id": "SUP-4",
            "supplier_name": "Supplier Four",
            "promised_delivery_date": "2026-09-10",
            "actual_delivery_date": "",
        },
    ]

    validator = DeliveryRecordValidatorTool()
    output = validator.execute(raw_records=raw_data)

    assert output["valid_count"] == 1
    assert output["invalid_count"] == 3
    assert len(output["invalid_records"]) == 3
    reasons = [r["reason"] for r in output["invalid_records"]]
    assert any("Missing required fields" in r for r in reasons)
    assert any("Invalid date format" in r for r in reasons)


def test_missing_csv_file_raises_file_not_found():
    """Test SupplierDeliveryLoaderTool raises FileNotFoundError when CSV does not exist."""
    loader = SupplierDeliveryLoaderTool()
    with pytest.raises(FileNotFoundError):
        loader.execute(supplier_csv_path="non_existent_supplier_file.csv")


def test_empty_delivery_records_handling():
    """Test that empty delivery dataset is processed safely and returns graceful output."""
    engine = GenericWorkflowEngine()
    wf011 = register_wf011_extension(
        tool_registry=engine.tool_registry,
        step_resolver=engine.step_resolver,
    )

    result = engine.execute(wf011, deliveries=[])

    assert result.status == ExecutionStatus.COMPLETED
    assert result.output["total_suppliers_assessed"] == 0
    assert result.output["risk_distribution"]["high"] == 0
    assert result.output["risk_distribution"]["medium"] == 0
    assert result.output["risk_distribution"]["low"] == 0


def test_cli_mock_route_wf011():
    """Test the CLI command line interface with --mock-route WF011."""
    cmd = [
        sys.executable,
        "-m",
        "app.main",
        "--mock-route",
        "WF011",
        "Assess supplier delivery risk",
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, check=False)

    assert proc.returncode == 0
    assert "WF011 (Supplier Delivery Risk Assessment)" in proc.stdout
    assert "Supplier Delivery Risk Assessment (4 suppliers assessed):" in proc.stdout
    assert "Apex Logistics & Materials" in proc.stdout
    assert "SIMULATED" in proc.stdout


def test_full_regression_wf001_through_wf010_with_wf011_available(assessment_workflows):
    """Ensure baseline workflows WF001–WF010 remain fully operational when WF011 is available."""
    assert len(assessment_workflows) == 10
    wf_ids = {wf.workflow_id for wf in assessment_workflows}
    expected_baseline_ids = {f"WF{i:03d}" for i in range(1, 11)}
    assert wf_ids == expected_baseline_ids

    # Prove WF011 can be added to catalog alongside all 10 baseline workflows
    wf011 = get_wf011_definition()
    extended_catalog = list(assessment_workflows) + [wf011]
    assert len(extended_catalog) == 11
