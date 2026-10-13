"""Tests for deterministic offline workflow router and fallback behavior."""

from pathlib import Path
import openpyxl
import pytest

from app.agent.offline_router import OfflineWorkflowRouter
from app.models.workflow import WorkflowDefinition
from app.orchestrator import WorkflowOrchestrator
from app.registry.registry import WorkflowRegistry


@pytest.fixture(scope="module")
def workbook_path() -> Path:
    return Path(__file__).parent.parent / "data" / "workflows.xlsx"


@pytest.fixture(scope="module")
def workflow_registry(workbook_path: Path) -> WorkflowRegistry:
    return WorkflowRegistry.from_excel(workbook_path)


@pytest.fixture(scope="module")
def available_workflows(workflow_registry: WorkflowRegistry):
    return workflow_registry.list_all()


@pytest.fixture
def offline_router() -> OfflineWorkflowRouter:
    return OfflineWorkflowRouter()


def test_test_questions_from_workbook_route_correctly(
    workbook_path: Path, available_workflows, offline_router: OfflineWorkflowRouter
):
    """Test (a): Every request in Test_Questions routes to its correct workflow offline."""
    wb = openpyxl.load_workbook(workbook_path, read_only=True)
    ws = wb["Test_Questions"]

    test_cases = []
    for row in ws.iter_rows(values_only=True):
        if not row or row[0] == "Workflow_ID" or not row[0]:
            continue
        wf_id = str(row[0]).strip()
        request_text = str(row[1]).strip()
        test_cases.append((wf_id, request_text))

    assert len(test_cases) == 10, f"Expected 10 test questions, found {len(test_cases)}"

    for expected_wf_id, request_text in test_cases:
        decision = offline_router.route(request_text, available_workflows)
        assert not decision.requires_clarification, (
            f"Query '{request_text}' unexpectedly required clarification: {decision.reasoning}"
        )
        assert decision.workflow_id == expected_wf_id, (
            f"Query '{request_text}' expected {expected_wf_id}, got {decision.workflow_id} "
            f"(reasoning: {decision.reasoning})"
        )
        assert decision.routing_mode == "offline"
        assert decision.confidence >= 0.70
        assert "Offline keyword match" in decision.reasoning


def test_recruiter_exact_example_routes_to_wf001(
    available_workflows, offline_router: OfflineWorkflowRouter
):
    """Verify recruiter's exact question routes to WF001 offline."""
    query = "Check today's inventory and identify products that need restocking."
    decision = offline_router.route(query, available_workflows)
    assert not decision.requires_clarification
    assert decision.workflow_id == "WF001"
    assert decision.routing_mode == "offline"
    assert decision.confidence >= 0.70


CUSTOM_PARAPHRASES = [
    ("WF001", "Check inventory and tell me which products require restocking."),
    ("WF002", "Compare our internal catalog prices with supplier costs and flag large differences."),
    ("WF003", "Clean the supplier CSV file, detect columns, and filter out invalid rows."),
    ("WF004", "Write product descriptions, bullet points, and SEO metadata for our latest product."),
    ("WF005", "Can you check tracking and shipping status for customer order ORD-1002?"),
    ("WF006", "Detect duplicate catalog listings that have matching titles or identical SKUs."),
    ("WF007", "Draft a comprehensive marketing brief including audience messaging and channel checklist."),
    ("WF008", "Group SEO search queries by user intent and assign keyword priorities."),
    ("WF009", "Match this new task to an engineer based on skills and current capacity."),
    ("WF010", "Show execution health report, error rates, and slowest steps across automated pipelines."),
]


@pytest.mark.parametrize("expected_wf_id, request_text", CUSTOM_PARAPHRASES)
def test_custom_paraphrases_route_correctly(
    expected_wf_id: str,
    request_text: str,
    available_workflows,
    offline_router: OfflineWorkflowRouter,
):
    """Test (b): At least 10 custom paraphrases route to correct workflows offline."""
    decision = offline_router.route(request_text, available_workflows)
    assert not decision.requires_clarification, (
        f"Query '{request_text}' required clarification: {decision.reasoning}"
    )
    assert decision.workflow_id == expected_wf_id, (
        f"Query '{request_text}' routed to {decision.workflow_id} instead of {expected_wf_id}"
    )
    assert decision.routing_mode == "offline"


@pytest.mark.parametrize(
    "unrelated_query",
    [
        "What is the weather in Paris?",
        "Write me a poem about cats",
        "Tell me a funny joke about programming",
        "How do I bake sourdough bread?",
    ],
)
def test_unrelated_requests_require_clarification(
    unrelated_query: str, available_workflows, offline_router: OfflineWorkflowRouter
):
    """Test (c): Unrelated requests return needs_clarification and execute no tools."""
    decision = offline_router.route(unrelated_query, available_workflows)
    assert decision.requires_clarification is True
    assert decision.workflow_id is None
    assert decision.confidence == 0.0
    assert decision.routing_mode == "offline"

    # Orchestrator run should produce needs_clarification and execute zero steps
    orch = WorkflowOrchestrator(router=offline_router)
    report = orch.run(unrelated_query)
    assert report.status == "needs_clarification"
    assert report.selected_workflow_id is None
    assert len(report.steps) == 0
    assert report.routing_mode == "offline"


@pytest.mark.parametrize("blank_query", ["", "   ", "\t\n  "])
def test_empty_and_whitespace_input_require_clarification(
    blank_query: str, available_workflows, offline_router: OfflineWorkflowRouter
):
    """Test (d): Empty and whitespace input return needs_clarification."""
    decision = offline_router.route(blank_query, available_workflows)
    assert decision.requires_clarification is True
    assert decision.workflow_id is None
    assert decision.confidence == 0.0
    assert decision.routing_mode == "offline"

    orch = WorkflowOrchestrator(router=offline_router)
    report = orch.run(blank_query)
    assert report.status == "needs_clarification"
    assert len(report.steps) == 0
    assert report.routing_mode == "offline"


def test_offline_input_extraction():
    """Verify input extraction from query string (order_id, email, file_path)."""
    from app.agent.offline_router import extract_inputs_from_query

    extracted = extract_inputs_from_query(
        "Where is order ORD-1234 for customer user@test.com using data.csv?"
    )
    assert extracted["order_id"] == "ORD-1234"
    assert extracted["customer_email"] == "user@test.com"
    assert extracted["file_path"] == "data.csv"
