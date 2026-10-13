"""Execution models for generic workflow execution."""

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ExecutionStatus(str, Enum):
    """Status lifecycle for workflow and step execution."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    NEEDS_CLARIFICATION = "needs_clarification"


class StepExecutionResult(BaseModel):
    """Result of executing an individual workflow step."""

    step_number: int
    step_name: str
    status: ExecutionStatus = ExecutionStatus.PENDING
    output: Optional[Any] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class WorkflowExecutionResult(BaseModel):
    """Result of executing a full workflow."""

    workflow_id: str
    status: ExecutionStatus = ExecutionStatus.PENDING
    output: Optional[Any] = None
    step_results: List[StepExecutionResult] = Field(default_factory=list)
    error: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
