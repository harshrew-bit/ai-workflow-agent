import React from 'react';
import { ArrowDown, ShieldAlert } from 'lucide-react';

export const ArchitecturePage: React.FC = () => {
  const stages = [
    {
      step: '01',
      title: 'Natural-Language Request',
      module: 'CLI (app/main.py) or API (api/main.py)',
      description: 'Accepts raw natural-language prompt without hardcoded assumptions or artificial path parameters.',
    },
    {
      step: '02',
      title: 'Workflow Router',
      module: 'app/agent/router.py & app/agent/offline_router.py',
      description: 'Routes prompt to a catalog workflow. Uses Gemini 1.5 Flash if API key is configured; otherwise uses deterministic tokenized trigger matching.',
      hasBranch: true,
      branchTitle: 'Low Confidence / Off-Topic Branch',
      branchDesc: 'If confidence < 0.70 or off-topic (e.g., "weather in Paris"), halts with status NEEDS_CLARIFICATION and exit code 4 without executing tools.',
    },
    {
      step: '03',
      title: 'Workflow Catalog Ingestion',
      module: 'app/registry/registry.py',
      description: 'Ingests definitions directly from data/workflows.xlsx at startup. Validates that the selected workflow ID actually exists in the catalog.',
    },
    {
      step: '04',
      title: 'Application Orchestrator',
      module: 'app/orchestrator.py',
      description: 'Coordinates end-to-end lifecycle: drops untrusted LLM-extracted filesystem paths, injects safe server defaults, and passes workflow to engine.',
    },
    {
      step: '05',
      title: 'Generic Execution Engine',
      module: 'app/engine/base.py',
      description: 'Zero-workflow-specific code. Linearly executes steps through registered tools, propagating state via ExecutionContext.',
    },
    {
      step: '06',
      title: 'Configurable Step Resolver',
      module: 'app/engine/resolver.py',
      description: 'Maps human-readable step strings (e.g., "Load inventory", "Compare current stock") into registered tool names.',
    },
    {
      step: '07',
      title: 'Domain Business Tools',
      module: 'app/tools/*.py',
      description: 'Specialized Python classes inheriting from BaseTool. Executes deterministic logic (exact Decimal comparisons, CSV normalization, deduplication).',
    },
    {
      step: '08',
      title: 'Structured Execution Report',
      module: 'app/models/report.py',
      description: 'Produces final machine-readable ExecutionReport containing status, step timeline, structured final output, routing metadata, and warnings.',
    },
  ];

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      <div className="mb-8 text-center sm:text-left">
        <span className="text-xs font-mono font-medium text-brand-blue uppercase tracking-wider">
          System Design & Component Pipeline
        </span>
        <h1 className="text-3xl font-bold text-charcoal-900 mt-1">
          Execution Engine Architecture
        </h1>
        <p className="text-sm text-charcoal-500 mt-2 max-w-3xl">
          The application strictly decouples business workflow definitions (stored in Excel) from the execution engine, router, and registered domain tools.
        </p>
      </div>

      {/* Interactive Flow */}
      <div className="space-y-4">
        {stages.map((st, idx) => (
          <React.Fragment key={st.step}>
            <div className="bg-cream-50 rounded-xl p-5 border border-charcoal-100 shadow-warm hover:border-brand-blue/40 transition-all">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-2">
                <div className="flex items-center space-x-3">
                  <span className="w-7 h-7 rounded-lg bg-charcoal-900 text-cream-50 text-xs font-mono font-bold flex items-center justify-center">
                    {st.step}
                  </span>
                  <h3 className="font-bold text-base text-charcoal-900">
                    {st.title}
                  </h3>
                </div>
                <code className="text-[11px] font-mono bg-cream-200 text-charcoal-700 px-2 py-0.5 rounded border border-charcoal-200/60">
                  {st.module}
                </code>
              </div>
              <p className="text-xs sm:text-sm text-charcoal-600 leading-relaxed pl-10">
                {st.description}
              </p>

              {/* Clarification Side Branch */}
              {st.hasBranch && (
                <div className="mt-3 ml-10 p-3 rounded-lg bg-amber-50 border border-amber-200 text-amber-900 text-xs flex items-start space-x-2">
                  <ShieldAlert className="w-4 h-4 text-amber-600 flex-shrink-0 mt-0.5" />
                  <div>
                    <strong className="font-semibold">{st.branchTitle}: </strong>
                    <span>{st.branchDesc}</span>
                  </div>
                </div>
              )}
            </div>

            {idx < stages.length - 1 && (
              <div className="flex justify-center">
                <ArrowDown className="w-4 h-4 text-charcoal-300" />
              </div>
            )}
          </React.Fragment>
        ))}
      </div>
    </div>
  );
};
