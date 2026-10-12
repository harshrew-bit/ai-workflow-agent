"""Tests for LLM-powered natural language workflow router."""

import json
from pathlib import Path
import pytest

from app.agent.provider import FakeLLMProvider
from app.agent.router import LLMWorkflowRouter, RoutingDecision
from app.models.workflow import WorkflowDefinition
from app.registry.loader import load_workflows_from_excel
from app.registry.registry import WorkflowRegistry


@pytest.fixture
def assessment_workflows(assessment_workbook_path: Path):
    """Load the ten official workflows from data/workflows.xlsx."""
    return load_workflows_from_excel(assessment_workbook_path)


def test_router_successful_workflow_selection(assessment_workflows):
    """Test 1: Router correctly selects WF001 for inventory restocking query."""
    fake_response = json.dumps({
        "workflow_id": "WF001",
        "confidence": 0.96,
        "reasoning": "The query specifically asks for products requiring restocking, matching the Inventory Restock Check trigger.",
        "extracted_inputs": {},
        "requires_clarification": False,
    })

    provider = FakeLLMProvider(default_response=fake_response)
    router = LLMWorkflowRouter(provider=provider)

    decision = router.route("Which products need restocking?", assessment_workflows)

    assert decision.workflow_id == "WF001"
    assert decision.confidence == 0.96
    assert not decision.requires_clarification
    assert "restocking" in decision.reasoning.lower()


def test_router_input_extraction(assessment_workflows):
    """Test 2: Router extracts specific parameter (e.g. order ID) from user query."""
    fake_response = json.dumps({
        "workflow_id": "WF005",
        "confidence": 0.98,
        "reasoning": "Query is asking for the status of order ORD-1001, matching Customer Order Status workflow.",
        "extracted_inputs": {
            "order_id": "ORD-1001",
        },
        "requires_clarification": False,
    })

    provider = FakeLLMProvider(default_response=fake_response)
    router = LLMWorkflowRouter(provider=provider)

    decision = router.route("Where is order ORD-1001?", assessment_workflows)

    assert decision.workflow_id == "WF005"
    assert decision.confidence == 0.98
    assert not decision.requires_clarification
    assert decision.extracted_inputs == {"order_id": "ORD-1001"}


def test_router_second_workflow_example(assessment_workflows):
    """Show routing decision on a second workflow: WF002 price validation."""
    fake_response = json.dumps({
        "workflow_id": "WF002",
        "confidence": 0.94,
        "reasoning": "Query asks to validate vendor prices exceeding 10% variance.",
        "extracted_inputs": {
            "threshold_percentage": "10%",
        },
        "requires_clarification": False,
    })

    provider = FakeLLMProvider(default_response=fake_response)
    router = LLMWorkflowRouter(provider=provider)

    decision = router.route(
        "Find products where vendor price differs by more than 10%.",
        assessment_workflows,
    )

    assert decision.workflow_id == "WF002"
    assert decision.confidence == 0.94
    assert not decision.requires_clarification
    assert decision.extracted_inputs.get("threshold_percentage") == "10%"


def test_router_unknown_request_requires_clarification(assessment_workflows):
    """Test 3: Unrelated or unknown query sets workflow_id to None and requests clarification."""
    fake_response = json.dumps({
        "workflow_id": None,
        "confidence": 0.05,
        "reasoning": "The query asks for the capital of France, which is unrelated to any inventory, e-commerce, or business workflows.",
        "extracted_inputs": {},
        "requires_clarification": True,
    })

    provider = FakeLLMProvider(default_response=fake_response)
    router = LLMWorkflowRouter(provider=provider)

    decision = router.route("What is the capital of France?", assessment_workflows)

    assert decision.workflow_id is None
    assert decision.requires_clarification is True
    assert decision.confidence == 0.05


def test_router_rejects_invented_or_unregistered_workflow_id(assessment_workflows):
    """Test 4: Registry validation rejects hallucinated / non-existent workflow IDs."""
    fake_response = json.dumps({
        "workflow_id": "WF999",  # Invented ID not in WF001..WF010
        "confidence": 0.95,
        "reasoning": "Matched to automated sanity workflow.",
        "extracted_inputs": {},
        "requires_clarification": False,
    })

    provider = FakeLLMProvider(default_response=fake_response)
    router = LLMWorkflowRouter(provider=provider)

    decision = router.route("Run automated check", assessment_workflows)

    # Must reject invented ID and require clarification
    assert decision.workflow_id is None
    assert decision.confidence == 0.0
    assert decision.requires_clarification is True
    assert "unregistered workflow ID 'WF999'" in decision.reasoning


def test_router_handles_malformed_model_output(assessment_workflows):
    """Test 5: Gracefully handles non-JSON or corrupted responses without crashing."""
    provider = FakeLLMProvider(default_response="I cannot help with this request as an AI.")
    router = LLMWorkflowRouter(provider=provider)

    decision = router.route("Check stock", assessment_workflows)

    assert decision.workflow_id is None
    assert decision.requires_clarification is True
    assert decision.confidence == 0.0
    assert "Malformed model response" in decision.reasoning


def test_router_handles_provider_timeout_and_exceptions(assessment_workflows):
    """Test 6: Provider exceptions (timeout, network, auth) are trapped cleanly."""
    provider = FakeLLMProvider(error_to_raise=TimeoutError("Request timed out after 30.0s"))
    router = LLMWorkflowRouter(provider=provider)

    decision = router.route("Check stock", assessment_workflows)

    assert decision.workflow_id is None
    assert decision.requires_clarification is True
    assert decision.confidence == 0.0
    assert "LLM provider error occurred" in decision.reasoning
    assert "timed out" in decision.reasoning.lower()


def test_router_routes_newly_registered_workflow_dynamically(assessment_workflows):
    """Test 7: Demonstrates routing WF011 when added to catalog, without touching router code."""
    # Define an 11th workflow
    wf011 = WorkflowDefinition(
        Workflow_ID="WF011",
        Workflow_Name="Customer Return Authorization",
        Trigger="Customer requests an RMA return authorization",
        Inputs="Order ID; return reason; product condition",
        Steps="Verify order → check return window → evaluate condition → issue RMA",
        Decision_Logic="If within 30 days and unused, approve return",
        Tools_Required="Order database; RMA generator",
        Expected_Output="RMA number and return shipping label",
    )

    extended_catalog = list(assessment_workflows) + [wf011]

    fake_response = json.dumps({
        "workflow_id": "WF011",
        "confidence": 0.95,
        "reasoning": "Customer is asking to return order ORD-8899, matching Customer Return Authorization.",
        "extracted_inputs": {
            "order_id": "ORD-8899",
            "reason": "Wrong size received",
        },
        "requires_clarification": False,
    })

    provider = FakeLLMProvider(default_response=fake_response)
    router = LLMWorkflowRouter(provider=provider)

    # Route against the extended catalog
    decision = router.route(
        "I need to return order ORD-8899 because I got the wrong size",
        extended_catalog,
    )

    assert decision.workflow_id == "WF011"
    assert decision.confidence == 0.95
    assert not decision.requires_clarification
    assert decision.extracted_inputs["order_id"] == "ORD-8899"


def test_router_low_confidence_triggers_clarification(assessment_workflows):
    """Test 8: Confidence below threshold automatically sets requires_clarification = True."""
    fake_response = json.dumps({
        "workflow_id": "WF006",
        "confidence": 0.52,  # Below default 0.70 threshold
        "reasoning": "Could be duplicate detection, but the user only said 'check my list'.",
        "extracted_inputs": {},
        "requires_clarification": False,
    })

    provider = FakeLLMProvider(default_response=fake_response)
    router = LLMWorkflowRouter(provider=provider, confidence_threshold=0.70)

    decision = router.route("Check my list", assessment_workflows)

    assert decision.workflow_id == "WF006"
    assert decision.confidence == 0.52
    assert decision.requires_clarification is True
    assert "below threshold" in decision.reasoning


def test_router_parses_markdown_wrapped_json(assessment_workflows):
    """Test 9: Successfully extracts JSON enclosed in markdown code fences."""
    raw_markdown = """Here is the routing decision:
```json
{
  "workflow_id": "WF004",
  "confidence": 0.91,
  "reasoning": "Request asks for SEO content generation for shoes.",
  "extracted_inputs": {
    "product_name": "Leather Shoes"
  },
  "requires_clarification": false
}
```
Hope this helps!"""

    provider = FakeLLMProvider(default_response=raw_markdown)
    router = LLMWorkflowRouter(provider=provider)

    decision = router.route("Generate SEO description for Leather Shoes", assessment_workflows)

    assert decision.workflow_id == "WF004"
    assert decision.confidence == 0.91
    assert not decision.requires_clarification
    assert decision.extracted_inputs == {"product_name": "Leather Shoes"}


def test_router_handles_empty_inputs(assessment_workflows):
    """Test 10: Empty queries or empty catalogs return clean clarification decisions."""
    router = LLMWorkflowRouter(provider=FakeLLMProvider())

    # Empty query
    d1 = router.route("   ", assessment_workflows)
    assert d1.workflow_id is None
    assert d1.requires_clarification is True

    # Empty workflows catalog
    d2 = router.route("Which products need restocking?", [])
    assert d2.workflow_id is None
    assert d2.requires_clarification is True


def test_openai_error_sanitization_does_not_leak_response_body_or_secrets(monkeypatch):
    """Regression Test 1a: HTTP error bodies with secrets are NOT exposed by OpenAICompatibleProvider."""
    import io
    import urllib.error
    from app.agent.provider import OpenAICompatibleProvider

    sensitive_body = (
        b'{"error": {"message": "Invalid API key provided: sk-live-SECRETKEY-ABC-12345", '
        b'"internal_trace": "/var/secrets/openai_account.json"}}'
    )

    def mock_urlopen(req, timeout=30.0, context=None):
        fp = io.BytesIO(sensitive_body)
        raise urllib.error.HTTPError(
            url="https://api.openai.com/v1/chat/completions",
            code=401,
            msg="Unauthorized",
            hdrs={},
            fp=fp,
        )

    monkeypatch.setattr("urllib.request.urlopen", mock_urlopen)

    provider = OpenAICompatibleProvider(api_key="sk-live-MYKEY")

    with pytest.raises(RuntimeError) as exc_info:
        provider.generate("test prompt")

    err_msg = str(exc_info.value)

    # 1. Useful, sanitized status is present
    assert "OpenAI API request failed: HTTP 401" in err_msg
    # 2. Raw sensitive error body and secret keys are NOT exposed
    assert "sk-live-SECRETKEY-ABC-12345" not in err_msg
    assert "internal_trace" not in err_msg
    assert "openai_account.json" not in err_msg


def test_gemini_error_sanitization_does_not_leak_response_body_or_secrets(monkeypatch):
    """Regression Test 1b: HTTP error bodies with secrets are NOT exposed by GeminiProvider."""
    import io
    import urllib.error
    from app.agent.provider import GeminiProvider

    sensitive_body = (
        b'{"error": {"code": 403, "message": "API key AIzaSy-SECRET-GEMINI-KEY has expired", '
        b'"account_email": "billing-admin@internal.corp"}}'
    )

    captured_requests = []

    def mock_urlopen(req, timeout=30.0, context=None):
        captured_requests.append(req)
        fp = io.BytesIO(sensitive_body)
        raise urllib.error.HTTPError(
            url="https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent",
            code=403,
            msg="Forbidden",
            hdrs={},
            fp=fp,
        )

    monkeypatch.setattr("urllib.request.urlopen", mock_urlopen)

    provider = GeminiProvider(api_key="AIzaSy-SECRET-GEMINI-KEY")

    with pytest.raises(RuntimeError) as exc_info:
        provider.generate("test prompt")

    err_msg = str(exc_info.value)

    # 1. Sanitized error message with status
    assert "Gemini API request failed: HTTP 403" in err_msg
    # 2. Sensitive response body contents are NOT exposed
    assert "AIzaSy-SECRET-GEMINI-KEY" not in err_msg
    assert "billing-admin@internal.corp" not in err_msg

    # 3. Verify API key was passed via header, NOT exposed in the request URL query string
    assert len(captured_requests) == 1
    req = captured_requests[0]
    assert "key=" not in req.full_url
    assert req.headers.get("X-goog-api-key") == "AIzaSy-SECRET-GEMINI-KEY"


def test_unconfigured_provider_fallback_clearly_requests_configuration(monkeypatch, assessment_workflows):
    """Regression Test 2: Unconfigured live provider clearly communicates inactive status."""
    from app.agent.provider import get_llm_provider

    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("LLM_PROVIDER", raising=False)

    provider = get_llm_provider()
    router = LLMWorkflowRouter(provider=provider)

    decision = router.route("Which products need restocking?", assessment_workflows)

    # Must preserve safe clarification without pretending live execution occurred
    assert decision.workflow_id is None
    assert decision.requires_clarification is True
    assert decision.confidence == 0.0
    assert "Live LLM provider is not configured" in decision.reasoning
    assert "Automated routing is inactive" in decision.reasoning


def test_confidence_semantics_documentation_and_threshold_enforcement(assessment_workflows):
    """Regression Test 3: Verify confidence semantics documentation and threshold policy."""
    # Check field documentation on RoutingDecision model
    field_desc = RoutingDecision.model_fields["confidence"].description or ""
    assert "model-reported" in field_desc.lower()
    assert "not a calibrated probability" in field_desc.lower()

    # Test confidence exactly at or above threshold vs below
    resp_pass = json.dumps({
        "workflow_id": "WF001",
        "confidence": 0.75,
        "reasoning": "Sufficient confidence",
        "extracted_inputs": {},
        "requires_clarification": False,
    })
    router_pass = LLMWorkflowRouter(
        provider=FakeLLMProvider(default_response=resp_pass),
        confidence_threshold=0.70,
    )
    d_pass = router_pass.route("Restock check", assessment_workflows)
    assert d_pass.workflow_id == "WF001"
    assert d_pass.requires_clarification is False

    resp_fail = json.dumps({
        "workflow_id": "WF001",
        "confidence": 0.69,
        "reasoning": "Borderline match",
        "extracted_inputs": {},
        "requires_clarification": False,
    })
    router_fail = LLMWorkflowRouter(
        provider=FakeLLMProvider(default_response=resp_fail),
        confidence_threshold=0.70,
    )
    d_fail = router_fail.route("Restock check", assessment_workflows)
    assert d_fail.workflow_id == "WF001"
    assert d_fail.requires_clarification is True
    assert "below threshold" in d_fail.reasoning

