import React, { useState } from 'react';
import { ArrowRight, Sparkles, SlidersHorizontal, BookOpen, ChevronDown, ChevronUp, Bookmark } from 'lucide-react';

interface HeroProps {
  onRunWorkflow: (request: string, forcedWorkflowId?: string) => void;
  onSelectSavedExample?: (slug: string) => void;
  isLoading: boolean;
  isDemoMode?: boolean;
}

export const Hero: React.FC<HeroProps> = ({
  onRunWorkflow,
  onSelectSavedExample,
  isLoading,
  isDemoMode = false,
}) => {
  const [requestText, setRequestText] = useState('');
  const [forcedWf, setForcedWf] = useState('');
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [showSavedExamples, setShowSavedExamples] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!requestText.trim() || isLoading) return;
    onRunWorkflow(requestText.trim(), forcedWf ? forcedWf : undefined);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      if (!requestText.trim() || isLoading) return;
      onRunWorkflow(requestText.trim(), forcedWf ? forcedWf : undefined);
    }
  };

  const quickChips = [
    {
      id: 'WF001',
      label: 'WF001 Restock Check',
      query: "Check today's inventory and identify products that need restocking.",
      slug: 'wf001_restock_check',
    },
    {
      id: 'WF002',
      label: 'WF002 Price Audit',
      query: "Find products where vendor price differs by more than 10%.",
      slug: 'wf002_price_validation',
    },
    {
      id: 'WF003',
      label: 'WF003 Vendor Catalog',
      query: "Process this vendor spreadsheet and show invalid rows.",
      slug: 'wf003_vendor_processing',
    },
    {
      id: 'WF004',
      label: 'WF004 Description Gen',
      query: "Generate SEO content for this product.",
      slug: 'wf004_product_description',
    },
    {
      id: 'WF005',
      label: 'WF005 Order Status',
      query: "Where is order ORD-1001?",
      slug: 'wf005_order_status',
    },
    {
      id: 'WF006',
      label: 'WF006 Duplicate Detection',
      query: "Find likely duplicate products in the catalog.",
      slug: 'wf006_duplicate_detection',
    },
    {
      id: 'WF007',
      label: 'WF007 Campaign Brief',
      query: "Create a marketing campaign brief for the summer sale.",
      slug: 'wf007_campaign_brief',
    },
    {
      id: 'WF008',
      label: 'WF008 SEO Keywords',
      query: "Classify SEO search keywords by search intent.",
      slug: 'wf008_seo_keywords',
    },
    {
      id: 'WF009',
      label: 'WF009 Task Assignment',
      query: "Assign an employee to a new task based on skills.",
      slug: 'wf009_task_assignment',
    },
    {
      id: 'WF010',
      label: 'WF010 Workflow Health',
      query: "Which workflows are failing most often?",
      slug: 'wf010_performance_report',
    },
    {
      id: 'WF011',
      label: 'WF011 Supplier Risk',
      query: "Assess supplier delivery risk across recent deliveries.",
      slug: 'wf011_supplier_risk',
    },
    {
      id: 'NONE',
      label: 'Unrelated Query',
      query: "What is the weather in Paris?",
      slug: 'unrelated_weather',
      isNegative: true,
    },
  ];

  const savedRunsCatalog = [
    {
      id: 'WF001',
      name: 'Inventory Restock Check',
      slug: 'wf001_restock_check',
      query: "Check today's inventory and identify products that need restocking.",
      file: 'examples/output/wf001_output.json',
    },
    {
      id: 'WF002',
      name: 'Product Price Validation',
      slug: 'wf002_price_validation',
      query: "Find products where vendor price differs by more than 10%.",
      file: 'examples/output/wf002_output.json',
    },
    {
      id: 'WF003',
      name: 'Vendor File Processing',
      slug: 'wf003_vendor_processing',
      query: "Process this vendor spreadsheet and show invalid rows.",
      file: 'examples/output/wf003_output.json',
    },
    {
      id: 'WF004',
      name: 'Product Description Generator',
      slug: 'wf004_product_description',
      query: "Generate SEO content for this product.",
      file: 'examples/output/wf004_output.json',
    },
    {
      id: 'WF005',
      name: 'Customer Order Status',
      slug: 'wf005_order_status',
      query: "Where is order ORD-1001?",
      file: 'examples/output/wf005_output.json',
    },
    {
      id: 'WF006',
      name: 'Duplicate Product Detection',
      slug: 'wf006_duplicate_detection',
      query: "Find likely duplicate products in the catalog.",
      file: 'examples/output/wf006_output.json',
    },
    {
      id: 'WF007',
      name: 'Marketing Campaign Brief',
      slug: 'wf007_campaign_brief',
      query: "Create a marketing campaign brief for the summer sale.",
      file: 'examples/output/wf007_output.json',
    },
    {
      id: 'WF008',
      name: 'SEO Keyword Classification',
      slug: 'wf008_seo_keywords',
      query: "Classify SEO search keywords by search intent.",
      file: 'examples/output/wf008_output.json',
    },
    {
      id: 'WF009',
      name: 'Employee Task Assignment',
      slug: 'wf009_task_assignment',
      query: "Assign an employee to a new task based on skills.",
      file: 'examples/output/wf009_output.json',
    },
    {
      id: 'WF010',
      name: 'Workflow Performance Report',
      slug: 'wf010_performance_report',
      query: "Which workflows are failing most often?",
      file: 'examples/output/wf010_output.json',
    },
    {
      id: 'WF011',
      name: 'Supplier Delivery Risk Assessment',
      slug: 'wf011_supplier_risk',
      query: "Assess supplier delivery risk across recent deliveries.",
      file: 'examples/output/wf011_output.json',
    },
    {
      id: 'NEG-1',
      name: 'Negative Test: Weather in Paris',
      slug: 'unrelated_weather',
      query: "What is the weather in Paris?",
      file: 'examples/output/unrelated_weather_output.json',
    },
  ];

  return (
    <section className="pt-8 pb-8 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto">
      {/* Monospace Badge */}
      <div className="flex justify-center mb-4">
        <span className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full text-[11px] font-mono font-medium bg-blush-200 text-charcoal-700 border border-blush-300 shadow-sm">
          <Sparkles className="w-3 h-3 text-brand-magenta" />
          <span>WORKBOOK-DRIVEN · REUSABLE WORKFLOWS · DETERMINISTIC TOOLS</span>
        </span>
      </div>

      {/* Main Headline */}
      <div className="text-center max-w-3xl mx-auto mb-6">
        <h1 className="text-3xl sm:text-5xl font-extrabold tracking-tight text-charcoal-900 leading-tight">
          Understand the request.
          <br />
          <span className="bg-gradient-to-r from-brand-blue to-brand-magenta bg-clip-text text-transparent">
            Route it. Execute it. Report it.
          </span>
        </h1>
        <p className="mt-3 text-sm sm:text-base text-charcoal-500 max-w-2xl mx-auto leading-relaxed">
          A Python workflow agent that turns natural-language requests into structured business operations
          using Excel-defined workflows and reusable domain tools.
        </p>
      </div>

      {/* Primary Request Input */}
      <form onSubmit={handleSubmit} className="max-w-3xl mx-auto mb-4">
        <div className="relative rounded-2xl bg-cream-50 p-2 shadow-warm border border-charcoal-100 focus-within:border-brand-blue focus-within:ring-2 focus-within:ring-brand-blue/20 transition-all">
          <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-2">
            <textarea
              rows={2}
              value={requestText}
              onChange={(e) => setRequestText(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask something like: Check inventory and identify products that need restocking…"
              className="w-full px-4 py-2 bg-transparent text-charcoal-900 placeholder-charcoal-400 text-sm sm:text-base focus:outline-none resize-none font-sans"
              disabled={isLoading}
            />
            <div className="flex items-center justify-end sm:justify-start px-2 sm:px-0">
              <button
                type="submit"
                disabled={!requestText.trim() || isLoading}
                className="flex-shrink-0 inline-flex items-center space-x-2 px-5 py-3 rounded-xl bg-charcoal-900 text-cream-50 font-medium text-sm hover:bg-charcoal-800 disabled:opacity-40 disabled:cursor-not-allowed transition-all shadow-sm"
              >
                <span>{isLoading ? 'Executing…' : 'Run workflow'}</span>
                <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
        <p className="mt-1.5 px-2 text-[11px] font-mono text-charcoal-400 flex items-center justify-between">
          <span>Press Enter to run, Shift+Enter for newline</span>
          {requestText.length > 0 && (
            <button
              type="button"
              onClick={() => setRequestText('')}
              className="hover:text-charcoal-700 underline"
            >
              Clear input
            </button>
          )}
        </p>

        {/* Optional Forced Route Controls */}
        <div className="flex items-center justify-between mt-2 px-2 text-xs text-charcoal-500">
          <button
            type="button"
            onClick={() => setShowAdvanced(!showAdvanced)}
            className="inline-flex items-center space-x-1 hover:text-charcoal-800 font-mono"
          >
            <SlidersHorizontal className="w-3.5 h-3.5" />
            <span>{showAdvanced ? 'Hide advanced routing options' : 'Advanced: force workflow ID'}</span>
          </button>
          {forcedWf && (
            <span className="font-mono text-amber-700 bg-amber-50 px-2 py-0.5 rounded border border-amber-200">
              Forced route: {forcedWf}
            </span>
          )}
        </div>

        {showAdvanced && (
          <div className="mt-2 p-3 bg-cream-200 rounded-xl border border-charcoal-100 flex flex-wrap items-center gap-3 text-xs">
            <label className="font-medium text-charcoal-700">Force specific workflow:</label>
            <select
              value={forcedWf}
              onChange={(e) => setForcedWf(e.target.value)}
              className="bg-cream-50 border border-charcoal-200 rounded px-2 py-1 text-charcoal-800 font-mono text-xs focus:outline-none"
            >
              <option value="">None (Automatic Routing)</option>
              {['WF001', 'WF002', 'WF003', 'WF004', 'WF005', 'WF006', 'WF007', 'WF008', 'WF009', 'WF010', 'WF011'].map((id) => (
                <option key={id} value={id}>
                  {id}
                </option>
              ))}
            </select>
            <span className="text-charcoal-500 text-[11px]">
              Forces deterministic selection for boundary verification (bypasses routing intent).
            </span>
          </div>
        )}
      </form>

      {/* Quick-Try Scenario Chips */}
      <div className="max-w-4xl mx-auto mb-4">
        <p className="text-[11px] font-mono text-charcoal-400 text-center uppercase tracking-wider mb-2">
          Quick-Try Examples (Click chip to populate input, then click Run workflow)
        </p>
        <div className="flex flex-wrap items-center justify-center gap-1.5">
          {quickChips.map((chip) => (
            <button
              key={chip.id}
              type="button"
              onClick={() => setRequestText(chip.query)}
              disabled={isLoading}
              title={`Populate prompt: "${chip.query}"`}
              className={`px-2.5 py-1 rounded-lg text-xs font-mono transition-all border ${
                chip.isNegative
                  ? 'bg-amber-50/80 text-amber-900 border-amber-200 hover:bg-amber-100'
                  : 'bg-cream-50 text-charcoal-700 border-charcoal-100 hover:border-brand-blue hover:text-brand-blue shadow-2xs'
              }`}
            >
              {chip.label}
            </button>
          ))}
        </div>
      </div>

      {/* Separated "Explore Saved Examples" Disclosure */}
      <div className="max-w-4xl mx-auto border-t border-charcoal-100/70 pt-3">
        <div className="flex justify-center">
          <button
            type="button"
            onClick={() => setShowSavedExamples(!showSavedExamples)}
            className="inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-mono font-medium text-charcoal-600 hover:text-charcoal-900 bg-cream-50 border border-charcoal-200 shadow-2xs transition-all"
          >
            <BookOpen className="w-3.5 h-3.5 text-brand-blue" />
            <span>Explore saved examples (22 verified benchmark reports)</span>
            {showSavedExamples ? (
              <ChevronUp className="w-3.5 h-3.5 ml-1" />
            ) : (
              <ChevronDown className="w-3.5 h-3.5 ml-1" />
            )}
          </button>
        </div>

        {showSavedExamples && (
          <div className="mt-3 bg-cream-50 border border-charcoal-200 rounded-2xl p-4 shadow-sm animate-fadeIn">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-3 mb-3 border-b border-charcoal-100 gap-1">
              <div>
                <h3 className="text-xs font-bold font-mono text-charcoal-800 uppercase tracking-wide">
                  Verified Execution Archive
                </h3>
                <p className="text-[11px] text-charcoal-500">
                  Inspect authentic execution reports recorded in <code>examples/output/</code>.
                  Each report reflects an actual run through the generic engine.
                </p>
              </div>
              {isDemoMode && (
                <span className="self-start sm:self-auto px-2 py-0.5 rounded text-[10px] font-mono font-medium bg-amber-100 text-amber-800 border border-amber-300">
                  Offline Inspection Active
                </span>
              )}
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-xs">
              {savedRunsCatalog.map((item) => (
                <div
                  key={item.slug}
                  className="p-2.5 rounded-xl bg-cream-100 border border-charcoal-100 flex items-center justify-between gap-2 hover:border-charcoal-300 transition-colors"
                >
                  <div className="min-w-0 flex-1 font-mono">
                    <div className="flex items-center space-x-2">
                      <span className="font-bold text-charcoal-800">{item.id}</span>
                      <span className="text-[11px] text-charcoal-600 truncate">{item.name}</span>
                    </div>
                    <p className="text-[10px] text-charcoal-400 truncate mt-0.5" title={item.file}>
                      Saved example: {item.file}
                    </p>
                  </div>
                  <button
                    type="button"
                    onClick={() => onSelectSavedExample && onSelectSavedExample(item.slug)}
                    className="flex-shrink-0 inline-flex items-center space-x-1 px-2.5 py-1 rounded-md text-[11px] font-mono font-medium bg-charcoal-800 text-cream-50 hover:bg-charcoal-900 transition-all shadow-2xs"
                  >
                    <Bookmark className="w-3 h-3 text-amber-300" />
                    <span>View saved example</span>
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </section>
  );
};
