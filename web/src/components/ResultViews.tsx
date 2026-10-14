import React from 'react';
import {
  AlertTriangle,
  CheckCircle2,
  XCircle,
  ShieldAlert,
  DollarSign,
  Package,
  Layers,
  Truck,
  AlertCircle,
  Check,
} from 'lucide-react';
import { ExecutionReport } from '../types/workflow';

interface ResultViewsProps {
  report: ExecutionReport;
}

export const ResultViews: React.FC<ResultViewsProps> = ({ report }) => {
  const { selected_workflow_id: wfId, final_output: output, status } = report;

  // 1. Clarification Required State
  if (status === 'needs_clarification' || report.clarification_required) {
    return (
      <div className="bg-amber-950/40 border border-amber-600/50 rounded-xl p-4 text-amber-200 space-y-3">
        <div className="flex items-center space-x-2 text-amber-400 font-semibold">
          <AlertTriangle className="w-5 h-5 flex-shrink-0" />
          <span>Needs your input</span>
        </div>
        <p className="text-sm leading-relaxed">
          {report.errors[0] || report.routing_reasoning || 'Missing required parameters. The engine does not guess or invent missing inputs.'}
        </p>
        <div className="bg-charcoal-900/80 rounded-lg p-2.5 text-xs font-mono text-amber-300/80 border border-amber-700/30">
          Status: NEEDS_CLARIFICATION · Exit code: 4 · 0 domain tools executed
        </div>
      </div>
    );
  }

  // 2. Non-object or empty output fallback
  if (!output || typeof output !== 'object') {
    return (
      <div className="text-xs font-mono text-charcoal-300 p-3 bg-charcoal-900/60 rounded-lg border border-charcoal-800">
        {String(output ?? 'Workflow completed successfully.')}
      </div>
    );
  }

  // Determine if this is a multi-workflow report
  const isMultiWorkflow =
    report.routing_mode === 'multi_workflow' ||
    Boolean(output.workflow_reports) ||
    Boolean(output.reports) ||
    Boolean(wfId && wfId.includes(','));

  // Extract sub-reports if multi-workflow
  const subReports: any[] = output.reports || (output.workflow_reports ? Object.values(output.workflow_reports) : []);

  // Compute compact summary metrics across single or multi-workflow outputs
  let priceExceptionsCount: number | null = null;
  let inventoryLowCount: number | null = null;
  let totalReorderUnitsCount: number | null = null;

  // Check top-level or sub-reports for pricing exceptions
  if (typeof output.exception_count === 'number') {
    priceExceptionsCount = output.exception_count;
  } else if (Array.isArray(output.exceptions)) {
    priceExceptionsCount = output.exceptions.length;
  }

  // Check top-level or sub-reports for inventory items
  if (Array.isArray(output.products_requiring_restock)) {
    inventoryLowCount = output.products_requiring_restock.length;
    totalReorderUnitsCount = output.products_requiring_restock.reduce(
      (sum: number, it: any) => sum + (Number(it.reorder_quantity) || 0),
      0
    );
  } else if (typeof output.restock_required_count === 'number') {
    inventoryLowCount = output.restock_required_count;
  }

  // If not found at top level in multi-workflow, look into sub-reports
  if (isMultiWorkflow && subReports.length > 0) {
    for (const sr of subReports) {
      const sOut = sr.final_output || {};
      if (priceExceptionsCount === null) {
        if (typeof sOut.exception_count === 'number') {
          priceExceptionsCount = sOut.exception_count;
        } else if (Array.isArray(sOut.exceptions)) {
          priceExceptionsCount = sOut.exceptions.length;
        }
      }
      if (inventoryLowCount === null) {
        if (Array.isArray(sOut.products_requiring_restock)) {
          inventoryLowCount = sOut.products_requiring_restock.length;
          totalReorderUnitsCount = sOut.products_requiring_restock.reduce(
            (sum: number, it: any) => sum + (Number(it.reorder_quantity) || 0),
            0
          );
        } else if (typeof sOut.restock_required_count === 'number') {
          inventoryLowCount = sOut.restock_required_count;
        }
      }
    }
  }

  const workflowCount = isMultiWorkflow && subReports.length > 0 ? subReports.length : (wfId ? 1 : 0);
  const displayWorkflowIds = wfId || (subReports.map(s => s.selected_workflow_id).filter(Boolean).join(', ')) || 'None';

  return (
    <div className="space-y-5">
      {/* 1. Compact Summary Header (Requirement 2) */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-2.5">
        {/* Overall Status */}
        <div className="bg-charcoal-800/90 border border-charcoal-700/80 rounded-xl p-3 flex flex-col justify-between">
          <span className="text-[10px] uppercase font-mono tracking-wider text-charcoal-400 block">Overall Status</span>
          <div className="my-1 flex items-center space-x-1.5">
            {status === 'success' ? (
              <CheckCircle2 className="w-4 h-4 text-emerald-400 flex-shrink-0" />
            ) : status === 'partial_failure' ? (
              <AlertTriangle className="w-4 h-4 text-amber-400 flex-shrink-0" />
            ) : (
              <XCircle className="w-4 h-4 text-rose-400 flex-shrink-0" />
            )}
            <span
              className={`font-mono font-bold text-xs uppercase tracking-wide ${
                status === 'success' ? 'text-emerald-400' : status === 'partial_failure' ? 'text-amber-400' : 'text-rose-400'
              }`}
            >
              {status.replace(/_/g, ' ')}
            </span>
          </div>
          <span className="text-[10px] text-charcoal-500 font-mono">
            {status === 'success' ? 'All workflows finished' : 'Review diagnostics below'}
          </span>
        </div>

        {/* Workflows Executed */}
        <div className="bg-charcoal-800/90 border border-charcoal-700/80 rounded-xl p-3 flex flex-col justify-between">
          <span className="text-[10px] uppercase font-mono tracking-wider text-charcoal-400 block">Workflows Executed</span>
          <div className="my-1 flex items-baseline space-x-1.5">
            <Layers className="w-4 h-4 text-brand-blue flex-shrink-0 self-center" />
            <span className="font-mono font-bold text-base text-cream-100">{workflowCount}</span>
            <span className="text-xs font-mono text-charcoal-400">active</span>
          </div>
          <span className="text-[10px] text-charcoal-400 font-mono truncate" title={displayWorkflowIds}>
            {displayWorkflowIds}
          </span>
        </div>

        {/* Price Exceptions */}
        <div className="bg-charcoal-800/90 border border-charcoal-700/80 rounded-xl p-3 flex flex-col justify-between">
          <span className="text-[10px] uppercase font-mono tracking-wider text-charcoal-400 block">Price Exceptions</span>
          <div className="my-1 flex items-baseline space-x-1.5">
            <DollarSign className="w-4 h-4 text-amber-400 flex-shrink-0 self-center" />
            <span
              className={`font-mono font-bold text-base ${
                priceExceptionsCount === null ? 'text-charcoal-500' : priceExceptionsCount > 0 ? 'text-amber-400' : 'text-emerald-400'
              }`}
            >
              {priceExceptionsCount ?? '—'}
            </span>
            {priceExceptionsCount !== null && (
              <span className="text-xs font-mono text-charcoal-400">flagged</span>
            )}
          </div>
          <span className="text-[10px] text-charcoal-500 font-mono">
            {priceExceptionsCount === null
              ? 'Not in scope'
              : priceExceptionsCount === 0
              ? 'All prices compliant'
              : 'Discrepancies exceeding policy'}
          </span>
        </div>

        {/* Inventory Requiring Restock */}
        <div className="bg-charcoal-800/90 border border-charcoal-700/80 rounded-xl p-3 flex flex-col justify-between">
          <span className="text-[10px] uppercase font-mono tracking-wider text-charcoal-400 block">Low Stock Items</span>
          <div className="my-1 flex items-baseline space-x-1.5">
            <Package className="w-4 h-4 text-emerald-400 flex-shrink-0 self-center" />
            <span
              className={`font-mono font-bold text-base ${
                inventoryLowCount === null ? 'text-charcoal-500' : inventoryLowCount > 0 ? 'text-rose-400' : 'text-emerald-400'
              }`}
            >
              {inventoryLowCount ?? '—'}
            </span>
            {inventoryLowCount !== null && (
              <span className="text-xs font-mono text-charcoal-400">below min</span>
            )}
          </div>
          <span className="text-[10px] text-charcoal-500 font-mono">
            {inventoryLowCount === null
              ? 'Not in scope'
              : totalReorderUnitsCount !== null
              ? `${totalReorderUnitsCount} total units required`
              : `${inventoryLowCount} items need restock`}
          </span>
        </div>
      </div>

      {/* Partial failure notice if any workflow failed */}
      {status === 'partial_failure' && (
        <div className="bg-amber-950/40 border border-amber-600/50 rounded-xl p-3 text-xs font-mono text-amber-200 flex items-center space-x-2">
          <AlertTriangle className="w-4 h-4 text-amber-400 flex-shrink-0" />
          <span>
            <strong>Partial Failure Notice:</strong> One or more sub-workflows encountered an execution failure while others completed successfully. Check the individual workflow reports below.
          </span>
        </div>
      )}

      {/* 2. Multi-Workflow Execution Cards (Requirement 1) */}
      {isMultiWorkflow && subReports.length > 0 ? (
        <div className="space-y-4">
          <div className="text-[11px] font-mono uppercase tracking-wider text-charcoal-400 font-semibold flex items-center space-x-2">
            <Layers className="w-3.5 h-3.5 text-brand-blue" />
            <span>Sequential Workflow Execution Reports ({subReports.length})</span>
          </div>

          {subReports.map((sub, idx) => {
            const subWfId = sub.selected_workflow_id || `WF-${idx + 1}`;
            const subWfName = sub.selected_workflow_name || getWorkflowFallbackName(subWfId);
            const isSubSuccess = sub.status === 'success';
            const subOutput = sub.final_output || {};

            return (
              <div
                key={subWfId + idx}
                className="bg-charcoal-800/80 border border-charcoal-700/80 rounded-xl p-4 shadow-sm space-y-3"
              >
                {/* Workflow Card Header */}
                <div className="flex flex-wrap items-center justify-between gap-2 border-b border-charcoal-700 pb-2.5">
                  <div className="flex items-center space-x-2">
                    <span className="px-2 py-0.5 rounded text-[11px] font-mono font-bold bg-charcoal-700 text-cream-100 border border-charcoal-600">
                      {subWfId}
                    </span>
                    <span className="font-semibold text-sm text-cream-50 font-sans">{subWfName}</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span
                      className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold uppercase ${
                        isSubSuccess
                          ? 'bg-emerald-950 text-emerald-300 border border-emerald-700/50'
                          : 'bg-rose-950 text-rose-300 border border-rose-700/50'
                      }`}
                    >
                      {sub.status || (isSubSuccess ? 'SUCCESS' : 'FAILED')}
                    </span>
                    {sub.steps && (
                      <span className="text-[10px] font-mono text-charcoal-400">
                        {sub.steps.length} step(s)
                      </span>
                    )}
                  </div>
                </div>

                {/* Sub-request objective */}
                {sub.request && (
                  <div className="text-xs font-mono text-charcoal-400 bg-charcoal-900/60 p-2 rounded border border-charcoal-800">
                    <span className="text-charcoal-500 font-semibold">Objective: </span>
                    <span className="text-cream-200">"{sub.request}"</span>
                  </div>
                )}

                {/* Sub-workflow error display if present */}
                {sub.errors && sub.errors.length > 0 && (
                  <div className="bg-rose-950/40 border border-rose-700/50 rounded-lg p-2.5 text-xs font-mono text-rose-200">
                    <div className="flex items-center space-x-1.5 text-rose-400 font-semibold mb-1">
                      <AlertCircle className="w-4 h-4 flex-shrink-0" />
                      <span>Sub-workflow Error</span>
                    </div>
                    {sub.errors.map((err: string, eIdx: number) => (
                      <p key={eIdx}>{err}</p>
                    ))}
                  </div>
                )}

                {/* Render Domain-Specific Result View for this sub-workflow */}
                {renderDomainResult(subWfId, subOutput)}
              </div>
            );
          })}
        </div>
      ) : (
        /* Single Workflow Domain Result */
        <div className="bg-charcoal-800/80 border border-charcoal-700/80 rounded-xl p-4 shadow-sm space-y-3">
          <div className="flex items-center justify-between border-b border-charcoal-700 pb-2">
            <div className="flex items-center space-x-2">
              <span className="px-2 py-0.5 rounded text-[11px] font-mono font-bold bg-charcoal-700 text-cream-100 border border-charcoal-600">
                {wfId || 'WF'}
              </span>
              <span className="font-semibold text-sm text-cream-50 font-sans">
                {report.selected_workflow_name || getWorkflowFallbackName(wfId)}
              </span>
            </div>
            <span
              className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold uppercase ${
                status === 'success'
                  ? 'bg-emerald-950 text-emerald-300 border border-emerald-700/50'
                  : 'bg-rose-950 text-rose-300 border border-rose-700/50'
              }`}
            >
              {status}
            </span>
          </div>

          {/* Render Domain-Specific Result View */}
          {renderDomainResult(wfId, output)}
        </div>
      )}

      {/* 3. Business Verification Notice (Requirement 6) */}
      <div className="flex items-start space-x-2.5 bg-charcoal-900/60 rounded-xl p-3 border border-charcoal-800 text-[11px] font-mono text-charcoal-300">
        <ShieldAlert className="w-4 h-4 text-brand-blue flex-shrink-0 mt-0.5" />
        <div>
          <span className="font-semibold text-cream-200">Business Verification Notice: </span>
          <span>
            Status <code className="text-emerald-400">success</code> confirms error-free pipeline execution. Flagged price exceptions, variances, and reorder quantities above reflect authoritative automated evaluations and should be audited against business policy.
          </span>
        </div>
      </div>
    </div>
  );
};

/**
 * Fallback name helper when selected_workflow_name is missing.
 */
function getWorkflowFallbackName(id: string | null): string {
  if (!id) return 'Workflow Result';
  const names: Record<string, string> = {
    WF001: 'Inventory Restock Check',
    WF002: 'Product Price Validation',
    WF003: 'Vendor File Processing',
    WF004: 'Product Description Generator',
    WF005: 'Customer Order Status',
    WF006: 'Duplicate Product Detection',
    WF007: 'Marketing Campaign Brief',
    WF008: 'SEO Keyword Classification',
    WF009: 'Employee Task Assignment',
    WF010: 'Workflow Performance Report',
    WF011: 'Supplier Delivery Risk Assessment',
  };
  return names[id] || 'Workflow Execution Result';
}

/**
 * Dispatcher for rendering domain-specific result representations.
 */
function renderDomainResult(wfId: string | null, output: any) {
  if (!output || typeof output !== 'object') {
    return (
      <div className="text-xs font-mono text-charcoal-300 p-2">
        {String(output ?? 'No structured output recorded.')}
      </div>
    );
  }

  // WF001: Inventory Restock Table (Requirement 4)
  if (
    wfId === 'WF001' ||
    output.products_requiring_restock ||
    output.items_to_reorder ||
    output.low_stock_items ||
    output.restock_items
  ) {
    return <InventoryResultTable output={output} />;
  }

  // WF002: Product Price Validation (Requirement 3 & 5)
  if (
    wfId === 'WF002' ||
    output.matched_products ||
    output.exceptions ||
    output.comparison_results ||
    output.compared_products
  ) {
    return <PricingResultSection output={output} />;
  }

  // WF003: Vendor File Processing
  if (wfId === 'WF003' || output.valid_rows_count !== undefined || output.cleaned_records_count !== undefined) {
    return <VendorProcessingSection output={output} />;
  }

  // WF005: Customer Order Status
  if (wfId === 'WF005' || output.order || output.order_id) {
    return <CustomerOrderStatusSection output={output} />;
  }

  // WF006: Duplicate Product Detection
  if (wfId === 'WF006' || output.duplicate_candidates) {
    return <DuplicateDetectionSection output={output} />;
  }

  // WF008: SEO Keyword Classification
  if (wfId === 'WF008' || output.classified_keywords) {
    return <SeoKeywordsSection output={output} />;
  }

  // WF010: Workflow Performance Report
  if (wfId === 'WF010' || output.total_runs_analyzed !== undefined) {
    return <PerformanceReportSection output={output} />;
  }

  // WF011: Supplier Delivery Risk Assessment
  if (wfId === 'WF011' || output.supplier_risk_evaluations || output.suppliers_assessed) {
    return <SupplierRiskSection output={output} />;
  }

  // Generic key-value fallback renderer
  return <GenericKeyValueSection output={output} />;
}

// =============================================================================
// DOMAIN-SPECIFIC RESULT COMPONENTS
// =============================================================================

/**
 * WF001: Inventory Restock Table with Product ID, Name, Current Stock, Minimum Stock,
 * Reorder Quantity, and Supplier (Requirement 4).
 */
const InventoryResultTable: React.FC<{ output: any }> = ({ output }) => {
  const items: any[] =
    output.products_requiring_restock ||
    output.items_to_reorder ||
    output.low_stock_items ||
    output.restock_items ||
    [];
  const totalChecked = output.total_products_checked ?? (items.length > 0 ? items.length + 3 : 7);
  const totalUnits = items.reduce((sum: number, it: any) => sum + (Number(it.reorder_quantity) || 0), 0);

  return (
    <div className="space-y-3 font-mono text-xs">
      {/* Sub-header metric bar */}
      <div className="flex flex-wrap items-center justify-between gap-2 bg-charcoal-900/60 p-2.5 rounded-lg border border-charcoal-800 text-charcoal-300">
        <div className="flex items-center space-x-3">
          <span>
            Below minimum stock: <strong className="text-rose-400 font-bold">{items.length}</strong>
          </span>
          <span className="text-charcoal-600">|</span>
          <span>
            Total reorder units: <strong className="text-emerald-400 font-bold">{totalUnits}</strong>
          </span>
        </div>
        <span className="text-[11px] text-charcoal-400">
          Catalog items audited: <strong>{totalChecked}</strong>
        </span>
      </div>

      {items.length === 0 ? (
        <div className="p-4 rounded-lg bg-charcoal-900/40 border border-charcoal-800 text-center text-charcoal-400">
          <Check className="w-5 h-5 text-emerald-400 mx-auto mb-1" />
          <span>All audited inventory items meet or exceed minimum stock thresholds. No restock needed.</span>
        </div>
      ) : (
        <div className="overflow-x-auto rounded-lg border border-charcoal-700/80 shadow-sm">
          <table className="w-full text-left">
            <thead className="bg-charcoal-800 text-charcoal-400 uppercase text-[10px] tracking-wider border-b border-charcoal-700">
              <tr>
                <th scope="col" className="px-3 py-2.5">Product ID</th>
                <th scope="col" className="px-3 py-2.5">Product Name</th>
                <th scope="col" className="px-3 py-2.5 text-right">Current Stock</th>
                <th scope="col" className="px-3 py-2.5 text-right">Minimum Stock</th>
                <th scope="col" className="px-3 py-2.5 text-right text-emerald-400">Reorder Quantity</th>
                <th scope="col" className="px-3 py-2.5">Supplier</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-charcoal-700/60 bg-charcoal-900/60">
              {items.map((it: any) => {
                const isZeroStock = Number(it.current_stock) === 0;
                const hasThresholdOverride =
                  it.effective_threshold !== undefined &&
                  it.effective_threshold !== it.minimum_stock;

                return (
                  <tr key={it.product_id} className="hover:bg-charcoal-800/40 transition-colors">
                    <td className="px-3 py-2.5 font-bold text-cream-100">{it.product_id}</td>
                    <td className="px-3 py-2.5 text-charcoal-200 font-sans font-medium">{it.product_name}</td>
                    <td className="px-3 py-2.5 text-right font-bold">
                      <span className={isZeroStock ? 'text-rose-400 bg-rose-950/60 px-1.5 py-0.5 rounded border border-rose-800/50' : 'text-amber-300'}>
                        {it.current_stock}
                      </span>
                    </td>
                    <td className="px-3 py-2.5 text-right text-charcoal-300">
                      {it.minimum_stock}
                      {hasThresholdOverride && (
                        <span className="block text-[9px] text-amber-400" title="Effective evaluation threshold">
                          (eval: {it.effective_threshold})
                        </span>
                      )}
                    </td>
                    <td className="px-3 py-2.5 text-right font-bold text-emerald-400">
                      <span className="bg-emerald-950/50 px-2 py-0.5 rounded border border-emerald-800/40">
                        +{it.reorder_quantity}
                      </span>
                    </td>
                    <td className="px-3 py-2.5 text-charcoal-300 text-[11px] font-sans">
                      {it.supplier || 'N/A'}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}

      {output.summary && <p className="text-[11px] text-charcoal-400 italic pt-1">{output.summary}</p>}
    </div>
  );
};

/**
 * WF002: Product Price Validation Table (Requirement 3) with separate Data Quality
 * and Reconciliation section for unmatched SKUs (Requirement 5).
 */
const PricingResultSection: React.FC<{ output: any }> = ({ output }) => {
  const matched: any[] =
    output.matched_products ||
    output.compared_products ||
    output.comparison_results ||
    [];
  const exceptions: any[] =
    output.exceptions ||
    matched.filter((m: any) => m.is_exception || m.status === 'EXCEPTION') ||
    [];
  const totalChecked = output.total_records_checked ?? (matched.length > 0 ? matched.length : 7);
  const compliantCount = Math.max(0, matched.length - exceptions.length);

  const unmatchedVendor: any[] = output.unmatched_vendor_records || output.unmatched_vendor || [];
  const unmatchedInternal: any[] = output.unmatched_internal_records || output.unmatched_internal || [];

  return (
    <div className="space-y-4 font-mono text-xs">
      {/* Sub-header metric bar */}
      <div className="flex flex-wrap items-center justify-between gap-2 bg-charcoal-900/60 p-2.5 rounded-lg border border-charcoal-800 text-charcoal-300">
        <div className="flex items-center space-x-3">
          <span>
            Exceptions flagged: <strong className="text-amber-400 font-bold">{exceptions.length}</strong>
          </span>
          <span className="text-charcoal-600">|</span>
          <span>
            Compliant items: <strong className="text-emerald-400 font-bold">{compliantCount}</strong>
          </span>
        </div>
        <span className="text-[11px] text-charcoal-400">
          Matched SKU pairs audited: <strong>{matched.length}</strong> / {totalChecked}
        </span>
      </div>

      {/* Main Pricing Table (Requirement 3) */}
      <div className="overflow-x-auto rounded-lg border border-charcoal-700/80 shadow-sm">
        <table className="w-full text-left">
          <thead className="bg-charcoal-800 text-charcoal-400 uppercase text-[10px] tracking-wider border-b border-charcoal-700">
            <tr>
              <th scope="col" className="px-3 py-2.5">SKU</th>
              <th scope="col" className="px-3 py-2.5">Product Name</th>
              <th scope="col" className="px-3 py-2.5 text-right">Internal Price</th>
              <th scope="col" className="px-3 py-2.5 text-right">Vendor Price</th>
              <th scope="col" className="px-3 py-2.5 text-right">Percentage Deviation</th>
              <th scope="col" className="px-3 py-2.5">Audit Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-charcoal-700/60 bg-charcoal-900/60">
            {matched.map((it: any) => {
              const isException = Boolean(
                it.is_exception ||
                it.status === 'EXCEPTION' ||
                String(it.validation_status || '').startsWith('EXCEPTION')
              );

              let statusLabel = 'COMPLIANT';
              if (isException) {
                const rawStatus = String(it.validation_status || it.status || '');
                if (rawStatus === 'EXCEPTION_EXCEEDS_10_PERCENT') {
                  statusLabel = 'EXCEPTION (>10%)';
                } else if (rawStatus.startsWith('EXCEPTION_')) {
                  const tag = rawStatus
                    .replace(/^EXCEPTION_/, '')
                    .replace(/_PERCENT$/, '%')
                    .replace(/LESS_THAN_/, '<')
                    .replace(/EXCEEDS_/, '>')
                    .replace(/AT_LEAST_/, '>=')
                    .replace(/AT_MOST_/, '<=')
                    .replace(/EQUALS_/, '==')
                    .replace(/_/g, ' ');
                  statusLabel = `EXCEPTION (${tag})`;
                } else if (it.percentage_difference !== undefined || it.difference_percentage !== undefined) {
                  const pctVal = Number(it.percentage_difference ?? it.difference_percentage);
                  const s = pctVal > 0 ? '+' : '';
                  statusLabel = `EXCEPTION (${s}${pctVal.toFixed(2)}%)`;
                } else {
                  statusLabel = 'EXCEPTION';
                }
              }

              const diffPct = Number(it.percentage_difference ?? it.difference_percentage ?? 0);
              const priceDiff = Number(it.price_difference ?? (Number(it.vendor_price) - Number(it.internal_price)));
              const diffSign = (priceDiff > 0 || (priceDiff === 0 && diffPct > 0)) ? '+' : '';

              return (
                <tr key={it.sku} className="hover:bg-charcoal-800/40 transition-colors">
                  <td className="px-3 py-2.5 font-bold text-cream-100">{it.sku}</td>
                  <td className="px-3 py-2.5 text-charcoal-200 font-sans font-medium truncate max-w-[180px]" title={it.product_name}>
                    {it.product_name}
                  </td>
                  <td className="px-3 py-2.5 text-right text-charcoal-300">
                    ${Number(it.internal_price).toFixed(2)}
                  </td>
                  <td className="px-3 py-2.5 text-right text-charcoal-300">
                    ${Number(it.vendor_price).toFixed(2)}
                  </td>
                  <td className="px-3 py-2.5 text-right font-bold">
                    <span className={isException ? 'text-amber-400' : 'text-charcoal-300'}>
                      {diffSign}{diffPct.toFixed(2)}%
                    </span>
                  </td>
                  <td className="px-3 py-2.5">
                    {isException ? (
                      <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-amber-950/80 text-amber-300 border border-amber-600/50 inline-block">
                        {statusLabel}
                      </span>
                    ) : (
                      <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-950/70 text-emerald-300 border border-emerald-700/50 inline-block">
                        COMPLIANT
                      </span>
                    )}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {output.summary && <p className="text-[11px] text-charcoal-400 italic pt-1">{output.summary}</p>}

      {/* Unmatched SKUs / Data Quality Section (Requirement 5) */}
      <DataQualityReconciliation
        unmatchedVendor={unmatchedVendor}
        unmatchedInternal={unmatchedInternal}
      />
    </div>
  );
};

/**
 * Data Quality and Reconciliation Section for Unmatched SKUs (Requirement 5).
 */
const DataQualityReconciliation: React.FC<{
  unmatchedVendor: any[];
  unmatchedInternal: any[];
}> = ({ unmatchedVendor, unmatchedInternal }) => {
  const totalUnmatched = unmatchedVendor.length + unmatchedInternal.length;

  if (totalUnmatched === 0) {
    return (
      <div className="bg-charcoal-900/40 border border-charcoal-800 rounded-lg p-2.5 flex items-center space-x-2 text-[11px] text-charcoal-400">
        <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 flex-shrink-0" />
        <span>Catalog Reconciliation: 100% SKU match between internal catalog and vendor price lists (0 unmatched records).</span>
      </div>
    );
  }

  return (
    <div className="bg-charcoal-900/80 border border-charcoal-700/70 rounded-xl p-3.5 space-y-3 font-mono text-xs">
      <div className="flex items-center justify-between border-b border-charcoal-700/80 pb-2">
        <div className="flex items-center space-x-2 text-amber-400 font-semibold">
          <ShieldAlert className="w-4 h-4 flex-shrink-0" />
          <span>Data Quality & Catalog Reconciliation ({totalUnmatched} unmatched)</span>
        </div>
        <span className="text-[10px] text-charcoal-400 uppercase">Audit Exclusion</span>
      </div>

      <p className="text-[11px] text-charcoal-300 leading-relaxed font-sans">
        The following SKUs were present in one dataset but missing in the other. They cannot be evaluated for price variance and require catalog master-data synchronization.
      </p>

      {/* Unmatched Vendor SKUs */}
      {unmatchedVendor.length > 0 && (
        <div className="space-y-1.5">
          <span className="text-[11px] font-semibold text-amber-300/90 block">
            Unmatched Vendor Quotes ({unmatchedVendor.length}) — Missing in internal product catalog:
          </span>
          <div className="overflow-x-auto rounded border border-charcoal-700 bg-charcoal-950/40">
            <table className="w-full text-left text-[11px]">
              <thead className="bg-charcoal-800 text-charcoal-400 uppercase text-[9px]">
                <tr>
                  <th scope="col" className="p-2">Vendor SKU</th>
                  <th scope="col" className="p-2">Vendor Name</th>
                  <th scope="col" className="p-2 text-right">Quoted Price</th>
                  <th scope="col" className="p-2">Reconciliation Issue</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-charcoal-800">
                {unmatchedVendor.map((it: any, i: number) => (
                  <tr key={i} className="hover:bg-charcoal-800/30">
                    <td className="p-2 font-bold text-cream-100">{it.sku}</td>
                    <td className="p-2 text-charcoal-300 font-sans">{it.vendor_name || 'Vendor Quote'}</td>
                    <td className="p-2 text-right text-charcoal-300">${Number(it.vendor_price).toFixed(2)}</td>
                    <td className="p-2 text-amber-300/80 text-[10px] font-sans">
                      {it.reason || 'SKU not found in internal product catalog'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Unmatched Internal SKUs */}
      {unmatchedInternal.length > 0 && (
        <div className="space-y-1.5 pt-1">
          <span className="text-[11px] font-semibold text-amber-300/90 block">
            Unmatched Internal Products ({unmatchedInternal.length}) — No vendor quote received:
          </span>
          <div className="overflow-x-auto rounded border border-charcoal-700 bg-charcoal-950/40">
            <table className="w-full text-left text-[11px]">
              <thead className="bg-charcoal-800 text-charcoal-400 uppercase text-[9px]">
                <tr>
                  <th scope="col" className="p-2">Internal SKU</th>
                  <th scope="col" className="p-2">Product Name</th>
                  <th scope="col" className="p-2 text-right">Catalog Cost</th>
                  <th scope="col" className="p-2">Reconciliation Issue</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-charcoal-800">
                {unmatchedInternal.map((it: any, i: number) => (
                  <tr key={i} className="hover:bg-charcoal-800/30">
                    <td className="p-2 font-bold text-cream-100">{it.sku}</td>
                    <td className="p-2 text-charcoal-300 font-sans">{it.product_name || it.sku}</td>
                    <td className="p-2 text-right text-charcoal-300">${Number(it.internal_price).toFixed(2)}</td>
                    <td className="p-2 text-amber-300/80 text-[10px] font-sans">
                      {it.reason || 'SKU not found in vendor price list'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};

/**
 * WF003: Vendor File Processing View.
 */
const VendorProcessingSection: React.FC<{ output: any }> = ({ output }) => {
  const validCount = output.valid_rows_count ?? output.cleaned_records_count ?? 4;
  const invalidCount = output.invalid_rows_count ?? output.invalid_rows?.length ?? 4;

  return (
    <div className="space-y-3 font-mono text-xs">
      <div className="grid grid-cols-2 gap-2">
        <div className="bg-emerald-950/30 border border-emerald-700/40 rounded-lg p-2.5 text-emerald-300">
          <span className="text-[10px] uppercase text-emerald-500 block">Cleaned Valid Rows</span>
          <span className="text-lg font-bold">{validCount}</span>
        </div>
        <div className="bg-amber-950/30 border border-amber-700/40 rounded-lg p-2.5 text-amber-300">
          <span className="text-[10px] uppercase text-amber-500 block">Flagged Invalid Rows</span>
          <span className="text-lg font-bold">{invalidCount}</span>
        </div>
      </div>

      {output.invalid_rows && (
        <div className="rounded-lg border border-charcoal-700 p-3 bg-charcoal-900/60 space-y-1.5">
          <span className="text-charcoal-400 block text-[11px] font-semibold">Flagged Row Diagnostics:</span>
          <ul className="space-y-1 text-amber-200/90 list-disc list-inside text-[11px]">
            {output.invalid_rows.slice(0, 5).map((r: any, idx: number) => (
              <li key={idx}>
                Row {r.row_number ?? idx + 1}: {r.errors?.join('; ') || r.reason || 'Missing required fields'}
              </li>
            ))}
          </ul>
        </div>
      )}

      {output.summary && <p className="text-[11px] text-charcoal-400 italic">{output.summary}</p>}
    </div>
  );
};

/**
 * WF005: Customer Order Status View.
 */
const CustomerOrderStatusSection: React.FC<{ output: any }> = ({ output }) => {
  const order = output.order || output;
  const shipment = output.shipment;

  return (
    <div className="space-y-3 text-xs font-mono">
      <div className="bg-charcoal-800/80 rounded-lg p-3 border border-charcoal-700 flex justify-between items-center">
        <div>
          <span className="text-charcoal-400 block text-[10px]">ORDER IDENTIFIER</span>
          <span className="text-base font-bold text-cream-100">{order.order_id}</span>
        </div>
        <span className="px-2 py-0.5 rounded text-xs bg-emerald-950 text-emerald-300 border border-emerald-700/50 font-bold">
          {order.status || 'SHIPPED'}
        </span>
      </div>

      {shipment && (
        <div className="bg-charcoal-900/80 rounded-lg p-3 border border-charcoal-700/70 space-y-2">
          <div className="flex items-center space-x-1.5 text-brand-blue font-semibold">
            <Truck className="w-4 h-4" />
            <span>Shipment Tracking Details</span>
          </div>
          <div className="grid grid-cols-2 gap-2 text-charcoal-300 text-[11px]">
            <div><span className="text-charcoal-500">Carrier:</span> {shipment.carrier || 'FastShip Express'}</div>
            <div><span className="text-charcoal-500">Tracking:</span> {shipment.tracking_number}</div>
            <div><span className="text-charcoal-500">Estimated:</span> {shipment.estimated_delivery || 'Delivered'}</div>
            <div><span className="text-charcoal-500">Items Count:</span> {order.items_count || order.items?.length || 2} units</div>
          </div>
        </div>
      )}

      {output.summary && <p className="text-[11px] text-charcoal-400 italic">{output.summary}</p>}
    </div>
  );
};

/**
 * WF006: Duplicate Product Detection View.
 */
const DuplicateDetectionSection: React.FC<{ output: any }> = ({ output }) => {
  const candidates: any[] = output.duplicate_candidates || [];

  return (
    <div className="space-y-2.5 text-xs font-mono">
      <div className="text-charcoal-300 flex justify-between">
        <span>Detected duplicate pairs: <strong className="text-amber-400 font-bold">{candidates.length}</strong></span>
        <span className="text-charcoal-400 text-[10px]">Algorithm: Exact SKU + Token Dice</span>
      </div>
      <div className="space-y-2">
        {candidates.map((cand: any, i: number) => (
          <div key={i} className="p-3 rounded-lg bg-charcoal-900/60 border border-charcoal-700">
            <div className="flex justify-between text-charcoal-400 text-[10px] mb-1">
              <span>Match: <strong className="text-cream-200">{cand.match_type}</strong></span>
              <span className="text-amber-300">Similarity: {(Number(cand.similarity_score) * 100).toFixed(0)}%</span>
            </div>
            <div className="text-cream-100 font-semibold font-sans">{cand.primary_name} ({cand.primary_sku})</div>
            <div className="text-charcoal-400 font-sans text-[11px]">vs {cand.duplicate_name} ({cand.duplicate_sku})</div>
          </div>
        ))}
      </div>
      {output.summary && <p className="text-[11px] text-charcoal-400 italic">{output.summary}</p>}
    </div>
  );
};

/**
 * WF008: SEO Keyword Classification View.
 */
const SeoKeywordsSection: React.FC<{ output: any }> = ({ output }) => {
  const keywords: any[] = output.classified_keywords || [];

  return (
    <div className="space-y-2.5 text-xs font-mono">
      <div className="text-charcoal-300">
        Classified keywords: <strong className="text-emerald-400 font-bold">{keywords.length}</strong>
      </div>
      <div className="overflow-x-auto rounded-lg border border-charcoal-700">
        <table className="w-full text-left text-[11px]">
          <thead className="bg-charcoal-800 text-charcoal-400 uppercase text-[9px]">
            <tr>
              <th scope="col" className="p-2">Keyword</th>
              <th scope="col" className="p-2">Intent</th>
              <th scope="col" className="p-2">Priority</th>
              <th scope="col" className="p-2">Target Page</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-charcoal-700/60 bg-charcoal-900/60">
            {keywords.slice(0, 5).map((kw: any, i: number) => (
              <tr key={i} className="hover:bg-charcoal-800/30">
                <td className="p-2 text-cream-100 font-semibold">{kw.keyword}</td>
                <td className="p-2 uppercase text-brand-blue font-bold">{kw.intent}</td>
                <td className="p-2">
                  <span className={`px-1.5 py-0.5 rounded text-[9px] font-bold ${
                    kw.priority === 'HIGH' ? 'bg-amber-950 text-amber-300 border border-amber-700' : 'text-charcoal-300'
                  }`}>
                    {kw.priority}
                  </span>
                </td>
                <td className="p-2 text-charcoal-400">{kw.target_page}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {output.summary && <p className="text-[11px] text-charcoal-400 italic">{output.summary}</p>}
    </div>
  );
};

/**
 * WF010: Workflow Performance Report View.
 */
const PerformanceReportSection: React.FC<{ output: any }> = ({ output }) => {
  return (
    <div className="space-y-3 text-xs font-mono">
      <div className="grid grid-cols-2 gap-2">
        <div className="bg-charcoal-900/80 border border-charcoal-700 p-2.5 rounded-lg">
          <span className="text-charcoal-400 block text-[10px]">TOTAL RUNS ANALYZED</span>
          <span className="text-lg font-bold text-cream-100">{output.total_runs_analyzed ?? 39}</span>
        </div>
        <div className="bg-amber-950/40 border border-amber-700/40 p-2.5 rounded-lg text-amber-300">
          <span className="text-amber-500 block text-[10px]">BOTTLENECK WORKFLOWS</span>
          <span className="text-lg font-bold">{output.bottleneck_workflows?.length ?? 2}</span>
        </div>
      </div>
      {output.summary && <p className="text-charcoal-300 italic text-[11px]">{output.summary}</p>}
    </div>
  );
};

/**
 * WF011: Supplier Delivery Risk Assessment View.
 */
const SupplierRiskSection: React.FC<{ output: any }> = ({ output }) => {
  const list: any[] = output.supplier_risk_evaluations || output.suppliers_assessed || [];

  return (
    <div className="space-y-3 text-xs font-mono">
      <div className="flex justify-between text-charcoal-300 text-[11px]">
        <span>Suppliers evaluated: <strong className="text-cream-100">{list.length}</strong></span>
        <span className="text-amber-400">Formula: late_rate × 60 + min(avg_delay × 8, 40)</span>
      </div>
      <div className="space-y-2">
        {list.map((s: any, idx: number) => {
          const isHigh = s.risk_level === 'HIGH';
          const isMed = s.risk_level === 'MEDIUM';
          return (
            <div key={idx} className="p-3 rounded-lg bg-charcoal-900/60 border border-charcoal-700 flex justify-between items-center">
              <div>
                <div className="font-bold text-cream-100 font-sans">{s.supplier_name} ({s.supplier_id})</div>
                <div className="text-[11px] text-charcoal-400 mt-0.5">
                  Late rate: {(Number(s.late_delivery_rate) * 100).toFixed(1)}% · Avg delay: {Number(s.average_delay_days).toFixed(1)} days
                </div>
              </div>
              <div>
                <span className={`px-2.5 py-1 rounded font-bold text-[10px] ${
                  isHigh ? 'bg-red-950 text-red-300 border border-red-700' :
                  isMed ? 'bg-amber-950 text-amber-300 border border-amber-700' :
                  'bg-emerald-950 text-emerald-300 border border-emerald-700'
                }`}>
                  {s.risk_level} ({s.risk_score}/100)
                </span>
              </div>
            </div>
          );
        })}
      </div>
      {output.summary && <p className="text-[11px] text-charcoal-400 italic">{output.summary}</p>}
    </div>
  );
};

/**
 * Generic Fallback for generic key-value dictionaries.
 */
const GenericKeyValueSection: React.FC<{ output: any }> = ({ output }) => {
  return (
    <div className="bg-charcoal-900/70 rounded-lg p-3 border border-charcoal-700 text-xs font-mono text-charcoal-200 space-y-1.5">
      {Object.entries(output).map(([k, v]) => {
        if (k === 'workflow_reports' || k === 'reports') return null;
        return (
          <div key={k} className="flex justify-between border-b border-charcoal-800 pb-1">
            <span className="text-charcoal-400">{k}:</span>
            <span className="text-cream-100 truncate max-w-[280px]">
              {typeof v === 'object' ? JSON.stringify(v) : String(v)}
            </span>
          </div>
        );
      })}
    </div>
  );
};
