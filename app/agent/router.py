"""Integration boundary for natural-language workflow routing."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Sequence
from pydantic import BaseModel, Field

from app.models.workflow import WorkflowDefinition


class RoutingDecision(BaseModel):
    """Result of evaluating a natural language request against registered workflows."""

    workflow_id: Optional[str] = None
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    reasoning: str = ""
    extracted_inputs: Dict[str, Any] = Field(default_factory=dict)
    requires_clarification: bool = False


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
