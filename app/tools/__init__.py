"""Reusable workflow tool interfaces, registry, and domain tools."""

from app.tools.base import BaseTool, ToolMetadata
from app.tools.campaign_brief import (
    CampaignChannelRecommenderTool,
    CampaignChecklistCreatorTool,
    CampaignInputsValidatorTool,
    CampaignMessagingCreatorTool,
    CampaignObjectiveIdentifierTool,
    CampaignProductSummarizerTool,
    ValidatedCampaignInputs,
    extract_and_validate_campaign_inputs,
)
from app.tools.content_generation import (
    MetaDescriptionGeneratorTool,
    ProductAttributeValidatorTool,
    ProductDescriptionGeneratorTool,
    SeoTitleGeneratorTool,
    ShortDescriptionGeneratorTool,
    ValidatedProductAttributes,
    validate_product_content_attributes,
)
from app.tools.duplicate_detection import (
    AttributeComparatorTool,
    CatalogLoaderTool,
    CatalogNormalizerTool,
    CatalogProduct,
    DuplicateCandidate,
    DuplicateConfidenceAssignerTool,
    DuplicateGrouperTool,
    IdentifierComparatorTool,
    NormalizedProduct,
    detect_duplicates,
    load_catalog_csv,
    normalize_catalog_products,
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
from app.tools.order_status import (
    OrderDataSearchTool,
    OrderIdentifierValidatorTool,
    OrderRecord,
    OrderStatusRetrieverTool,
    OrderStatusSummarizerTool,
    ShipmentInfoRetrieverTool,
    ShipmentRecord,
    extract_order_identifier,
)
from app.tools.performance_report import (
    ErrorIdentifierTool,
    ExecutionTimeCalculatorTool,
    LogLoaderTool,
    RateCalculatorTool,
    RecommendationsGeneratorTool,
    SlowStepsIdentifierTool,
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
from app.tools.seo_keywords import (
    CategoryMapperTool,
    IntentClassifierTool,
    KeywordDeduplicatorTool,
    KeywordReaderTool,
    KeywordRecord,
    PriorityIdentifierTool,
    ResultsExporterTool,
)
from app.tools.task_assignment import (
    AssignmentSummarizerTool,
    CandidateRankerTool,
    EmployeeCandidate,
    EmployeeSelectorTool,
    SkillsComparatorTool,
    TaskRequirement,
    TaskRequirementsAnalyzerTool,
    WorkloadCheckerTool,
)
from app.tools.supplier_risk import (
    DeliveryMetricsCalculatorTool,
    DeliveryRecord,
    DeliveryRecordValidatorTool,
    SupplierDeliveryLoaderTool,
    SupplierRiskEvaluation,
    SupplierRiskEvaluatorTool,
    SupplierRiskMetrics,
    SupplierRiskReporterTool,
    get_wf011_definition,
    register_wf011_extension,
)
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

    # WF005: Customer Order Status
    registry.register(OrderIdentifierValidatorTool())
    registry.register(OrderDataSearchTool())
    registry.register(OrderStatusRetrieverTool())
    registry.register(ShipmentInfoRetrieverTool())
    registry.register(OrderStatusSummarizerTool())

    # WF006: Duplicate Product Detection
    registry.register(CatalogLoaderTool())
    registry.register(CatalogNormalizerTool())
    registry.register(IdentifierComparatorTool())
    registry.register(AttributeComparatorTool())
    registry.register(DuplicateGrouperTool())
    registry.register(DuplicateConfidenceAssignerTool())

    # WF007: Marketing Campaign Brief
    registry.register(CampaignInputsValidatorTool())
    registry.register(CampaignObjectiveIdentifierTool())
    registry.register(CampaignProductSummarizerTool())
    registry.register(CampaignMessagingCreatorTool())
    registry.register(CampaignChannelRecommenderTool())
    registry.register(CampaignChecklistCreatorTool())

    # WF008: SEO Keyword Classification
    registry.register(KeywordReaderTool())
    registry.register(KeywordDeduplicatorTool())
    registry.register(IntentClassifierTool())
    registry.register(CategoryMapperTool())
    registry.register(PriorityIdentifierTool())
    registry.register(ResultsExporterTool())

    # WF009: Employee Task Assignment
    registry.register(TaskRequirementsAnalyzerTool())
    registry.register(SkillsComparatorTool())
    registry.register(WorkloadCheckerTool())
    registry.register(CandidateRankerTool())
    registry.register(EmployeeSelectorTool())
    registry.register(AssignmentSummarizerTool())

    # WF010: Workflow Performance Report
    registry.register(LogLoaderTool())
    registry.register(RateCalculatorTool())
    registry.register(ExecutionTimeCalculatorTool())
    registry.register(ErrorIdentifierTool())
    registry.register(SlowStepsIdentifierTool())
    registry.register(RecommendationsGeneratorTool())

    # WF011: Supplier Delivery Risk Assessment
    registry.register(SupplierDeliveryLoaderTool())
    registry.register(DeliveryRecordValidatorTool())
    registry.register(DeliveryMetricsCalculatorTool())
    registry.register(SupplierRiskEvaluatorTool())
    registry.register(SupplierRiskReporterTool())

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
    # WF005
    "OrderRecord",
    "ShipmentRecord",
    "extract_order_identifier",
    "OrderIdentifierValidatorTool",
    "OrderDataSearchTool",
    "OrderStatusRetrieverTool",
    "ShipmentInfoRetrieverTool",
    "OrderStatusSummarizerTool",
    # WF006
    "CatalogProduct",
    "NormalizedProduct",
    "DuplicateCandidate",
    "load_catalog_csv",
    "normalize_catalog_products",
    "detect_duplicates",
    "CatalogLoaderTool",
    "CatalogNormalizerTool",
    "IdentifierComparatorTool",
    "AttributeComparatorTool",
    "DuplicateGrouperTool",
    "DuplicateConfidenceAssignerTool",
    # WF007
    "ValidatedCampaignInputs",
    "extract_and_validate_campaign_inputs",
    "CampaignInputsValidatorTool",
    "CampaignObjectiveIdentifierTool",
    "CampaignProductSummarizerTool",
    "CampaignMessagingCreatorTool",
    "CampaignChannelRecommenderTool",
    "CampaignChecklistCreatorTool",
    # WF008
    "KeywordRecord",
    "KeywordReaderTool",
    "KeywordDeduplicatorTool",
    "IntentClassifierTool",
    "CategoryMapperTool",
    "PriorityIdentifierTool",
    "ResultsExporterTool",
    # WF009
    "TaskRequirement",
    "EmployeeCandidate",
    "TaskRequirementsAnalyzerTool",
    "SkillsComparatorTool",
    "WorkloadCheckerTool",
    "CandidateRankerTool",
    "EmployeeSelectorTool",
    "AssignmentSummarizerTool",
    # WF010
    "LogLoaderTool",
    "RateCalculatorTool",
    "ExecutionTimeCalculatorTool",
    "ErrorIdentifierTool",
    "SlowStepsIdentifierTool",
    "RecommendationsGeneratorTool",
    # WF011
    "DeliveryRecord",
    "SupplierRiskMetrics",
    "SupplierRiskEvaluation",
    "SupplierDeliveryLoaderTool",
    "DeliveryRecordValidatorTool",
    "DeliveryMetricsCalculatorTool",
    "SupplierRiskEvaluatorTool",
    "SupplierRiskReporterTool",
    "get_wf011_definition",
    "register_wf011_extension",
]
