"""Data models for structured workflow execution reports."""

from typing import Any, List, Optional
from pydantic import BaseModel, Field


class StepReport(BaseModel):
    """Execution report for an individual workflow step."""

    step_number: int
    step_name: str
    status: str = Field(description="Step status: completed, failed, or skipped")
    output_summary: Optional[str] = None
    output: Optional[Any] = None
    error: Optional[str] = None


class ExecutionReport(BaseModel):
    """End-to-end structured execution report for an orchestration run."""

    request: str
    selected_workflow_id: Optional[str] = None
    selected_workflow_name: Optional[str] = None
    routing_confidence: float = 0.0
    routing_reasoning: str = ""
    status: str = Field(
        description="Overall status: success, partial_failure, failed, or needs_clarification"
    )
    steps: List[StepReport] = Field(default_factory=list)
    final_output: Optional[Any] = None
    errors: List[str] = Field(default_factory=list)
    clarification_required: bool = False
