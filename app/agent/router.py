"""Integration boundary and LLM-powered natural language workflow router."""

from abc import ABC, abstractmethod
import json
import math
import re
from typing import Any, Dict, List, Optional, Sequence
from pydantic import BaseModel, Field, ValidationError

from app.agent.prompts import ROUTING_SYSTEM_PROMPT, build_routing_user_prompt
from app.agent.provider import LLMProvider, get_llm_provider
from app.models.workflow import WorkflowDefinition


class RoutingDecision(BaseModel):
    """Result of evaluating a natural language request against registered workflows.

    Note on confidence semantics:
    `confidence` is the subjective, model-reported routing score (a float between 0.0 and 1.0)
    indicating how strongly the LLM claims the request matches the selected workflow.
    It is NOT a statistically calibrated posterior probability. The application uses this
    raw score against a configurable threshold to determine if clarification is required.
    """

    workflow_id: Optional[str] = None
    confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Model-reported routing score (0.0 to 1.0), not a calibrated probability.",
    )
    reasoning: str = ""
    extracted_inputs: Dict[str, Any] = Field(default_factory=dict)
    requires_clarification: bool = False
    raw_response: Optional[str] = None


class WorkflowRouter(ABC):
    """Abstract router interface for matching natural language queries to workflows.

    The router operates dynamically across whatever workflows are registered in
    the system, ensuring new workflows (such as WF011) can be routed without
    modifying router code or hardcoding if-else branches.
    """

    @abstractmethod
    def route(
        self,
        query: str,
        available_workflows: Sequence[WorkflowDefinition],
    ) -> RoutingDecision:
        """Route a user request to the best matching workflow definition."""
        pass


def _extract_json_from_text(raw_text: str) -> Dict[str, Any]:
    """Extract and parse a JSON object from text, handling markdown blocks."""
    cleaned = raw_text.strip()

    # 1. Direct JSON parse
    try:
        parsed = json.loads(cleaned)
        if isinstance(parsed, dict):
            return parsed
    except json.JSONDecodeError:
        pass

    # 2. Markdown fenced code block ```json ... ```
    match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", cleaned, re.DOTALL)
    if match:
        parsed = json.loads(match.group(1))
        if isinstance(parsed, dict):
            return parsed

    # 3. Outer braces extraction
    start_idx = cleaned.find("{")
    end_idx = cleaned.rfind("}")
    if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
        parsed = json.loads(cleaned[start_idx : end_idx + 1])
        if isinstance(parsed, dict):
            return parsed

    raise ValueError(f"No valid JSON object found in model output: {raw_text[:200]}")


class LLMWorkflowRouter(WorkflowRouter):
    """Concrete LLM-powered router that matches requests to registered workflows.

    Confidence Semantics:
    The router relies on the model-reported routing score (`confidence`). This is the
    LLM's self-assessed match certainty, not a mathematically calibrated probability.
    No secondary calibration mechanism is applied. Matches falling below the
    `confidence_threshold` (default 0.70) are flagged for human-in-the-loop clarification
    (`requires_clarification = True`).

    Features:
    - Purely dynamic: passes registered workflow definitions as context; no hardcoded branches.
    - Strict validation: validates selected ID against available workflows; rejects hallucinated IDs.
    - Confidence policy: flags low-confidence or ambiguous requests for clarification.
    - Resilient error handling: captures provider exceptions, timeouts, and malformed outputs without secret leakage.
    - Decoupled from execution: only routes and extracts; does not run tools.
    """

    def __init__(
        self,
        provider: Optional[LLMProvider] = None,
        confidence_threshold: float = 0.70,
        timeout: float = 30.0,
    ) -> None:
        self.provider: LLMProvider = provider or get_llm_provider()
        self.confidence_threshold: float = confidence_threshold
        self.timeout: float = timeout

    def route(
        self,
        query: str,
        available_workflows: Sequence[WorkflowDefinition],
    ) -> RoutingDecision:
        """Evaluate a user request and route it to an available workflow definition."""
        clean_query = (query or "").strip()

        # Guard: empty query
        if not clean_query:
            return RoutingDecision(
                workflow_id=None,
                confidence=0.0,
                reasoning="Empty user query provided. Clarification required.",
                requires_clarification=True,
            )

        # Guard: no workflows registered
        if not available_workflows:
            return RoutingDecision(
                workflow_id=None,
                confidence=0.0,
                reasoning="No registered workflows available in the system catalog.",
                requires_clarification=True,
            )

        registered_ids = {wf.workflow_id for wf in available_workflows}
        prompt = build_routing_user_prompt(clean_query, available_workflows)

        # 1. Query LLM provider with error boundary
        try:
            raw_response = self.provider.generate(
                prompt=prompt,
                system_prompt=ROUTING_SYSTEM_PROMPT,
                timeout=self.timeout,
            )
        except Exception as exc:
            return RoutingDecision(
                workflow_id=None,
                confidence=0.0,
                reasoning=f"LLM provider error occurred: {exc}",
                requires_clarification=True,
                raw_response=None,
            )

        # 2. Extract and parse structured JSON
        try:
            parsed_data = _extract_json_from_text(raw_response)
        except Exception as exc:
            return RoutingDecision(
                workflow_id=None,
                confidence=0.0,
                reasoning=f"Malformed model response; failed to parse JSON: {exc}",
                requires_clarification=True,
                raw_response=raw_response,
            )

        # 3. Validate against Pydantic schema
        try:
            # Handle null or string "null" workflow_id
            wf_id = parsed_data.get("workflow_id")
            if wf_id in (None, "", "null", "None"):
                parsed_data["workflow_id"] = None

            # Clamp confidence to valid float range
            raw_conf = parsed_data.get("confidence", 0.0)
            try:
                conf = float(raw_conf)
                # min()/max() silently turn NaN into 1.0; reject non-finite values outright.
                if not math.isfinite(conf):
                    raise ValueError("non-finite confidence")
                parsed_data["confidence"] = max(0.0, min(1.0, conf))
            except (ValueError, TypeError):
                parsed_data["confidence"] = 0.0

            decision = RoutingDecision.model_validate(parsed_data)
            decision.raw_response = raw_response
        except (ValidationError, Exception) as exc:
            return RoutingDecision(
                workflow_id=None,
                confidence=0.0,
                reasoning=f"Schema validation failed for model output: {exc}",
                requires_clarification=True,
                raw_response=raw_response,
            )

        # 4. Strict validation against actual registry
        selected_id = decision.workflow_id
        if selected_id is not None:
            if selected_id not in registered_ids:
                # The model suggested an invented/unregistered ID: REJECT IT
                decision.workflow_id = None
                decision.confidence = 0.0
                decision.requires_clarification = True
                decision.reasoning = (
                    f"Model proposed unregistered workflow ID '{selected_id}'. "
                    f"Rejected by registry validation. {decision.reasoning}"
                ).strip()
            elif decision.confidence < self.confidence_threshold:
                # Confidence below acceptable threshold: flag for clarification
                decision.requires_clarification = True
                decision.reasoning = (
                    f"Confidence ({decision.confidence:.2f}) is below threshold ({self.confidence_threshold:.2f}). "
                    f"{decision.reasoning}"
                ).strip()

        # If workflow_id is None, ensure clarification is marked
        if decision.workflow_id is None:
            decision.requires_clarification = True

        return decision
