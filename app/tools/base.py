"""Base interfaces and metadata for reusable workflow tools."""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class ToolMetadata(BaseModel):
    """Metadata describing a reusable tool."""

    name: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1)
    parameters_schema: Dict[str, Any] = Field(default_factory=dict)


class BaseTool(ABC):
    """Abstract base class for all reusable tools.

    Tools provide discrete capabilities (e.g., CSV reader, calculator, text validation)
    that can be invoked by generic workflow steps.
    """

    @property
    @abstractmethod
    def metadata(self) -> ToolMetadata:
        """Metadata describing this tool."""
        pass

    @property
    def name(self) -> str:
        """Name of the tool."""
        return self.metadata.name

    @property
    def description(self) -> str:
        """Description of what the tool does."""
        return self.metadata.description

    @abstractmethod
    def execute(self, **kwargs: Any) -> Any:
        """Execute the tool with given keyword arguments."""
        pass

    def __call__(self, **kwargs: Any) -> Any:
        return self.execute(**kwargs)
