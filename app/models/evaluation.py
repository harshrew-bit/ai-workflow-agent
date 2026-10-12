"""Evaluation request data model."""

from typing import Any
from pydantic import BaseModel, ConfigDict, Field, ValidationInfo, field_validator


class EvaluationRequest(BaseModel):
    """Validated data model for test evaluation requests from Test_Questions sheet."""

    model_config = ConfigDict(populate_by_name=True, extra="forbid")

    workflow_id: str = Field(..., alias="Workflow_ID", min_length=1)
    test_request: str = Field(..., alias="Test_Request", min_length=1)
    what_to_check: str = Field(..., alias="What_To_Check", min_length=1)

    @field_validator(
        "workflow_id",
        "test_request",
        "what_to_check",
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
    def request(self) -> str:
        """Alias for test_request."""
        return self.test_request
