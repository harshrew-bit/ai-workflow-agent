import React from 'react';

export const DecisionsPage: React.FC = () => {
  const decisions = [
    {
      title: '1. Excel Workbook as Source of Truth',
      decision: 'Ingest workflow schemas (triggers, inputs, steps, decision logic, tools) directly from data/workflows.xlsx at startup.',
      why: 'Business stakeholders manage definitions in spreadsheets. The application acts as an executor rather than altering or inventing business logic.',
      tradeoff: 'Updating workflows requires restarting the process or triggering a catalog reload; changes are not dynamically saved to a remote database.',
    },
    {
      title: '2. LLM Request Interpretation with Hallucination Gates',
      decision: 'Use an LLM router strictly for intent classification and parameter extraction with mandatory registry verification.',
      why: 'Natural language prompts vary widely. An LLM maps conversational requests to catalog IDs without brittle regex.',
      tradeoff: 'LLMs can hallucinate non-existent IDs (e.g. WF099); the router rejects unregistered IDs and requires confidence >= 0.70.',
    },
    {
      title: '3. Deterministic Offline Router for Hermetic Evaluation',
      decision: 'Implement OfflineWorkflowRouter that tokenizes and stems queries against workbook triggers and names when no LLM key is configured.',
      why: 'Enables 100% reproducible testing, CI execution, and recruiter evaluation without third-party API quotas, costs, or network outages.',
      tradeoff: 'Keyword and synonym matching cannot reason about complex conversational metaphors or multi-sentence prompts outside the catalog vocabulary.',
    },
    {
      title: '4. Exact Decimal Arithmetic for Price Audits (WF002)',
      decision: 'Use Python Decimal arithmetic end-to-end for price parsing, percentage difference calculations, and strictly greater than 10% thresholding.',
      why: 'Standard IEEE 754 floats introduce precision errors (e.g., 0.1 + 0.2 != 0.3) that misclassify boundary products around financial thresholds.',
      tradeoff: 'Slightly more verbose model definitions requiring Decimal to float serialization at API boundaries.',
    },
    {
      title: '5. Clarification Over Guessing Missing Inputs',
      decision: 'Return status NEEDS_CLARIFICATION (exit code 4) instead of inventing defaults when mandatory inputs (like product_name in WF004) are absent.',
      why: 'In enterprise automation, generating or executing actions with fabricated data leads to erroneous inventory orders or incorrect briefs.',
      tradeoff: 'The agent will not auto-generate placeholder copy or assume missing fields without explicit user input.',
    },
    {
      title: '6. Structured Reports and Documented Exit Codes',
      decision: 'Enforce ExecutionReport contract with explicit statuses (success=0, failed=1, partial_failure=3, needs_clarification=4).',
      why: 'Downstream pipelines, CI scripts, and monitoring tools rely on deterministic process exit codes and stable JSON output schemas.',
      tradeoff: 'CLI and API adapters must strictly conform to the 4-status lifecycle rather than returning generic HTTP 200/500 responses.',
    },
    {
      title: '7. Provider Abstraction with Sanitized Error Handling',
      decision: 'Isolate external LLM interactions behind LLMProvider, sanitizing raw exception strings to prevent secret and endpoint leakage.',
      why: 'Network failures or authorization rejections must never leak API keys, authorization headers, or internal file paths to stdout or clients.',
      tradeoff: 'Debugging remote provider errors requires checking sanitized error categories rather than dumping full HTTP debug traces.',
    },
    {
      title: '8. Forced Routing for Boundary & Extension Testing',
      decision: 'Support --mock-route / forced_workflow_id with prominent labeling and mismatch advisory warnings.',
      why: 'Allows engineers to test specific workflow tool execution and boundary logic deterministically regardless of prompt phrasing.',
      tradeoff: 'Must be visibly labelled so evaluators do not confuse forced execution with autonomous LLM routing decisions.',
    },
    {
      title: '9. Reusable Orchestration and Zero-Engine-Modification Extensibility',
      decision: 'Implement GenericWorkflowEngine that executes any workflow purely from step names and registered tool bindings.',
      why: 'New workflows (proven by WF011) can be registered into the system without changing a single line of core orchestrator or engine code.',
      tradeoff: 'Requires disciplined registration across the 6 extension points (definition, tools, tool registry, step resolver, CLI/API, tests).',
    },
  ];

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      <div className="mb-8">
        <span className="text-xs font-mono font-medium text-brand-blue uppercase tracking-wider">
          Engineering Rationale
        </span>
        <h1 className="text-3xl font-bold text-charcoal-900 mt-1">
          Technical Decisions & Architectural Trade-offs
        </h1>
        <p className="text-sm text-charcoal-500 mt-2 max-w-3xl">
          Honest engineering compromises and verified architectural patterns implemented across the repository.
        </p>
      </div>

      <div className="space-y-5">
        {decisions.map((d) => (
          <div key={d.title} className="bg-cream-50 rounded-2xl p-6 border border-charcoal-100 shadow-warm">
            <h3 className="text-base font-bold text-charcoal-900 mb-3">{d.title}</h3>
            <div className="space-y-3 text-xs sm:text-sm">
              <div className="flex items-start space-x-2">
                <span className="font-mono text-xs font-bold text-brand-blue uppercase w-20 flex-shrink-0">Decision:</span>
                <span className="text-charcoal-800">{d.decision}</span>
              </div>
              <div className="flex items-start space-x-2">
                <span className="font-mono text-xs font-bold text-emerald-700 uppercase w-20 flex-shrink-0">Why:</span>
                <span className="text-charcoal-600">{d.why}</span>
              </div>
              <div className="flex items-start space-x-2">
                <span className="font-mono text-xs font-bold text-amber-700 uppercase w-20 flex-shrink-0">Trade-off:</span>
                <span className="text-charcoal-600">{d.tradeoff}</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
