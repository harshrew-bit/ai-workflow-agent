# AI Workflow Agent — Foundation & LLM-Powered Router

A modular, Excel-driven AI workflow automation system built with Python 3.12, Pydantic, and openpyxl.

The system dynamically loads, validates, and registers business workflows directly from `data/workflows.xlsx`, routes natural language requests to workflows using an LLM-powered router, and executes workflow steps through registered tools with strict separation of concerns.

---

## Architectural Design

The codebase enforces strict separation of concerns across dedicated modules:

- **`app/models/`**: Strongly-typed, validated Pydantic data models:
  - `WorkflowDefinition`: Model encapsulating workflow definitions (`Workflow_ID`, `Workflow_Name`, `Trigger`, `Inputs`, `Steps`, `Decision_Logic`, `Tools_Required`, `Expected_Output`), with whitespace normalization, non-empty validation, and parsed convenience properties.
  - `EvaluationRequest`: Model representing test queries from `Test_Questions` (`Workflow_ID`, `Test_Request`, `What_To_Check`).
  - `WorkflowExecutionResult`, `StepExecutionResult`, `ExecutionStatus`: Generic workflow execution outcomes.
- **`app/registry/`**: Dynamic workbook loading and in-memory workflow registry:
  - `loader.py`: Validates workbook structure, verifies sheets (`Workflows`, `Test_Questions`), verifies required headers, skips blank rows, detects duplicate workflow IDs, and returns validated model instances.
  - `registry.py`: `WorkflowRegistry` provides registration, lookup, duplicate detection, and dynamic membership checks without hardcoded IDs.
  - `exceptions.py`: Actionable exception hierarchy (`WorkbookNotFoundError`, `InvalidWorkbookError`, `MissingSheetError`, `MissingColumnError`, `DuplicateWorkflowIDError`, `WorkflowValidationError`, `WorkflowNotFoundError`).
- **`app/engine/`**: Generic execution interface and step resolution:
  - `context.py`: `ExecutionContext` carrying workflow state, inputs, intermediate variables, and step history.
  - `resolver.py`: `StepResolver`, `ConfigurableStepResolver`, and `StepBinding` implementing extensible, decoupled step-to-tool resolution without hardcoding workflow IDs.
  - `base.py`: `WorkflowExecutor` abstract interface and `GenericWorkflowEngine` driving genuine step-by-step tool execution, passing arguments, saving intermediate outputs, and enforcing accurate error statuses.
- **`app/agent/`**: Natural-language routing and LLM provider integration:
  - `provider.py`: Lightweight provider abstraction (`LLMProvider`, `OpenAICompatibleProvider`, `GeminiProvider`, and `FakeLLMProvider`) without heavy external SDK dependencies. API credentials are read from environment variables and never logged.
  - `prompts.py`: Dynamic workflow catalog injection and system prompt builder.
  - `router.py`: `WorkflowRouter` interface and `LLMWorkflowRouter` implementation with structured JSON output, strict registry validation, confidence thresholds, and robust error handling.
- **`app/tools/`**: Reusable tool abstractions, registry, and domain implementations:
  - `base.py`: `BaseTool` abstract interface and `ToolMetadata`.
  - `registry.py`: `ToolRegistry` for registering and discovering tools dynamically.
  - `inventory.py`: Domain tools for WF001 (`inventory_loader`, `stock_comparator`, `low_stock_identifier`, `reorder_calculator`, `restock_reporter`).
  - `pricing.py`: Domain tools for WF002 (`price_data_loader`, `sku_matcher`, `price_comparator`, `percentage_difference_calculator`, `price_exception_flagger`).
  - `vendor_processing.py`: Domain tools for WF003 (`vendor_file_reader`, `column_detector`, `column_normalizer`, `required_fields_validator`, `invalid_rows_identifier`, `clean_dataset_producer`).
  - `content_generation.py`: Domain tools for WF004 (`attribute_validator`, `product_description_generator`, `short_description_generator`, `seo_title_generator`, `meta_description_generator`).
  - `order_status.py`: Domain tools for WF005 (`order_identifier_validator`, `order_data_search`, `order_status_retriever`, `shipment_info_retriever`, `order_status_summarizer`).
  - `duplicate_detection.py`: Domain tools for WF006 (`catalog_loader`, `catalog_normalizer`, `identifier_comparator`, `attribute_comparator`, `duplicate_grouper`, `duplicate_confidence_assigner`).
  - `campaign_brief.py`: Domain tools for WF007 (`campaign_inputs_validator`, `campaign_objective_identifier`, `campaign_product_summarizer`, `campaign_messaging_creator`, `campaign_channel_recommender`, `campaign_checklist_creator`).
- **`app/orchestrator.py`**: `WorkflowOrchestrator` coordinating the full end-to-end pipeline:
  `Natural-language request → Router → Registry → Engine → Step Resolver → Domain Tools → ExecutionReport`.
- **`app/main.py`**: Command-line interface for natural-language workflow execution.
- **`app/api/`**: Reserved API boundary for future REST / service endpoints.

---

## End-to-End Workflow Execution (WF001 – WF007)

The system features complete end-to-end orchestration across seven business workflows dynamically loaded from `data/workflows.xlsx`:

```
Natural Language Request
         │
         ▼
 ┌──────────────────────┐
 │   LLM Router         │ (extracts parameters, validates confidence, matches workflow)
 └──────────┬───────────┘
            │
            ▼
 ┌──────────────────────┐
 │  Workflow Registry   │ (validates ID against dynamic Excel catalog)
 └──────────┬───────────┘
            │
            ▼
 ┌──────────────────────┐
 │   Generic Engine     │ (resolves step bindings & passes context variables)
 └──────────┬───────────┘
            │
            ▼
 ┌────────────────────────────────────────────────────────┐
 │   Registered Domain Tools (Executed Sequentially)      │
 │   - WF001: 5 inventory & restock tools                 │
 │   - WF002: 5 SKU matching & price comparison tools     │
 │   - WF003: 6 file parsing & normalization tools        │
 │   - WF004: 5 attribute validation & SEO content tools  │
 │   - WF005: 5 order lookup & shipment tracking tools    │
 │   - WF006: 6 duplicate detection & grouping tools      │
 │   - WF007: 6 campaign brief synthesis tools            │
 └──────────┬─────────────────────────────────────────────┘
            │
            ▼
 ┌──────────────────────┐
 │   ExecutionReport    │ (structured summary with step metrics)
 └──────────────────────┘
```

### Supported Workflows & Business Rules

#### 1. WF001 — Inventory Restock Check
- **Trigger**: "Which products need restocking?"
- **Decision Logic**: If `current_stock < minimum_stock`, flag product for restock.
- **Boundary Condition**: Items exactly at threshold (`current_stock == minimum_stock`) are marked adequately stocked (`reorder_quantity = 0`).
- **Zero Stock**: If `current_stock == 0`, `reorder_quantity = minimum_stock`.

#### 2. WF002 — Product Price Validation
- **Trigger**: "Find products where vendor price differs by more than 10%."
- **Steps**: Load product prices $\to$ match products by SKU $\to$ compare internal and vendor prices $\to$ calculate percentage difference $\to$ flag exceptions.
- **Decision Logic**: Flag records strictly when `percentage_difference > 10.0%`.
- **Boundary Condition**: Differences of exactly `10.0%` are marked `COMPLIANT`. Differences of `10.01%` or higher are flagged as `EXCEPTION (>10%)`.
- **Data Integrity**: Handles missing SKUs, invalid/negative prices, and tracks unmatched vendor and internal records.

#### 3. WF003 — Vendor File Processing
- **Trigger**: "Process this vendor spreadsheet and show invalid rows."
- **Steps**: Read file $\to$ detect columns $\to$ normalize column names $\to$ validate required fields $\to$ identify invalid rows $\to$ produce cleaned dataset.
- **Decision Logic**: Rows missing SKU or product name are invalid.
- **Column Normalization**: Detects synonyms such as `Item_SKU`, `Item_Title`, `Unit_Price`, `Quantity_Available` and normalizes to canonical names.
- **Safety**: Separates valid records from invalid rows with actionable diagnostics; **never overwrites the input file**.

#### 4. WF004 — Product Description Generator
- **Trigger**: "Generate SEO content for this product."
- **Steps**: Validate required attributes $\to$ create product description $\to$ generate short description $\to$ generate SEO title $\to$ generate meta description.
- **Decision Logic**: Strictly forbids hallucinating or inventing missing attributes. Unprovided optional attributes are explicitly omitted and marked in report metadata.
- **Validation**: Requires `product_name`; raises validation error if empty.
- **Simulation Transparency**: When generated in simulated/offline mode, output is clearly badged with `is_simulated = True`.

#### 5. WF005 — Customer Order Status
- **Trigger**: "What is the status of order ORD-1001?" / "Where is my order?"
- **Steps**: Validate identifier $\to$ search order data $\to$ retrieve order status $\to$ retrieve shipment information $\to$ summarize current status.
- **Decision Logic**: Look up order using order ID or customer email. If found, retrieve shipment tracking status, carrier, and estimated delivery. If no order matches, execute workbook decision logic: **prompt the user for another identifier**.
- **Privacy & Safety**: Never exposes unnecessary PII or calls live carrier APIs. All lookups resolve safely against simulated offline datasets.

#### 6. WF006 — Duplicate Product Detection
- **Trigger**: "Find duplicate products in catalog."
- **Steps**: Load products $\to$ normalize names/SKUs $\to$ compare identifiers $\to$ compare product attributes $\to$ group likely duplicates $\to$ assign confidence.
- **Decision Logic**:
  - Exact normalized SKU match $\to$ `DEFINITE` duplicate (`100%` similarity).
  - High attribute similarity (Token Dice $\ge 0.75$ with matching brand) $\to$ `LIKELY` duplicate.
  - Moderate attribute similarity ($0.65 \le \text{Dice} < 0.75$) $\to$ `POSSIBLE` duplicate (manual review recommended).
  - Distinct items (e.g. MacBook Pro vs Dell Monitor) $\to$ not flagged.
- **Transparency**: Every analysis explicitly documents matching methodology and tokenization limitations.

#### 7. WF007 — Marketing Campaign Brief
- **Trigger**: "Generate marketing campaign brief."
- **Steps**: Validate inputs $\to$ identify campaign objective $\to$ summarize products $\to$ create messaging $\to$ create channel recommendations $\to$ create campaign checklist.
- **Decision Logic**: Requires both `campaign_goal` and `dates`/timeline. If either is missing, raises a validation error rather than hallucinating dates or goals.
- **No Hallucination**: Does not invent promotional discounts or pricing claims if not explicitly provided by the user. Badged with `is_simulated = True`.

> [!NOTE]
> **Sample Datasets Notice**:
> - `data/sample_inventory.csv`: Realistic inventory levels and costs (WF001).
> - `data/sample_internal_prices.csv` & `data/sample_vendor_prices.csv`: Multi-supplier product catalog and vendor quotes (WF002).
> - `data/sample_vendor_catalog.csv`: Ingestion file containing column variations and mixed valid/invalid records (WF003).
> - `data/sample_orders.csv` & `data/sample_shipments.csv`: Simulated orders and tracking records (WF005).
> - `data/sample_products_catalog.csv`: Multi-category catalog with exact SKU duplicates, near-duplicate models, and distinct items (WF006).
>
> All sample data is simulated for testing and demonstration purposes without external side effects.
>
> **Workflow Implementation Status**: Workflows WF001 through WF007 are fully implemented end-to-end with genuine domain tools. Workflows WF008–WF010 are registered and ready for routing in `data/workflows.xlsx`.

---

## CLI Usage

The system includes a CLI interface (`app/main.py`) to run natural language queries end-to-end:

```bash
# WF001: Inventory Restock Check
python3 -m app.main --mock-route WF001 "Which products need restocking?"

# WF002: Product Price Validation
python3 -m app.main --mock-route WF002 "Find products where vendor price differs by more than 10%."

# WF003: Vendor File Processing
python3 -m app.main --mock-route WF003 "Process this vendor spreadsheet and show invalid rows."

# WF004: Product Description Generator
python3 -m app.main --mock-route WF004 "Generate SEO content for this product."

# WF004 with custom parameters
python3 -m app.main --mock-route WF004 --product-name "Pro Wireless Mouse" --color "Midnight Blue" --category "Electronics" "Generate product content"

# WF005: Customer Order Status (known order)
python3 -m app.main --mock-route WF005 --order-id "ORD-1001" "What is the status of order ORD-1001?"

# WF005: Customer Order Status (unknown order -> prompts for another identifier)
python3 -m app.main --mock-route WF005 --order-id "UNKNOWN-999" "Where is my order UNKNOWN-999?"

# WF006: Duplicate Product Detection
python3 -m app.main --mock-route WF006 "Find duplicate products in catalog"

# WF007: Marketing Campaign Brief
python3 -m app.main --mock-route WF007 --campaign-goal "Launch Summer Trail Runners" --dates "June 1 - July 15" --promotion "20% off with promo SUMMER20" --products "Trail Runner Pro, Quick-Dry Socks" "Generate marketing campaign brief"

# Output as structured JSON
python3 -m app.main --mock-route WF002 --json "Validate prices"
```

---

## Extensibility Design

The system does **not** hardcode workflow IDs (WF001–WF010) into routing or engine logic:
- The registry accepts any valid `WorkflowDefinition` programmatically or via Excel.
- The `LLMWorkflowRouter` constructs its prompt dynamically from whatever workflows are supplied in `available_workflows`. Adding an 11th workflow (`WF011`) makes it immediately eligible for natural-language routing without changing router code.
- Hallucinated or unregistered workflow IDs returned by the model are strictly rejected by registry validation.
- Tool bindings are mapped through `ConfigurableStepResolver`; business rules are evaluated deterministically by tools, not the router.

---

## Confidence & Clarification Policy

`LLMWorkflowRouter` applies the following validation policy to all decisions:

1. **Confidence Semantics**:
   The `confidence` score in `RoutingDecision` represents the **model-reported routing certainty score** (0.0 to 1.0) returned by the LLM, **not a mathematically calibrated probability**. The system compares this score directly against `confidence_threshold` (default `0.70`). No artificial secondary calibration mechanism is applied.
2. **Registry Verification (Zero Hallucination Tolerance)**:
   The selected `workflow_id` must match a workflow currently registered in the catalog. If the model returns an unregistered or invented ID, the match is rejected, `workflow_id` is set to `None`, `confidence` is reset to `0.0`, and `requires_clarification` is set to `True`.
3. **Threshold Enforcement**:
   Matches scoring below `confidence_threshold` are flagged with `requires_clarification = True`, preventing execution on weak guesses.
4. **Ambiguous or Unrelated Requests**:
   If the user query does not match any registered workflow trigger or lacks critical parameters, the router returns `workflow_id = None` and `requires_clarification = True`.
5. **Sanitized Provider Error Handling**:
   Network errors, timeouts, or HTTP errors are sanitized to prevent secret leakage. Raw HTTP response bodies, request URLs with credentials, and authorization headers are never exposed in exceptions or user-facing reasoning.
6. **Explicit Unconfigured Fallback**:
   When no live LLM credentials (`OPENAI_API_KEY` or `GEMINI_API_KEY`) are present, the system defaults to a safe fallback provider that returns `workflow_id = None`, `requires_clarification = True`, and explicitly states that automated live LLM routing is inactive. It never silently pretends a live model completed the routing.

---

## Setup & Environment

### Prerequisites
- Python 3.12+

### Virtual Environment Setup

```bash
# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate  # On macOS/Linux
# .venv\Scripts\activate   # On Windows

# Install minimal project dependencies
pip install pydantic openpyxl pytest
```

### LLM Provider Configuration

Configure environment variables in `.env` (copied from `.env.example`):

```bash
cp .env.example .env
```

To configure an OpenAI-compatible provider:
```env
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini
```

To configure Google Gemini:
```env
LLM_PROVIDER=gemini
GEMINI_API_KEY=AIza...
GEMINI_MODEL=gemini-1.5-flash
```

For hermetic, offline testing, `FakeLLMProvider` is used by default with zero network calls or credentials required.

---

## Running Tests

All automated tests use `pytest` and execute against both the assessment workbook `data/workflows.xlsx` (in read-only mode) and temporary fixtures for edge-case validation.

```bash
# Run the complete test suite
pytest -v

# Run specific test modules
pytest tests/test_wf001_inventory.py
pytest tests/test_wf002_pricing.py
pytest tests/test_wf003_vendor_processing.py
pytest tests/test_wf004_content_generation.py
pytest tests/test_wf005_order_status.py
pytest tests/test_wf006_duplicate_detection.py
pytest tests/test_wf007_campaign_brief.py
pytest tests/test_orchestrator_wf005_wf007.py
pytest tests/test_orchestrator_wf002_wf004.py
pytest tests/test_orchestrator.py
pytest tests/test_router.py
pytest tests/test_execution.py
pytest tests/test_loader.py
pytest tests/test_registry.py
pytest tests/test_models.py
pytest tests/test_engine_interfaces.py
```
