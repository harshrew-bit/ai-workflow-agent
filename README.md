# AI Workflow Agent

A modular, Excel-driven AI workflow automation system built with **Python 3.12**, **Pydantic v2**, and **openpyxl**.

The system dynamically loads and validates business workflow definitions directly from an Excel workbook (`data/workflows.xlsx`), routes natural-language requests using an LLM-powered router (supporting **Google Gemini**, **OpenAI-compatible APIs**, or an offline **fallback**), resolves human-readable steps to registered domain tools, and executes them through a generic, reusable execution engine.

---

## Table of Contents

- [Quick Demo (No API Key Needed)](#quick-demo-no-api-key-needed)
- [Live LLM Routing: Status](#live-llm-routing-status)
- [Key Features & Technology Stack](#key-features--technology-stack)
- [Architecture Overview](#architecture-overview)
- [Deterministic Offline Router & Scoring](#deterministic-offline-router--scoring)
- [Project Structure](#project-structure)
- [Official Workflow Catalog (WF001 – WF010)](#official-workflow-catalog-wf001--wf010)
- [Setup & Installation](#setup--installation)
- [LLM Provider Configuration](#llm-provider-configuration)
- [CLI Usage](#cli-usage)
  - [Offline Natural Language Routing](#1-offline-natural-language-routing)
  - [Live LLM Routing](#2-live-llm-routing)
  - [Deterministic Demonstration Mode (`--mock-route`)](#3-deterministic-demonstration-mode---mock-route)
  - [Structured JSON Output](#4-structured-json-output)
- [Routing, Confidence & Clarification Policy](#routing-confidence--clarification-policy)
- [Tool Execution, Data Safety & Simulation Transparency](#tool-execution-data-safety--simulation-transparency)
- [Demonstration Extension: WF011 Supplier Delivery Risk Assessment](#demonstration-extension-wf011-supplier-delivery-risk-assessment)
- [How to Extend the System with New Workflows](#how-to-extend-the-system-with-new-workflows)
- [Testing & Verification](#testing--verification)
- [Sample Datasets](#sample-datasets)
- [Limitations & Future Improvements](#limitations--future-improvements)

---

## Quick Demo (No API Key Needed)

The agent runs fully offline out of the box using deterministic token matching against the official workbook definitions. Try these three commands in your terminal:

### 1. Inventory Restock Check (WF001)
```bash
python -m app.main "Check today's inventory and identify products that need restocking."
```
- **Expected Outcome**: Status `SUCCESS`, Selected Workflow `WF001 (Inventory Restock Check)`, `Routing Mode: OFFLINE`.
- **Result**: Identifies 4 low-stock items (`PRD-001`, `PRD-003`, `PRD-005`, `PRD-007`) requiring 61 total reorder units, exits with code `0`.

### 2. Customer Order Status (WF005)
```bash
python -m app.main "Where is order ORD-1001?"
```
- **Expected Outcome**: Status `SUCCESS`, Selected Workflow `WF005 (Customer Order Status)`, `Routing Mode: OFFLINE`.
- **Result**: Extracts order ID `ORD-1001`, returns status `SHIPPED` with carrier tracking details (`FastShip Express`, `TRK-987654321`), exits with code `0`.

### 3. Off-Topic Query Rejection
```bash
python -m app.main "What is the weather in Paris?"
```
- **Expected Outcome**: Status `NEEDS_CLARIFICATION`, Selected Workflow `None`, `Routing Mode: OFFLINE`.
- **Result**: Cleanly flags that the request cannot be matched to any registered workflow, executes zero domain tools, exits with code `4`.

---

## Live LLM Routing: Status

- **Status**: **VERIFIED — WF002 end-to-end**.
- **Provider**: Google Gemini API using `gemini-2.5-flash-lite`, configured through environment variables.
- **Verification result**: Live LLM routing selected `WF002 (Product Price Validation)` and the complete workflow executed successfully using the sample internal and vendor price CSVs.
- **Observed output**: 7 products matched and compared; 3 exceptions exceeded the strict 10% price-difference threshold. Unmatched SKUs were also reported.
- **Verification scope**: Live API execution has been verified for WF002. The other official workflows have been exercised using local sample data and offline tests; this does not imply that all workflows have been individually verified with a live LLM.
- **Offline behavior**: The deterministic offline router remains available when live LLM configuration is unavailable. See [`examples/live/README.md`](examples/live/README.md) for setup instructions and live-routing verification commands.

---

## Key Features & Technology Stack

- **Excel-Driven Dynamic Catalog**: Workflows are loaded at runtime from `data/workflows.xlsx`. Adding or updating workflows in the catalog requires no changes to core engine or router code.
- **LLM-Powered Semantic Router**: Translates natural-language requests into structured routing decisions with parameter extraction, zero-hallucination validation against the active registry, and confidence thresholding.
- **Generic Workflow Execution Engine**: `GenericWorkflowEngine` executes parsed workflow steps sequentially by resolving tools dynamically through dependency injection. It contains **zero workflow-specific branching** (`if workflow_id == ...`).
- **10 Official End-to-End Workflows**: Fully implemented domain tools for all workflows in the assessment workbook (WF001–WF010), handling boundary conditions, edge cases, and deterministic business rules.
- **Proven Extensibility (WF011)**: Includes a standalone demonstration extension (`WF011 — Supplier Delivery Risk Assessment`) proving that new workflows can be registered and executed through clean extension points without modifying core engine abstractions.
- **Zero Heavy SDK Dependencies**: HTTP communication with Google Gemini and OpenAI is implemented using Python's standard library `urllib` and `certifi`, avoiding bulky external SDKs.
- **Strict Data Safety & Offline Simulation**: All integrations operate against offline simulated sample data. No real external APIs, ERPs, or production databases are contacted, and inputs are never destructively overwritten.
- **Sanitized Error Handling**: Network and API exceptions are sanitized to ensure credentials, authorization headers, and raw provider payloads are never leaked into logs or application reasoning.

### Technology Stack

| Component | Technology | Purpose |
|---|---|---|
| Language | **Python 3.12+** | Core runtime |
| Data Modeling | **Pydantic v2** (`pydantic>=2.0.0`) | Validated data contracts, settings, and execution reports |
| Excel Ingestion | **openpyxl** (`openpyxl>=3.1.5`) | Workbook parsing and header validation |
| Environment Config | **python-dotenv** (`python-dotenv>=1.0.0`) | `.env` file discovery and loading |
| TLS / Certificates | **certifi** (`certifi>=2024.2.2`) | Mozilla root CA bundle for secure Gemini HTTPS requests |
| Test Framework | **pytest** (`pytest>=8.0.0`) | Automated test suite (run `pytest -q`) |

---

## Architecture Overview

The system decouples catalog ingestion, intent routing, step resolution, and tool execution into distinct, testable layers:

```mermaid
flowchart TD
    UserReq["User Natural Language Request"] --> Orchestrator["WorkflowOrchestrator"]

    subgraph CatalogLayer["1. Catalog & Discovery Layer"]
        ExcelFile["data/workflows.xlsx"] --> Loader["Excel Loader\n(app/registry/loader.py)"]
        Loader --> Registry["WorkflowRegistry\n(app/registry/registry.py)"]
    end

    subgraph RoutingLayer["2. Routing & LLM Layer"]
        Orchestrator --> Router["LLMWorkflowRouter\n(app/agent/router.py)"]
        Registry -. Catalog Metadata .-> Router
        Router --> Provider["LLMProvider\n(Gemini / OpenAI / Fake)"]
        Provider -. JSON Response .-> Router
        Router --> Decision["RoutingDecision\n(workflow_id, confidence, extracted_inputs)"]
    end

    Decision --> Validate{"Validate against\nRegistry?"}
    Validate -- "Unregistered / Low Confidence" --> Clarify["ExecutionReport\n(status: needs_clarification)"]
    Validate -- "Valid Match" --> ExecPrep["Prepare Execution Context & Inputs"]

    subgraph EngineLayer["3. Generic Execution Layer"]
        ExecPrep --> Engine["GenericWorkflowEngine\n(app/engine/base.py)"]
        Engine --> StepLoop["For each step in workflow.parsed_steps:"]
        StepLoop --> Resolver["ConfigurableStepResolver\n(app/engine/resolver.py)"]
        Resolver --> ToolReg["ToolRegistry\n(app/tools/registry.py)"]
        ToolReg --> ConcreteTool["Execute BaseTool Instance\n(app/tools/*.py)"]
        ConcreteTool --> Context["Update ExecutionContext\n(last_output, step_n_output)"]
        Context -. Context Variables .-> StepLoop
    end

    Engine --> FinalReport["ExecutionReport\n(status: success, step reports, structured output)"]
```

### Architectural Responsibilities

1. **`app/models/`**: Defines Pydantic models for workflow metadata (`WorkflowDefinition`), test requests (`EvaluationRequest`), step results (`StepExecutionResult`), and reports (`ExecutionReport`).
2. **`app/registry/`**: Loads `data/workflows.xlsx` via `openpyxl`, verifies sheets and columns, skips empty rows, validates data integrity, and populates the in-memory `WorkflowRegistry`.
3. **`app/agent/`**: Manages LLM communications (`provider.py`), formats system prompts dynamically (`prompts.py`), and routes natural-language requests into structured `RoutingDecision` objects (`router.py`).
4. **`app/engine/`**: Manages execution state (`context.py`), maps human-readable step names to tool names (`resolver.py`), and drives generic step-by-step execution (`base.py`).
5. **`app/tools/`**: Houses the `BaseTool` interface, `ToolRegistry`, and domain implementations across all business workflows.
6. **`app/orchestrator.py`**: Coordinates the entire pipeline (`User Request → Router → Registry → Engine → Step Resolver → Tools → Report`).
7. **`app/main.py`**: Command-line entrypoint with argument parsing, formatted table outputs, and raw JSON output options.

---

## Project Structure

```
ai-workflow-agent/
├── app/
│   ├── __init__.py
│   ├── main.py                  # CLI entrypoint and output formatters
│   ├── orchestrator.py          # End-to-end pipeline orchestrator
│   ├── agent/
│   │   ├── __init__.py
│   │   ├── prompts.py           # Dynamic system prompt & catalog formatting
│   │   ├── provider.py          # LLM providers (Gemini, OpenAI, FakeLLM)
│   │   └── router.py            # Natural-language workflow router
│   ├── api/
│   │   └── __init__.py          # Reserved API interface package
│   ├── engine/
│   │   ├── __init__.py
│   │   ├── base.py              # GenericWorkflowEngine (zero ID-specific logic)
│   │   ├── context.py           # ExecutionContext state store
│   │   └── resolver.py          # StepResolver and ConfigurableStepResolver
│   ├── models/
│   │   ├── __init__.py
│   │   ├── evaluation.py        # EvaluationRequest and test models
│   │   ├── execution.py         # StepExecutionResult & WorkflowExecutionResult
│   │   ├── report.py            # ExecutionReport and StepReport models
│   │   └── workflow.py          # WorkflowDefinition model and helpers
│   ├── registry/
│   │   ├── __init__.py
│   │   ├── exceptions.py        # Actionable catalog exception hierarchy
│   │   ├── loader.py            # openpyxl Excel ingestion and validator
│   │   └── registry.py          # Dynamic in-memory WorkflowRegistry
│   └── tools/
│       ├── __init__.py          # create_default_tool_registry()
│       ├── base.py              # BaseTool and ToolMetadata contracts
│       ├── campaign_brief.py    # WF007 domain tools
│       ├── content_generation.py# WF004 domain tools
│       ├── duplicate_detection.py# WF006 domain tools
│       ├── inventory.py         # WF001 domain tools
│       ├── order_status.py      # WF005 domain tools
│       ├── performance_report.py# WF010 domain tools
│       ├── pricing.py           # WF002 domain tools
│       ├── registry.py          # Reusable ToolRegistry
│       ├── seo_keywords.py      # WF008 domain tools
│       ├── supplier_risk.py     # WF011 demonstration extension domain tools
│       ├── task_assignment.py   # WF009 domain tools
│       └── vendor_processing.py # WF003 domain tools
├── data/
│   ├── workflows.xlsx           # Official assessment workbook (WF001–WF010)
│   ├── sample_employees.csv     # Simulated employee skills & workloads (WF009)
│   ├── sample_internal_prices.csv # Internal price list (WF002)
│   ├── sample_inventory.csv     # Inventory levels & reorder thresholds (WF001)
│   ├── sample_keywords.csv      # Search queries, volumes, CPC (WF008)
│   ├── sample_orders.csv        # Customer orders (WF005)
│   ├── sample_products_catalog.csv # Product catalog with duplicates (WF006)
│   ├── sample_shipments.csv     # Shipping carrier tracking records (WF005)
│   ├── sample_supplier_deliveries.csv # Simulated supplier deliveries (WF011)
│   ├── sample_vendor_catalog.csv# Unprocessed vendor feed with bad rows (WF003)
│   ├── sample_vendor_prices.csv # Vendor quotes (WF002)
│   └── sample_workflow_logs.csv # Execution telemetry logs (WF010)
├── examples/                    # Benchmark requests, expected outputs, and live docs
│   ├── requests.md              # Catalog of 22 benchmark test requests
│   ├── expected.json            # Reference expected workflows, statuses, exit codes
│   ├── live/                    # Live LLM routing verification guide
│   └── output/                  # Generated benchmark text and JSON outputs
├── scripts/                     # Verification runner scripts (Bash & PowerShell)
│   ├── run_examples.sh          # Offline benchmark verification runner (Bash)
│   └── run_examples.ps1         # Offline benchmark verification runner (PowerShell)
├── tests/                       # Comprehensive automated test suite (run pytest -q)
├── .env.example                 # Documented environment configuration template
├── .gitignore                   # Ignore patterns for secrets, venv, caches
├── pyproject.toml               # Project metadata, dependencies, and pytest config
└── README.md                    # Technical documentation
```

---

## Official Workflow Catalog (WF001 – WF010)

The ten official workflows defined in `data/workflows.xlsx` are implemented end-to-end with dedicated domain tools and deterministic business logic:

### 1. WF001 — Inventory Restock Check
- **Workbook Name**: Inventory Restock Check
- **Trigger**: *"Which products need restocking?"*
- **Steps**: Load inventory $\to$ compare current stock with minimum threshold $\to$ identify low-stock products $\to$ calculate reorder quantity $\to$ generate restock list.
- **Key Business Rules**:
  - A product requires restocking strictly when $\text{current\_stock} < \text{minimum\_stock}$.
  - Boundary: Items exactly at threshold ($\text{current\_stock} == \text{minimum\_stock}$) are marked adequately stocked ($\text{reorder\_quantity} = 0$).
  - Zero Stock: If $\text{current\_stock} == 0$, $\text{reorder\_quantity} = \text{minimum\_stock}$. Otherwise, $\text{reorder\_quantity} = \text{minimum\_stock} - \text{current\_stock}$.

### 2. WF002 — Product Price Validation
- **Workbook Name**: Product Price Validation
- **Trigger**: *"Find products where vendor price differs by more than 10%."*
- **Steps**: Load product prices $\to$ match products by SKU $\to$ compare internal and vendor prices $\to$ calculate percentage difference $\to$ flag exceptions.
- **Key Business Rules**:
  - Matches records using SKU case-insensitively.
  - Computes percentage difference: $\frac{|\text{internal\_price} - \text{vendor\_price}|}{\text{internal\_price}} \times 100\%$.
  - **Fixed 10.0% Threshold Policy & Exact Arithmetic**: Evaluates the decision rule using exact `Decimal` arithmetic: flagged as an exception strictly when $|\text{vendor\_price} - \text{internal\_price}| > (\text{internal\_price} \times 10 / 100)$. A difference of exactly $10.0\%$ (such as \$3.30 vs \$3.63 or \$100.00 vs \$110.00) is marked compliant.
  - **Strict Dataset Integrity (Abort on Error)**: Unlike WF003 (which filters invalid rows and produces a cleaned dataset), WF002 enforces strict dataset integrity. Malformed CSV rows (e.g. unquoted commas like `$1,200`), missing SKUs, non-finite/negative prices, duplicate SKUs, currency mismatches, or missing/blank currency values cause the workflow to abort immediately with actionable diagnostics and line numbers.
  - **Unmatched Tracking**: Unmatched vendor SKUs and unmatched internal SKUs are tracked with explicit reasons and displayed alongside matched validation results in CLI and execution reports.

### 3. WF003 — Vendor File Processing
- **Workbook Name**: Vendor File Processing
- **Trigger**: *"Process this vendor spreadsheet and show invalid rows."*
- **Steps**: Read file $\to$ detect columns $\to$ normalize column names $\to$ validate required fields $\to$ identify invalid rows $\to$ produce cleaned dataset.
- **Key Business Rules**:
  - Dynamically detects and normalizes synonym headers (e.g., `Item_SKU`, `Product_ID` $\to$ `sku`; `Unit_Price`, `Cost` $\to$ `price`).
  - Flags rows missing required fields (`sku`, `product_name`, `price`) or carrying malformed numbers.
  - **Non-destructive safety**: Produces a cleaned dataset and detailed error diagnostics; **never mutates or overwrites the input file**.

### 4. WF004 — Product Description Generator
- **Workbook Name**: Product Description Generator
- **Trigger**: *"Generate SEO content for this product."*
- **Steps**: Validate required attributes $\to$ create product description $\to$ generate short description $\to$ generate SEO title $\to$ generate meta description.
- **Key Business Rules**:
  - Requires `product_name`; raises an explicit validation error if missing.
  - **Zero Attribute Hallucination**: Generates copy strictly grounded in supplied attributes (`material`, `color`, `category`, `target_audience`). Unprovided optional attributes are omitted and explicitly marked as missing.
  - Badged with `is_simulated: True`.

### 5. WF005 — Customer Order Status
- **Workbook Name**: Customer Order Status
- **Trigger**: *"What is the status of order ORD-1001?"* / *"Where is my order?"*
- **Steps**: Validate identifier $\to$ search order data $\to$ retrieve order status $\to$ retrieve shipment information $\to$ summarize current status.
- **Key Business Rules**:
  - Validates order ID or customer email.
  - Joins matching order records with shipping carrier telemetry (carrier, tracking number, estimated delivery date).
  - Unknown Orders: If no order matches, prompts the user to provide an alternative identifier rather than failing silently.
  - Redacts sensitive PII and queries local simulated files without contacting live third-party carriers.

### 6. WF006 — Duplicate Product Detection
- **Workbook Name**: Duplicate Product Detection
- **Trigger**: *"Find duplicate products in catalog."*
- **Steps**: Load products $\to$ normalize names/SKUs $\to$ compare identifiers $\to$ compare product attributes $\to$ group likely duplicates $\to$ assign confidence.
- **Key Business Rules**:
  - Exact normalized SKU match $\to$ `DEFINITE` duplicate ($1.0$ confidence).
  - High attribute token overlap (Token Dice score $\ge 0.75$ with matching brand) $\to$ `LIKELY` duplicate.
  - Moderate attribute overlap ($0.65 \le \text{Dice} < 0.75$) $\to$ `POSSIBLE` duplicate (manual review recommended).
  - Completely distinct products are not grouped together.

### 7. WF007 — Marketing Campaign Brief
- **Workbook Name**: Marketing Campaign Brief
- **Trigger**: *"Generate marketing campaign brief."*
- **Steps**: Validate inputs $\to$ identify campaign objective $\to$ summarize products $\to$ create messaging $\to$ create channel recommendations $\to$ create campaign checklist.
- **Key Business Rules**:
  - Requires `campaign_goal` and `dates`; raises an error if either is omitted.
  - **No Fabricated Claims**: Never invents unverified discounts or promotional claims unless explicitly provided by the user.
  - Produces structured deliverables: core objective, audience messaging, recommended channels, and launch checklist.

### 8. WF008 — SEO Keyword Classification
- **Workbook Name**: SEO Keyword Classification
- **Trigger**: *"Classify these keywords and map them to pages."*
- **Steps**: Read keywords $\to$ remove duplicates $\to$ classify search intent $\to$ map keywords to categories $\to$ identify high-priority keywords $\to$ export results.
- **Key Business Rules**:
  - Deduplicates keywords case-insensitively while preserving maximum search volume.
  - Classifies intent into four deterministic categories: `informational`, `commercial`, `transactional`, or `navigational`.
  - Maps keywords to product categories and target URL slugs.
  - Assigns `HIGH`, `MEDIUM`, or `LOW` priority based on conversion intent, volume, and CPC.

### 9. WF009 — Employee Task Assignment
- **Workbook Name**: Employee Task Assignment
- **Trigger**: *"Assign this urgent task to the best available developer."*
- **Steps**: Understand task requirements $\to$ compare employee skills $\to$ check current workload $\to$ rank candidates $\to$ select employee $\to$ generate assignment summary.
- **Key Business Rules**:
  - Extracts required skills, priority, and deadline from task descriptions.
  - Evaluates matching skills against candidate employee profiles.
  - Evaluates bandwidth based on logged hours and weekly maximum capacity.
  - Computes composite suitability score: $0.5 \times \text{skill\_match} + 0.5 \times \text{capacity\_ratio}$.
  - **Escalation Trigger**: Triggers an explicit escalation alert (`escalation_required: True`, `assigned_employee: None`) if no employee has matching skills or all qualified candidates are at 100% capacity.

### 10. WF010 — Workflow Performance Report
- **Workbook Name**: Workflow Performance Report
- **Trigger**: *"Which workflows are failing most often?"*
- **Steps**: Load execution logs $\to$ calculate success/failure rate $\to$ calculate average execution time $\to$ identify frequent errors $\to$ identify slow steps $\to$ generate recommendations.
- **Key Business Rules**:
  - Analyzes execution logs to compute total runs, success rates, failure rates, and average runtimes.
  - Strictly flags workflows with failure rate exceeding $10.0\%$ (e.g., WF003 at $25.0\%$).
  - Flags workflows with average latency exceeding the configured threshold (default $5.0\text{s}$, e.g., WF003 at $6.15\text{s}$).
  - Groups and ranks top recurring error messages and isolates bottleneck steps exceeding $4.0\text{s}$.
  - Produces actionable, prioritized improvement recommendations.

---

## Setup & Installation

### Prerequisites
- **Python 3.12+**
- `git`

### 1. Clone the Repository
```bash
git clone https://github.com/harshrew-bit/ai-workflow-agent.git
cd ai-workflow-agent
```

### 2. Create and Activate a Virtual Environment

**On macOS / Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

**On Windows:**
```powershell
python -m venv .venv
.venv\Scripts\activate
```

### 3. Install the Project in Editable Mode
Install the package in editable mode with development dependencies using the project's `pyproject.toml` configuration:

```bash
python -m pip install -e ".[dev]"
```

This installs:
- `openpyxl>=3.1.5` (Excel workbook parsing)
- `pydantic>=2.0.0` (data modeling & validation)
- `python-dotenv>=1.0.0` (automatic `.env` loading)
- `certifi>=2024.2.2` (secure SSL certificate store for HTTPS)
- `pytest>=8.0.0` (automated testing suite)

---

## LLM Provider Configuration

The router supports **Google Gemini**, **OpenAI-compatible APIs**, and a hermetic **Fake / Fallback provider**. Configuration is loaded from environment variables via `python-dotenv`.

Copy the example template to create your `.env` file:
```bash
cp .env.example .env
```

### Option A: Google Gemini (Recommended)

Set the following in `.env` or export in your shell:
```env
LLM_PROVIDER=gemini
GEMINI_API_KEY=your_actual_gemini_api_key_here
GEMINI_MODEL=gemini-2.5-flash-lite
```

*Implementation detail*: `GeminiProvider` sends the API key in the `x-goog-api-key` HTTP header rather than query parameters, preventing credentials from appearing in URL logs or tracebacks. It uses `certifi.where()` to establish secure SSL connections without requiring the external Google GenAI SDK.

### Option B: OpenAI or OpenAI-Compatible Endpoints

```env
LLM_PROVIDER=openai
OPENAI_API_KEY=your_actual_openai_api_key_here
OPENAI_MODEL=gpt-4o-mini
# Optional custom base URL (defaults to https://api.openai.com/v1):
# OPENAI_BASE_URL=https://api.openai.com/v1
```

### Option C: Offline Testing & Fallback (Default)

When neither `GEMINI_API_KEY` nor `OPENAI_API_KEY` is configured in the environment, the system automatically defaults to a safe **unconfigured fallback provider**:
- It **never** crashes or attempts unauthorized network requests.
- It **never** pretends an LLM made a decision.
- It returns `workflow_id = None`, `confidence = 0.0`, and `requires_clarification = True`, explicitly reporting that automated live routing is inactive.

---

## CLI Usage

The command-line interface is accessed via `python -m app.main`. View all options with:
```bash
python -m app.main --help
```

### 1. Offline Natural Language Routing (Default)

When no live API keys (`GEMINI_API_KEY` or `OPENAI_API_KEY`) are set, the system automatically uses the **deterministic offline router**:

```bash
# Workflow queries route automatically based on explainable token overlap:
python -m app.main "Which products need restocking?"
python -m app.main "Where is order ORD-1001?"
python -m app.main "Find products where vendor price differs by more than 10%."

# Off-topic requests are rejected safely:
python -m app.main "What is the weather in Paris?"
# Result: Status: NEEDS_CLARIFICATION — No tools executed (exit code 4).
```

### 2. Live LLM Routing

When configured with an active Gemini or OpenAI API key, queries are routed through the live model:

```bash
# Example with Gemini configured in environment:
python -m app.main "Which products need restocking?"

# Example with explicit arguments:
python -m app.main --order-id "ORD-1001" "Where is my order?"
```

### 3. Deterministic Demonstration Mode (`--mock-route`)

To evaluate workflow tool execution, boundary conditions, and reports deterministically without calling live external LLM APIs, pass `--mock-route <WORKFLOW_ID>`.

> [!NOTE]
> `--mock-route WFxxx` forces deterministic workflow selection for testing and demonstration. It displays `Routing Mode: FORCED (--mock-route; this is not a routing decision)`.
> If the query matches another workflow significantly better than the forced workflow, a visible advisory warning is printed (e.g., `[WARNING] Forced route selected WF003, but request appears to match WF001`).

```bash
# WF001: Inventory Restock Check
python -m app.main --mock-route WF001 "Which products need restocking?"

# WF002: Product Price Validation
python -m app.main --mock-route WF002 "Find products where vendor price differs by more than 10%."

# WF003: Vendor File Processing
# Writes cleaned_<stem>.csv and invalid_rows_<stem>.csv to <repo>/outputs/ (or --output-dir)
python -m app.main --mock-route WF003 "Process this vendor spreadsheet and show invalid rows."

# WF004: Product Description Generator
# Without a product name the workflow requires clarification (exit 4); inputs are never invented
python -m app.main --mock-route WF004 "Generate SEO content for this product."
python -m app.main --mock-route WF004 --product-name "Ergonomic Desk Chair" --color "Black" --material "Mesh" "Generate copy"

# WF005: Customer Order Status (known order)
python -m app.main --mock-route WF005 --order-id "ORD-1001" "What is the status of order ORD-1001?"

# WF005: Customer Order Status (unknown order -> needs_clarification, exit 4)
python -m app.main --mock-route WF005 --order-id "ORD-9999" "Check order status"

# WF006: Duplicate Product Detection
python -m app.main --mock-route WF006 "Find duplicate products in catalog"

# WF007: Marketing Campaign Brief
python -m app.main --mock-route WF007 --campaign-goal "Launch Eco Line" --dates "Nov 1 - Nov 30" "Create campaign brief"

# WF008: SEO Keyword Classification
python -m app.main --mock-route WF008 "Classify these keywords and map them to pages."

# WF009: Employee Task Assignment
# Missing task skills request clarification (exit 4); no skill is invented
python -m app.main --mock-route WF009 "Assign this urgent task to the best available developer."
python -m app.main --mock-route WF009 --task-desc "Develop GraphQL service" --skills "graphql, python" --task-priority "Urgent" "Assign task"

# WF010: Workflow Performance Report
python -m app.main --mock-route WF010 "Which workflows are failing most often?"

# WF011: Supplier Delivery Risk Assessment (Demonstration Extension)
python -m app.main --mock-route WF011 "Assess supplier delivery risk"
```

### 4. Structured JSON Output

Append `--json` to any CLI command to output the full machine-readable `ExecutionReport`:

```bash
python -m app.main --mock-route WF001 --json "Which products need restocking?"
```

---

## Routing, Confidence & Clarification Policy

`LLMWorkflowRouter` and `OfflineWorkflowRouter` apply the following validation policy to all decisions:

1. **Confidence Semantics**:
   The `confidence` score in `RoutingDecision` represents the **model-reported routing certainty score** (0.0 to 1.0) returned by the LLM (or normalized token score in offline mode), **not a mathematically calibrated probability**. The system compares this score directly against `confidence_threshold` (default `0.70`).
2. **Registry Verification (Zero Hallucination Tolerance)**:
   The selected `workflow_id` must match a workflow currently registered in the catalog. If the model returns an unregistered or invented ID (e.g., `WF999`), the decision is rejected, `workflow_id` is set to `None`, `confidence` is reset to `0.0`, and `requires_clarification` is set to `True`.
3. **Threshold Enforcement**:
   Matches scoring below `confidence_threshold` are flagged with `requires_clarification = True`, preventing execution on weak guesses.
4. **Ambiguous or Unrelated Requests**:
   If the user query does not match any registered workflow trigger or lacks critical parameters, the router returns `workflow_id = None` and `requires_clarification = True`.
5. **Sanitized Provider Error Handling**:
   Network errors, timeouts, or HTTP errors are sanitized to prevent secret leakage. Raw HTTP response bodies, request URLs containing credentials, and authorization headers are never exposed in exceptions or user-facing reasoning.
6. **Automatic Offline Router Fallback**:
   When no live LLM credentials are configured (`GEMINI_API_KEY` and `OPENAI_API_KEY` are unset), the orchestrator automatically delegates natural-language routing to `OfflineWorkflowRouter` (`app/agent/offline_router.py`), reporting `Routing Mode: OFFLINE`.

---

## Deterministic Offline Router & Scoring

When running without live API credentials, natural language queries are routed through `OfflineWorkflowRouter` (`app/agent/offline_router.py`).

### How Scoring Works
1. **Source of Truth**: Queries are scored against the active `WorkflowRegistry` loaded directly from `data/workflows.xlsx`.
2. **Explainable Tokenization**:
   - Lowercases query text and strips punctuation.
   - Filters common English stopwords and conversational fillers (`check`, `please`, `help`, `show`, `user`, etc.).
   - Normalizes morphological inflections: plurals (`-ies`, `-es`, `-s`), gerunds (`-ing`), and past tense (`-ed`).
   - Maps domain synonyms to normalized concepts (`stock` → `inventory`, `supplier` → `vendor`, `developer` → `employee`, `failures` → `fail`, etc.).
3. **Field Weighting**:
   - `workflow.trigger`: Weight **3.5** (primary trigger intent)
   - `workflow.workflow_name`: Weight **2.5** (domain name)
   - `workflow.parsed_steps`: Weight **1.5** (step actions and entities)
   - `workflow.tools_required`: Weight **1.0** (tool identifiers)
4. **Confidence & Decision Rules**:
   - A workflow is selected if its score meets or exceeds the threshold (**3.0**) and strictly exceeds the second-highest candidate.
   - Ambiguous queries, score ties, low-scoring queries, or off-topic queries (e.g., *"What is the weather in Paris?"*) return `status: needs_clarification` (exit code 4) and execute zero domain tools.
   - The execution report reasoning details the matched terms (e.g., `matched terms [identify, inventory, product, restock]`).

### Limitations
- **Vocabulary Coverage**: Token matching relies on word roots and synonym dictionaries; queries phrased with entirely disjoint vocabulary or figurative expressions cannot be mapped.
- **Complex Semantic Reasoning**: The offline router does not perform contextual reasoning, multi-turn dialogue, or creative extraction beyond regex patterns. Live LLM routing is recommended for open-ended interactions.

---

## Tool Execution, Data Safety & Simulation Transparency

The execution engine and tool registry enforce strict operational safety:

- **Genuine Tool Invocation**: `GenericWorkflowEngine` never marks a step `COMPLETED` without invoking the actual registered `BaseTool.execute()` method.
- **Cascading Context**: Results from earlier steps are recorded in `ExecutionContext` (`last_output`, `step_1_output`, etc.) and automatically mapped to downstream step inputs.
- **Non-Destructive File Ingestion**: Ingestion workflows (such as WF003 vendor processing) validate data in memory and write cleaned views; they **never overwrite or mutate input files**.
- **Simulated Offline Operations**:
  - Sample inventory, order, shipping, employee, and supplier records are purely local synthetic data.
  - No real-world shipping carriers (FedEx, UPS), ERPs (SAP), or HR tools (Jira, Workday) are called.
  - Outputs and reports from simulated domain workflows carry explicit `is_simulated: True` metadata.

---

## Exit Codes

The process exit code reflects the report status (the contract is covered by `tests/test_phase2_fixes.py`).

| Code | Meaning |
|---|---|
| `0` | `success` |
| `1` | `failed` (a step raised an error, or required inputs were missing and the workflow does not define a clarification rule) |
| `2` | usage error (missing request, unknown flag; reported by argparse) |
| `3` | `partial_failure` (some steps completed before a failure) |
| `4` | `needs_clarification` (the user must supply missing information; `clarification_required` is `true`) |

`--json` always prints valid JSON to stdout, and the exit code still applies.

## Missing Input & Clarification Behavior

Missing required inputs are handled consistently. When the user must supply information, the report has `status: needs_clarification`, `clarification_required: true`, a user-facing message in `errors`, and the CLI exits with code 4. Nothing is executed past the failing input, and no value is invented.

- **WF004 (Product Description Generator):** a missing required `product_name` returns `needs_clarification`.
- **WF005 (Customer Order Status):** if no order matches the identifier, the workflow asks for another Order ID or email (`needs_clarification`).
- **WF007 (Marketing Campaign Brief):** a missing campaign goal or dates returns `needs_clarification`, and no brief is generated.
- **WF009 (Employee Task Assignment):** a missing task description, or missing required skills, returns `needs_clarification`. A default skill is never substituted.
- **Other workflows:** errors such as an unreadable file fail with a clear message (`failed`, exit 1). The workbook defines no clarification rule for them.
- Mock mode never invents inputs.

## Mock Routing (`--mock-route`)

- `--mock-route WFxxx` skips live LLM routing and always selects `WFxxx`. A request that does not fit that workflow is still executed, so use it for deterministic tests and demos, not as evidence of routing quality.
- Mock mode does not extract inputs from the request text, with one exception: for WF005 it extracts `ORD-<digits>` and an email address. Other inputs must be passed as flags, for example `--product-name`, `--campaign-goal`, `--dates`, `--vendor-file`.
- An unregistered ID such as `WF099` is rejected by router validation and returns `needs_clarification` (exit 4).
- There is no default request. Running `python -m app.main` without a request prints a usage error (exit 2).

## Input Validation

- **Price CSVs (WF002):** a header row is required. Every row must have exactly as many cells as the header, so an unquoted thousands separator such as `$1,200` is rejected with a line number. Values with thousands separators must be quoted. Prices must be finite and strictly positive, and `NaN`, `Infinity`, zero, and negative values are rejected. SKUs must be unique, compared case-insensitively. A currency mismatch between the two files is rejected, and a blank currency is rejected when a currency column exists. Currency codes are compared case-insensitively.
- **Vendor files (WF003):** column names are normalized through synonyms. Rows missing a SKU or product name are invalid, as are malformed or negative prices.
- **LLM routing:** a non-finite confidence (`NaN`, `Infinity`) fails closed to `needs_clarification`. Confidence below 0.70 also requires clarification. Routed workflow IDs must exist in the registry.
- **WF009 employees:** an employee is viable only if they hold every required skill and have available hours. Escalation is raised when no viable employee exists.

## Security Restrictions

- **LLM-supplied file paths are ignored.** Values extracted by the router whose keys contain `path`, `file`, or `csv` are dropped before tool execution, and the report notes what was ignored. File paths come only from explicit CLI flags or configured defaults, so a model response cannot make a tool read an arbitrary local file.
- **Secrets:** API keys are read from the environment, sent in headers rather than URLs, and never printed. Provider errors are sanitized. `.env` is gitignored, and `.env.example` contains placeholders only.
- **Source files are never modified.** WF003 writes new files only, and a guard refuses any output path that resolves to the source file.
- **Spreadsheet formula injection:** WF003 CSV output prefixes any cell beginning with `=`, `+`, `-`, or `@` with an apostrophe, so spreadsheet applications treat it as text.

## WF003 Output Files

WF003 writes three files to `<repo>/outputs/` by default. Use `--output-dir` to change the location. The input file is never modified. Existing files with the same names are replaced.

- `cleaned_<stem>.csv`: valid records, columns `sku, product_name, price, category, stock`.
- `invalid_rows_<stem>.csv`: rejected rows, columns `row_number, sku, product_name, price, category, stock, errors`. `row_number` is the 1-based data-row index, not the file line number.
- `validation_summary_<stem>.json`: a JSON object with `source_file` (the input file name), `processed_rows`, `valid_rows`, `invalid_rows` (processed equals valid plus invalid), and `output_files` (the names of the three files).
- `<stem>` is the input file name without its extension. For `sample_vendor_catalog.csv` the names are `cleaned_sample_vendor_catalog.csv`, `invalid_rows_sample_vendor_catalog.csv`, and `validation_summary_sample_vendor_catalog.json`.
- Both CSV files neutralise spreadsheet formula injection: a cell beginning with `=`, `+`, `-`, or `@` is prefixed with an apostrophe.
- The filenames and formats are a project decision. The workbook names a cleaned file, an invalid-row report, and a validation summary, but specifies no names or formats.
- An empty input with only a header produces empty outputs with headers. A zero-byte input fails and writes nothing.

## WF009 Ranking and Assignment

- Only employees who possess every required skill are assigned. A partially qualified employee is never assigned, regardless of capacity or priority.
- Qualified employees are ranked by available capacity, highest first. The selected employee is the top-ranked qualified employee with available hours.
- If no qualified employee has available capacity, the workflow escalates (`escalation_required: true`, status `success`). If no employee holds every required skill, it escalates with a reason that says so.
- The composite score is shown for reference only and does not drive ranking.

## Demonstration Extension: WF011 Supplier Delivery Risk Assessment

To prove that the architecture supports additional workflows without modifying core engine abstractions, the repository includes a demonstration extension: **WF011 — Supplier Delivery Risk Assessment**.

> [!IMPORTANT]
> **WF011 is a demonstration extension**, created in Python to prove architectural extensibility. It is **not** part of the official assessment workbook (`data/workflows.xlsx`), which remains strictly preserved with its original SHA-256 checksum.

### Business Logic & Deterministic Thresholds

1. **Delay Calculation**: For each delivery, computes $\text{delay\_days} = \text{actual\_date} - \text{promised\_date}$. Shipments with $\text{delay\_days} > 0$ are flagged as late.
2. **Per-Supplier Metrics**: Calculates total shipments, late shipments, late delivery rate ($\frac{\text{late}}{\text{total}}$), and average delay in days for late deliveries.
3. **Deterministic Risk Score (0 to 100)**:
   $$\text{risk\_score} = \min\left(100.0, \, (\text{late\_delivery\_rate} \times 60.0) + \min(\text{average\_delay\_days} \times 8.0, \, 40.0)\right)$$
4. **Risk Categorization**:
   - **HIGH RISK**: $\text{risk\_score} \ge 50.0$ OR $\text{late\_delivery\_rate} \ge 0.35$ OR $\text{average\_delay\_days} \ge 7.0$. Action: Formal vendor review, source backup suppliers.
   - **MEDIUM RISK**: $\text{risk\_score} \ge 25.0$ OR $\text{late\_delivery\_rate} \ge 0.15$ OR $\text{average\_delay\_days} \ge 3.0$. Action: Monitor lead times weekly.
   - **LOW RISK**: Otherwise. Action: Maintain preferred status.

### Verification Command
```bash
python -m app.main --mock-route WF011 "Assess supplier delivery risk"
```

---

## How to Extend the System with New Workflows

The system demonstrates zero-engine-modification extensibility. Adding an additional workflow requires **no modifications to core execution engine code**:

### What Remains Unchanged
- **`app/engine/base.py` (`GenericWorkflowEngine`)**: **0 lines changed**. It executes any workflow purely from step names and registered tool bindings.
- **`app/orchestrator.py` (`WorkflowOrchestrator`)**: **0 lines changed**.
- **`app/agent/router.py` (`LLMWorkflowRouter`)**: **0 lines changed**.
- **`data/workflows.xlsx`**: Preserved unchanged.

### The 6-Step Extension Checklist (Verified by WF011)

Adding a new workflow requires following these 6 extension points without altering core execution engine abstractions:

1. **Workflow Definition**: Define the workflow schema either by adding a row to an Excel catalog or instantiating a `WorkflowDefinition` model (e.g., `WF011` in `app/registry.py`).
2. **Domain Tools**: Implement tool classes inheriting from `BaseTool` with typed metadata and execute logic in `app/tools/<domain>.py`.
3. **Tool Registry**: Register the domain tools in `ToolRegistry` via `create_default_tool_registry()` in `app/registry.py`.
4. **Step Resolver**: Bind each human-readable workflow step to its registered tool name in `ConfigurableStepResolver` via `create_default_step_resolver()` in `app/registry.py`.
5. **CLI Options**: Expose any domain-specific CLI arguments in `app/main.py` if arguments are exposed to users.
6. **Automated Tests**: Add end-to-end and unit regression tests covering normal execution, boundaries, and errors in `tests/test_<domain>.py`.

```python
# Example: Registering tools and bindings in app/registry.py
from app.tools.base import BaseTool, ToolMetadata

class InvoiceLoaderTool(BaseTool):
    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(name="invoice_loader", description="Loads invoice records")

    def execute(self, **kwargs):
        return {"invoices_loaded": 10}

# 1. Register tool in ToolRegistry
tool_registry.register(InvoiceLoaderTool())

# 2. Bind human-readable step in ConfigurableStepResolver
step_resolver.bind(
    workflow_id="WF012",
    step_name="Load invoice",
    tool_name="invoice_loader",
)

# 3. Register workflow definition in WorkflowRegistry
workflow_registry.register(wf)
```

---

## Testing & Verification

Run the automated test suite with `pytest -q` to view the current passing test count and verify complete pass status:

### Run All Tests
```bash
pytest -v
```

### Run Quick Summary
```bash
pytest -q
```

### Run Tests by Feature Area
```bash
# Core models, loader, registry, interfaces
pytest tests/test_models.py tests/test_loader.py tests/test_registry.py tests/test_engine_interfaces.py

# Router and execution engine
pytest tests/test_router.py tests/test_execution.py tests/test_orchestrator.py

# Official workflows (WF001 – WF010)
pytest tests/test_wf001_inventory.py
pytest tests/test_wf002_pricing.py
pytest tests/test_wf003_vendor_processing.py
pytest tests/test_wf004_content_generation.py
pytest tests/test_wf005_order_status.py
pytest tests/test_wf006_duplicate_detection.py
pytest tests/test_wf007_campaign_brief.py
pytest tests/test_wf008_seo_keywords.py
pytest tests/test_wf009_task_assignment.py
pytest tests/test_wf010_performance_report.py

# End-to-end multi-workflow integration suites
pytest tests/test_orchestrator_wf002_wf004.py
pytest tests/test_orchestrator_wf005_wf007.py
pytest tests/test_orchestrator_wf008_wf010.py

# Extensibility demonstration (WF011)
pytest tests/test_wf011_extensibility.py
```

### Check Code Formatting and Whitespace
```bash
git diff --check
```
### Run the Offline Benchmark Suite

Run the 22 benchmark requests and verify their expected workflow IDs, statuses, exit codes, and offline routing mode:

```bash
bash scripts/run_examples.sh
```

The script writes text and JSON reports to `examples/output/`. These benchmark results verify deterministic offline routing and execution contracts; they do not measure live LLM routing quality or prove that every workflow has been tested against a live API.

### Live API Verification

Configure your credentials as described in [LLM Provider Configuration](#llm-provider-configuration), then run a representative live request:

```bash
python -m app.main \
  "Find products where vendor price differs by more than 10%." \
  --internal-csv data/sample_internal_prices.csv \
  --vendor-csv data/sample_vendor_prices.csv
```

A successful run should select `WF002 (Product Price Validation)` and report the price-validation results. Live API availability can vary, so use the output of the actual run when reporting its status.

---

## Sample Datasets

All sample datasets reside in `data/` and represent realistic, synthetic test fixtures:

| File | Associated Workflow | Purpose & Key Characteristics |
|---|---|---|
| `workflows.xlsx` | All (WF001–WF010) | Official assessment workbook defining the 10 core business workflows. |
| `sample_inventory.csv` | WF001 | Products with varied stock counts, reorder thresholds, zero stock, and exact threshold items. |
| `sample_internal_prices.csv` | WF002 | Internal product price list with SKUs and baseline prices. |
| `sample_vendor_prices.csv` | WF002 | Vendor quotes with compliant prices, >10% discrepancies, and unmatched SKUs. |
| `sample_vendor_catalog.csv` | WF003 | Raw vendor catalog containing header variations (`Item_SKU`, `Unit_Price`) and malformed rows. |
| `sample_orders.csv` | WF005 | Customer orders with order IDs, order dates, line items, and totals. |
| `sample_shipments.csv` | WF005 | Shipping tracking numbers, carriers (FedEx, UPS), and delivery statuses linked to orders. |
| `sample_products_catalog.csv` | WF006 | Product catalog with exact SKU duplicates, near-duplicate models (Token Dice), and distinct items. |
| `sample_keywords.csv` | WF008 | SEO search queries with search volumes, CPC bids, competition scores, and intentional duplicates. |
| `sample_employees.csv` | WF009 | Employee profiles with technical skills, hourly availability, and current workloads. |
| `sample_workflow_logs.csv` | WF010 | 39 execution runs with realistic failure rates (>10% on WF003 & WF005) and latency bottlenecks (>5s on WF003). |
| `sample_supplier_deliveries.csv` | WF011 | 19 simulated deliveries across 4 suppliers with varying delivery punctuality and delays. |

---

## Limitations & Future Improvements

### Current Limitations
1. **Synchronous Step Execution**: `GenericWorkflowEngine` executes steps sequentially. Workflows with independent parallel steps execute linearly.
2. **Local In-Memory State**: State is preserved within an `ExecutionContext` during a single run. Intermediate step states are not persisted to an external database (e.g., PostgreSQL or Redis).
3. **Read-Only Workbook Storage**: In the current architecture, official workflow metadata is ingested from an Excel workbook at startup rather than queried from a dynamic relational database.
4. **Offline Domain Tools**: All business tools operate on local files and simulated data. Connecting to live production APIs (FedEx, Salesforce, Workday, SAP) would require enterprise authentication and rate-limiting infrastructure.

### Future Improvements
1. **Asynchronous & Parallel Execution**: Upgrade `GenericWorkflowEngine` to evaluate step dependency graphs (DAGs) and execute independent steps concurrently with `asyncio`.
2. **REST API Service Layer**: Expose the orchestrator through a FastAPI application in `app/api/` with streaming server-sent events (SSE) for step-by-step UI progress.
3. **Database-Backed Catalog**: Support database-backed workflow definitions (PostgreSQL / SQLite) alongside Excel workbooks for real-time CRUD management.
4. **Interactive Human-in-the-Loop Approval**: Allow tools (e.g., automated purchase orders or price adjustments) to pause execution and wait for human supervisor approval before proceeding.
