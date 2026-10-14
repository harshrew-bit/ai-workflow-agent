import React from 'react';
import { Terminal, CheckCircle2, XCircle, ShieldAlert, Loader2, AlertTriangle, Bookmark } from 'lucide-react';
import { ExecutionReport, AppExecutionState } from '../types/workflow';
import { ResultViews } from './ResultViews';

interface ExecutionTraceProps {
  report: ExecutionReport | null;
  executionState: AppExecutionState;
  isLoading?: boolean;
  isSavedExample?: boolean;
  savedExampleTitle?: string;
  errorMessage?: string | null;
  isDemoFallback?: boolean;
}

export const ExecutionTrace: React.FC<ExecutionTraceProps> = ({
  report,
  executionState,
  isLoading = false,
  isSavedExample = false,
  savedExampleTitle,
  errorMessage,
  isDemoFallback = false,
}) => {
  const isRunning = executionState === 'running' || isLoading;
  const isIdle = executionState === 'idle' || (!report && !isRunning && executionState !== 'error');
  const isError = executionState === 'error';

  // 1. Loading State (Running)
  if (isRunning) {
    return (
      <div
        role="status"
        aria-live="polite"
        className="bg-charcoal-800 rounded-2xl text-cream-50 shadow-warm-lg border border-charcoal-700/80 overflow-hidden font-sans"
      >
        <div className="flex items-center justify-between px-5 py-3 border-b border-charcoal-700/80 bg-charcoal-900/60">
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 rounded-full bg-rose-500/80" />
            <div className="w-3 h-3 rounded-full bg-amber-500/80" />
            <div className="w-3 h-3 rounded-full bg-emerald-500/80" />
            <span className="text-xs font-mono text-charcoal-400 ml-2 tracking-wide">
              workflow_execution.trace
            </span>
          </div>
          <span className="inline-flex items-center space-x-1.5 px-2.5 py-0.5 rounded text-[11px] font-mono font-semibold tracking-wider bg-brand-blue/30 text-blue-300 border border-brand-blue/50 animate-pulse">
            <Loader2 className="w-3 h-3 animate-spin text-blue-300" />
            <span>RUNNING</span>
          </span>
        </div>

        <div className="p-8 text-center space-y-4">
          <Loader2 className="w-8 h-8 text-brand-blue animate-spin mx-auto" />
          <h3 className="text-base font-semibold text-cream-100">Executing Workflow Request</h3>
          <p className="text-xs text-charcoal-400 max-w-md mx-auto leading-relaxed font-mono">
            Submitting request to FastAPI backend engine...
            <br />
            Evaluating router rules and executing sequential step domain tools.
          </p>
        </div>
      </div>
    );
  }

  // 2. Idle State: Clean three-section panel awaiting submission
  if (isIdle) {
    return (
      <div className="bg-charcoal-800 rounded-2xl text-cream-50 shadow-warm-lg border border-charcoal-700/80 overflow-hidden font-sans">
        {/* Titlebar */}
        <div className="flex items-center justify-between px-5 py-3 border-b border-charcoal-700/80 bg-charcoal-900/60">
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 rounded-full bg-charcoal-600" />
            <div className="w-3 h-3 rounded-full bg-charcoal-600" />
            <div className="w-3 h-3 rounded-full bg-charcoal-600" />
            <span className="text-xs font-mono text-charcoal-400 ml-2 tracking-wide">
              workflow_execution.trace
            </span>
          </div>
          <span className="px-2.5 py-0.5 rounded text-[11px] font-mono font-medium tracking-wider bg-charcoal-800 text-charcoal-400 border border-charcoal-700">
            IDLE
          </span>
        </div>

        {/* 3 Existing Sections in Idle State */}
        <div className="p-5 sm:p-6 space-y-5">
          {/* 01 — Routing Decision (Idle) */}
          <section className="bg-charcoal-700/50 rounded-xl p-4 border border-charcoal-700/70">
            <div className="flex items-center justify-between mb-2 border-b border-charcoal-600/40 pb-2">
              <span className="text-[11px] font-mono tracking-wider text-charcoal-400 uppercase font-semibold">
                01 — Routing Decision
              </span>
              <span className="text-[10px] font-mono text-charcoal-500 uppercase">
                Awaiting Request
              </span>
            </div>
            <p className="text-xs font-mono text-charcoal-400 leading-relaxed">
              No request submitted yet. The router will evaluate your natural-language intent against registered Excel workflows.
            </p>
          </section>

          {/* 02 — Step Execution Timeline (Idle) */}
          <section className="bg-charcoal-700/50 rounded-xl p-4 border border-charcoal-700/70">
            <div className="flex items-center justify-between mb-2 border-b border-charcoal-600/40 pb-2">
              <span className="text-[11px] font-mono tracking-wider text-charcoal-400 uppercase font-semibold">
                02 — Step Execution Timeline
              </span>
              <span className="text-[10px] font-mono text-charcoal-500 uppercase">
                0 Steps Run
              </span>
            </div>
            <p className="text-xs font-mono text-charcoal-400 leading-relaxed">
              No domain tools executed. Resolved workflow steps and their execution outputs will appear sequentially here.
            </p>
          </section>

          {/* 03 — Final Structured Result (Idle with required message) */}
          <section className="bg-charcoal-700/50 rounded-xl p-4 border border-charcoal-700/70 text-center py-6">
            <div className="flex items-center justify-between mb-4 border-b border-charcoal-600/40 pb-2 text-left">
              <span className="text-[11px] font-mono tracking-wider text-charcoal-400 uppercase font-semibold">
                03 — Final Structured Result
              </span>
              <span className="text-[10px] font-mono text-charcoal-500 uppercase">
                Pending
              </span>
            </div>
            <Terminal className="w-8 h-8 text-charcoal-500 mx-auto mb-2 opacity-60" />
            <p className="text-sm font-medium text-cream-200">
              Your execution trace will appear here after you submit a request.
            </p>
            <p className="text-xs text-charcoal-400 mt-1 max-w-md mx-auto">
              Type a prompt above or click an example scenario, then press <strong>Run workflow</strong> to trace execution.
            </p>
          </section>
        </div>
      </div>
    );
  }

  // 3. Error State (Network or Execution Failure without fabricated report)
  if (isError && !report) {
    return (
      <div className="bg-charcoal-800 rounded-2xl text-cream-50 shadow-warm-lg border border-charcoal-700/80 overflow-hidden font-sans">
        <div className="flex items-center justify-between px-5 py-3 border-b border-charcoal-700/80 bg-charcoal-900/60">
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 rounded-full bg-rose-500" />
            <div className="w-3 h-3 rounded-full bg-charcoal-600" />
            <div className="w-3 h-3 rounded-full bg-charcoal-600" />
            <span className="text-xs font-mono text-charcoal-400 ml-2 tracking-wide">
              workflow_execution.trace
            </span>
          </div>
          <span className="px-2.5 py-0.5 rounded text-[11px] font-mono font-semibold tracking-wider bg-rose-950 text-rose-300 border border-rose-700/60">
            ERROR
          </span>
        </div>

        <div className="p-6 text-center space-y-3">
          <XCircle className="w-8 h-8 text-rose-400 mx-auto" />
          <h3 className="text-base font-semibold text-rose-200">Execution Error</h3>
          <p className="text-xs text-charcoal-300 font-mono max-w-lg mx-auto bg-charcoal-900/80 p-3 rounded-lg border border-rose-900/40 text-left">
            {errorMessage || 'An error occurred during workflow execution.'}
          </p>
        </div>
      </div>
    );
  }

  // 4. Executed Report (Live or Explicit Saved Example)
  if (!report) return null;

  const {
    selected_workflow_id: wfId,
    selected_workflow_name: wfName,
    routing_mode: mode,
    routing_confidence: confidence,
    routing_reasoning: reasoning,
    status,
    steps,
    warnings,
    exit_code,
  } = report;

  const isSuccess = status === 'success';
  const isClarification = status === 'needs_clarification';
  const isForced = mode === 'forced';
  const isLlm = mode === 'llm';

  return (
    <div className="bg-charcoal-800 rounded-2xl text-cream-50 shadow-warm-lg border border-charcoal-700/80 overflow-hidden font-sans">
      {/* Window Titlebar */}
      <div className="flex items-center justify-between px-5 py-3 border-b border-charcoal-700/80 bg-charcoal-900/60">
        <div className="flex items-center space-x-2">
          <div className="w-3 h-3 rounded-full bg-rose-500/80" />
          <div className="w-3 h-3 rounded-full bg-amber-500/80" />
          <div className="w-3 h-3 rounded-full bg-emerald-500/80" />
          <span className="text-xs font-mono text-charcoal-400 ml-2 tracking-wide">
            workflow_execution.trace
          </span>
        </div>
        <div className="flex items-center space-x-2">
          {(isSavedExample || isDemoFallback) && (
            <span className="inline-flex items-center space-x-1 px-2 py-0.5 rounded text-[10px] font-mono font-medium bg-amber-900/70 text-amber-300 border border-amber-700/70">
              <Bookmark className="w-3 h-3" />
              <span>SAVED EXAMPLE</span>
            </span>
          )}
          <span
            className={`px-2.5 py-0.5 rounded text-[11px] font-mono font-semibold tracking-wider ${
              isSuccess
                ? 'bg-emerald-950 text-emerald-300 border border-emerald-700/60'
                : isClarification
                ? 'bg-amber-950 text-amber-300 border border-amber-700/60'
                : 'bg-rose-950 text-rose-300 border border-rose-700/60'
            }`}
          >
            {status.toUpperCase()}
          </span>
          {exit_code !== undefined && (
            <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-charcoal-700 text-charcoal-300">
              EXIT {exit_code}
            </span>
          )}
        </div>
      </div>

      {/* Saved Example Notification Banner */}
      {(isSavedExample || isDemoFallback) && (
        <div className="bg-amber-950/40 border-b border-amber-700/40 px-5 py-2 flex items-center space-x-2 text-xs font-mono text-amber-200">
          <Bookmark className="w-3.5 h-3.5 text-amber-400 flex-shrink-0" />
          <span>
            <strong>Recorded Result:</strong> This is a verified saved execution report
            {savedExampleTitle ? ` (${savedExampleTitle})` : ''} from <code>examples/output/</code>, not a newly executed request.
          </span>
        </div>
      )}

      {/* Advisory Warnings & Forced Route Warning */}
      {isForced && (
        <div className="bg-amber-950/60 border-b border-amber-600/40 px-5 py-2.5 flex items-start space-x-2 text-xs font-mono text-amber-200">
          <AlertTriangle className="w-4 h-4 text-amber-400 flex-shrink-0 mt-0.5" />
          <div>
            <strong>FORCED ROUTE WARNING:</strong> This workflow was forced via operational override. This is not an automatic AI routing decision.
          </div>
        </div>
      )}

      {warnings && warnings.length > 0 && (
        <div className="bg-amber-950/60 border-b border-amber-600/40 px-5 py-2.5 flex items-start space-x-2 text-xs font-mono text-amber-200">
          <ShieldAlert className="w-4 h-4 text-amber-400 flex-shrink-0 mt-0.5" />
          <div>
            {warnings.map((warn, i) => (
              <p key={i}>{warn}</p>
            ))}
          </div>
        </div>
      )}

      {/* 3 Main Sections */}
      <div className="p-5 sm:p-6 space-y-6">
        {/* 01 — ROUTING CARD */}
        <section className="bg-charcoal-700/60 rounded-xl p-4 border border-charcoal-700">
          <div className="flex items-center justify-between mb-3 border-b border-charcoal-600/50 pb-2">
            <span className="text-[11px] font-mono tracking-wider text-charcoal-400 uppercase font-semibold">
              01 — Routing Decision
            </span>
            <div className="flex items-center space-x-2">
              <span
                className={`px-2 py-0.5 rounded text-[10px] font-mono uppercase font-bold ${
                  isForced
                    ? 'bg-amber-900/60 text-amber-300 border border-amber-600/40'
                    : isLlm
                    ? 'bg-brand-blue/30 text-blue-300 border border-brand-blue/50'
                    : 'bg-charcoal-800 text-charcoal-300 border border-charcoal-600'
                }`}
              >
                {isForced ? 'FORCED ROUTE' : isLlm ? 'LIVE LLM' : 'OFFLINE ROUTER'}
              </span>
              {typeof confidence === 'number' && (
                <span className="text-xs font-mono text-charcoal-400">
                  Confidence: <strong className="text-cream-100">{confidence.toFixed(2)}</strong>
                </span>
              )}
            </div>
          </div>

          <div className="space-y-2 text-xs font-mono">
            <div className="flex items-baseline space-x-2">
              <span className="text-charcoal-400">Selected Workflow:</span>
              <span className="font-bold text-sm text-cream-50">
                {wfId ? `${wfId} — ${wfName}` : 'None (No workflow matched)'}
              </span>
            </div>
            <div className="text-charcoal-300 bg-charcoal-800/80 p-2.5 rounded border border-charcoal-700/80 leading-relaxed">
              <span className="text-charcoal-400">Reasoning: </span>
              {reasoning || 'No router reasoning provided.'}
            </div>
          </div>
        </section>

        {/* 02 — EXECUTION STEPS TIMELINE */}
        <section className="bg-charcoal-700/60 rounded-xl p-4 border border-charcoal-700">
          <div className="flex items-center justify-between mb-3 border-b border-charcoal-600/50 pb-2">
            <span className="text-[11px] font-mono tracking-wider text-charcoal-400 uppercase font-semibold">
              02 — Step Execution Timeline
            </span>
            <span className="text-xs font-mono text-charcoal-400">
              {steps.length} Step(s) Run
            </span>
          </div>

          {steps.length === 0 ? (
            <div className="text-xs font-mono text-charcoal-400 p-3 bg-charcoal-800/60 rounded border border-charcoal-700/50">
              0 domain tools executed (clarification required before step execution).
            </div>
          ) : (
            <div className="space-y-2.5">
              {steps.map((st) => {
                const isStepCompleted = st.status === 'completed';
                return (
                  <div
                    key={st.step_number}
                    className="flex items-start space-x-3 p-2.5 rounded-lg bg-charcoal-800/70 border border-charcoal-700/70"
                  >
                    <div className="mt-0.5">
                      {isStepCompleted ? (
                        <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                      ) : (
                        <XCircle className="w-4 h-4 text-rose-400" />
                      )}
                    </div>
                    <div className="flex-1 text-xs font-mono">
                      <div className="flex items-center justify-between">
                        <span className="font-semibold text-cream-100">
                          Step {st.step_number}: {st.step_name.charAt(0).toUpperCase() + st.step_name.slice(1)}
                        </span>
                        <span className="text-[10px] text-charcoal-400 uppercase">
                          {st.status}
                        </span>
                      </div>
                      {st.output_summary && (
                        <p className="mt-1 text-charcoal-300 text-[11px] leading-relaxed">
                          {st.output_summary}
                        </p>
                      )}
                      {st.error && (
                        <p className="mt-1 text-rose-300 text-[11px] font-bold">
                          Error: {st.error}
                        </p>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </section>

        {/* 03 — STRUCTURED RESULT CARD */}
        <section className="bg-charcoal-700/60 rounded-xl p-4 border border-charcoal-700">
          <div className="flex items-center justify-between mb-3 border-b border-charcoal-600/50 pb-2">
            <span className="text-[11px] font-mono tracking-wider text-charcoal-400 uppercase font-semibold">
              03 — Final Structured Result
            </span>
            <span className="text-xs font-mono text-charcoal-400">
              Outcome: <strong className={isSuccess ? 'text-emerald-400' : 'text-amber-400'}>{status}</strong>
            </span>
          </div>

          <ResultViews report={report} />
        </section>
      </div>
    </div>
  );
};
