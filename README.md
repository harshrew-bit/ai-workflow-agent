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
  - `inventory.py`: Production-grade domain tools for WF001 (`inventory_loader`, `stock_comparator`, `low_stock_identifier`, `reorder_calculator`, `restock_reporter`) with strict validation.
- **`app/orchestrator.py`**: `WorkflowOrchestrator` coordinating the full end-to-end pipeline:
  `Natural-language request → Router → Registry → Engine → Step Resolver → Domain Tools → ExecutionReport`.
- **`app/main.py`**: Command-line interface for natural-language workflow execution.
- **`app/api/`**: Reserved API boundary for future REST / service endpoints.

---

## End-to-End Workflow Execution (WF001)

The system features complete end-to-end orchestration for **WF001: Inventory Restock Check**:

```
Natural Language Request
         │
         ▼
 ┌──────────────────────┐
 │   LLM Router         │ (extracts parameters, matches WF001)
 └──────────┬───────────┘
            │
            ▼
 ┌──────────────────────┐
 │  Workflow Registry   │ (validates WF001 against data/workflows.xlsx)
 └──────────┬───────────┘
            │
            ▼
 ┌──────────────────────┐
 │   Generic Engine     │ (resolves step bindings & passes context)
 └──────────┬───────────┘
            │
            ▼
 ┌────────────────────────────────────────────────────────┐
 │   Domain Tools (Executed Sequentially)                 │
 │   1. inventory_loader     (parses & validates CSV)    │
 │   2. stock_comparator     (compares stock vs threshold)│
 │   3. low_stock_identifier (filters restock candidates) │
 │   4. reorder_calculator   (computes reorder qty/cost)  │
 │   5. restock_reporter     (formats structured report)  │
 └──────────┬─────────────────────────────────────────────┘
            │
            ▼
 ┌──────────────────────┐
 │   ExecutionReport    │ (structured summary with step metrics)
 └──────────────────────┘
```

### WF001 Business Rules & Edge Cases
- **Restock Condition**: Triggered strictly when `current_stock < minimum_stock`.
- **Boundary Condition**: If `current_stock == minimum_stock`, the item is marked as adequately stocked (`needs_reorder = False`, `reorder_quantity = 0`).
- **Zero Stock**: If `current_stock == 0`, `reorder_quantity = minimum_stock`.
- **Reorder Formula**: `reorder_quantity = minimum_stock - current_stock`. Estimated reorder cost is computed as `reorder_quantity * unit_cost`.
- **Validation**: Strict column verification, positive numeric coercion, and missing/empty file detection.

> [!NOTE]
> **Sample Dataset Notice**: `data/sample_inventory.csv` provides realistic sample inventory records across multiple suppliers and stock levels. Purchase orders and restock summaries are simulated internally; no live supplier APIs or external purchase orders are dispatched.
>
> **Workflow Implementation Status**: WF001 is fully implemented end-to-end with genuine domain tools. Workflows WF002–WF010 are registered and ready for routing in `data/workflows.xlsx`, with domain tools to be delivered in subsequent milestones.

---

## CLI Usage

The system includes a CLI interface (`app/main.py`) to run natural language queries end-to-end:

```bash
# Natural-language execution (uses configured LLM provider or prompts for clarification)
python3 -m app.main "Which products need restocking?"

# Explicit mock routing (hermetic, offline testing without API key)
python3 -m app.main --mock-route WF001 "Check inventory levels"

# Specifying a custom inventory CSV file
python3 -m app.main --mock-route WF001 --csv-path data/sample_inventory.csv "Restock report"

# Output as structured JSON
python3 -m app.main --mock-route WF001 --json "Restock check"
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
pytest tests/test_orchestrator.py
pytest tests/test_router.py
pytest tests/test_execution.py
pytest tests/test_loader.py
pytest tests/test_registry.py
pytest tests/test_models.py
pytest tests/test_engine_interfaces.py
```
