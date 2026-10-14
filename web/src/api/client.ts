import { ExecutionReport, HealthResponse, WorkflowDefinition, ExampleItem } from '../types/workflow';
import { STATIC_RUNS } from '../data/staticRuns';
import { DEFAULT_WORKFLOWS } from '../data/defaultWorkflows';

const API_BASE = 'http://127.0.0.1:8000';

export async function checkBackendHealth(): Promise<HealthResponse | null> {
  try {
    const res = await fetch(`${API_BASE}/api/health`, {
      method: 'GET',
      headers: { 'Accept': 'application/json' },
    });
    if (!res.ok) return null;
    return await res.json();
  } catch (err) {
    return null;
  }
}

export async function fetchWorkflows(): Promise<WorkflowDefinition[]> {
  try {
    const res = await fetch(`${API_BASE}/api/workflows`, {
      method: 'GET',
      headers: { 'Accept': 'application/json' },
    });
    if (res.ok) {
      return await res.json();
    }
  } catch (err) {
    // Graceful fallback to embedded workbook data
  }
  return DEFAULT_WORKFLOWS;
}

export async function fetchExamples(): Promise<ExampleItem[]> {
  try {
    const res = await fetch(`${API_BASE}/api/examples`, {
      method: 'GET',
      headers: { 'Accept': 'application/json' },
    });
    if (res.ok) {
      return await res.json();
    }
  } catch (err) {
    // Fallback based on static runs
  }
  return Object.entries(STATIC_RUNS).map(([slug, report]) => ({
    slug,
    request: report.request,
    expected_workflow_id: report.selected_workflow_id,
    expected_status: report.status,
    expected_exit_code: report.status === 'success' ? 0 : 4,
    category: slug.includes('paraphrase') ? 'paraphrase' : slug.includes('unrelated') ? 'unrelated' : 'workbook',
  }));
}

export function getSavedExample(slug: string): ExecutionReport | null {
  return STATIC_RUNS[slug] || null;
}

export async function executeWorkflow(
  requestText: string,
  forcedWorkflowId?: string,
  inputs?: Record<string, any>,
  useLiveLlm: boolean = false
): Promise<{ report: ExecutionReport; isDemoFallback: boolean }> {
  try {
    const res = await fetch(`${API_BASE}/api/run`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      body: JSON.stringify({
        request: requestText,
        forced_workflow_id: forcedWorkflowId || null,
        inputs: inputs || null,
        use_live_llm: useLiveLlm,
      }),
    });

    if (res.ok) {
      const data = await res.json();
      return { report: data, isDemoFallback: false };
    }

    if (res.status === 422) {
      const errData = await res.json();
      throw new Error(errData.detail || 'Validation error');
    }

    const errorText = await res.text();
    throw new Error(`Backend returned HTTP ${res.status}: ${errorText || res.statusText}`);
  } catch (err: any) {
    if (err.message && (err.message.includes('Validation error') || err.message.includes('Backend returned HTTP'))) {
      throw err;
    }
    throw new Error(
      'Backend server is unavailable at http://127.0.0.1:8000. Live execution is currently unavailable. You can explore verified saved examples below or start the backend with `uvicorn api.main:app --port 8000`.'
    );
  }
}
