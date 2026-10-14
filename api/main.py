"""FastAPI backend adapter exposing the AI Workflow Agent orchestrator."""

import json
from pathlib import Path
import re
from typing import Any, Dict, List, Optional
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from app.agent.normalization import (
    parse_comparison_operator,
    parse_integer_threshold,
    parse_percentage_threshold,
    parse_time_threshold_seconds,
)
from app.agent.offline_router import OfflineWorkflowRouter
from app.agent.provider import FakeLLMProvider, is_live_llm_configured
from app.agent.router import LLMWorkflowRouter
from app.main import (
    EXIT_FAILED,
    EXIT_NEEDS_CLARIFICATION,
    EXIT_PARTIAL_FAILURE,
    EXIT_SUCCESS,
    _MOCK_EMAIL_RE,
    _MOCK_ORDER_ID_RE,
    _STATUS_EXIT_CODES,
    to_sentence_case,
)
from app.models.report import ExecutionReport, StepReport
from app.models.workflow import WorkflowDefinition
from app.orchestrator import WorkflowOrchestrator
from app.tools.supplier_risk import register_wf011_extension

REPO_ROOT = Path(__file__).resolve().parent.parent
OUTPUTS_DIR = REPO_ROOT / "outputs"
OUTPUTS_DIR.mkdir(exist_ok=True)
EXAMPLES_DIR = REPO_ROOT / "examples"
EXAMPLES_OUTPUT_DIR = EXAMPLES_DIR / "output"

# Allowlist of acceptable runtime input keys from web clients
ALLOWED_INPUT_KEYS = {
    "product_name",
    "category",
    "material",
    "color",
    "target_audience",
    "order_id",
    "customer_email",
    "campaign_goal",
    "dates",
    "promotion",
    "product_list",
    "keywords",
    "task_description",
    "required_skills",
    "priority",
    "deadline",
    "threshold",
    "price_threshold",
    "threshold_percentage",
    "comparison_operator",
    "operator",
    "threshold_override",
    "minimum_stock",
    "minimum_threshold",
    "failure_threshold",
    "failure_rate_threshold",
    "time_threshold_seconds",
    "time_threshold",
    "latency_threshold",
}

app = FastAPI(
    title="AI Workflow Agent API",
    description="Thin adapter exposing the Excel-driven AI Workflow Automation engine.",
    version="0.1.0",
)

# Enable CORS for local development and frontend clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _create_orchestrator(router=None, use_live_llm: bool = False) -> WorkflowOrchestrator:
    """Create orchestrator configured with default workbook and WF011 extension."""
    if router is None:
        if use_live_llm and is_live_llm_configured():
            router = LLMWorkflowRouter()
        else:
            router = OfflineWorkflowRouter()

    orchestrator = WorkflowOrchestrator(router=router)
    register_wf011_extension(
        registry=orchestrator.registry,
        tool_registry=orchestrator.tool_registry,
        step_resolver=orchestrator.step_resolver,
    )
    return orchestrator


# Pre-warmed default orchestrator (offline by default for safe local development)
_default_orchestrator = _create_orchestrator()


class HealthResponse(BaseModel):
    status: str
    workbook_loaded: bool
    workflow_count: int
    llm_configured: bool
    offline_router_available: bool


class WorkflowSummary(BaseModel):
    workflow_id: str
    workflow_name: str
    trigger: str
    inputs: str
    steps: str
    parsed_steps: List[str]
    decision_logic: str
    tools_required: str
    parsed_tools: List[str]
    expected_output: str


class ExampleSummary(BaseModel):
    slug: str
    request: str
    expected_workflow_id: Optional[str] = None
    expected_status: str
    expected_exit_code: int
    category: str


class RunRequest(BaseModel):
    request: str = Field(..., min_length=1, max_length=500)
    forced_workflow_id: Optional[str] = None
    inputs: Optional[Dict[str, Any]] = None
    use_live_llm: Optional[bool] = False


class RunResponse(BaseModel):
    request: str
    selected_workflow_id: Optional[str] = None
    selected_workflow_name: Optional[str] = None
    routing_confidence: float = 0.0
    routing_reasoning: str = ""
    status: str
    steps: List[StepReport] = Field(default_factory=list)
    final_output: Optional[Any] = None
    errors: List[str] = Field(default_factory=list)
    clarification_required: bool = False
    routing_mode: str = "offline"
    warnings: List[str] = Field(default_factory=list)
    exit_code: int = 0


@app.get("/api/health", response_model=HealthResponse)
def get_health() -> HealthResponse:
    """Return safe health check without leaking secrets or environment variables."""
    registry = _default_orchestrator.registry
    all_wfs = registry.list_all()
    return HealthResponse(
        status="ok",
        workbook_loaded=len(all_wfs) > 0,
        workflow_count=len(all_wfs),
        llm_configured=is_live_llm_configured(),
        offline_router_available=True,
    )


@app.get("/api/workflows", response_model=List[WorkflowSummary])
def get_workflows() -> List[WorkflowSummary]:
    """Return all registered workflow definitions from Excel workbook and extensions."""
    wfs = _default_orchestrator.registry.list_all()
    summaries = []
    for wf in wfs:
        summaries.append(
            WorkflowSummary(
                workflow_id=wf.workflow_id,
                workflow_name=wf.workflow_name,
                trigger=wf.trigger,
                inputs=wf.inputs,
                steps=wf.steps,
                parsed_steps=wf.parsed_steps,
                decision_logic=wf.decision_logic,
                tools_required=wf.tools_required,
                parsed_tools=wf.parsed_tools,
                expected_output=wf.expected_output,
            )
        )
    return summaries


@app.get("/api/examples", response_model=List[ExampleSummary])
def get_examples() -> List[ExampleSummary]:
    """Return benchmark query examples from the repository."""
    expected_file = EXAMPLES_DIR / "expected.json"
    results: List[ExampleSummary] = []
    if expected_file.exists():
        try:
            with open(expected_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            for slug, item in data.items():
                category = "workbook" if "paraphrase" not in slug and "unrelated" not in slug else (
                    "paraphrase" if "paraphrase" in slug else "unrelated"
                )
                results.append(
                    ExampleSummary(
                        slug=slug,
                        request=item.get("request", ""),
                        expected_workflow_id=item.get("expected_workflow_id"),
                        expected_status=item.get("expected_status", "success"),
                        expected_exit_code=item.get("expected_exit_code", 0),
                        category=category,
                    )
                )
        except Exception:
            pass
    return results


@app.get("/api/static-runs")
def list_static_runs() -> List[Dict[str, Any]]:
    """List available pre-computed static demonstration runs."""
    if not EXAMPLES_OUTPUT_DIR.exists():
        return []
    runs = []
    for p in sorted(EXAMPLES_OUTPUT_DIR.glob("*.json")):
        slug = p.stem
        try:
            with open(p, "r", encoding="utf-8") as f:
                report_data = json.load(f)
            runs.append({
                "slug": slug,
                "request": report_data.get("request", ""),
                "selected_workflow_id": report_data.get("selected_workflow_id"),
                "selected_workflow_name": report_data.get("selected_workflow_name"),
                "status": report_data.get("status", "success"),
                "routing_mode": report_data.get("routing_mode", "offline"),
            })
        except Exception:
            continue
    return runs


@app.get("/api/static-runs/{slug}")
def get_static_run(slug: str) -> Dict[str, Any]:
    """Retrieve genuine pre-computed JSON output for a benchmark slug."""
    # Sanitize slug: only alphanumeric and underscores
    clean_slug = re.sub(r"[^a-zA-Z0-9_]", "", slug)
    target_path = (EXAMPLES_OUTPUT_DIR / f"{clean_slug}.json").resolve()
    
    # Path traversal protection
    if not target_path.is_relative_to(EXAMPLES_OUTPUT_DIR.resolve()) or not target_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Static run for '{clean_slug}' not found",
        )
    
    with open(target_path, "r", encoding="utf-8") as f:
        return json.load(f)


@app.post("/api/run", response_model=RunResponse)
def run_workflow(payload: RunRequest) -> RunResponse:
    """Execute a natural-language workflow request through the existing orchestrator."""
    clean_request = payload.request.strip()
    if not clean_request:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Request text cannot be empty or whitespace only.",
        )

    # Validate forced workflow ID if supplied
    forced_id = payload.forced_workflow_id
    if forced_id:
        forced_id = forced_id.strip()
        if not _default_orchestrator.registry.get_or_none(forced_id):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Unknown workflow ID for forced routing: '{forced_id}'",
            )

    # Validate inputs against allowlist & reject path-like keys or values
    user_inputs = payload.inputs or {}
    for key, val in user_inputs.items():
        lowered_key = key.lower()
        if any(tok in lowered_key for tok in ("path", "file", "csv")):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Prohibited input key '{key}': browser-supplied file paths are not allowed.",
            )
        if key not in ALLOWED_INPUT_KEYS:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Unrecognized or unsupported input key: '{key}'",
            )
        if isinstance(val, str) and (".." in val or "/" in val or "\\" in val):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Invalid characters in input value for '{key}'.",
            )
        try:
            if key in ("threshold", "price_threshold", "threshold_percentage"):
                parse_percentage_threshold(val, "Price validation threshold")
            elif key in ("comparison_operator", "operator"):
                parse_comparison_operator(val)
            elif key in ("threshold_override", "minimum_stock", "minimum_threshold"):
                parse_integer_threshold(val, "Stock threshold override")
            elif key in ("failure_threshold", "failure_rate_threshold"):
                parse_percentage_threshold(val, "Failure rate threshold")
            elif key in ("time_threshold_seconds", "time_threshold", "latency_threshold"):
                parse_time_threshold_seconds(val)
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=str(exc),
            )

    # Prepare runtime inputs with approved server-side outputs directory
    runtime_inputs: Dict[str, Any] = dict(user_inputs)
    runtime_inputs["output_dir"] = str(OUTPUTS_DIR)

    # Configure router for forced mode if requested
    router = None
    if forced_id:
        fake_json = json.dumps({
            "workflow_id": forced_id,
            "confidence": 0.95,
            "reasoning": f"Simulated routing selection for {forced_id}",
            "extracted_inputs": {},
            "requires_clarification": False,
        })
        router = LLMWorkflowRouter(provider=FakeLLMProvider(default_response=fake_json))

    orchestrator = _create_orchestrator(router=router, use_live_llm=bool(payload.use_live_llm))

    # Auto-extract order identifiers for WF005 in forced mode
    if forced_id == "WF005":
        order_match = _MOCK_ORDER_ID_RE.search(clean_request)
        if order_match:
            runtime_inputs.setdefault("order_id", order_match.group(0).upper())
        email_match = _MOCK_EMAIL_RE.search(clean_request)
        if email_match:
            runtime_inputs.setdefault("customer_email", email_match.group(0))

    try:
        report = orchestrator.run(clean_request, **runtime_inputs)
    except Exception as e:
        # Prevent secret leakage and sanitize internal paths in exception messages
        err_msg = str(e).replace(str(REPO_ROOT), "<repo>")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal workflow execution error: {err_msg}",
        )

    # Label forced route mode and add advisory warning if another workflow is a much better match
    if forced_id:
        report.routing_mode = "forced"
        offline_scorer = OfflineWorkflowRouter()
        ranked = offline_scorer.score_workflows(clean_request, orchestrator.registry.list_all())
        if ranked:
            top_wf, top_score, _ = ranked[0]
            forced_score = 0.0
            for wf, s, _ in ranked:
                if wf.workflow_id == forced_id:
                    forced_score = s
                    break
            if top_wf.workflow_id != forced_id and top_score >= 3.0 and top_score > forced_score:
                warning_msg = (
                    f"[WARNING] Forced route selected {forced_id}, but request appears to match "
                    f"{top_wf.workflow_id} ({top_wf.workflow_name})."
                )
                report.warnings.append(warning_msg)

    exit_code = _STATUS_EXIT_CODES.get(report.status, EXIT_FAILED)

    return RunResponse(
        request=report.request,
        selected_workflow_id=report.selected_workflow_id,
        selected_workflow_name=report.selected_workflow_name,
        routing_confidence=report.routing_confidence,
        routing_reasoning=report.routing_reasoning,
        status=report.status,
        steps=report.steps,
        final_output=report.final_output,
        errors=report.errors,
        clarification_required=report.clarification_required,
        routing_mode=report.routing_mode,
        warnings=report.warnings,
        exit_code=exit_code,
    )
