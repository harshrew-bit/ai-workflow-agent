import { describe, it, expect } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { ResultViews } from '../components/ResultViews';
import { RawJsonViewer } from '../components/RawJsonViewer';
import { ExecutionReport } from '../types/workflow';

describe('ResultViews Component Presentation', () => {
  it('renders multi-workflow results in separate cards with summary metrics', () => {
    const multiReport: ExecutionReport = {
      request: 'Check restock needs and audit vendor prices',
      selected_workflow_id: 'WF001, WF002',
      selected_workflow_name: 'WF001: Daily Inventory Check, WF002: Product Price Validation',
      routing_confidence: 1.0,
      routing_reasoning: 'Multi-intent request detected: inventory restocking and vendor price validation.',
      status: 'success',
      routing_mode: 'multi_workflow',
      clarification_required: false,
      warnings: [],
      exit_code: 0,
      errors: [],
      steps: [
        {
          step_number: 1,
          step_name: 'WF001: Daily Inventory Check',
          status: 'completed',
          output_summary: '2 items need restocking',
        },
        {
          step_number: 2,
          step_name: 'WF002: Product Price Validation',
          status: 'completed',
          output_summary: '3 price exceptions flagged',
        },
      ],
      final_output: {
        routing_mode: 'multi_workflow',
        aggregate_status: 'success',
        executed_workflows: ['WF001', 'WF002'],
        reports: [
          {
            request: 'Check restock needs',
            selected_workflow_id: 'WF001',
            selected_workflow_name: 'Daily Inventory Restock Analysis',
            routing_confidence: 1.0,
            routing_reasoning: 'Inventory request',
            status: 'success',
            steps: [],
            errors: [],
            clarification_required: false,
            routing_mode: 'offline',
            warnings: [],
            final_output: {
              items_to_reorder: [
                {
                  product_id: 'PROD-101',
                  product_name: 'Industrial Widget A',
                  current_stock: 5,
                  minimum_stock: 20,
                  reorder_quantity: 15,
                  supplier: 'Acme Supply Co.',
                },
                {
                  product_id: 'PROD-102',
                  product_name: 'Precision Gear B',
                  current_stock: 2,
                  minimum_stock: 10,
                  reorder_quantity: 8,
                  supplier: 'Global Mech Ltd.',
                },
              ],
              total_items_to_reorder: 2,
              total_reorder_units: 23,
            },
          },
          {
            request: 'Audit vendor prices',
            selected_workflow_id: 'WF002',
            selected_workflow_name: 'Vendor Price Audit & Exception Flagging',
            routing_confidence: 1.0,
            routing_reasoning: 'Pricing request',
            status: 'success',
            steps: [],
            errors: [],
            clarification_required: false,
            routing_mode: 'offline',
            warnings: [],
            final_output: {
              comparison_results: [
                {
                  sku: 'SKU-001',
                  product_name: 'Hex Bolt 50mm',
                  internal_price: 10.0,
                  vendor_price: 12.0,
                  percentage_difference: 20.0,
                  status: 'EXCEPTION',
                },
                {
                  sku: 'SKU-002',
                  product_name: 'Steel Washer M8',
                  internal_price: 5.0,
                  vendor_price: 5.1,
                  percentage_difference: 2.0,
                  status: 'COMPLIANT',
                },
              ],
              exceptions: [
                {
                  sku: 'SKU-001',
                  product_name: 'Hex Bolt 50mm',
                  internal_price: 10.0,
                  vendor_price: 12.0,
                  difference_percentage: 20.0,
                },
              ],
              total_exceptions: 1,
              unmatched_vendor_records: [
                {
                  sku: 'VEND-999',
                  vendor_name: 'Legacy Supplier Inc',
                  vendor_price: 45.0,
                  reason: 'SKU not found in internal price catalog',
                },
              ],
              unmatched_internal_records: [
                {
                  sku: 'SKU-777',
                  product_name: 'Obsolete Bracket',
                  internal_price: 18.5,
                  reason: 'SKU not quoted by vendor in latest catalog',
                },
              ],
            },
          },
        ],
      },
    };

    render(<ResultViews report={multiReport} />);

    // 1. Compact Summary Metrics at the top
    expect(screen.getByText('Overall Status')).toBeInTheDocument();
    expect(screen.getByText('Workflows Executed')).toBeInTheDocument();
    expect(screen.getByText('Price Exceptions')).toBeInTheDocument();
    expect(screen.getByText('Low Stock Items')).toBeInTheDocument();

    // 2. Both workflows rendered in separate cards
    expect(screen.getByText(/Daily Inventory Restock Analysis/i)).toBeInTheDocument();
    expect(screen.getByText(/Vendor Price Audit & Exception Flagging/i)).toBeInTheDocument();

    // 3. Inventory Table columns and values
    expect(screen.getByText('Industrial Widget A')).toBeInTheDocument();
    expect(screen.getByText('Precision Gear B')).toBeInTheDocument();
    expect(screen.getByText('Acme Supply Co.')).toBeInTheDocument();
    expect(screen.getByText('Global Mech Ltd.')).toBeInTheDocument();
    expect(screen.getByText('PROD-101')).toBeInTheDocument();

    // 4. Pricing Table columns and values
    expect(screen.getByText('Hex Bolt 50mm')).toBeInTheDocument();
    expect(screen.getByText('Steel Washer M8')).toBeInTheDocument();
    expect(screen.getByText('+20.00%')).toBeInTheDocument();
    expect(screen.getByText('+2.00%')).toBeInTheDocument();
    expect(screen.getByText('COMPLIANT')).toBeInTheDocument();
    expect(screen.getByText('EXCEPTION (+20.00%)')).toBeInTheDocument();

    // 5. Data Quality Section for unmatched SKUs
    expect(screen.getByText(/Data Quality & Catalog Reconciliation/i)).toBeInTheDocument();
    expect(screen.getByText('VEND-999')).toBeInTheDocument();
    expect(screen.getByText('Legacy Supplier Inc')).toBeInTheDocument();
    expect(screen.getByText('SKU not found in internal price catalog')).toBeInTheDocument();
    expect(screen.getByText('SKU-777')).toBeInTheDocument();
    expect(screen.getByText('Obsolete Bracket')).toBeInTheDocument();
    expect(screen.getByText('SKU not quoted by vendor in latest catalog')).toBeInTheDocument();

    // 6. Business verification notice
    expect(
      screen.getByText(/Business Verification Notice/i)
    ).toBeInTheDocument();
    expect(
      screen.getByText(/confirms error-free pipeline execution/i)
    ).toBeInTheDocument();
  });

  it('toggles raw JSON viewer with Technical details label', () => {
    const report: ExecutionReport = {
      request: 'Test request',
      selected_workflow_id: 'WF001',
      selected_workflow_name: 'Test Workflow',
      routing_confidence: 1.0,
      routing_reasoning: 'Test reasoning',
      status: 'success',
      routing_mode: 'offline',
      clarification_required: false,
      warnings: [],
      errors: [],
      steps: [],
      final_output: { test_key: 'test_value' },
    };

    render(<RawJsonViewer report={report} />);

    const button = screen.getByRole('button', {
      name: /Technical details \(Raw ExecutionReport JSON\)/i,
    });
    expect(button).toBeInTheDocument();

    // Initially collapsed
    expect(screen.queryByText(/"test_key": "test_value"/i)).not.toBeInTheDocument();

    // Click to expand
    fireEvent.click(button);
    expect(screen.getByText(/"test_key": "test_value"/i)).toBeInTheDocument();

    // Click again to collapse
    fireEvent.click(button);
    expect(screen.queryByText(/"test_key": "test_value"/i)).not.toBeInTheDocument();
  });
});
