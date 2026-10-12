"""Reusable workflow tool interfaces, registry, and domain tools."""

from app.tools.base import BaseTool, ToolMetadata
from app.tools.content_generation import (
    MetaDescriptionGeneratorTool,
    ProductAttributeValidatorTool,
    ProductDescriptionGeneratorTool,
    SeoTitleGeneratorTool,
    ShortDescriptionGeneratorTool,
    ValidatedProductAttributes,
    validate_product_content_attributes,
)
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
from app.tools.pricing import (
    InternalPriceRecord,
    PercentageDifferenceCalculatorTool,
    PriceComparatorTool,
    PriceComparisonItem,
    PriceDataLoaderTool,
    PriceExceptionFlaggerTool,
    ProductSkuMatcherTool,
    VendorPriceRecord,
    compare_and_flag_prices,
    load_internal_prices_csv,
    load_vendor_prices_csv,
    match_prices_by_sku,
)
from app.tools.registry import ToolRegistry
from app.tools.vendor_processing import (
    CleanDatasetProducerTool,
    ColumnDetectorTool,
    ColumnNormalizerTool,
    InvalidRowRecord,
    InvalidRowsIdentifierTool,
    NormalizedVendorRecord,
    RequiredFieldsValidatorTool,
    VendorFileReaderTool,
    detect_and_normalize_columns,
    read_vendor_file_records,
    validate_vendor_records,
)


def create_default_tool_registry() -> ToolRegistry:
    """Create and populate a ToolRegistry with all registered domain tools."""
    registry = ToolRegistry()

    # WF001: Inventory Restock Check
    registry.register(InventoryLoaderTool())
    registry.register(StockThresholdComparatorTool())
    registry.register(LowStockIdentifierTool())
    registry.register(ReorderQuantityCalculatorTool())
    registry.register(RestockReportGeneratorTool())

    # WF002: Product Price Validation
    registry.register(PriceDataLoaderTool())
    registry.register(ProductSkuMatcherTool())
    registry.register(PriceComparatorTool())
    registry.register(PercentageDifferenceCalculatorTool())
    registry.register(PriceExceptionFlaggerTool())

    # WF003: Vendor File Processing
    registry.register(VendorFileReaderTool())
    registry.register(ColumnDetectorTool())
    registry.register(ColumnNormalizerTool())
    registry.register(RequiredFieldsValidatorTool())
    registry.register(InvalidRowsIdentifierTool())
    registry.register(CleanDatasetProducerTool())

    # WF004: Product Description Generator
    registry.register(ProductAttributeValidatorTool())
    registry.register(ProductDescriptionGeneratorTool())
    registry.register(ShortDescriptionGeneratorTool())
    registry.register(SeoTitleGeneratorTool())
    registry.register(MetaDescriptionGeneratorTool())

    return registry


__all__ = [
    "BaseTool",
    "ToolMetadata",
    "ToolRegistry",
    "create_default_tool_registry",
    # WF001
    "InventoryItem",
    "RestockItem",
    "read_and_validate_inventory_csv",
    "calculate_restock_requirements",
    "InventoryLoaderTool",
    "StockThresholdComparatorTool",
    "LowStockIdentifierTool",
    "ReorderQuantityCalculatorTool",
    "RestockReportGeneratorTool",
    # WF002
    "InternalPriceRecord",
    "VendorPriceRecord",
    "PriceComparisonItem",
    "load_internal_prices_csv",
    "load_vendor_prices_csv",
    "match_prices_by_sku",
    "compare_and_flag_prices",
    "PriceDataLoaderTool",
    "ProductSkuMatcherTool",
    "PriceComparatorTool",
    "PercentageDifferenceCalculatorTool",
    "PriceExceptionFlaggerTool",
    # WF003
    "InvalidRowRecord",
    "NormalizedVendorRecord",
    "read_vendor_file_records",
    "detect_and_normalize_columns",
    "validate_vendor_records",
    "VendorFileReaderTool",
    "ColumnDetectorTool",
    "ColumnNormalizerTool",
    "RequiredFieldsValidatorTool",
    "InvalidRowsIdentifierTool",
    "CleanDatasetProducerTool",
    # WF004
    "ValidatedProductAttributes",
    "validate_product_content_attributes",
    "ProductAttributeValidatorTool",
    "ProductDescriptionGeneratorTool",
    "ShortDescriptionGeneratorTool",
    "SeoTitleGeneratorTool",
    "MetaDescriptionGeneratorTool",
]
