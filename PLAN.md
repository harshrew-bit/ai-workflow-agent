# Implementation Plan — Premium AI Workflow Automation Frontend & README Repair

## 1. Objectives
1. **Repair README.md Mathematical Rendering**: Fix broken LaTeX/MathJax formulas in the WF011 section ("Business Logic & Deterministic Thresholds") causing GitHub `'_' allowed only in math mode` errors, using valid display math `$$ ... $$` and clean markdown separation.
2. **Build FastAPI Backend Adapter (`api/main.py`)**: Thin, secure adapter invoking the existing Python `WorkflowOrchestrator` directly (no shelling out, no re-implementing engine). Expose `/api/health`, `/api/workflows`, `/api/examples`, `/api/run`, and `/api/static-runs`.
3. **Build Polished React Frontend (`web/`)**: Modern Vite + React + TypeScript + Tailwind CSS application with warm peach/blush design, royal blue to magenta gradients, dark charcoal trace panel, rich workflow renderers, and honest offline demo mode.
4. **Comprehensive Verification**: Preserve all 277 existing tests, add new backend and frontend test suites, verify API and UI locally, test backend shutdown demo mode, and maintain strict secret/business-logic constraints.

---

## 2. Intended Files & Changes

### A. Documentation
- `README.md`: Fix math formulas in lines 636–646. Replace inline LaTeX containing unescaped text-mode underscores with separate GitHub display-math `$$ ... $$` blocks.

### B. Backend Configuration & Implementation
- `pyproject.toml`: Add optional dependency group `web = ["fastapi>=0.110.0", "uvicorn>=0.29.0", "httpx>=0.27.0"]`.
- `api/__init__.py`: Package init.
- `api/main.py`:
  - `GET /api/health`: Safe status check (workflow count, workbook loaded, llm_configured, offline_router_available). Zero secret leakage.
  - `GET /api/workflows`: Catalog of registered workflows (WF001–WF010 from workbook + WF011 extension).
  - `GET /api/examples`: Benchmark examples from `examples/expected.json` and `examples/requests.md`.
  - `GET /api/static-runs`: Securely serve genuine pre-computed JSON outputs from `examples/output/`.
  - `POST /api/run`: Execute user request via `WorkflowOrchestrator`. Reject empty requests (422), reject path traversal or browser-supplied filesystem paths, resolve approved sample CSV fixtures server-side, map report statuses to documented CLI exit codes.
- `tests/test_api.py`: Pytest suite using FastAPI `TestClient` covering health, secret isolation, workflow listing, offline routing, forced routing, path-like key rejection, and error handling.

### C. Frontend Implementation (`web/`)
- `web/package.json`: Vite, React 18, TypeScript, Tailwind CSS, Lucide React, Vitest, React Testing Library.
- `web/vite.config.ts`, `web/tailwind.config.js`, `web/postcss.config.js`, `web/tsconfig.json`.
- `web/src/types/workflow.ts`: TypeScript interfaces for `WorkflowDefinition`, `ExecutionReport`, `StepReport`, `HealthResponse`.
- `web/src/data/staticRuns.ts`: Genuine pre-bundled static reports from `examples/output/` for zero-backend fallback.
- `web/src/api/client.ts`: API service with transparent fallback to static runs in demo mode.
- `web/src/components/Header.tsx`: Navigation, logo, real-time backend/routing status badge.
- `web/src/components/Hero.tsx`: Warm peach gradient, headline with blue-to-magenta gradient, request input, quick-try chips for WF001–WF010 + off-topic test.
- `web/src/components/ExecutionTrace.tsx`: Dark charcoal panel (`workflow_execution.trace`) with 3 cards:
  - `01 — ROUTING`: Workflow ID/name, mode badge (LLM, offline, forced), confidence, reasoning.
  - `02 — EXECUTION`: Timeline with step number, sentence-case step name, status icon, output summary.
  - `03 — RESULT`: Status label, structured result renderers (restock table, price validation table, vendor cleaning metrics, etc.), exit code, clarification alerts.
- `web/src/components/RawJsonViewer.tsx`: Collapsible JSON with copy-to-clipboard functionality.
- `web/src/pages/`:
  - `HomePage.tsx`: Hero, trace panel, quick chips, raw JSON.
  - `ArchitecturePage.tsx`: Interactive architecture flow (Request → Router → Selection → Orchestrator → Steps → Tools → Report) with source file links.
  - `WorkbookPage.tsx`: Data table/cards of the 10 Excel workflows + WF011 extension.
  - `DecisionsPage.tsx`: Engineering decisions (Decision, Why, Trade-off) covering Excel truth, offline routing, Decimal arithmetic, clarification vs hallucination, etc.
  - `ExtendingPage.tsx`: The verified 6-step checklist for adding new workflows (WF011 case study).
  - `StatusPage.tsx`: Honest verification dashboard separating verified capabilities from unverified features.
- `web/src/__tests__/`: Component tests for quick-try submission, trace rendering, clarification state, forced route warnings, and demo mode.

---

## 3. Verification Sequence
1. **README Verification**: Inspect diff and verify formula syntax.
2. **Install Web Dependencies**: `pip install -e ".[web]"`.
3. **Run Existing Tests**: Verify baseline of 277 tests passes.
4. **Run API Tests**: Verify new API test suite passes with 100% success.
5. **Frontend Build & Test**: `npm install`, `npm run build`, `npm test`.
6. **Live API Execution**: Start uvicorn on port 8000, verify curl health check, run recruiter request, verify path rejection and forced routing.
7. **Demo Mode Verification**: Stop uvicorn, reload frontend, verify amber DEMO MODE badge and inspection of saved examples.
8. **Git Hygiene**: Check `git diff --check`, `git status`, verify no `.env` or sensitive files created.
