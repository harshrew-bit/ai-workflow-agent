"""Step-to-tool resolution interfaces and configuration."""

from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, Optional, Sequence, Union
from pydantic import BaseModel, Field

from app.engine.context import ExecutionContext
from app.models.workflow import WorkflowDefinition
from app.tools.registry import ToolRegistry


class StepResolutionError(Exception):
    """Base exception for step resolution failures."""

    pass


class UnresolvedStepError(StepResolutionError):
    """Raised when a workflow step cannot be mapped to any registered tool."""

    pass


class StepBinding(BaseModel):
    """Explicit binding configuration connecting a workflow step to an executable tool."""

    model_config = {"arbitrary_types_allowed": True}

    tool_name: str = Field(..., min_length=1, description="Name of the registered tool")
    step_name: Optional[str] = Field(default=None, description="Step name or pattern to bind")
    workflow_id: Optional[str] = Field(default=None, description="Optional workflow ID scope")
    input_mapper: Optional[
        Union[Callable[[ExecutionContext], Dict[str, Any]], Dict[str, Any]]
    ] = Field(default=None, description="Callable or dict mapping context variables to tool inputs")
    output_key: Optional[str] = Field(
        default=None, description="Context variable name to store the tool output in"
    )


class StepResolver(ABC):
    """Abstract interface for resolving human-readable workflow steps to executable tools."""

    @abstractmethod
    def resolve(
        self,
        step_name: str,
        workflow: WorkflowDefinition,
        context: ExecutionContext,
        tool_registry: ToolRegistry,
    ) -> Optional[StepBinding]:
        """Resolve a workflow step to an executable StepBinding, or None if unresolvable."""
        pass


class ConfigurableStepResolver(StepResolver):
    """Extensible step-to-tool resolver.

    Provides a clean, generic mechanism to map human-readable workflow steps
    to concrete tools without embedding workflow-specific code inside the engine.

    Resolution order:
    1. Workflow-scoped explicit binding (workflow_id + step_name)
    2. Global explicit binding (step_name)
    3. Direct tool name match (tool_registry has a tool with the step_name)
    4. Registered tool name match (normalized case-insensitive match against registered tools)
    """

    def __init__(self) -> None:
        self._workflow_bindings: Dict[tuple[str, str], StepBinding] = {}
        self._global_bindings: Dict[str, StepBinding] = {}

    def bind(
        self,
        step_name: str,
        tool_name: str,
        workflow_id: Optional[str] = None,
        input_mapper: Optional[
            Union[Callable[[ExecutionContext], Dict[str, Any]], Dict[str, Any]]
        ] = None,
        output_key: Optional[str] = None,
    ) -> "ConfigurableStepResolver":
        """Register an explicit binding between a step name and a tool."""
        binding = StepBinding(
            tool_name=tool_name,
            step_name=step_name,
            workflow_id=workflow_id,
            input_mapper=input_mapper,
            output_key=output_key,
        )
        return self.register_binding(binding)

    def register_binding(self, binding: StepBinding) -> "ConfigurableStepResolver":
        """Register a StepBinding instance."""
        norm_step = (binding.step_name or "").strip().lower()
        if binding.workflow_id:
            self._workflow_bindings[(binding.workflow_id, norm_step)] = binding
        else:
            self._global_bindings[norm_step] = binding
        return self

    def resolve(
        self,
        step_name: str,
        workflow: WorkflowDefinition,
        context: ExecutionContext,
        tool_registry: ToolRegistry,
    ) -> Optional[StepBinding]:
        """Resolve a step using workflow-scoped bindings, global bindings, or direct tool match."""
        norm_step = step_name.strip().lower()

        # 1. Workflow-specific explicit binding
        wf_key = (workflow.workflow_id, norm_step)
        if wf_key in self._workflow_bindings:
            return self._workflow_bindings[wf_key]

        # 2. Global explicit binding
        if norm_step in self._global_bindings:
            return self._global_bindings[norm_step]

        # 3. Direct match: if tool_registry has a tool named exactly like this step
        if tool_registry.has_tool(norm_step):
            tool = tool_registry.get(norm_step)
            return StepBinding(
                step_name=step_name,
                tool_name=tool.name if tool else step_name,
            )

        # 4. Registered tools case-insensitive match
        for reg_tool in tool_registry.list_tools():
            if reg_tool.name.strip().lower() == norm_step:
                return StepBinding(
                    step_name=step_name,
                    tool_name=reg_tool.name,
                )

        return None


def create_default_step_resolver() -> ConfigurableStepResolver:
    """Create and pre-configure step resolver with standard workflow step bindings."""
    resolver = ConfigurableStepResolver()

    # WF001: Inventory Restock Check
    resolver.bind(
        workflow_id="WF001",
        step_name="Load inventory",
        tool_name="inventory_loader",
    )
    resolver.bind(
        workflow_id="WF001",
        step_name="compare current stock with minimum threshold",
        tool_name="stock_comparator",
    )
    resolver.bind(
        workflow_id="WF001",
        step_name="identify low-stock products",
        tool_name="low_stock_identifier",
    )
    resolver.bind(
        workflow_id="WF001",
        step_name="calculate reorder quantity",
        tool_name="reorder_calculator",
    )
    resolver.bind(
        workflow_id="WF001",
        step_name="generate restock list",
        tool_name="restock_reporter",
    )

    # WF002: Product Price Validation
    resolver.bind(
        workflow_id="WF002",
        step_name="Load product prices",
        tool_name="price_data_loader",
    )
    resolver.bind(
        workflow_id="WF002",
        step_name="match products by SKU",
        tool_name="sku_matcher",
    )
    resolver.bind(
        workflow_id="WF002",
        step_name="compare internal and vendor prices",
        tool_name="price_comparator",
    )
    resolver.bind(
        workflow_id="WF002",
        step_name="calculate percentage difference",
        tool_name="percentage_difference_calculator",
    )
    resolver.bind(
        workflow_id="WF002",
        step_name="flag exceptions",
        tool_name="price_exception_flagger",
    )

    # WF003: Vendor File Processing
    resolver.bind(
        workflow_id="WF003",
        step_name="Read file",
        tool_name="vendor_file_reader",
    )
    resolver.bind(
        workflow_id="WF003",
        step_name="detect columns",
        tool_name="column_detector",
    )
    resolver.bind(
        workflow_id="WF003",
        step_name="normalize column names",
        tool_name="column_normalizer",
    )
    resolver.bind(
        workflow_id="WF003",
        step_name="validate required fields",
        tool_name="required_fields_validator",
    )
    resolver.bind(
        workflow_id="WF003",
        step_name="identify invalid rows",
        tool_name="invalid_rows_identifier",
    )
    resolver.bind(
        workflow_id="WF003",
        step_name="produce cleaned dataset",
        tool_name="clean_dataset_producer",
    )

    # WF004: Product Description Generator
    resolver.bind(
        workflow_id="WF004",
        step_name="Validate required attributes",
        tool_name="attribute_validator",
    )
    resolver.bind(
        workflow_id="WF004",
        step_name="create product description",
        tool_name="product_description_generator",
    )
    resolver.bind(
        workflow_id="WF004",
        step_name="generate short description",
        tool_name="short_description_generator",
    )
    resolver.bind(
        workflow_id="WF004",
        step_name="generate SEO title",
        tool_name="seo_title_generator",
    )
    resolver.bind(
        workflow_id="WF004",
        step_name="generate meta description",
        tool_name="meta_description_generator",
    )

    # WF005: Customer Order Status
    resolver.bind(
        workflow_id="WF005",
        step_name="Validate identifier",
        tool_name="order_identifier_validator",
    )
    resolver.bind(
        workflow_id="WF005",
        step_name="search order data",
        tool_name="order_data_search",
    )
    resolver.bind(
        workflow_id="WF005",
        step_name="retrieve order status",
        tool_name="order_status_retriever",
    )
    resolver.bind(
        workflow_id="WF005",
        step_name="retrieve shipment information",
        tool_name="shipment_info_retriever",
    )
    resolver.bind(
        workflow_id="WF005",
        step_name="summarize current status",
        tool_name="order_status_summarizer",
    )

    # WF006: Duplicate Product Detection
    resolver.bind(
        workflow_id="WF006",
        step_name="Load products",
        tool_name="catalog_loader",
    )
    resolver.bind(
        workflow_id="WF006",
        step_name="normalize names/SKUs",
        tool_name="catalog_normalizer",
    )
    resolver.bind(
        workflow_id="WF006",
        step_name="compare identifiers",
        tool_name="identifier_comparator",
    )
    resolver.bind(
        workflow_id="WF006",
        step_name="compare product attributes",
        tool_name="attribute_comparator",
    )
    resolver.bind(
        workflow_id="WF006",
        step_name="group likely duplicates",
        tool_name="duplicate_grouper",
    )
    resolver.bind(
        workflow_id="WF006",
        step_name="assign confidence",
        tool_name="duplicate_confidence_assigner",
    )

    # WF007: Marketing Campaign Brief
    resolver.bind(
        workflow_id="WF007",
        step_name="Validate inputs",
        tool_name="campaign_inputs_validator",
    )
    resolver.bind(
        workflow_id="WF007",
        step_name="identify campaign objective",
        tool_name="campaign_objective_identifier",
    )
    resolver.bind(
        workflow_id="WF007",
        step_name="summarize products",
        tool_name="campaign_product_summarizer",
    )
    resolver.bind(
        workflow_id="WF007",
        step_name="create messaging",
        tool_name="campaign_messaging_creator",
    )
    resolver.bind(
        workflow_id="WF007",
        step_name="create channel recommendations",
        tool_name="campaign_channel_recommender",
    )
    resolver.bind(
        workflow_id="WF007",
        step_name="create campaign checklist",
        tool_name="campaign_checklist_creator",
    )

    # WF008: SEO Keyword Classification
    resolver.bind(
        workflow_id="WF008",
        step_name="Read keywords",
        tool_name="keyword_reader",
    )
    resolver.bind(
        workflow_id="WF008",
        step_name="remove duplicates",
        tool_name="keyword_deduplicator",
    )
    resolver.bind(
        workflow_id="WF008",
        step_name="classify search intent",
        tool_name="intent_classifier",
    )
    resolver.bind(
        workflow_id="WF008",
        step_name="map keywords to categories",
        tool_name="category_mapper",
    )
    resolver.bind(
        workflow_id="WF008",
        step_name="identify high-priority keywords",
        tool_name="priority_identifier",
    )
    resolver.bind(
        workflow_id="WF008",
        step_name="export results",
        tool_name="results_exporter",
    )

    # WF009: Employee Task Assignment
    resolver.bind(
        workflow_id="WF009",
        step_name="Understand task requirements",
        tool_name="task_requirements_analyzer",
    )
    resolver.bind(
        workflow_id="WF009",
        step_name="compare employee skills",
        tool_name="skills_comparator",
    )
    resolver.bind(
        workflow_id="WF009",
        step_name="check current workload",
        tool_name="workload_checker",
    )
    resolver.bind(
        workflow_id="WF009",
        step_name="rank candidates",
        tool_name="candidate_ranker",
    )
    resolver.bind(
        workflow_id="WF009",
        step_name="select employee",
        tool_name="employee_selector",
    )
    resolver.bind(
        workflow_id="WF009",
        step_name="generate assignment summary",
        tool_name="assignment_summarizer",
    )

    # WF010: Workflow Performance Report
    resolver.bind(
        workflow_id="WF010",
        step_name="Load execution logs",
        tool_name="log_loader",
    )
    resolver.bind(
        workflow_id="WF010",
        step_name="calculate success/failure rate",
        tool_name="rate_calculator",
    )
    resolver.bind(
        workflow_id="WF010",
        step_name="calculate average execution time",
        tool_name="execution_time_calculator",
    )
    resolver.bind(
        workflow_id="WF010",
        step_name="identify frequent errors",
        tool_name="error_identifier",
    )
    resolver.bind(
        workflow_id="WF010",
        step_name="identify slow steps",
        tool_name="slow_steps_identifier",
    )
    resolver.bind(
        workflow_id="WF010",
        step_name="generate recommendations",
        tool_name="recommendations_generator",
    )

    # WF011: Supplier Delivery Risk Assessment
    resolver.bind(
        workflow_id="WF011",
        step_name="Load supplier delivery records",
        tool_name="supplier_delivery_loader",
    )
    resolver.bind(
        workflow_id="WF011",
        step_name="Validate delivery records",
        tool_name="delivery_record_validator",
    )
    resolver.bind(
        workflow_id="WF011",
        step_name="Calculate supplier delivery metrics",
        tool_name="delivery_metrics_calculator",
    )
    resolver.bind(
        workflow_id="WF011",
        step_name="Evaluate supplier risk levels",
        tool_name="supplier_risk_evaluator",
    )
    resolver.bind(
        workflow_id="WF011",
        step_name="Generate supplier risk report",
        tool_name="supplier_risk_reporter",
    )

    return resolver
