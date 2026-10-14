# Repository-Wide Correctness Audit, Bug Fixes, and Verification Report

**Repository:** `https://github.com/harshrew-bit/ai-workflow-agent`  
**Date:** 2026-10-14  
**Auditor:** Senior Python Engineer, AI-Agent Architect, QA & Security Reviewer  
**Scope:** WF001–WF011, Live & Offline LLM Routers, Generic Execution Engine, Step Resolvers, Tool Registries, CLI, FastAPI Adapter, React Web Frontend.

---

## 1. Executive Summary

This audit was conducted following the discovery of a functional discrepancy in **WF002 (Product Price Validation)**: when requested to *"flag any product whose price difference is less than 5%"*, the agent selected WF002 but flagged products exceeding 10%, identical to the default behavior.

The audit confirmed the root cause in `app/tools/pricing.py` and traced its systemic impact end-to-end across router extraction, API schema validation, orchestrator argument merging, CLI formatting, and web UI display. In addition, related input-propagation and threshold-coercion defects were audited across all other workflows (WF001–WF011).

All confirmed defects were remediated with exact Decimal arithmetic, backward-compatible defaults, dynamic operator and status handling, and strict input validation. **16 new regression tests** were added, bringing the total passing test count to **305 Python tests** and **8 React/TypeScript tests** with **0 failures**.

---

## 2. End-to-End Architectural Execution Trace

The execution lifecycle of natural language requests in this architecture is structured as follows:

```
[User Request / Web Client / CLI]
           │
           ▼
[Router Selection (LLM or Offline)]
  ├── Matches intent against WorkflowDefinition catalog
  └── Extracts explicit identifiers & parameters (thresholds, operators, IDs, emails)
           │
           ▼
[WorkflowOrchestrator.run()]
  ├── Resolves workflow definition (WF001–WF011)
  ├── Drops prohibited file path keys from untrusted router output
  ├── Merges default_inputs + decision.extracted_inputs + runtime_inputs
  └── Hands off to GenericWorkflowEngine
           │
           ▼
[GenericWorkflowEngine.execute()]
  ├── Loops through workflow.parsed_steps
  ├── Resolves step name to tool binding via ConfigurableStepResolver
  ├── Prepares arguments via _prepare_tool_kwargs(tool, context.inputs + variables)
  └── Invokes tool.execute(**kwargs)
           │
           ▼
[Domain Tool Execution & Boundary Checks]
  ├── Exact Decimal evaluation against requested or default thresholds
  └── Emits structured result dictionary + human-readable step summary
           │
           ▼
[ExecutionReport & Result Presentation]
  ├── Aggregates step reports into ExecutionReport
  ├── FastAPI adapter returns structured JSON (api/main.py)
  ├── React frontend renders custom workflow cards (web/src/components/ResultViews.tsx)
  └── CLI formats tabular summaries for console (app/main.py)
```

### Trace of the Primary Bug (WF002 "< 5%")

1. **User input:** *"Compare the vendor and internal prices for each product, and flag any product whose price difference is less than 5%."*
2. **Prior Bug:**
   - `app/agent/offline_router.py`: `extract_inputs_from_query` only captured `order_id`, `customer_email`, and `file_path`. Threshold `5.0` and operator `<` were dropped.
   - `api/main.py`: `ALLOWED_INPUT_KEYS` lacked `threshold`, `price_threshold`, and `comparison_operator`. Any client passing them received HTTP 422.
   - `app/tools/pricing.py`: `PriceExceptionFlaggerTool.execute()` hardcoded `fixed_threshold = 10.0`, discarding any passed `threshold`.
   - `evaluate_price_comparison()` only supported `abs_diff > threshold_amount` (`>`), lacking `<`, `<=`, `>=`, `==`.
   - `app/main.py` & `ResultViews.tsx` hardcoded `EXCEPTION (>10%)` in tables and cards.
3. **Remediated Path:**
   - `extract_inputs_from_query` regex parses operator `<` and threshold `5.0`.
   - `api/main.py` allows `threshold`, `price_threshold`, `comparison_operator`, `operator` in `ALLOWED_INPUT_KEYS`.
   - `PriceExceptionFlaggerTool.execute()` resolves explicit threshold and comparison operator, validating that threshold is finite and non-negative.
   - `evaluate_price_comparison()` computes `threshold_amount = (internal_price * 5) / 100` in exact Decimal arithmetic, evaluating `abs_diff < threshold_amount`.
   - Result yields exactly **2 exceptions** (SKU-001 at 4.0% and SKU-005 at 3.33%) and **5 compliant items**.
   - `validation_status` dynamically reports `EXCEPTION_LESS_THAN_5_PERCENT`.
   - UI and CLI render `EXCEPTION (<5%)` dynamically while preserving `EXCEPTION (>10%)` for default runs.

---

## 3. Prioritized Audit Findings

| ID | Severity | Workflow / Module | Evidence | Reproduction | Root Cause | Fix | Regression Test |
|---|---|---|---|---|---|---|---|
| **D1** | **P1** | WF002 / `pricing.py` | Line 630 hardcoded `fixed_threshold = DEFAULT_PRICE_THRESHOLD_PERCENTAGE` (10.0). | Call `PriceExceptionFlaggerTool.execute(..., threshold=5.0)` on items with `< 5%` diff. | Explicit threshold parameter ignored to enforce static 10% policy. | Parameterize `PriceExceptionFlaggerTool` and `evaluate_price_comparison` with dynamic thresholds and operators (`>`, `<`, `>=`, `<=`, `==`). | `test_wf002_orchestrator_flags_strictly_less_than_5_percent` |
| **D2** | **P1** | Router / `offline_router.py` | `extract_inputs_from_query` omitted numeric threshold & operator extraction. | Query `"flag price difference less than 5%"` yielded empty inputs `{}`. | Regex only matched order IDs, emails, and `.csv` filenames. | Added regex extractors for comparison operators, percentages, latency, and inventory thresholds. | `test_offline_router_extracts_threshold_and_operator` |
| **D3** | **P2** | API / `api/main.py` | `ALLOWED_INPUT_KEYS` lacked `threshold`, `price_threshold`, `comparison_operator`, `operator`. | Client sending `{"inputs": {"threshold": 5.0}}` received HTTP 422. | Strict allowlist omitted pricing & stock override parameters. | Added `threshold`, `price_threshold`, `comparison_operator`, `operator`, `threshold_override`, `minimum_stock` to allowlist. | `test_api_run_accepts_explicit_inputs_threshold_and_operator` |
| **D4** | **P2** | WF001 / `inventory.py` | `StockThresholdComparatorTool` only accepted `threshold_override`, ignoring `threshold` or `minimum_stock`. | Passing `threshold=25` from orchestrator had no effect. | Parameter name mismatch with router-extracted and workbook names. | Supported `threshold_override`, `threshold`, `minimum_stock`, `minimum_threshold` aliases with integer validation. | `test_stock_comparator_tool_resolves_threshold_aliases` |
| **D5** | **P2** | WF010 / `performance_report.py` | String thresholds (`"10.0"`, `"5.0"`) crashed with `TypeError: '>' not supported between 'float' and 'str'`. | Call `RateCalculatorTool.execute(failure_threshold="10.0")`. | Missing float coercion on string inputs from query or API JSON. | Added safe float coercion and finite validation in `RateCalculatorTool` and `ExecutionTimeCalculatorTool`. | `test_performance_report_tools_accept_string_thresholds` |
| **D6** | **P3** | CLI / `app/main.py` | Hardcoded `EXCEPTION (>10%)` in price validation report table. | CLI output for `< 5%` exception displayed `EXCEPTION (>10%)`. | Formatter did not inspect dynamic `validation_status`. | Parse `validation_status` dynamically to render `EXCEPTION (<5%)`, `EXCEPTION (>10%)`, etc. | `test_audit_correctness_regression.py` |
| **D7** | **P3** | Web UI / `ResultViews.tsx` | Hardcoded `EXCEPTION (>10%)` in JSX badge. | Table badge displayed `>10%` even for custom threshold runs. | Static template string in JSX badge. | Parse `validation_status` to dynamically display operator and threshold in table badges. | `npm test` (`app.test.tsx`) |

---

## 4. Potential Risks & Unconfirmed Issues

1. **Live LLM Router Extraction Consistency:**
   - *Risk:* In live Gemini mode (when API key is configured), the LLM must extract JSON fields such as `"threshold"` and `"comparison_operator"`.
   - *Assessment:* The system prompt in `app/agent/prompts.py` explicitly instructs the LLM: *"Extract all explicit input values mentioned by the user that are relevant to the selected workflow (e.g., order ID, customer email, thresholds, percentages, filenames)."* Handled safely: if the LLM omits the operator or threshold, the system defaults to `>` and `10.0%`.
2. **Workbook Business Rule Invariance:**
   - *Risk:* Overriding the default threshold must not break existing workbook-defined baseline behaviors.
   - *Assessment:* Confirmed that omitting threshold/operator inputs retains the 100% strict 10.0% rule. All 289 existing baseline unit and integration tests pass without changes to business rule defaults.

---

## 5. Before and After Behavior

### Case A: Natural Language Request "< 5%"
- **Query:** `"Compare the vendor and internal prices for each product, and flag any product whose price difference is less than 5%."`
- **Before:**
  - Selected WF002.
  - Flagged **3 items** (SKU-002: 15%, SKU-004: 15%, SKU-006: 25%).
  - Flagged items were actually $> 10\%$, completely ignoring the user's $< 5\%$ condition!
  - Summary: `"Validated 7 products: 3 exception(s) exceeding 10.0% threshold."`
- **After:**
  - Selected WF002.
  - Flagged **2 items** (SKU-001: 4.0%, SKU-005: 3.33%).
  - Items $> 5\%$ (SKU-002, SKU-003, SKU-004, SKU-006, SKU-007) marked `COMPLIANT`.
  - Summary: `"Validated 7 products: 2 exception(s) less than 5% threshold."`
  - Validation status: `EXCEPTION_LESS_THAN_5_PERCENT`.
  - UI badge: `EXCEPTION (<5%)`.

### Case B: Default Price Comparison (No Threshold)
- **Query:** `"Compare the vendor and internal prices for each product."`
- **Before & After:**
  - Selected WF002.
  - Flags **3 items** (SKU-002: 15%, SKU-004: 15%, SKU-006: 25%).
  - Exact 10.0% boundary items (SKU-003, SKU-007) are `COMPLIANT`.
  - Summary: `"Validated 7 products: 3 exception(s) exceeding 10.0% threshold."`
  - Validation status: `EXCEPTION_EXCEEDS_10_PERCENT`.
  - UI badge: `EXCEPTION (>10%)`.
  - Backward compatibility: **100% preserved**.

---

## 6. Verification and Test Results

### Automated Test Execution
- **Python Unit & Integration Suite (`pytest`):**
  - **Baseline:** 289 passed in 6.88s.
  - **New Regression Suite:** 16 passed in 1.35s (`tests/test_audit_correctness_regression.py`).
  - **Final Count:** **305 passed**, 4 warnings in 5.17s.
  - **Pass Rate:** 100%.
- **Frontend Unit & Component Suite (`vitest` in `web/`):**
  - **Pass Count:** **8 passed** in 0.99s.
  - **Pass Rate:** 100%.
- **Frontend Production Build (`npm run build` in `web/`):**
  - **TypeScript compilation (`tsc`):** Clean, 0 errors.
  - **Vite bundling:** 1497 modules transformed, output in 4.96s (`dist/assets/index-BGve40Zx.js`).
- **Git Diff Verification (`git diff --check`):**
  - 0 trailing whitespace errors, 0 merge conflicts.

### Security and Safety Checklist
- [x] `.env` is completely untouched and was never committed.
- [x] No API keys or secrets were printed, logged, or serialized into responses.
- [x] `data/workflows.xlsx` was not modified.
- [x] Sample datasets (`data/*.csv`) were not modified.
- [x] No live LLM calls were executed during tests (deterministic offline router and fake providers used).
- [x] No git commits or pushes were executed.
