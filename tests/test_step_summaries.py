"""Tests verifying informative step summaries across all workflows."""

import json
import re
import pytest

from app.agent.provider import FakeLLMProvider
from app.agent.router import LLMWorkflowRouter
from app.orchestrator import WorkflowOrchestrator


def _make_orchestrator_for_wf(wf_id: str) -> WorkflowOrchestrator:
    fake_json = json.dumps({
        "workflow_id": wf_id,
        "confidence": 0.95,
        "reasoning": f"Simulated routing for {wf_id}",
        "extracted_inputs": {},
        "requires_clarification": False,
    })
    router = LLMWorkflowRouter(provider=FakeLLMProvider(default_response=fake_json))
    return WorkflowOrchestrator(router=router)


def test_wf001_step_summaries_are_concrete_and_informative():
    orch = _make_orchestrator_for_wf("WF001")
    report = orch.run("Which products need restocking?")

    assert report.status == "success"
    assert len(report.steps) == 5

    summaries = [s.output_summary for s in report.steps]
    assert all(s is not None and len(s) > 0 for s in summaries)

    # Step 1: loader mentions loaded items
    assert "Loaded 7 inventory item(s)" in summaries[0]
    # Step 2: comparator mentions compared and threshold count
    assert "Compared 7 product(s) against minimum stock; 4 below threshold." in summaries[1]
    # Step 3: identifier mentions restock count
    assert "Identified 4 product(s) requiring restock." in summaries[2]
    # Step 4: calculator mentions reorders and units
    assert "Calculated reorder quantities for 4 product(s) (61 total units)." in summaries[3]
    # Step 5: reporter mentions restock summary
    assert "4 of 7 product(s) require restocking." in summaries[4]

    # Verify no generic placeholders appear
    for s in summaries:
        assert not re.search(r"completed with \d+ fields", s, re.IGNORECASE)


@pytest.mark.parametrize(
    "wf_id, runtime_inputs",
    [
        ("WF001", {}),
        ("WF002", {}),
        ("WF003", {}),
        (
            "WF004",
            {
                "product_name": "TrailPro Tent",
                "category": "Camping",
                "material": "Ripstop nylon",
                "color": "Forest Green",
                "target_audience": "Backpackers",
            },
        ),
        ("WF005", {"order_id": "ORD-1001"}),
        ("WF006", {}),
        (
            "WF007",
            {
                "campaign_goal": "Summer Sale",
                "dates": "July 1-15",
                "target_audience": "Outdoor enthusiasts",
            },
        ),
        ("WF008", {}),
        (
            "WF009",
            {
                "task_description": "Fix payment gateway bug",
                "required_skills": "Python, SQL",
            },
        ),
        ("WF010", {}),
    ],
)
def test_all_workflows_produce_informative_step_summaries(wf_id, runtime_inputs):
    orch = _make_orchestrator_for_wf(wf_id)
    report = orch.run(f"Execute {wf_id}", **runtime_inputs)

    assert len(report.steps) > 0
    for step in report.steps:
        if step.status == "completed":
            assert step.output_summary is not None
            assert len(step.output_summary.strip()) > 0
            # Strictly verify no placeholder text
            assert not re.search(r"completed with \d+ fields", step.output_summary, re.IGNORECASE)
