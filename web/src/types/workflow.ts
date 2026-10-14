export interface StepReport {
  step_number: number;
  step_name: string;
  status: 'completed' | 'failed' | 'skipped' | 'needs_clarification';
  output_summary?: string | null;
  output?: any;
  error?: string | null;
}

export interface ExecutionReport {
  request: string;
  selected_workflow_id: string | null;
  selected_workflow_name: string | null;
  routing_confidence: number;
  routing_reasoning: string;
  status: 'success' | 'partial_failure' | 'failed' | 'needs_clarification';
  steps: StepReport[];
  final_output: any;
  errors: string[];
  clarification_required: boolean;
  routing_mode: 'llm' | 'offline' | 'forced';
  warnings: string[];
  exit_code?: number;
}

export type AppExecutionState = 'idle' | 'running' | 'success' | 'needs_clarification' | 'partial_failure' | 'error';

export interface ExecutionViewState {
  state: AppExecutionState;
  report: ExecutionReport | null;
  isSavedExample: boolean;
  savedExampleTitle?: string;
  errorMessage?: string;
}

export interface WorkflowDefinition {
  workflow_id: string;
  workflow_name: string;
  trigger: string;
  inputs: string;
  steps: string;
  parsed_steps: string[];
  decision_logic: string;
  tools_required: string;
  parsed_tools: string[];
  expected_output: string;
}

export interface HealthResponse {
  status: string;
  workbook_loaded: boolean;
  workflow_count: number;
  llm_configured: boolean;
  offline_router_available: boolean;
}

export interface ExampleItem {
  slug: string;
  request: string;
  expected_workflow_id: string | null;
  expected_status: string;
  expected_exit_code: number;
  category: string;
}
