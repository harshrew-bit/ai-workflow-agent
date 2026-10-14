import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import App from '../App';
import { ExecutionTrace } from '../components/ExecutionTrace';
import { Header } from '../components/Header';
import { ExecutionReport } from '../types/workflow';
import * as apiClient from '../api/client';

describe('AI Workflow Agent Frontend: Request-Driven Behavior', () => {
  it('renders initial page state with empty input and idle execution panel', () => {
    render(<App />);

    // 1. Header and title
    expect(screen.getByText('AI Workflow Agent')).toBeInTheDocument();
    expect(screen.getByText(/Route it. Execute it. Report it./i)).toBeInTheDocument();

    // 2. Request input is empty
    const textarea = screen.getByPlaceholderText(/Ask something like: Check inventory/i) as HTMLTextAreaElement;
    expect(textarea).toBeInTheDocument();
    expect(textarea.value).toBe('');

    // 3. Run button exists and is disabled when input is empty
    const runBtn = screen.getByRole('button', { name: /Run workflow/i });
    expect(runBtn).toBeInTheDocument();
    expect(runBtn).toBeDisabled();

    // 4. Idle execution panel with 3 sections
    expect(screen.getByText(/01 — Routing Decision/i)).toBeInTheDocument();
    expect(screen.getByText(/02 — Step Execution Timeline/i)).toBeInTheDocument();
    expect(screen.getByText(/03 — Final Structured Result/i)).toBeInTheDocument();
    expect(
      screen.getByText('Your execution trace will appear here after you submit a request.')
    ).toBeInTheDocument();

    // 5. No premature success status or exit code
    expect(screen.queryByText('SUCCESS')).not.toBeInTheDocument();
    expect(screen.queryByText(/EXIT 0/i)).not.toBeInTheDocument();
  });

  it('clicking a quick-try chip populates input without auto-running', () => {
    render(<App />);

    const chip = screen.getByText('WF001 Restock Check');
    fireEvent.click(chip);

    // Input populated with query
    const textarea = screen.getByPlaceholderText(/Ask something like: Check inventory/i) as HTMLTextAreaElement;
    expect(textarea.value).toBe("Check today's inventory and identify products that need restocking.");

    // Button is now enabled
    const runBtn = screen.getByRole('button', { name: /Run workflow/i });
    expect(runBtn).not.toBeDisabled();

    // Trace remains idle (no auto-execution occurred)
    expect(
      screen.getByText('Your execution trace will appear here after you submit a request.')
    ).toBeInTheDocument();
    expect(screen.queryByText('SUCCESS')).not.toBeInTheDocument();
  });

  it('submitting a request triggers execution and calls API', async () => {
    const mockReport: ExecutionReport = {
      request: "Check today's inventory",
      selected_workflow_id: 'WF001',
      selected_workflow_name: 'Inventory Restock Check',
      routing_confidence: 0.95,
      routing_reasoning: 'Keyword matched inventory check.',
      status: 'success',
      steps: [
        {
          step_number: 1,
          step_name: 'load inventory',
          status: 'completed',
          output_summary: 'Loaded 7 inventory item(s).',
        },
      ],
      final_output: {
        products_requiring_restock: [
          {
            product_id: 'PRD-001',
            product_name: 'Wireless Ergonomic Mouse',
            current_stock: 5,
            minimum_stock: 20,
            reorder_quantity: 15,
          },
        ],
      },
      errors: [],
      clarification_required: false,
      routing_mode: 'offline',
      warnings: [],
      exit_code: 0,
    };

    const executeSpy = vi.spyOn(apiClient, 'executeWorkflow').mockResolvedValueOnce({
      report: mockReport,
      isDemoFallback: false,
    });

    render(<App />);

    const textarea = screen.getByPlaceholderText(/Ask something like: Check inventory/i);
    fireEvent.change(textarea, { target: { value: "Check today's inventory" } });

    const runBtn = screen.getByRole('button', { name: /Run workflow/i });
    fireEvent.click(runBtn);

    expect(executeSpy).toHaveBeenCalledWith("Check today's inventory", undefined);

    await waitFor(() => {
      expect(screen.getByText('WF001 — Inventory Restock Check')).toBeInTheDocument();
      expect(screen.getByText('Wireless Ergonomic Mouse')).toBeInTheDocument();
      expect(screen.getByText('EXIT 0')).toBeInTheDocument();
    });

    executeSpy.mockRestore();
  });

  it('renders clarification response when backend returns needs_clarification', () => {
    const mockClarification: ExecutionReport = {
      request: 'What is the weather in Paris?',
      selected_workflow_id: null,
      selected_workflow_name: null,
      routing_confidence: 0.0,
      routing_reasoning: 'Off-topic query',
      status: 'needs_clarification',
      steps: [],
      final_output: null,
      errors: ['Query could not be matched to any registered workflow.'],
      clarification_required: true,
      routing_mode: 'offline',
      warnings: [],
      exit_code: 4,
    };

    render(
      <ExecutionTrace
        report={mockClarification}
        executionState="needs_clarification"
        isLoading={false}
      />
    );

    expect(screen.getByText('NEEDS_CLARIFICATION')).toBeInTheDocument();
    expect(screen.getByText('Needs your input')).toBeInTheDocument();
    expect(screen.getAllByText(/0 domain tools executed/i).length).toBeGreaterThan(0);
  });

  it('handles network failure gracefully without fabricating success output', async () => {
    const executeSpy = vi.spyOn(apiClient, 'executeWorkflow').mockRejectedValueOnce(
      new Error('Backend server is unavailable at http://127.0.0.1:8000.')
    );

    render(<App />);

    const textarea = screen.getByPlaceholderText(/Ask something like: Check inventory/i);
    fireEvent.change(textarea, { target: { value: 'Arbitrary custom user query' } });

    const runBtn = screen.getByRole('button', { name: /Run workflow/i });
    fireEvent.click(runBtn);

    await waitFor(() => {
      const errorElements = screen.getAllByText(/Backend server is unavailable at http:\/\/127\.0\.0\.1:8000\./i);
      expect(errorElements.length).toBeGreaterThan(0);
    });

    // Does NOT fabricate a successful result
    expect(screen.queryByText('SUCCESS')).not.toBeInTheDocument();
    expect(screen.queryByText('Wireless Ergonomic Mouse')).not.toBeInTheDocument();

    executeSpy.mockRestore();
  });

  it('labels saved examples clearly when viewing saved examples', () => {
    const mockReport: ExecutionReport = {
      request: "Check today's inventory",
      selected_workflow_id: 'WF001',
      selected_workflow_name: 'Inventory Restock Check',
      routing_confidence: 0.95,
      routing_reasoning: 'Verified test run',
      status: 'success',
      steps: [],
      final_output: {},
      errors: [],
      clarification_required: false,
      routing_mode: 'offline',
      warnings: [],
      exit_code: 0,
    };

    render(
      <ExecutionTrace
        report={mockReport}
        executionState="success"
        isSavedExample={true}
        savedExampleTitle="wf001_restock_check"
      />
    );

    // Saved example badge and notification
    expect(screen.getByText('SAVED EXAMPLE')).toBeInTheDocument();
    expect(screen.getByText(/Recorded Result:/i)).toBeInTheDocument();
    expect(screen.getByText(/not a newly executed request/i)).toBeInTheDocument();
  });

  it('displays advisory warning on forced route override', () => {
    const mockForcedReport: ExecutionReport = {
      request: 'Check inventory',
      selected_workflow_id: 'WF003',
      selected_workflow_name: 'Vendor File Processing',
      routing_confidence: 0.95,
      routing_reasoning: 'Simulated route',
      status: 'success',
      steps: [],
      final_output: {},
      errors: [],
      clarification_required: false,
      routing_mode: 'forced',
      warnings: [],
      exit_code: 0,
    };

    render(
      <ExecutionTrace
        report={mockForcedReport}
        executionState="success"
      />
    );

    expect(screen.getByText('FORCED ROUTE')).toBeInTheDocument();
    expect(screen.getByText(/FORCED ROUTE WARNING/i)).toBeInTheDocument();
    expect(screen.getByText(/not an automatic AI routing decision/i)).toBeInTheDocument();
  });

  it('displays demo mode badge when backend is unavailable', () => {
    render(
      <Header
        currentTab="home"
        onSelectTab={() => {}}
        health={null}
        isDemoMode={true}
      />
    );
    expect(screen.getByText('Demo mode')).toBeInTheDocument();
  });
});
