import React, { useEffect, useState } from 'react';
import { FileSpreadsheet, ArrowRight } from 'lucide-react';
import { WorkflowDefinition } from '../types/workflow';
import { fetchWorkflows } from '../api/client';

export const WorkbookPage: React.FC = () => {
  const [workflows, setWorkflows] = useState<WorkflowDefinition[]>([]);
  const [selectedWf, setSelectedWf] = useState<WorkflowDefinition | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    fetchWorkflows().then((list) => {
      setWorkflows(list);
      if (list.length > 0) setSelectedWf(list[0]);
      setIsLoading(false);
    });
  }, []);

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      <div className="mb-6">
        <span className="text-xs font-mono font-medium text-brand-blue uppercase tracking-wider">
          Source of Truth Specification
        </span>
        <h1 className="text-3xl font-bold text-charcoal-900 mt-1">
          Excel Workflow Catalog (`data/workflows.xlsx`)
        </h1>
        <div className="mt-3 p-3 bg-cream-200 border border-charcoal-100 rounded-xl text-xs text-charcoal-600 flex items-start space-x-2">
          <FileSpreadsheet className="w-4 h-4 text-emerald-700 flex-shrink-0 mt-0.5" />
          <span>
            <strong>Workbook Integrity:</strong> The Excel workbook is the immutable source of truth for the original workflow definitions. This application reads and displays them; it strictly does not modify the workbook file (verified by persistent SHA-256 checksum).
          </span>
        </div>
      </div>

      {isLoading ? (
        <div className="text-center py-12 font-mono text-sm text-charcoal-400">Loading catalog…</div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Left Column: Workflow List */}
          <div className="space-y-2 md:col-span-1">
            <h3 className="text-xs font-mono uppercase text-charcoal-400 tracking-wider mb-2">
              Catalog Items ({workflows.length})
            </h3>
            <div className="space-y-1.5 max-h-[600px] overflow-y-auto pr-1">
              {workflows.map((wf) => {
                const isSelected = selectedWf?.workflow_id === wf.workflow_id;
                const isExtension = wf.workflow_id === 'WF011';
                return (
                  <button
                    key={wf.workflow_id}
                    onClick={() => setSelectedWf(wf)}
                    className={`w-full text-left p-3 rounded-xl border transition-all text-xs font-mono flex items-center justify-between ${
                      isSelected
                        ? 'bg-charcoal-900 text-cream-50 border-charcoal-900 shadow-sm'
                        : 'bg-cream-50 text-charcoal-800 border-charcoal-100 hover:bg-cream-200'
                    }`}
                  >
                    <div>
                      <div className="font-bold flex items-center space-x-1.5">
                        <span>{wf.workflow_id}</span>
                        {isExtension && (
                          <span className="text-[9px] bg-brand-blue/20 text-brand-blue px-1.5 py-0.2 rounded font-sans uppercase">
                            Extension
                          </span>
                        )}
                      </div>
                      <div className="text-[11px] opacity-80 truncate max-w-[170px] mt-0.5">
                        {wf.workflow_name}
                      </div>
                    </div>
                    <ArrowRight className={`w-3.5 h-3.5 ${isSelected ? 'text-cream-50' : 'text-charcoal-400'}`} />
                  </button>
                );
              })}
            </div>
          </div>

          {/* Right Column: Workflow Detail Specification */}
          <div className="md:col-span-2">
            {selectedWf ? (
              <div className="bg-cream-50 rounded-2xl border border-charcoal-100 p-6 shadow-warm space-y-5">
                <div className="border-b border-charcoal-100 pb-4 flex items-start justify-between">
                  <div>
                    <span className="text-xs font-mono text-brand-blue font-bold">
                      {selectedWf.workflow_id}
                    </span>
                    <h2 className="text-xl font-bold text-charcoal-900 mt-0.5">
                      {selectedWf.workflow_name}
                    </h2>
                  </div>
                  {selectedWf.workflow_id === 'WF011' && (
                    <span className="px-2.5 py-1 rounded text-xs font-mono bg-blue-50 text-brand-blue border border-blue-200">
                      Extension Demo
                    </span>
                  )}
                </div>

                <div className="space-y-4 text-xs font-sans">
                  <div>
                    <span className="font-mono text-[11px] font-bold text-charcoal-500 uppercase block mb-1">
                      Trigger
                    </span>
                    <p className="bg-cream-200 p-2.5 rounded-lg text-charcoal-800 leading-relaxed font-mono">
                      {selectedWf.trigger}
                    </p>
                  </div>

                  <div>
                    <span className="font-mono text-[11px] font-bold text-charcoal-500 uppercase block mb-1">
                      Expected Inputs
                    </span>
                    <p className="bg-cream-200 p-2.5 rounded-lg text-charcoal-800 font-mono">
                      {selectedWf.inputs}
                    </p>
                  </div>

                  <div>
                    <span className="font-mono text-[11px] font-bold text-charcoal-500 uppercase block mb-1">
                      Steps ({selectedWf.parsed_steps.length})
                    </span>
                    <div className="space-y-1.5">
                      {selectedWf.parsed_steps.map((st, i) => (
                        <div key={i} className="flex items-center space-x-2 bg-cream-200/80 p-2 rounded-lg font-mono text-charcoal-800">
                          <span className="w-5 h-5 rounded-full bg-charcoal-900 text-cream-50 flex items-center justify-center text-[10px] font-bold flex-shrink-0">
                            {i + 1}
                          </span>
                          <span>{st}</span>
                        </div>
                      ))}
                    </div>
                  </div>

                  <div>
                    <span className="font-mono text-[11px] font-bold text-charcoal-500 uppercase block mb-1">
                      Decision Logic & Business Rules
                    </span>
                    <p className="bg-cream-200 p-2.5 rounded-lg text-charcoal-800 font-mono leading-relaxed">
                      {selectedWf.decision_logic}
                    </p>
                  </div>

                  <div>
                    <span className="font-mono text-[11px] font-bold text-charcoal-500 uppercase block mb-1">
                      Tools Required
                    </span>
                    <p className="bg-cream-200 p-2.5 rounded-lg text-charcoal-800 font-mono">
                      {selectedWf.tools_required}
                    </p>
                  </div>

                  <div>
                    <span className="font-mono text-[11px] font-bold text-charcoal-500 uppercase block mb-1">
                      Expected Output
                    </span>
                    <p className="bg-cream-200 p-2.5 rounded-lg text-charcoal-800 font-mono">
                      {selectedWf.expected_output}
                    </p>
                  </div>
                </div>
              </div>
            ) : null}
          </div>
        </div>
      )}
    </div>
  );
};
