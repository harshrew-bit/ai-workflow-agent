import React from 'react';
import { Hero } from '../components/Hero';
import { ExecutionTrace } from '../components/ExecutionTrace';
import { RawJsonViewer } from '../components/RawJsonViewer';
import { ExecutionReport, AppExecutionState } from '../types/workflow';
import { AlertCircle } from 'lucide-react';

interface HomePageProps {
  report: ExecutionReport | null;
  executionState: AppExecutionState;
  errorMessage: string | null;
  isSavedExample: boolean;
  savedExampleTitle?: string;
  isDemoFallback: boolean;
  isDemoMode: boolean;
  onRunWorkflow: (request: string, forcedWorkflowId?: string) => void;
  onSelectSavedExample: (slug: string) => void;
  onClearError: () => void;
}

export const HomePage: React.FC<HomePageProps> = ({
  report,
  executionState,
  errorMessage,
  isSavedExample,
  savedExampleTitle,
  isDemoFallback,
  isDemoMode,
  onRunWorkflow,
  onSelectSavedExample,
  onClearError,
}) => {
  return (
    <div className="pb-16">
      <Hero
        onRunWorkflow={onRunWorkflow}
        onSelectSavedExample={onSelectSavedExample}
        isLoading={executionState === 'running'}
        isDemoMode={isDemoMode}
      />

      <main className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 mt-2">
        {/* Error notification banner if any */}
        {errorMessage && (
          <div className="mb-4 bg-rose-50 border border-rose-200 rounded-xl p-4 text-rose-800 text-sm flex items-start justify-between">
            <div className="flex items-start space-x-2">
              <AlertCircle className="w-5 h-5 text-rose-500 flex-shrink-0 mt-0.5" />
              <div>
                <strong className="font-semibold">Notice: </strong>
                <span>{errorMessage}</span>
              </div>
            </div>
            <button
              onClick={onClearError}
              className="text-xs font-mono font-medium text-rose-600 hover:text-rose-800 ml-4 flex-shrink-0"
            >
              Dismiss
            </button>
          </div>
        )}

        <ExecutionTrace
          report={report}
          executionState={executionState}
          isLoading={executionState === 'running'}
          isSavedExample={isSavedExample}
          savedExampleTitle={savedExampleTitle}
          errorMessage={errorMessage}
          isDemoFallback={isDemoFallback}
        />

        {report && <RawJsonViewer report={report} />}
      </main>
    </div>
  );
};
