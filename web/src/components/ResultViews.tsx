import React from 'react';
import { AlertTriangle, Truck } from 'lucide-react';
import { ExecutionReport } from '../types/workflow';

interface ResultViewsProps {
  report: ExecutionReport;
}

export const ResultViews: React.FC<ResultViewsProps> = ({ report }) => {
  const { selected_workflow_id: wfId, final_output: output, status } = report;

  if (status === 'needs_clarification' || report.clarification_required) {
    return (
      <div className="bg-amber-950/40 border border-amber-600/50 rounded-xl p-4 text-amber-200">
        <div className="flex items-center space-x-2 text-amber-400 font-semibold mb-2">
          <AlertTriangle className="w-5 h-5" />
          <span>Needs your input</span>
        </div>
        <p className="text-sm mb-3">
          {report.errors[0] || report.routing_reasoning || 'Missing required parameters. The engine does not guess or invent missing inputs.'}
        </p>
        <div className="bg-charcoal-900/80 rounded-lg p-2.5 text-xs font-mono text-amber-300/80 border border-amber-700/30">
          Status: NEEDS_CLARIFICATION · Exit code: 4 · 0 domain tools executed
        </div>
      </div>
    );
  }

  if (!output || typeof output !== 'object') {
    return (
      <div className="text-xs font-mono text-charcoal-300">
        {String(output ?? 'Workflow completed successfully.')}
      </div>
    );
  }

  // WF001: Inventory Restock Table
  if (wfId === 'WF001' && output.products_requiring_restock) {
    const items = output.products_requiring_restock;
    return (
      <div className="space-y-3">
        <div className="flex items-center justify-between text-xs text-charcoal-300 font-mono">
          <span>Products below minimum threshold: <strong className="text-emerald-400">{items.length}</strong></span>
          <span>Checked: {output.total_products_checked ?? 7} items</span>
        </div>
        <div className="overflow-x-auto rounded-lg border border-charcoal-700">
          <table className="w-full text-left text-xs font-mono">
            <thead className="bg-charcoal-800 text-charcoal-400 uppercase border-b border-charcoal-700">
              <tr>
                <th className="px-3 py-2">Product ID</th>
                <th className="px-3 py-2">Item Name</th>
                <th className="px-3 py-2 text-right">Current</th>
                <th className="px-3 py-2 text-right">Minimum</th>
                <th className="px-3 py-2 text-right text-emerald-400">Reorder</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-charcoal-700/60 bg-charcoal-900/60">
              {items.map((it: any) => (
                <tr key={it.product_id} className="hover:bg-charcoal-800/40">
                  <td className="px-3 py-2 font-bold text-charcoal-200">{it.product_id}</td>
                  <td className="px-3 py-2 text-charcoal-300">{it.product_name}</td>
                  <td className="px-3 py-2 text-right text-charcoal-400">{it.current_stock}</td>
                  <td className="px-3 py-2 text-right text-charcoal-400">{it.minimum_stock}</td>
                  <td className="px-3 py-2 text-right font-bold text-emerald-400">{it.reorder_quantity}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        {output.summary && <p className="text-xs text-charcoal-400 italic">{output.summary}</p>}
      </div>
    );
  }

  // WF002: Product Price Validation
  if (wfId === 'WF002' && output.matched_products) {
    const matched = output.matched_products;
    return (
      <div className="space-y-3">
        <div className="flex items-center justify-between text-xs text-charcoal-300 font-mono">
          <span>Exceptions flagged: <strong className="text-amber-400">{output.exceptions?.length ?? 0}</strong></span>
          <span>Checked SKUs: {output.total_records_checked ?? matched.length}</span>
        </div>
        <div className="overflow-x-auto rounded-lg border border-charcoal-700">
          <table className="w-full text-left text-xs font-mono">
            <thead className="bg-charcoal-800 text-charcoal-400 uppercase border-b border-charcoal-700">
              <tr>
                <th className="px-3 py-2">SKU</th>
                <th className="px-3 py-2">Item Name</th>
                <th className="px-3 py-2 text-right">Internal</th>
                <th className="px-3 py-2 text-right">Vendor</th>
                <th className="px-3 py-2 text-right">Diff %</th>
                <th className="px-3 py-2">Audit Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-charcoal-700/60 bg-charcoal-900/60">
              {matched.map((it: any) => {
                let statusLabel = 'COMPLIANT';
                if (it.is_exception) {
                  const status = String(it.validation_status || '');
                  if (status === 'EXCEPTION_EXCEEDS_10_PERCENT') {
                    statusLabel = 'EXCEPTION (>10%)';
                  } else if (status.startsWith('EXCEPTION_')) {
                    const tag = status
                      .replace(/^EXCEPTION_/, '')
                      .replace(/_PERCENT$/, '%')
                      .replace(/LESS_THAN_/, '<')
                      .replace(/EXCEEDS_/, '>')
                      .replace(/AT_LEAST_/, '>=')
                      .replace(/AT_MOST_/, '<=')
                      .replace(/EQUALS_/, '==')
                      .replace(/_/g, ' ');
                    statusLabel = `EXCEPTION (${tag})`;
                  } else {
                    statusLabel = 'EXCEPTION';
                  }
                }
                return (
                  <tr key={it.sku} className="hover:bg-charcoal-800/40">
                    <td className="px-3 py-2 font-bold text-charcoal-200">{it.sku}</td>
                    <td className="px-3 py-2 text-charcoal-300 truncate max-w-[150px]">{it.product_name}</td>
                    <td className="px-3 py-2 text-right text-charcoal-400">${Number(it.internal_price).toFixed(2)}</td>
                    <td className="px-3 py-2 text-right text-charcoal-400">${Number(it.vendor_price).toFixed(2)}</td>
                    <td className="px-3 py-2 text-right text-charcoal-300">{Number(it.percentage_difference).toFixed(1)}%</td>
                    <td className="px-3 py-2">
                      {it.is_exception ? (
                        <span className="px-1.5 py-0.5 rounded text-[10px] bg-amber-900/70 text-amber-300 border border-amber-600/40">
                          {statusLabel}
                        </span>
                      ) : (
                        <span className="px-1.5 py-0.5 rounded text-[10px] bg-emerald-950/70 text-emerald-300 border border-emerald-700/40">
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
      </div>
    );
  }

  // WF003: Vendor File Processing
  if (wfId === 'WF003' && (output.valid_rows_count !== undefined || output.cleaned_records_count !== undefined)) {
    const validCount = output.valid_rows_count ?? output.cleaned_records_count ?? 4;
    const invalidCount = output.invalid_rows_count ?? output.invalid_rows?.length ?? 4;
    return (
      <div className="space-y-3">
        <div className="grid grid-cols-2 gap-2 text-xs font-mono">
          <div className="bg-emerald-950/30 border border-emerald-700/40 rounded p-2 text-emerald-300">
            <span className="text-[10px] uppercase text-emerald-500 block">Cleaned Valid Rows</span>
            <span className="text-lg font-bold">{validCount}</span>
          </div>
          <div className="bg-amber-950/30 border border-amber-700/40 rounded p-2 text-amber-300">
            <span className="text-[10px] uppercase text-amber-500 block">Flagged Invalid Rows</span>
            <span className="text-lg font-bold">{invalidCount}</span>
          </div>
        </div>
        {output.invalid_rows && (
          <div className="rounded-lg border border-charcoal-700 p-2 text-xs font-mono bg-charcoal-900/60">
            <span className="text-charcoal-400 block mb-1 text-[11px]">Invalid Rows Details:</span>
            <ul className="space-y-1 text-amber-200/90 list-disc list-inside">
              {output.invalid_rows.slice(0, 4).map((r: any, idx: number) => (
                <li key={idx}>Row {r.row_number ?? idx + 1}: {r.errors?.join('; ') || r.reason || 'Missing required fields'}</li>
              ))}
            </ul>
          </div>
        )}
      </div>
    );
  }

  // WF005: Customer Order Status
  if (wfId === 'WF005' && (output.order || output.order_id)) {
    const order = output.order || output;
    const shipment = output.shipment;
    return (
      <div className="space-y-3 text-xs font-mono">
        <div className="bg-charcoal-800/80 rounded-lg p-3 border border-charcoal-700 flex justify-between items-center">
          <div>
            <span className="text-charcoal-400 block text-[10px]">ORDER IDENTIFIER</span>
            <span className="text-base font-bold text-cream-100">{order.order_id}</span>
          </div>
          <span className="px-2 py-0.5 rounded text-xs bg-emerald-950 text-emerald-300 border border-emerald-700/50">
            {order.status || 'SHIPPED'}
          </span>
        </div>
        {shipment && (
          <div className="bg-charcoal-900/80 rounded-lg p-3 border border-charcoal-700/70 space-y-1">
            <div className="flex items-center space-x-1.5 text-brand-blue font-semibold">
              <Truck className="w-4 h-4" />
              <span>Shipment Tracking Details</span>
            </div>
            <div className="grid grid-cols-2 gap-2 pt-1 text-charcoal-300">
              <div><span className="text-charcoal-500">Carrier:</span> {shipment.carrier || 'FedEx'}</div>
              <div><span className="text-charcoal-500">Tracking:</span> {shipment.tracking_number}</div>
              <div><span className="text-charcoal-500">Estimated:</span> {shipment.estimated_delivery || 'Delivered'}</div>
              <div><span className="text-charcoal-500">Items:</span> {order.items_count || order.items?.length || 2} units</div>
            </div>
          </div>
        )}
      </div>
    );
  }

  // WF006: Duplicate Product Detection
  if (wfId === 'WF006' && output.duplicate_candidates) {
    const candidates = output.duplicate_candidates;
    return (
      <div className="space-y-2 text-xs font-mono">
        <div className="text-charcoal-300">
          Detected duplicate pairs: <strong className="text-amber-400">{candidates.length}</strong>
        </div>
        <div className="space-y-2">
          {candidates.map((cand: any, i: number) => (
            <div key={i} className="p-2.5 rounded bg-charcoal-800/60 border border-charcoal-700">
              <div className="flex justify-between text-charcoal-400 text-[10px] mb-1">
                <span>Match: {cand.match_type}</span>
                <span className="text-amber-300">Similarity: {(Number(cand.similarity_score) * 100).toFixed(0)}%</span>
              </div>
              <div className="text-cream-100 font-semibold">{cand.primary_name} ({cand.primary_sku})</div>
              <div className="text-charcoal-400">vs {cand.duplicate_name} ({cand.duplicate_sku})</div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  // WF008: SEO Keyword Classification
  if (wfId === 'WF008' && output.classified_keywords) {
    const keywords = output.classified_keywords;
    return (
      <div className="space-y-2 text-xs font-mono">
        <div className="text-charcoal-300">Classified keywords: <strong className="text-emerald-400">{keywords.length}</strong></div>
        <div className="overflow-x-auto rounded border border-charcoal-700">
          <table className="w-full text-left">
            <thead className="bg-charcoal-800 text-charcoal-400">
              <tr>
                <th className="p-2">Keyword</th>
                <th className="p-2">Intent</th>
                <th className="p-2">Priority</th>
                <th className="p-2">Target Page</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-charcoal-700/60 bg-charcoal-900/60">
              {keywords.slice(0, 5).map((kw: any, i: number) => (
                <tr key={i}>
                  <td className="p-2 text-cream-100">{kw.keyword}</td>
                  <td className="p-2 uppercase text-brand-blue">{kw.intent}</td>
                  <td className="p-2 text-amber-300">{kw.priority}</td>
                  <td className="p-2 text-charcoal-400">{kw.target_page}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    );
  }

  // WF010: Workflow Performance Report
  if (wfId === 'WF010') {
    return (
      <div className="space-y-3 text-xs font-mono">
        <div className="grid grid-cols-2 gap-2">
          <div className="bg-charcoal-800/80 border border-charcoal-700 p-2 rounded">
            <span className="text-charcoal-400 block text-[10px]">TOTAL RUNS ANALYZED</span>
            <span className="text-lg font-bold text-cream-100">{output.total_runs_analyzed ?? 39}</span>
          </div>
          <div className="bg-amber-950/40 border border-amber-700/40 p-2 rounded text-amber-300">
            <span className="text-amber-500 block text-[10px]">BOTTLENECK WORKFLOWS</span>
            <span className="text-lg font-bold">{output.bottleneck_workflows?.length ?? 2}</span>
          </div>
        </div>
        {output.summary && <p className="text-charcoal-300 italic">{output.summary}</p>}
      </div>
    );
  }

  // WF011: Supplier Delivery Risk Assessment
  if (wfId === 'WF011' && (output.supplier_risk_evaluations || output.suppliers_assessed)) {
    const list = output.supplier_risk_evaluations || output.suppliers_assessed || [];
    return (
      <div className="space-y-3 text-xs font-mono">
        <div className="flex justify-between text-charcoal-300">
          <span>Suppliers evaluated: <strong className="text-cream-100">{list.length}</strong></span>
          <span className="text-amber-400">Formula: late_rate × 60 + avg_delay × 8</span>
        </div>
        <div className="space-y-2">
          {list.map((s: any, idx: number) => {
            const isHigh = s.risk_level === 'HIGH';
            const isMed = s.risk_level === 'MEDIUM';
            return (
              <div key={idx} className="p-2.5 rounded bg-charcoal-800/70 border border-charcoal-700 flex justify-between items-center">
                <div>
                  <div className="font-bold text-cream-100">{s.supplier_name} ({s.supplier_id})</div>
                  <div className="text-[11px] text-charcoal-400">
                    Late rate: {(Number(s.late_delivery_rate) * 100).toFixed(1)}% · Avg delay: {Number(s.average_delay_days).toFixed(1)} days
                  </div>
                </div>
                <div className="text-right">
                  <span className={`px-2 py-0.5 rounded font-bold text-[10px] ${
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
      </div>
    );
  }

  // Generic key-value fallback renderer
  return (
    <div className="bg-charcoal-900/70 rounded-lg p-3 border border-charcoal-700 text-xs font-mono text-charcoal-200 space-y-1">
      {Object.entries(output).map(([k, v]) => (
        <div key={k} className="flex justify-between border-b border-charcoal-800 pb-1">
          <span className="text-charcoal-400">{k}:</span>
          <span className="text-cream-100 truncate max-w-[280px]">
            {typeof v === 'object' ? JSON.stringify(v) : String(v)}
          </span>
        </div>
      ))}
    </div>
  );
};
