"""Reusable workflow tool interfaces, registry, and domain tools."""

from app.tools.base import BaseTool, ToolMetadata
from app.tools.inventory import (
    InventoryItem,
    InventoryLoaderTool,
    LowStockIdentifierTool,
    ReorderQuantityCalculatorTool,
    RestockItem,
    RestockReportGeneratorTool,
    StockThresholdComparatorTool,
    calculate_restock_requirements,
    read_and_validate_inventory_csv,
)
from app.tools.registry import ToolRegistry


def create_default_tool_registry() -> ToolRegistry:
    """Create and populate a ToolRegistry with all registered domain tools."""
    registry = ToolRegistry()
    registry.register(InventoryLoaderTool())
    registry.register(StockThresholdComparatorTool())
    registry.register(LowStockIdentifierTool())
    registry.register(ReorderQuantityCalculatorTool())
    registry.register(RestockReportGeneratorTool())
    return registry


__all__ = [
    "BaseTool",
    "ToolMetadata",
    "ToolRegistry",
    "create_default_tool_registry",
    "InventoryItem",
    "RestockItem",
    "read_and_validate_inventory_csv",
    "calculate_restock_requirements",
    "InventoryLoaderTool",
    "StockThresholdComparatorTool",
    "LowStockIdentifierTool",
    "ReorderQuantityCalculatorTool",
    "RestockReportGeneratorTool",
]
