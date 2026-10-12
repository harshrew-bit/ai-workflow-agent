# AI Workflow Agent — Foundation Milestone

A modular, Excel-driven AI workflow automation system built with Python 3.12, Pydantic, and openpyxl.

This milestone establishes the foundational layer: dynamic loading, validation, and registration of business workflows directly from `data/workflows.xlsx`, with clean separation of concerns and an extensible architecture designed so that new workflows (e.g. WF011) can be registered without modifying the core router or execution engine.

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
- **`app/engine/`**: Generic execution interface:
  - `context.py`: `ExecutionContext` carrying workflow state, inputs, intermediate variables, and step history.
  - `base.py`: `WorkflowExecutor` abstract interface and `GenericWorkflowEngine` driving step-by-step execution generically.
- **`app/agent/`**: Reserved natural-language routing integration boundary:
  - `router.py`: `WorkflowRouter` abstract interface and `RoutingDecision` model designed to evaluate queries dynamically against registered workflows without if-else branching.
- **`app/tools/`**: Reusable tool abstractions and registry:
  - `base.py`: `BaseTool` abstract interface and `ToolMetadata`.
  - `registry.py`: `ToolRegistry` for registering and discovering tools dynamically.
- **`app/api/`**: Reserved API boundary for future REST / service endpoints.

---

## Extensibility Design

The system does **not** hardcode workflow IDs (WF001–WF010) into routing or engine logic:
- The registry accepts any valid `WorkflowDefinition` programmatically or via Excel.
- Workflows declare required tools as metadata strings; the engine evaluates steps dynamically.
- When an 11th workflow (such as WF011) is added in future milestones, it is registered directly into the `WorkflowRegistry`. The core execution engine and router evaluate it without code modifications.

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

---

## Running Tests

All automated tests use `pytest` and execute against both the assessment workbook `data/workflows.xlsx` (in read-only mode) and temporary fixtures for edge-case validation.

```bash
# Run the complete test suite
pytest

# Run tests with verbose output
pytest -v

# Run a specific test module
pytest tests/test_loader.py
pytest tests/test_registry.py
pytest tests/test_models.py
pytest tests/test_engine_interfaces.py
```

### Test Coverage Highlights

1. **Successful Loading of All 10 Workflows**: Confirms that WF001 through WF010 are parsed from `data/workflows.xlsx` with all fields preserved verbatim.
2. **Loading All 10 Evaluation Requests**: Confirms all rows from `Test_Questions` are loaded and validated.
3. **Duplicate Workflow ID Detection**: Asserts that duplicate IDs raise `DuplicateWorkflowIDError` with row and ID context.
4. **Missing Required Column Detection**: Validates that missing columns in either sheet raise `MissingColumnError`.
5. **Missing Workflow ID Detection**: Validates that rows with empty or missing IDs raise `WorkflowValidationError`.
6. **Missing or Unreadable Workbook**: Validates that non-existent paths raise `WorkbookNotFoundError` and corrupted files raise `InvalidWorkbookError`.
7. **Generic Registration Interface**: Demonstrates adding an arbitrary workflow definition (WF011) to the registry programmatically and retrieving it without altering engine or router code.
