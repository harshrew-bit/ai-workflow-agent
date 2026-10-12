"""Registry for reusable workflow tools."""

from typing import Dict, List, Optional
from app.tools.base import BaseTool


class ToolRegistry:
    """Registry managing available reusable tools.

    Allows tools to be registered and retrieved dynamically by workflows.
    """

    def __init__(self) -> None:
        self._tools: Dict[str, BaseTool] = {}

    def register(self, tool: BaseTool, *, allow_overwrite: bool = False) -> BaseTool:
        """Register a tool in the registry."""
        normalized_name = tool.name.strip().lower()
        if not allow_overwrite and normalized_name in self._tools:
            raise ValueError(f"Tool '{tool.name}' is already registered.")
        self._tools[normalized_name] = tool
        return tool

    def get(self, name: str) -> Optional[BaseTool]:
        """Look up a tool by name (case-insensitive)."""
        return self._tools.get(name.strip().lower())

    def has_tool(self, name: str) -> bool:
        """Check if a tool is registered."""
        return name.strip().lower() in self._tools

    def list_tools(self) -> List[BaseTool]:
        """Return all registered tools."""
        return list(self._tools.values())

    def list_names(self) -> List[str]:
        """Return names of all registered tools."""
        return [tool.name for tool in self._tools.values()]

    def __len__(self) -> int:
        return len(self._tools)

    def clear(self) -> None:
        """Clear all registered tools."""
        self._tools.clear()
