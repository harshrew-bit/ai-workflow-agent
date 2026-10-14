"""Regression tests for repository-wide correctness audit and bug fixes.

Covers:
- WF002 Price Validation: dynamic threshold and comparison operator support (<, >, <=, >=, ==).
- WF002 exact boundary behavior, validation_status naming, rejection of invalid/non-finite thresholds.
- Offline router extraction of threshold and operator from natural language queries.
- API runtime inputs allowlist and request execution for custom threshold/operator.
- WF001 threshold alias resolution.
- WF010 string threshold coercion without TypeError.
"""

from decimal import Decimal
import json
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

from api.main import app
from app.agent.normalization import (
    detect_query_ambiguity,
    extract_deterministic_inputs,
    merge_execution_inputs,
    normalize_workflow_inputs,
    parse_comparison_operator,
    parse_integer_threshold,
    parse_percentage_threshold,
    parse_time_threshold_seconds,
)
from app.agent.offline_router import OfflineWorkflowRouter, extract_inputs_from_query
from app.agent.provider import FakeLLMProvider
from app.agent.router import LLMWorkflowRouter
from app.orchestrator import WorkflowOrchestrator
from app.registry.registry import WorkflowRegistry
from app.tools.inventory import StockThresholdComparatorTool
from app.tools.performance_report import (
    ExecutionTimeCalculatorTool,
    RateCalculatorTool,
    RecommendationsGeneratorTool,
)
from app.tools.pricing import (
    PriceExceptionFlaggerTool,
    compare_and_flag_prices,
    evaluate_price_comparison,
)
from app.tools.supplier_risk import register_wf011_extension

client = TestClient(app)


# ------------------------------------------------------------------------------
# 1. WF002: Evaluate Price Comparison with Dynamic Operators & Boundaries
# ------------------------------------------------------------------------------

def test_evaluate_price_comparison_default_greater_than_10_percent():
    """Default rule: flag differences strictly greater than 10.0%."""
    # 100 vs 110.00 is exactly 10.0% -> NOT strictly greater -> COMPLIANT
    diff, pct, is_exc, status = evaluate_price_comparison(100.0, 110.0)
    assert not is_exc
    assert status == "COMPLIANT"

    # 100 vs 110.01 is > 10.0% -> EXCEPTION_EXCEEDS_10_PERCENT
    diff, pct, is_exc, status = evaluate_price_comparison(100.0, 110.01)
    assert is_exc
    assert status == "EXCEPTION_EXCEEDS_10_PERCENT"


def test_evaluate_price_comparison_less_than_operator():
    """Strictly less than: flag differences strictly less than threshold."""
    # 25 vs 26 is 4.0% difference (< 5.0%) -> flagged as exception
    diff, pct, is_exc, status = evaluate_price_comparison(
        25.0, 26.0, threshold_percentage=5.0, comparison_operator="<"
    )
    assert is_exc
    assert status == "EXCEPTION_LESS_THAN_5_PERCENT"
    assert pct == 4.0

    # 100 vs 105 is exactly 5.0% -> not strictly less than 5% -> COMPLIANT
    diff, pct, is_exc, status = evaluate_price_comparison(
        100.0, 105.0, threshold_percentage=5.0, comparison_operator="<"
    )
    assert not is_exc
    assert status == "COMPLIANT"

    # 100 vs 115 is 15.0% (> 5.0%) -> COMPLIANT
    diff, pct, is_exc, status = evaluate_price_comparison(
        100.0, 115.0, threshold_percentage=5.0, comparison_operator="<"
    )
    assert not is_exc
    assert status == "COMPLIANT"


def test_evaluate_price_comparison_inclusive_boundaries():
    """Test inclusive operators: >=, <=, =="""
    # Exactly 5.0%:
    # >= 5.0% -> True
    _, _, is_exc_gte, status_gte = evaluate_price_comparison(
        100.0, 105.0, threshold_percentage=5.0, comparison_operator=">="
    )
    assert is_exc_gte
    assert status_gte == "EXCEPTION_AT_LEAST_5_PERCENT"

    # <= 5.0% -> True
    _, _, is_exc_lte, status_lte = evaluate_price_comparison(
        100.0, 105.0, threshold_percentage=5.0, comparison_operator="<="
    )
    assert is_exc_lte
    assert status_lte == "EXCEPTION_AT_MOST_5_PERCENT"

    # == 5.0% -> True
    _, _, is_exc_eq, status_eq = evaluate_price_comparison(
        100.0, 105.0, threshold_percentage=5.0, comparison_operator="=="
    )
    assert is_exc_eq
    assert status_eq == "EXCEPTION_EQUALS_5_PERCENT"

    # 100 vs 106 (6.0%):
    # == 5.0% -> False
    _, _, is_exc_neq, status_neq = evaluate_price_comparison(
        100.0, 106.0, threshold_percentage=5.0, comparison_operator="=="
    )
    assert not is_exc_neq
    assert status_neq == "COMPLIANT"


@pytest.mark.parametrize("invalid_threshold", [-1.0, -10, float("nan"), float("inf"), float("-inf")])
def test_evaluate_price_comparison_rejects_invalid_thresholds(invalid_threshold):
    """Negative and non-finite thresholds must be rejected."""
    with pytest.raises(ValueError):
        evaluate_price_comparison(100.0, 112.0, threshold_percentage=invalid_threshold)


def test_evaluate_price_comparison_rejects_invalid_operator():
    """Unrecognized operator strings must raise ValueError."""
    with pytest.raises(ValueError, match="Unsupported comparison operator"):
        evaluate_price_comparison(100.0, 112.0, threshold_percentage=10.0, comparison_operator="INVALID_OP")


# ------------------------------------------------------------------------------
# 2. WF002: End-to-End Orchestrator with Sample Data for "< 5%"
# ------------------------------------------------------------------------------

def test_wf002_orchestrator_flags_strictly_less_than_5_percent():
    """Verify customer request: flag any product whose price difference is less than 5%.

    On sample prices:
    - SKU-001: 4.0% (< 5%) -> Flagged
    - SKU-002: 15.0% -> Compliant
    - SKU-003: 10.0% -> Compliant
    - SKU-004: 15.0% -> Compliant
    - SKU-005: 3.33% (< 5%) -> Flagged
    - SKU-006: 25.0% -> Compliant
    - SKU-007: 10.0% -> Compliant
    Total flagged: exactly 2 (SKU-001, SKU-005).
    """
    orchestrator = WorkflowOrchestrator(router=OfflineWorkflowRouter())
    report = orchestrator.run(
        "Compare the vendor and internal prices for each product, and flag any product whose price difference is less than 5%."
    )

    assert report.status == "success"
    assert report.selected_workflow_id == "WF002"
    final = report.final_output
    assert final["total_matched"] == 7
    assert final["exception_count"] == 2
    assert len(final["exceptions"]) == 2

    flagged_skus = {e["sku"] for e in final["exceptions"]}
    assert flagged_skus == {"SKU-001", "SKU-005"}

    # Verify status labels
    for exc in final["exceptions"]:
        assert exc["validation_status"] == "EXCEPTION_LESS_THAN_5_PERCENT"

    # Verify compliant items
    compliant_items = [p for p in final["matched_products"] if not p["is_exception"]]
    assert len(compliant_items) == 5
    compliant_skus = {p["sku"] for p in compliant_items}
    assert compliant_skus == {"SKU-002", "SKU-003", "SKU-004", "SKU-006", "SKU-007"}


def test_wf002_orchestrator_default_request_preserves_10_percent():
    """When no threshold or operator is requested, standard 10% policy flags 3 items."""
    orchestrator = WorkflowOrchestrator(router=OfflineWorkflowRouter())
    report = orchestrator.run("Compare the vendor and internal prices for each product.")

    assert report.status == "success"
    assert report.selected_workflow_id == "WF002"
    final = report.final_output
    assert final["exception_count"] == 3
    flagged_skus = {e["sku"] for e in final["exceptions"]}
    assert flagged_skus == {"SKU-002", "SKU-004", "SKU-006"}


# ------------------------------------------------------------------------------
# 3. Offline Router Input Extraction
# ------------------------------------------------------------------------------

def test_offline_router_extracts_threshold_and_operator():
    """Verify regex extraction of operator and percentage from various query phrases."""
    q1 = "flag any product whose price difference is less than 5%"
    extracted1 = extract_inputs_from_query(q1, workflow_id="WF002")
    assert extracted1["threshold"] == 5.0
    assert extracted1["comparison_operator"] == "<"

    q2 = "Find vendor price differences at least 15%"
    extracted2 = extract_inputs_from_query(q2, workflow_id="WF002")
    assert extracted2["threshold"] == 15.0
    assert extracted2["comparison_operator"] == ">="

    q3 = "Flag differences at most 10%"
    extracted3 = extract_inputs_from_query(q3, workflow_id="WF002")
    assert extracted3["threshold"] == 10.0
    assert extracted3["comparison_operator"] == "<="

    q4 = "Flag failure rate above 12% in workflow performance"
    extracted4 = extract_inputs_from_query(q4, workflow_id="WF010")
    assert extracted4["failure_threshold"] == 12.0

    q5 = "Check inventory with minimum stock threshold 25"
    extracted5 = extract_inputs_from_query(q5, workflow_id="WF001")
    assert extracted5["threshold_override"] == 25


# ------------------------------------------------------------------------------
# 4. API Adapter Validation & Execution
# ------------------------------------------------------------------------------

def test_api_run_accepts_and_executes_less_than_5_percent_query():
    """POST /api/run with less than 5% query returns 200 and 2 exceptions."""
    resp = client.post(
        "/api/run",
        json={
            "request": "Compare the vendor and internal prices for each product, and flag any product whose price difference is less than 5%."
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "success"
    assert data["selected_workflow_id"] == "WF002"
    final = data["final_output"]
    assert final["exception_count"] == 2
    skus = [e["sku"] for e in final["exceptions"]]
    assert set(skus) == {"SKU-001", "SKU-005"}


def test_api_run_accepts_explicit_inputs_threshold_and_operator():
    """Explicit threshold and comparison_operator in inputs dict are allowed."""
    resp = client.post(
        "/api/run",
        json={
            "request": "Compare internal and vendor product prices",
            "inputs": {
                "threshold": 5.0,
                "comparison_operator": "<",
            },
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "success"
    assert data["selected_workflow_id"] == "WF002"
    assert data["final_output"]["exception_count"] == 2


# ------------------------------------------------------------------------------
# 5. WF001 Stock Comparator Alias Support
# ------------------------------------------------------------------------------

def test_stock_comparator_tool_resolves_threshold_aliases():
    """StockThresholdComparatorTool resolves minimum_stock / threshold aliases."""
    tool = StockThresholdComparatorTool()
    sample_items = [
        {"product_id": "P1", "product_name": "Item 1", "current_stock": 20, "minimum_stock": 10},
        {"product_id": "P2", "product_name": "Item 2", "current_stock": 20, "minimum_stock": 30},
    ]

    # Without override: P1 is above (20 >= 10), P2 is low (20 < 30) -> 1 low stock
    res_default = tool.execute(inventory_items=sample_items)
    assert sum(1 for it in res_default["compared_items"] if it["is_low_stock"]) == 1

    # With minimum_stock alias = 25: both P1 (20 < 25) and P2 (20 < 25) are low -> 2 low stock
    res_alias = tool.execute(inventory_items=sample_items, minimum_stock=25)
    assert sum(1 for it in res_alias["compared_items"] if it["is_low_stock"]) == 2
    assert res_alias["compared_items"][0]["effective_threshold"] == 25


# ------------------------------------------------------------------------------
# 6. WF010 String Threshold Coercion
# ------------------------------------------------------------------------------

def test_performance_report_tools_accept_string_thresholds():
    """RateCalculatorTool and ExecutionTimeCalculatorTool accept string thresholds without TypeError."""
    rate_tool = RateCalculatorTool()
    time_tool = ExecutionTimeCalculatorTool()

    sample_logs = [
        {"workflow_id": "WF001", "status": "FAILURE", "execution_time_seconds": 6.0},
        {"workflow_id": "WF001", "status": "SUCCESS", "execution_time_seconds": 4.0},
    ]

    # Pass failure_threshold as string "10.0"
    rate_res = rate_tool.execute(raw_logs=sample_logs, failure_threshold="10.0")
    assert rate_res["workflow_rates"]["WF001"]["failure_rate_percent"] == 50.0
    assert "WF001" in rate_res["flagged_high_failure_workflows"]

    # Pass time_threshold_seconds as string "5.0"
    time_res = time_tool.execute(raw_logs=sample_logs, time_threshold_seconds="5.0")
    assert time_res["workflow_times"]["WF001"]["avg_execution_time_seconds"] == 5.0


# ------------------------------------------------------------------------------
# 7. Reproduction A: Directional Price Differences Require Clarification
# ------------------------------------------------------------------------------

def test_reproduction_a_offline_router_flags_clarification():
    """Reproduction A: 'within 5 percent below their internal prices' is directional.

    Offline router must flag requires_clarification=True rather than forcing symmetric abs diff.
    """
    registry = WorkflowRegistry.from_excel("data/workflows.xlsx")
    router = OfflineWorkflowRouter()
    decision = router.route(
        "Identify products whose vendor prices are within 5 percent below their internal prices.",
        registry.list_all(),
    )
    assert decision.requires_clarification is True
    assert decision.workflow_id == "WF002"
    assert "directional price comparison" in decision.reasoning


def test_reproduction_a_orchestrator_offline_returns_needs_clarification():
    """Orchestrator must return needs_clarification report for Reproduction A via offline router."""
    orchestrator = WorkflowOrchestrator(router=OfflineWorkflowRouter())
    report = orchestrator.run(
        "Identify products whose vendor prices are within 5 percent below their internal prices."
    )
    assert report.status == "needs_clarification"
    assert report.clarification_required is True
    assert report.selected_workflow_id == "WF002"
    assert "directional price comparison" in report.routing_reasoning
    assert report.steps == []
    assert report.final_output is None


def test_reproduction_a_orchestrator_live_llm_returns_needs_clarification():
    """Even if an LLM returns requires_clarification=False, the orchestrator detects directional ambiguity."""
    fake_json = json.dumps({
        "workflow_id": "WF002",
        "confidence": 0.95,
        "reasoning": "Product price check.",
        "extracted_inputs": {},
        "requires_clarification": False,
    })
    router = LLMWorkflowRouter(provider=FakeLLMProvider(default_response=fake_json))
    orchestrator = WorkflowOrchestrator(router=router)

    report = orchestrator.run(
        "Identify products whose vendor prices are within 5 percent below their internal prices."
    )
    assert report.status == "needs_clarification"
    assert report.clarification_required is True
    assert report.selected_workflow_id == "WF002"
    assert "directional price comparison" in report.routing_reasoning


def test_reproduction_a_api_returns_needs_clarification():
    """POST /api/run with Reproduction A query safely returns status needs_clarification."""
    resp = client.post(
        "/api/run",
        json={
            "request": "Identify products whose vendor prices are within 5 percent below their internal prices."
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "needs_clarification"
    assert data["clarification_required"] is True
    assert data["selected_workflow_id"] == "WF002"


@pytest.mark.parametrize(
    "directional_query",
    [
        "Show products where vendor price is 5% below internal price",
        "Find products with vendor prices cheaper than internal by 10%",
        "Show products where vendor price is 5% above internal price",
        "List products priced lower than internal by 8%",
    ],
)
def test_other_directional_queries_require_clarification(directional_query):
    """Directional pricing phrases cannot be safely evaluated as symmetric variance."""
    orchestrator = WorkflowOrchestrator(router=OfflineWorkflowRouter())
    report = orchestrator.run(directional_query)
    assert report.status == "needs_clarification"
    assert report.clarification_required is True


# ------------------------------------------------------------------------------
# 8. Reproduction B: Absolute Deviation At Least 20%
# ------------------------------------------------------------------------------

def test_reproduction_b_offline_router_flags_only_sku_006():
    """Reproduction B: 'absolute vendor price deviation is at least 20% of the internal price'.

    Evaluates abs(vendor - internal) >= 20% of internal:
    On sample prices:
    - SKU-001: 4.0%
    - SKU-002: 15.0%
    - SKU-003: 10.0%
    - SKU-004: 15.0%
    - SKU-005: 3.33%
    - SKU-006: 25.0% (>= 20%) -> FLAGGED!
    - SKU-007: 10.0%
    Total flagged: exactly 1 (SKU-006).
    """
    orchestrator = WorkflowOrchestrator(router=OfflineWorkflowRouter())
    report = orchestrator.run(
        "Show products where the absolute vendor price deviation is at least 20% of the internal price."
    )
    assert report.status == "success"
    assert report.selected_workflow_id == "WF002"
    final = report.final_output
    assert final["total_matched"] == 7
    assert final["exception_count"] == 1
    assert len(final["exceptions"]) == 1

    exc = final["exceptions"][0]
    assert exc["sku"] == "SKU-006"
    assert exc["percentage_difference"] == 25.0
    assert exc["validation_status"] == "EXCEPTION_AT_LEAST_20_PERCENT"


def test_reproduction_b_live_llm_with_empty_extracted_inputs_uses_query_extraction():
    """If live LLM selects WF002 but returns empty extracted_inputs, query extraction provides >= 20%."""
    fake_json = json.dumps({
        "workflow_id": "WF002",
        "confidence": 0.95,
        "reasoning": "Matches Product Price Validation.",
        "extracted_inputs": {},
        "requires_clarification": False,
    })
    router = LLMWorkflowRouter(provider=FakeLLMProvider(default_response=fake_json))
    orchestrator = WorkflowOrchestrator(router=router)

    report = orchestrator.run(
        "Show products where the absolute vendor price deviation is at least 20% of the internal price."
    )
    assert report.status == "success"
    assert report.selected_workflow_id == "WF002"
    final = report.final_output
    assert final["exception_count"] == 1
    assert final["exceptions"][0]["sku"] == "SKU-006"


def test_reproduction_b_live_llm_with_threshold_percentage_alias():
    """If live LLM returns threshold_percentage alias '20%', normalization canonicalizes it."""
    fake_json = json.dumps({
        "workflow_id": "WF002",
        "confidence": 0.95,
        "reasoning": "Matches Product Price Validation.",
        "extracted_inputs": {
            "threshold_percentage": "20%",
            "comparison_operator": ">=",
        },
        "requires_clarification": False,
    })
    router = LLMWorkflowRouter(provider=FakeLLMProvider(default_response=fake_json))
    orchestrator = WorkflowOrchestrator(router=router)

    report = orchestrator.run("Check product price validation")
    assert report.status == "success"
    assert report.selected_workflow_id == "WF002"
    final = report.final_output
    assert final["exception_count"] == 1
    assert final["exceptions"][0]["sku"] == "SKU-006"


def test_reproduction_b_api_endpoint_flags_only_sku_006():
    """POST /api/run with Reproduction B query flags only SKU-006 with use_live_llm=false."""
    resp = client.post(
        "/api/run",
        json={
            "request": "Show products where the absolute vendor price deviation is at least 20% of the internal price.",
            "use_live_llm": False,
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "success"
    assert data["selected_workflow_id"] == "WF002"
    final = data["final_output"]
    assert final["exception_count"] == 1
    assert {e["sku"] for e in final["exceptions"]} == {"SKU-006"}
    assert "at least 20% threshold" in final["summary"]


def test_reproduction_b_api_endpoint_runtime_inputs_override_query():
    """POST /api/run with explicit runtime inputs overriding query-extracted parameters."""
    resp = client.post(
        "/api/run",
        json={
            "request": "Show products where the absolute vendor price deviation is at least 20% of the internal price.",
            "use_live_llm": False,
            "inputs": {
                "threshold": 5.0,
                "comparison_operator": "<",
            },
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "success"
    assert data["selected_workflow_id"] == "WF002"
    final = data["final_output"]
    assert final["exception_count"] == 2
    assert {e["sku"] for e in final["exceptions"]} == {"SKU-001", "SKU-005"}
    assert "less than 5% threshold" in final["summary"]


# ------------------------------------------------------------------------------
# 9. Precedence Contract & Symbolic Operators
# ------------------------------------------------------------------------------

def test_input_precedence_runtime_overrides_query_and_model():
    """Explicit runtime inputs override query-extracted and model-extracted inputs."""
    # Query asks for >= 20% (would flag 1: SKU-006)
    # But runtime input specifies threshold=5.0 and operator='<' (flags 2: SKU-001, SKU-005)
    orchestrator = WorkflowOrchestrator(router=OfflineWorkflowRouter())
    report = orchestrator.run(
        "Show products where the absolute vendor price deviation is at least 20% of the internal price.",
        threshold=5.0,
        comparison_operator="<",
    )
    assert report.status == "success"
    final = report.final_output
    assert final["exception_count"] == 2
    skus = {e["sku"] for e in final["exceptions"]}
    assert skus == {"SKU-001", "SKU-005"}


@pytest.mark.parametrize(
    "query_text,expected_op,expected_thresh",
    [
        ("price diff >= 20%", ">=", 20.0),
        ("price diff <= 10%", "<=", 10.0),
        ("price diff == 5%", "==", 5.0),
        ("price diff > 15%", ">", 15.0),
        ("price diff < 5%", "<", 5.0),
        ("difference at least 12.5%", ">=", 12.5),
        ("difference at most 8%", "<=", 8.0),
    ],
)
def test_symbolic_operator_extractions(query_text, expected_op, expected_thresh):
    """Symbolic and word comparison operators and percentages are extracted correctly."""
    extracted = extract_deterministic_inputs(query_text, workflow_id="WF002")
    assert extracted["threshold"] == expected_thresh
    assert extracted["comparison_operator"] == expected_op


def test_price_flagger_tool_accepts_percentage_string_and_aliases():
    """PriceExceptionFlaggerTool accepts threshold_percentage string '20%' and operator aliases."""
    tool = PriceExceptionFlaggerTool()
    sample_pairs = [
        {
            "sku": "SKU-001",
            "product_name": "P1",
            "vendor_name": "V",
            "internal_price": Decimal("100.00"),
            "vendor_price": Decimal("125.00"),  # 25% diff
        },
        {
            "sku": "SKU-002",
            "product_name": "P2",
            "vendor_name": "V",
            "internal_price": Decimal("100.00"),
            "vendor_price": Decimal("115.00"),  # 15% diff
        },
    ]

    # Pass threshold_percentage='20%' and operator='>='
    res = tool.execute(
        price_evaluations=sample_pairs,
        threshold_percentage="20%",
        operator=">=",
    )
    assert res["exception_count"] == 1
    assert res["exceptions"][0]["sku"] == "SKU-001"


# ------------------------------------------------------------------------------
# 9. Parsing Helpers: Comprehensive Unit Tests
# ------------------------------------------------------------------------------

def test_parse_percentage_threshold_valid_and_invalid():
    """Verify parse_percentage_threshold accepts valid values and rejects malformed/negative/non-finite."""
    # Valid
    assert parse_percentage_threshold(0) == 0.0
    assert parse_percentage_threshold(10.5) == 10.5
    assert parse_percentage_threshold(Decimal("15.2")) == 15.2
    assert parse_percentage_threshold("20%") == 20.0
    assert parse_percentage_threshold("25.5 percent") == 25.5
    assert parse_percentage_threshold("  12 % ") == 12.0

    # Invalid: booleans, None, negative, non-finite, malformed text
    for invalid in [True, False, None, -5, "-5%", "-0.1", "abc", float("nan"), float("inf"), float("-inf")]:
        with pytest.raises(ValueError, match="Price validation threshold"):
            parse_percentage_threshold(invalid)


def test_parse_comparison_operator_valid_and_invalid():
    """Verify parse_comparison_operator validates supported operators and rejects unsupported."""
    # Valid canonical
    for op in (">", "<", ">=", "<=", "=="):
        assert parse_comparison_operator(op) == op

    # Valid synonyms
    assert parse_comparison_operator("gt") == ">"
    assert parse_comparison_operator("greater than") == ">"
    assert parse_comparison_operator("exceeds") == ">"
    assert parse_comparison_operator("lt") == "<"
    assert parse_comparison_operator("less than") == "<"
    assert parse_comparison_operator("under") == "<"
    assert parse_comparison_operator("gte") == ">="
    assert parse_comparison_operator("at least") == ">="
    assert parse_comparison_operator("lte") == "<="
    assert parse_comparison_operator("at most") == "<="
    assert parse_comparison_operator("eq") == "=="
    assert parse_comparison_operator("equals") == "=="

    # Invalid: non-strings, unsupported operator symbols
    for invalid in [None, 123, "!=", "contains", "~", "", "   "]:
        with pytest.raises(ValueError, match="Unsupported comparison operator"):
            parse_comparison_operator(invalid)


def test_parse_integer_threshold_valid_and_invalid():
    """Verify parse_integer_threshold accepts non-negative integers and rejects invalid."""
    # Valid
    assert parse_integer_threshold(0) == 0
    assert parse_integer_threshold(15) == 15
    assert parse_integer_threshold("15") == 15
    assert parse_integer_threshold(Decimal("25")) == 25
    assert parse_integer_threshold(10.0) == 10

    # Invalid: booleans, negative, floats with decimal part, non-finite, text, None
    for invalid in [True, False, None, -1, "-5", 12.5, "12.5", "abc", float("nan"), float("inf")]:
        with pytest.raises(ValueError, match="Stock threshold override"):
            parse_integer_threshold(invalid)


def test_parse_time_threshold_seconds_valid_and_invalid():
    """Verify parse_time_threshold_seconds accepts seconds with units and rejects minutes/invalid."""
    # Valid numeric & string units
    assert parse_time_threshold_seconds(0) == 0.0
    assert parse_time_threshold_seconds(10) == 10.0
    assert parse_time_threshold_seconds(5.5) == 5.5
    assert parse_time_threshold_seconds("10") == 10.0
    assert parse_time_threshold_seconds("10s") == 10.0
    assert parse_time_threshold_seconds("10 sec") == 10.0
    assert parse_time_threshold_seconds("10 seconds") == 10.0
    assert parse_time_threshold_seconds("10 SECONDS") == 10.0
    assert parse_time_threshold_seconds("5.5 s") == 5.5

    # Invalid: booleans, None, negative, non-finite, unsupported units (m, ms, min), text
    for invalid in [True, False, None, -5, "-5s", "10m", "10 minutes", "10ms", "abc", float("nan"), float("inf")]:
        with pytest.raises(ValueError, match="Execution time threshold"):
            parse_time_threshold_seconds(invalid)


# ------------------------------------------------------------------------------
# 10. Explicit Invalid Inputs: Never Silently Fall Back to Defaults
# ------------------------------------------------------------------------------

def test_wf001_invalid_explicit_threshold_override_fails_properly():
    """WF001 must fail or partial_fail when given an invalid threshold override, never silently fall back."""
    orchestrator = WorkflowOrchestrator(router=OfflineWorkflowRouter())

    # Passing malformed threshold_override="abc"
    report_abc = orchestrator.run("Check warehouse inventory restock", threshold_override="abc")
    assert report_abc.status in ("failed", "partial_failure")
    assert any("Stock threshold override must be a non-negative integer" in err for err in report_abc.errors)

    # Passing negative threshold_override=-5
    report_neg = orchestrator.run("Check warehouse inventory restock", threshold_override=-5)
    assert report_neg.status in ("failed", "partial_failure")
    assert any("Stock threshold override must be a non-negative integer" in err for err in report_neg.errors)


def test_wf010_invalid_explicit_failure_threshold_fails_properly():
    """WF010 must fail or partial_fail when given an invalid failure threshold, never silently fall back."""
    orchestrator = WorkflowOrchestrator(router=OfflineWorkflowRouter())

    report_abc = orchestrator.run("Generate workflow performance report", failure_threshold="abc")
    assert report_abc.status in ("failed", "partial_failure")
    assert any("Failure rate threshold must be a finite non-negative number" in err for err in report_abc.errors)

    report_neg = orchestrator.run("Generate workflow performance report", failure_threshold=-5)
    assert report_neg.status in ("failed", "partial_failure")
    assert any("Failure rate threshold must be a finite non-negative number" in err for err in report_neg.errors)


def test_wf010_invalid_explicit_time_threshold_fails_properly():
    """WF010 must fail or partial_fail when given an invalid time threshold, never silently fall back."""
    orchestrator = WorkflowOrchestrator(router=OfflineWorkflowRouter())

    report_unit = orchestrator.run("Generate workflow performance report", time_threshold_seconds="10m")
    assert report_unit.status in ("failed", "partial_failure")
    assert any("Execution time threshold must be a finite non-negative number" in err for err in report_unit.errors)

    report_abc = orchestrator.run("Generate workflow performance report", time_threshold_seconds="abc")
    assert report_abc.status in ("failed", "partial_failure")
    assert any("Execution time threshold must be a finite non-negative number" in err for err in report_abc.errors)


def test_wf002_invalid_explicit_threshold_and_operator_fails_properly():
    """WF002 must fail or partial_fail when given invalid threshold or operator, never silently fall back."""
    orchestrator = WorkflowOrchestrator(router=OfflineWorkflowRouter())

    # Invalid threshold string
    report_thresh = orchestrator.run("Check product price validation", threshold="abc")
    assert report_thresh.status in ("failed", "partial_failure")
    assert any("Price validation threshold must be a finite non-negative number" in err for err in report_thresh.errors)

    # Invalid comparison operator
    report_op = orchestrator.run("Check product price validation", comparison_operator="invalid_op")
    assert report_op.status in ("failed", "partial_failure")
    assert any("Unsupported comparison operator" in err for err in report_op.errors)


# ------------------------------------------------------------------------------
# 11. Deterministic Alias Resolution & Precedence Contract
# ------------------------------------------------------------------------------

def test_conflicting_aliases_deterministic_precedence():
    """Higher-priority canonical aliases must outrank lower-priority aliases within the same input set."""
    # WF002: threshold > price_threshold > threshold_percentage
    norm_wf002 = normalize_workflow_inputs({
        "threshold": 5.0,
        "price_threshold": 12.0,
        "threshold_percentage": 25.0,
    })
    assert norm_wf002["threshold"] == 5.0
    assert norm_wf002["price_threshold"] == 5.0
    assert norm_wf002["threshold_percentage"] == 5.0

    # WF002: comparison_operator > operator
    norm_op = normalize_workflow_inputs({
        "comparison_operator": "<",
        "operator": ">",
    })
    assert norm_op["comparison_operator"] == "<"
    assert norm_op["operator"] == "<"

    # WF001: threshold_override > minimum_stock > minimum_threshold
    norm_wf001 = normalize_workflow_inputs({
        "threshold_override": 10,
        "minimum_stock": 50,
        "minimum_threshold": 100,
    })
    assert norm_wf001["threshold_override"] == 10
    assert norm_wf001["minimum_stock"] == 10

    # WF010: failure_threshold > failure_rate_threshold
    norm_wf010 = normalize_workflow_inputs({
        "failure_threshold": 4.0,
        "failure_rate_threshold": 20.0,
    })
    assert norm_wf010["failure_threshold"] == 4.0

    # WF010: time_threshold_seconds > time_threshold > latency_threshold
    norm_time = normalize_workflow_inputs({
        "time_threshold_seconds": 2.5,
        "time_threshold": 10.0,
        "latency_threshold": 15.0,
    })
    assert norm_time["time_threshold_seconds"] == 2.5


def test_merge_execution_inputs_runtime_outranks_query_and_defaults():
    """Explicit runtime inputs outrank query-extracted values and catalog defaults."""
    default_inputs = {"threshold": 10.0, "comparison_operator": ">"}
    router_extracted = {"threshold": 8.0, "comparison_operator": ">"}
    query_extracted = {"threshold": 5.0, "comparison_operator": "<"}
    runtime_inputs = {"threshold": 15.0, "comparison_operator": ">="}

    merged, _ = merge_execution_inputs(
        default_inputs=default_inputs,
        router_extracted=router_extracted,
        query_extracted=query_extracted,
        runtime_inputs=runtime_inputs,
        workflow_id="WF002",
    )
    assert merged["threshold"] == 15.0
    assert merged["comparison_operator"] == ">="


def test_merge_execution_inputs_invalid_runtime_overrides_defaults():
    """An invalid runtime input overrides default and is preserved so it fails rather than silently using default."""
    default_inputs = {"threshold": 10.0}
    runtime_inputs = {"threshold_percentage": "abc"}

    merged, _ = merge_execution_inputs(
        default_inputs=default_inputs,
        router_extracted={},
        query_extracted={},
        runtime_inputs=runtime_inputs,
        workflow_id="WF002",
    )
    # The invalid value "abc" has overridden the 10.0 default
    assert merged["threshold"] == "abc"


# ------------------------------------------------------------------------------
# 12. API Boundary Validation: HTTP 422 for Invalid Explicit Inputs
# ------------------------------------------------------------------------------

@pytest.mark.parametrize(
    "invalid_input_payload,expected_error_substring",
    [
        ({"threshold": "abc"}, "Price validation threshold must be a finite non-negative number"),
        ({"threshold": -5}, "Price validation threshold must be a finite non-negative number"),
        ({"comparison_operator": "invalid_op"}, "Unsupported comparison operator"),
        ({"threshold_override": "abc"}, "Stock threshold override must be a non-negative integer"),
        ({"threshold_override": -5}, "Stock threshold override must be a non-negative integer"),
        ({"failure_threshold": "abc"}, "Failure rate threshold must be a finite non-negative number"),
        ({"failure_threshold": -5}, "Failure rate threshold must be a finite non-negative number"),
        ({"time_threshold_seconds": "10m"}, "Execution time threshold must be a finite non-negative number"),
        ({"time_threshold_seconds": "abc"}, "Execution time threshold must be a finite non-negative number"),
    ],
)
def test_api_run_rejects_invalid_inputs_with_http_422(invalid_input_payload, expected_error_substring):
    """POST /api/run immediately returns HTTP 422 with clear error details for invalid explicit inputs."""
    resp = client.post(
        "/api/run",
        json={
            "request": "Audit products",
            "inputs": invalid_input_payload,
        },
    )
    assert resp.status_code == 422
    data = resp.json()
    assert expected_error_substring in data["detail"]


def test_api_run_less_than_10_percent_flags_exactly_two_exceptions():
    """POST /api/run with 'less than 10%' returns success with exactly SKU-001 and SKU-005."""
    resp = client.post(
        "/api/run",
        json={
            "request": "Find products where vendor price differs by less than 10%.",
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "success"
    assert data["selected_workflow_id"] == "WF002"
    final = data["final_output"]
    assert final["exception_count"] == 2
    flagged_skus = {e["sku"] for e in final["exceptions"]}
    assert flagged_skus == {"SKU-001", "SKU-005"}


# ------------------------------------------------------------------------------
# 11. Issue 1: Price-Audit vs Supplier Delivery Risk Routing
# ------------------------------------------------------------------------------

def test_price_audit_routes_to_wf002_not_wf011():
    """Verify price-audit query with 'audit' and 'discrepancies' routes to WF002, not WF011."""
    orch = WorkflowOrchestrator(router=OfflineWorkflowRouter())
    register_wf011_extension(registry=orch.registry)

    report = orch.run("Audit the vendor prices and show significant discrepancies.")
    assert report.status == "success"
    assert report.selected_workflow_id == "WF002"
    assert report.selected_workflow_name == "Product Price Validation"
    assert "discrepancies" not in report.errors


def test_supplier_delivery_risk_routes_to_wf011():
    """Verify delivery-risk query with 'supplier audit' routes to WF011."""
    orch = WorkflowOrchestrator(router=OfflineWorkflowRouter())
    register_wf011_extension(
        registry=orch.registry,
        tool_registry=orch.tool_registry,
        step_resolver=orch.step_resolver,
    )

    report = orch.run("Conduct a periodic supplier audit for delivery delays and late shipments.")
    assert report.status == "success"
    assert report.selected_workflow_id == "WF011"
    assert report.selected_workflow_name == "Supplier Delivery Risk Assessment"
    assert "high_risk_suppliers" in report.final_output


def test_ambiguous_supplier_audit_requests_clarification():
    """Verify bare 'supplier audit' query without delivery or pricing terms requires clarification."""
    orch = WorkflowOrchestrator(router=OfflineWorkflowRouter())
    register_wf011_extension(registry=orch.registry)

    report = orch.run("Perform a supplier audit on vendor records.")
    assert report.status == "needs_clarification"
    assert report.clarification_required is True
    assert "delivery performance (WF011) or vendor price validation (WF002)" in report.routing_reasoning


# ------------------------------------------------------------------------------
# 12. Issue 2: Multi-Workflow Execution & Parameter Isolation
# ------------------------------------------------------------------------------

def test_multi_workflow_execution_two_objectives():
    """Verify request with two objectives executes both workflows and returns separate reports."""
    orch = WorkflowOrchestrator(router=OfflineWorkflowRouter())
    report = orch.run("Check vendor prices and identify inventory that needs restocking. Give me both results.")

    assert report.status == "success"
    assert "WF002" in report.selected_workflow_id
    assert "WF001" in report.selected_workflow_id
    assert report.routing_mode == "multi_workflow"

    # Check separate reports
    assert "workflow_reports" in report.final_output
    wf_reports = report.final_output["workflow_reports"]
    assert "WF001" in wf_reports
    assert "WF002" in wf_reports
    assert wf_reports["WF001"]["status"] == "success"
    assert wf_reports["WF002"]["status"] == "success"


def test_multi_workflow_parameter_isolation_and_reports():
    """Verify multi-workflow request isolates parameters so pricing threshold does not bleed into inventory."""
    orch = WorkflowOrchestrator(router=OfflineWorkflowRouter())
    query = (
        "First identify inventory items that need restocking. "
        "Then audit vendor prices using a 15% absolute deviation threshold. "
        "Return both reports separately, with the workflow ID and execution status for each."
    )
    report = orch.run(query)

    assert report.status == "success"
    assert "WF001" in report.selected_workflow_id
    assert "WF002" in report.selected_workflow_id

    wf1 = report.final_output["workflow_reports"]["WF001"]["final_output"]
    wf2 = report.final_output["workflow_reports"]["WF002"]["final_output"]

    # WF001 must have preserved original catalog minimum_stock values
    restock_items = wf1["products_requiring_restock"]
    min_stock_by_pid = {item["product_id"]: item["minimum_stock"] for item in restock_items}
    assert min_stock_by_pid["PRD-001"] == 20
    assert min_stock_by_pid["PRD-003"] == 30
    assert min_stock_by_pid["PRD-005"] == 12
    assert min_stock_by_pid["PRD-007"] == 15

    # WF002 must have applied the 15% threshold: strictly > 15% flags only SKU-006 (25%)
    assert wf2["exception_count"] == 1
    assert wf2["exceptions"][0]["sku"] == "SKU-006"
    assert wf2["exceptions"][0]["percentage_difference"] == 25.0
    assert "exceeding 15% threshold" in wf2["summary"]


def test_single_workflow_with_and_not_split():
    """Verify ordinary single workflow with 'and' in description is not split into multi-workflow."""
    orch = WorkflowOrchestrator(router=OfflineWorkflowRouter())
    report = orch.run("Compare vendor and internal prices and flag any product whose price difference is at least 20%.")

    assert report.status == "success"
    assert report.selected_workflow_id == "WF002"
    assert report.routing_mode != "multi_workflow"
    assert report.final_output["exception_count"] == 1
    assert report.final_output["exceptions"][0]["sku"] == "SKU-006"


def test_multi_workflow_partial_failure(tmp_path: Path):
    """Verify that if one workflow in a multi-workflow request fails, aggregate status is partial_failure."""
    bad_csv = tmp_path / "corrupt_inventory.csv"
    bad_csv.write_text("bad,header\n")

    orch = WorkflowOrchestrator(router=OfflineWorkflowRouter())
    query = "Check vendor prices and identify inventory that needs restocking. Give me both results."
    # Pass bad inventory CSV path so WF001 fails, while WF002 succeeds
    report = orch.run(query, csv_path=str(bad_csv))

    assert report.status == "partial_failure"
    assert len(report.errors) > 0
    wf_reports = report.final_output["workflow_reports"]
    assert wf_reports["WF002"]["status"] == "success"
    assert wf_reports["WF001"]["status"] in ("failed", "partial_failure")


# ------------------------------------------------------------------------------
# 13. Issue 3: Historical Price Comparison Integrity
# ------------------------------------------------------------------------------

def test_historical_price_comparison_without_data_requires_clarification():
    """Verify month-over-month comparison without historical data requests clarification without substituting internal catalog."""
    orch = WorkflowOrchestrator(router=OfflineWorkflowRouter())
    report = orch.run("Compare this month's vendor prices against last month's prices.")

    assert report.status == "needs_clarification"
    assert report.clarification_required is True
    assert "historical vendor price data is not available" in report.routing_reasoning.lower()
    # Ensure internal catalog price was never substituted as output
    assert report.final_output is None


def test_historical_price_comparison_with_data_succeeds(tmp_path: Path):
    """Verify historical price comparison executes when a prior vendor price file is supplied."""
    prior_csv = tmp_path / "prior_vendor_prices.csv"
    prior_csv.write_text(
        "sku,vendor_name,vendor_price,currency\n"
        "SKU-001,Alpha Suppliers,20.00,USD\n"  # was 20.00, current is 26.00 (+30%)
        "SKU-006,CableLine Global,12.50,USD\n"  # was 12.50, current is 12.50 (0%)
    )

    orch = WorkflowOrchestrator(router=OfflineWorkflowRouter())
    report = orch.run(
        "Compare this month's vendor prices against last month's prices.",
        prior_vendor_csv_path=str(prior_csv),
        vendor_csv_path="data/sample_vendor_prices.csv",
    )

    assert report.status == "success"
    assert report.selected_workflow_id == "WF002"
    assert report.final_output is not None
    # SKU-001 has 30% difference from prior 20.00 to current 26.00, so it is flagged!
    assert report.final_output["exception_count"] >= 1
    flagged = {e["sku"] for e in report.final_output["exceptions"]}
    assert "SKU-001" in flagged


# ------------------------------------------------------------------------------
# 14. Issue 4: Inventory Catalog Minimum-Stock Preservation
# ------------------------------------------------------------------------------

def test_inventory_source_minimum_stock_preserved_throughout_execution():
    """Verify original catalog minimum_stock values survive every step and appear in final output."""
    orch = WorkflowOrchestrator(router=OfflineWorkflowRouter())
    report = orch.run("Which inventory items need restocking?")

    assert report.status == "success"
    assert report.selected_workflow_id == "WF001"

    # Step 1: loader
    step1_items = {it["product_id"]: it["minimum_stock"] for it in report.steps[0].output["inventory_items"]}
    assert step1_items["PRD-001"] == 20
    assert step1_items["PRD-003"] == 30
    assert step1_items["PRD-004"] == 10
    assert step1_items["PRD-005"] == 12

    # Step 2: comparator
    step2_items = {it["product_id"]: it["minimum_stock"] for it in report.steps[1].output["compared_items"]}
    assert step2_items["PRD-001"] == 20
    assert step2_items["PRD-003"] == 30

    # Step 4: reorder calculator
    step4_items = {it["product_id"]: it["minimum_stock"] for it in report.steps[3].output["restock_items"]}
    assert step4_items["PRD-001"] == 20
    assert step4_items["PRD-003"] == 30

    # Step 5: final output
    final_items = {it["product_id"]: it["minimum_stock"] for it in report.final_output["products_requiring_restock"]}
    assert final_items["PRD-001"] == 20
    assert final_items["PRD-003"] == 30
    assert final_items["PRD-005"] == 12
    assert final_items["PRD-007"] == 15


def test_inventory_threshold_override_preserves_catalog_min_stock():
    """Verify explicit threshold override records effective_threshold separately without mutating minimum_stock."""
    orch = WorkflowOrchestrator(router=OfflineWorkflowRouter())
    report = orch.run("Which inventory items need restocking?", threshold_override=15)

    assert report.status == "success"
    final_items = report.final_output["products_requiring_restock"]
    for it in final_items:
        # minimum_stock is unchanged catalog value
        if it["product_id"] == "PRD-001":
            assert it["minimum_stock"] == 20
            assert it["effective_threshold"] == 15
            assert it["reorder_quantity"] == 15  # 20 - 5 = 15
        elif it["product_id"] == "PRD-003":
            assert it["minimum_stock"] == 30
            assert it["effective_threshold"] == 15
            assert it["reorder_quantity"] == 30  # 30 - 0 = 30


def test_pricing_threshold_does_not_override_inventory_stock():
    """Verify that a pricing parameter 'threshold=15.0' passed into WF001 does not override inventory minimum stock."""
    orch = WorkflowOrchestrator(router=OfflineWorkflowRouter())
    report = orch.run("Identify inventory items that need restocking", threshold=15.0)

    assert report.status == "success"
    final_items = report.final_output["products_requiring_restock"]
    pids = {it["product_id"] for it in final_items}
    # Under standard rules, PRD-004 (cur=10, min=10) is NOT low stock!
    # If 15.0 override had leaked, PRD-004 would have been flagged (10 < 15)!
    assert "PRD-004" not in pids
    assert pids == {"PRD-001", "PRD-003", "PRD-005", "PRD-007"}


# ------------------------------------------------------------------------------
# 15. Issue 5: Exact 10% Boundary and Mathematical Operators
# ------------------------------------------------------------------------------

def test_exact_10_percent_boundary_not_flagged_for_greater_than():
    """Verify that an exact 10.0% deviation is NOT an exception under strict '>' comparison."""
    # Internal: 10.00, Vendor: 11.00 -> diff: 1.00 = exactly 10.0%
    diff, pct_diff, is_exc, status = evaluate_price_comparison(
        internal_price=Decimal("10.00"),
        vendor_price=Decimal("11.00"),
        threshold_percentage=Decimal("10.0"),
        comparison_operator=">",
    )
    assert pct_diff == 10.0
    assert is_exc is False
    assert status == "COMPLIANT"

    # Under '>=' operator, exact 10.0% IS an exception
    _, _, is_exc_gte, status_gte = evaluate_price_comparison(
        internal_price=Decimal("10.00"),
        vendor_price=Decimal("11.00"),
        threshold_percentage=Decimal("10.0"),
        comparison_operator=">=",
    )
    assert is_exc_gte is True
    assert "AT_LEAST" in status_gte


def test_15_and_25_percent_flagged_for_default_10_percent():
    """Verify deviations strictly greater than 10.0% (15% and 25%) are flagged as exceptions."""
    # 15.0%
    _, _, is_exc_15, status_15 = evaluate_price_comparison(
        internal_price=Decimal("100.00"),
        vendor_price=Decimal("115.00"),
        threshold_percentage=Decimal("10.0"),
        comparison_operator=">",
    )
    assert is_exc_15 is True
    assert status_15 == "EXCEPTION_EXCEEDS_10_PERCENT"

    # 25.0%
    _, _, is_exc_25, status_25 = evaluate_price_comparison(
        internal_price=Decimal("10.00"),
        vendor_price=Decimal("12.50"),
        threshold_percentage=Decimal("10.0"),
        comparison_operator=">",
    )
    assert is_exc_25 is True
    assert status_25 == "EXCEPTION_EXCEEDS_10_PERCENT"



