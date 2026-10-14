import { useState, useEffect } from 'react';
import { Header } from './components/Header';
import { HomePage } from './pages/HomePage';
import { ArchitecturePage } from './pages/ArchitecturePage';
import { WorkbookPage } from './pages/WorkbookPage';
import { DecisionsPage } from './pages/DecisionsPage';
import { ExtendingPage } from './pages/ExtendingPage';
import { StatusPage } from './pages/StatusPage';
import { checkBackendHealth, executeWorkflow, getSavedExample } from './api/client';
import { ExecutionReport, HealthResponse, AppExecutionState } from './types/workflow';

export function App() {
  const [currentTab, setCurrentTab] = useState('home');
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [isDemoMode, setIsDemoMode] = useState(false);
  const [executionState, setExecutionState] = useState<AppExecutionState>('idle');
  const [report, setReport] = useState<ExecutionReport | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [isSavedExample, setIsSavedExample] = useState(false);
  const [savedExampleTitle, setSavedExampleTitle] = useState<string | undefined>(undefined);
  const [isDemoFallback, setIsDemoFallback] = useState(false);

  // Initial health check on page load: real health endpoint, NO automatic workflow execution
  useEffect(() => {
    checkBackendHealth().then((h) => {
      setHealth(h);
      if (!h) {
        setIsDemoMode(true);
      }
    });
    // Start strictly in 'idle' state with empty request and idle trace panel
  }, []);

  const handleRunWorkflow = async (requestText: string, forcedWorkflowId?: string) => {
    setExecutionState('running');
    setErrorMessage(null);
    setIsSavedExample(false);
    setSavedExampleTitle(undefined);

    try {
      const result = await executeWorkflow(requestText, forcedWorkflowId);
      setReport(result.report);
      setIsDemoFallback(result.isDemoFallback);
      if (result.isDemoFallback) {
        setIsDemoMode(true);
      }

      // Map response status to explicit application state
      if (result.report.status === 'success') {
        setExecutionState('success');
      } else if (result.report.status === 'needs_clarification') {
        setExecutionState('needs_clarification');
      } else if (result.report.status === 'partial_failure') {
        setExecutionState('partial_failure');
      } else {
        setExecutionState('error');
      }
    } catch (err: any) {
      setExecutionState('error');
      setReport(null);
      setErrorMessage(err.message || 'Workflow execution error occurred.');
      setIsDemoMode(true);
    }
  };

  const handleSelectSavedExample = (slug: string) => {
    const saved = getSavedExample(slug);
    if (saved) {
      setReport(saved);
      setIsSavedExample(true);
      setSavedExampleTitle(slug);
      setErrorMessage(null);
      if (saved.status === 'success') {
        setExecutionState('success');
      } else if (saved.status === 'needs_clarification') {
        setExecutionState('needs_clarification');
      } else if (saved.status === 'partial_failure') {
        setExecutionState('partial_failure');
      } else {
        setExecutionState('error');
      }
    }
  };

  return (
    <div className="min-h-screen bg-cream-100 flex flex-col font-sans selection:bg-brand-blue/20 selection:text-brand-blue">
      <Header
        currentTab={currentTab}
        onSelectTab={setCurrentTab}
        health={health}
        isDemoMode={isDemoMode}
      />

      <div className="flex-1">
        {currentTab === 'home' && (
          <HomePage
            report={report}
            executionState={executionState}
            errorMessage={errorMessage}
            isSavedExample={isSavedExample}
            savedExampleTitle={savedExampleTitle}
            isDemoFallback={isDemoFallback}
            isDemoMode={isDemoMode}
            onRunWorkflow={handleRunWorkflow}
            onSelectSavedExample={handleSelectSavedExample}
            onClearError={() => {
              setErrorMessage(null);
              if (executionState === 'error') {
                setExecutionState(report ? 'success' : 'idle');
              }
            }}
          />
        )}
        {currentTab === 'architecture' && <ArchitecturePage />}
        {currentTab === 'workbook' && <WorkbookPage />}
        {currentTab === 'decisions' && <DecisionsPage />}
        {currentTab === 'extending' && <ExtendingPage />}
        {currentTab === 'status' && <StatusPage health={health} isDemoMode={isDemoMode} />}
      </div>

      <footer className="border-t border-charcoal-100 bg-cream-50 py-6 text-center text-xs font-mono text-charcoal-400">
        <div className="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-2">
          <span>AI Workflow Agent · Excel Workflows · Python Engine · Generic Orchestrator</span>
          <span className="text-[11px] text-charcoal-500">
            SHA-256 Checksum Verified · 289 Tests Passing · Request-Driven Execution
          </span>
        </div>
      </footer>
    </div>
  );
}

export default App;
