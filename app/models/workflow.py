"""Workflow definition data model."""

from typing import Any, List
from pydantic import BaseModel, ConfigDict, Field, ValidationInfo, field_validator


class WorkflowDefinition(BaseModel):
    """Validated data model for a business workflow definition.

    Preserves all original workflow properties from the Excel specification:
    trigger, inputs, steps, decision logic, required tools, and expected output.
    """

    model_config = ConfigDict(populate_by_name=True, extra="forbid")

    workflow_id: str = Field(..., alias="Workflow_ID", min_length=1)
    workflow_name: str = Field(..., alias="Workflow_Name", min_length=1)
    trigger: str = Field(..., alias="Trigger", min_length=1)
    inputs: str = Field(..., alias="Inputs", min_length=1)
    steps: str = Field(..., alias="Steps", min_length=1)
    decision_logic: str = Field(..., alias="Decision_Logic", min_length=1)
    tools_required: str = Field(..., alias="Tools_Required", min_length=1)
    expected_output: str = Field(..., alias="Expected_Output", min_length=1)

    @field_validator(
        "workflow_id",
        "workflow_name",
        "trigger",
        "inputs",
        "steps",
        "decision_logic",
        "tools_required",
        "expected_output",
        mode="before",
    )
    @classmethod
    def validate_non_empty_string(cls, value: Any, info: ValidationInfo) -> str:
        """Ensure all fields are non-empty strings and strip surrounding whitespace."""
        if value is None:
            raise ValueError(f"Field '{info.field_name}' cannot be None.")
        str_val = str(value).strip()
        if not str_val:
            raise ValueError(f"Field '{info.field_name}' must be a non-empty string.")
        return str_val

    @property
    def id(self) -> str:
        """Alias for workflow_id."""
        return self.workflow_id

    @property
    def name(self) -> str:
        """Alias for workflow_name."""
        return self.workflow_name

    @property
    def parsed_steps(self) -> List[str]:
        """Convenience property returning individual steps split by arrow delimiters."""
        delimiter = "→" if "→" in self.steps else "->"
        return [s.strip() for s in self.steps.split(delimiter) if s.strip()]

    @property
    def parsed_tools(self) -> List[str]:
        """Convenience property returning individual tools split by semicolons."""
        return [t.strip() for t in self.tools_required.split(";") if t.strip()]

    @property
    def parsed_inputs(self) -> List[str]:
        """Convenience property returning individual inputs split by semicolons."""
        return [i.strip() for i in self.inputs.split(";") if i.strip()]
