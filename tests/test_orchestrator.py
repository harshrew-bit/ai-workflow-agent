"""End-to-end integration tests for WorkflowOrchestrator."""

import json
from pathlib import Path
import pytest

from app.agent.provider import FakeLLMProvider
from app.agent.router import LLMWorkflowRouter
from app.orchestrator import WorkflowOrchestrator


@pytest.fixture
def fake_wf001_router() -> LLMWorkflowRouter:
    """Return a router configured with a deterministic FakeLLMProvider for WF001."""
    fake_json = json.dumps({
        "workflow_id": "WF001",
        "confidence": 0.95,
        "reasoning": "User asks which products need restocking, matching Inventory Restock Check trigger.",
        "extracted_inputs": {},
        "requires_clarification": False,
    })
    return LLMWorkflowRouter(provider=FakeLLMProvider(default_response=fake_json))


def test_full_pipeline_wf001_success(fake_wf001_router: LLMWorkflowRouter):
    """Test 8: Full end-to-end execution of WF001 via orchestrator."""
    orchestrator = WorkflowOrchestrator(router=fake_wf001_router)

    report = orchestrator.run("Which products need restocking?")

    # Verify overall report attributes
    assert report.status == "success"
    assert report.selected_workflow_id == "WF001"
    assert report.selected_workflow_name == "Inventory Restock Check"
    assert report.routing_confidence == 0.95
    assert not report.clarification_required
    assert len(report.errors) == 0

    # Verify all 5 steps executed
    assert len(report.steps) == 5
    expected_step_names = [
        "Load inventory",
        "compare current stock with minimum threshold",
        "identify low-stock products",
        "calculate reorder quantity",
        "generate restock list",
    ]
    for idx, (step_rep, expected_name) in enumerate(zip(report.steps, expected_step_names), start=1):
        assert step_rep.step_number == idx
        assert step_rep.step_name == expected_name
        assert step_rep.status == "completed"
        assert step_rep.error is None
        assert step_rep.output_summary is not None

    # Verify final structured output
    final = report.final_output
    assert isinstance(final, dict)
    assert final["total_products_checked"] == 7
    assert final["restock_required_count"] == 4
    assert len(final["products_requiring_restock"]) == 4

    # Verify zero stock and low stock items are present
    pids = [item["product_id"] for item in final["products_requiring_restock"]]
    assert "PRD-001" in pids
    assert "PRD-003" in pids  # zero stock item
    assert "PRD-005" in pids
    assert "PRD-007" in pids

    # Item exactly at threshold must NOT be present
    assert "PRD-004" not in pids


def test_ambiguous_routing_causes_no_tool_execution():
    """Test 9: Ambiguous/unrecognized query returns needs_clarification and executes zero tools."""
    ambiguous_json = json.dumps({
        "workflow_id": None,
        "confidence": 0.20,
        "reasoning": "Query is ambiguous and could match multiple tasks. Clarification required.",
        "extracted_inputs": {},
        "requires_clarification": True,
    })
    router = LLMWorkflowRouter(provider=FakeLLMProvider(default_response=ambiguous_json))
    orchestrator = WorkflowOrchestrator(router=router)

    report = orchestrator.run("Can you update my stuff?")

    assert report.status == "needs_clarification"
    assert report.selected_workflow_id is None
    assert report.clarification_required is True
    # Zero tools executed
    assert len(report.steps) == 0
    assert report.final_output is None


def test_low_confidence_routing_causes_no_tool_execution():
    """Test 9b: Low-confidence match triggers clarification and does not execute tools."""
    low_conf_json = json.dumps({
        "workflow_id": "WF001",
        "confidence": 0.45,  # Below 0.70 threshold
        "reasoning": "Weak similarity to restock check.",
        "extracted_inputs": {},
        "requires_clarification": False,
    })
    router = LLMWorkflowRouter(
        provider=FakeLLMProvider(default_response=low_conf_json),
        confidence_threshold=0.70,
    )
    orchestrator = WorkflowOrchestrator(router=router)

    report = orchestrator.run("Check some numbers")

    assert report.status == "needs_clarification"
    assert report.clarification_required is True
    assert len(report.steps) == 0
    assert report.final_output is None


def test_unknown_workflow_id_causes_safe_failure():
    """Test 10: Model suggesting an unknown/hallucinated workflow ID fails safely."""
    hallucinated_json = json.dumps({
        "workflow_id": "WF999",  # Invalid ID not in Excel
        "confidence": 0.90,
        "reasoning": "Made-up workflow.",
        "extracted_inputs": {},
        "requires_clarification": False,
    })
    router = LLMWorkflowRouter(provider=FakeLLMProvider(default_response=hallucinated_json))
    orchestrator = WorkflowOrchestrator(router=router)

    report = orchestrator.run("Do something impossible")

    # Router rejects WF999, so orchestrator treats as clarification / failure
    assert report.status in ("needs_clarification", "failed")
    assert report.clarification_required is True
    assert len(report.steps) == 0
    assert report.final_output is None


def test_tool_failure_appears_accurately_in_execution_report(tmp_path: Path, fake_wf001_router: LLMWorkflowRouter):
    """Test 11: Tool failure halts execution and reports error accurately."""
    orchestrator = WorkflowOrchestrator(router=fake_wf001_router)

    # Supply path to a non-existent CSV file
    non_existent = str(tmp_path / "non_existent.csv")
    report = orchestrator.run("Which products need restocking?", csv_path=non_existent)

    # Step 1 should fail
    assert report.status in ("failed", "partial_failure")
    assert len(report.steps) == 1
    assert report.steps[0].status == "failed"
    assert "not found" in str(report.steps[0].error).lower()
    assert len(report.errors) > 0
    assert "not found" in report.errors[0].lower()


def test_no_live_api_key_required_in_test(monkeypatch):
    """Test 12: Verify test environment works hermetically without real API keys."""
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("LLM_PROVIDER", raising=False)

    fake_json = json.dumps({
        "workflow_id": "WF001",
        "confidence": 0.95,
        "reasoning": "Offline deterministic test response.",
        "extracted_inputs": {},
        "requires_clarification": False,
    })
    provider = FakeLLMProvider(default_response=fake_json)
    router = LLMWorkflowRouter(provider=provider)

    orchestrator = WorkflowOrchestrator(router=router)
    report = orchestrator.run("Which products need restocking?")

    assert report.status == "success"
    assert report.selected_workflow_id == "WF001"


def test_cli_mock_route_wf001(monkeypatch, capsys):
    """Test CLI explicit --mock-route WF001 runs end-to-end without API keys."""
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("LLM_PROVIDER", raising=False)

    from app.main import main

    monkeypatch.setattr(
        "sys.argv",
        ["app.main", "--mock-route", "WF001", "Which products need restocking?"],
    )
    main()

    captured = capsys.readouterr()
    assert "SUCCESS" in captured.out
    assert "WF001 (Inventory Restock Check)" in captured.out
    assert "Simulated routing selection for WF001" in captured.out
    assert "PRD-001" in captured.out
    assert "PRD-003" in captured.out
    assert "PRD-005" in captured.out
    assert "PRD-007" in captured.out
    assert "4 of 7 product(s) require restocking" in captured.out


def test_cli_unconfigured_requests_clarification(monkeypatch, capsys):
    """Test CLI default without API key safely requests clarification without executing tools."""
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("LLM_PROVIDER", raising=False)

    from app.main import main

    monkeypatch.setattr(
        "sys.argv",
        ["app.main", "Which products need restocking?"],
    )
    with pytest.raises(SystemExit) as exc:
        main()
    assert exc.value.code == 4  # exit code 4 = needs clarification (documented contract)

    captured = capsys.readouterr()
    assert "NEEDS_CLARIFICATION" in captured.out
    assert "Live LLM provider is not configured" in captured.out
    assert "No tools were executed." in captured.out
