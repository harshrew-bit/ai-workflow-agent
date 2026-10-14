import React from 'react';
import { Layers, Terminal, Sparkles, CheckCircle2, ArrowRight } from 'lucide-react';

export const ExtendingPage: React.FC = () => {
  const extensionChecklist = [
    {
      step: 1,
      title: 'Workflow Definition Schema',
      file: 'data/workflows.xlsx or WorkflowDefinition model',
      desc: 'Define workflow ID, name, trigger, required inputs, human-readable steps, decision rules, and required tools.',
      code: `wf11 = WorkflowDefinition(
    Workflow_ID="WF011",
    Workflow_Name="Supplier Delivery Risk Assessment",
    Trigger="Assess supplier delivery risk across recent purchase order fulfillment",
    Inputs="Supplier delivery records CSV",
    Steps="Load deliveries -> Validate records -> Calculate metrics -> Evaluate risk -> Generate report",
    Decision_Logic="Score = (late_rate * 60) + min(avg_delay * 8, 40). Score >= 50 or late_rate >= 0.35 is HIGH RISK.",
    Tools_Required="supplier_delivery_loader, delivery_record_validator, delivery_metrics_calculator, supplier_risk_evaluator, supplier_risk_reporter",
    Expected_Output="Supplier delivery risk assessment report",
)`,
    },
    {
      step: 2,
      title: 'Implement Domain Tool Classes',
      file: 'app/tools/supplier_risk.py',
      desc: 'Create domain tool classes inheriting from BaseTool with typed metadata and execute() implementation.',
      code: `class SupplierDeliveryLoaderTool(BaseTool):
    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="supplier_delivery_loader",
            description="Loads raw supplier delivery records from CSV",
        )

    def execute(self, **kwargs: Any) -> Dict[str, Any]:
        records = load_supplier_delivery_records(kwargs.get("supplier_csv_path"))
        return {"raw_records": records, "total_loaded": len(records)}`,
    },
    {
      step: 3,
      title: 'Register Tools in ToolRegistry',
      file: 'app/registry.py (create_default_tool_registry)',
      desc: 'Register each newly created tool instance into the central ToolRegistry.',
      code: `tool_registry.register(SupplierDeliveryLoaderTool())
tool_registry.register(DeliveryRecordValidatorTool())
tool_registry.register(DeliveryMetricsCalculatorTool())
tool_registry.register(SupplierRiskEvaluatorTool())
tool_registry.register(SupplierRiskReporterTool())`,
    },
    {
      step: 4,
      title: 'Bind Step Strings in StepResolver',
      file: 'app/registry.py (create_default_step_resolver)',
      desc: 'Bind each human-readable step name from the workflow specification to its registered tool name.',
      code: `step_resolver.bind("WF011", "Load deliveries", "supplier_delivery_loader")
step_resolver.bind("WF011", "Validate records", "delivery_record_validator")
step_resolver.bind("WF011", "Calculate metrics", "delivery_metrics_calculator")
step_resolver.bind("WF011", "Evaluate risk", "supplier_risk_evaluator")
step_resolver.bind("WF011", "Generate report", "supplier_risk_reporter")`,
    },
    {
      step: 5,
      title: 'Expose CLI / API Options & Input Mapping',
      file: 'app/main.py, app/orchestrator.py, api/main.py',
      desc: 'Map domain-specific flags or server-side fixtures (e.g. sample_supplier_deliveries.csv for WF011).',
      code: `parser.add_argument("--supplier-csv", default=None, help="Supplier delivery records CSV path (WF011)")
parser.add_argument("--enable-wf011", action="store_true", help="Enable demonstration extension WF011")`,
    },
    {
      step: 6,
      title: 'Add Automated Unit & Regression Tests',
      file: 'tests/test_wf011_extensibility.py',
      desc: 'Write automated pytest suites verifying generic engine execution, boundary decisions, and error handling.',
      code: `def test_generic_engine_executes_wf011_without_engine_modifications():
    engine = GenericWorkflowEngine(tool_registry=tool_reg, step_resolver=step_res)
    result = engine.execute(wf011)
    assert result.status == ExecutionStatus.COMPLETED
    assert result.workflow_id == "WF011"`,
    },
  ];

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      <div className="mb-8">
        <span className="text-xs font-mono font-medium text-brand-blue uppercase tracking-wider">
          Architecture Extensibility
        </span>
        <h1 className="text-3xl font-bold text-charcoal-900 mt-1">
          Extending the System: Adding New Workflows
        </h1>
        <p className="text-sm text-charcoal-500 mt-2 max-w-3xl leading-relaxed">
          Demonstrated by <strong>WF011 (Supplier Delivery Risk Assessment)</strong>. The system proves zero-engine-modification extensibility: core generic engine classes remain 100% untouched.
        </p>
      </div>

      {/* Crucial Distinction Section */}
      <section className="bg-cream-50 border border-charcoal-200 rounded-2xl p-6 shadow-sm mb-10">
        <h2 className="text-base font-bold text-charcoal-900 flex items-center space-x-2 mb-2 font-mono uppercase tracking-wide">
          <Layers className="w-5 h-5 text-brand-blue" />
          <span>Crucial Distinction: Executing a Request vs. Implementing a New Workflow</span>
        </h2>
        <p className="text-xs sm:text-sm text-charcoal-600 mb-6 leading-relaxed">
          It is essential to distinguish between asking the AI agent to execute an existing capability and engineering a new workflow into the system.
          <strong> Entering a prompt in the user interface does NOT automatically synthesize a new backend workflow</strong>; it routes your request to an already registered workflow from the catalog.
        </p>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Card 1: Executing an Existing Workflow */}
          <div className="bg-cream-100 rounded-xl p-4 border border-charcoal-200/80">
            <div className="flex items-center space-x-2 mb-2">
              <span className="p-1 rounded bg-brand-blue/10 text-brand-blue">
                <Terminal className="w-4 h-4" />
              </span>
              <h3 className="font-bold text-sm text-charcoal-900">1. Executing a Request</h3>
            </div>
            <p className="text-xs text-charcoal-600 mb-3 leading-relaxed">
              When a user submits a natural-language request like <em>"Check inventory and flag low stock"</em>:
            </p>
            <ul className="space-y-1.5 text-xs text-charcoal-700 font-mono">
              <li className="flex items-start space-x-2">
                <ArrowRight className="w-3.5 h-3.5 text-brand-blue flex-shrink-0 mt-0.5" />
                <span>Router evaluates prompt intent against known workflow triggers</span>
              </li>
              <li className="flex items-start space-x-2">
                <ArrowRight className="w-3.5 h-3.5 text-brand-blue flex-shrink-0 mt-0.5" />
                <span>Selects existing registered workflow (e.g. WF001) or asks clarification</span>
              </li>
              <li className="flex items-start space-x-2">
                <ArrowRight className="w-3.5 h-3.5 text-brand-blue flex-shrink-0 mt-0.5" />
                <span>Engine runs pre-existing bound domain tools and generates report</span>
              </li>
            </ul>
            <div className="mt-3 p-2 bg-cream-200/70 rounded text-[11px] text-charcoal-500 font-mono">
              Scope: Runtime execution of already registered business logic.
            </div>
          </div>

          {/* Card 2: Implementing a New Workflow */}
          <div className="bg-emerald-50/70 rounded-xl p-4 border border-emerald-200">
            <div className="flex items-center space-x-2 mb-2">
              <span className="p-1 rounded bg-emerald-600 text-cream-50">
                <Sparkles className="w-4 h-4" />
              </span>
              <h3 className="font-bold text-sm text-emerald-950">2. Implementing a New Workflow</h3>
            </div>
            <p className="text-xs text-emerald-900 mb-3 leading-relaxed">
              To support an entirely new business process (such as WF011 for Supplier Risk):
            </p>
            <ul className="space-y-1.5 text-xs text-emerald-950 font-mono">
              <li className="flex items-start space-x-2">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 flex-shrink-0 mt-0.5" />
                <span>Define workflow specification (inputs, steps, decision logic, tools)</span>
              </li>
              <li className="flex items-start space-x-2">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 flex-shrink-0 mt-0.5" />
                <span>Implement domain tool classes inheriting from <code>BaseTool</code></span>
              </li>
              <li className="flex items-start space-x-2">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 flex-shrink-0 mt-0.5" />
                <span>Register tools in <code>ToolRegistry</code> & bind steps in <code>StepResolver</code></span>
              </li>
              <li className="flex items-start space-x-2">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 flex-shrink-0 mt-0.5" />
                <span>Wire input mapping in orchestrator & add automated pytest suites</span>
              </li>
            </ul>
            <div className="mt-3 p-2 bg-emerald-100 rounded text-[11px] text-emerald-900 font-mono font-medium">
              Scope: Software engineering process. Proven by WF011 in Milestone 5.
            </div>
          </div>
        </div>
      </section>

      {/* Unchanged vs Created Summary */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-8">
        <div className="bg-emerald-50 border border-emerald-200 rounded-xl p-4 text-xs">
          <span className="font-mono font-bold text-emerald-800 uppercase block mb-1">
            0 Core Engine Lines Changed (Reused As-Is)
          </span>
          <ul className="space-y-1 text-emerald-900 font-mono">
            <li>✓ `app/engine/base.py` (GenericWorkflowEngine)</li>
            <li>✓ `app/orchestrator.py` (WorkflowOrchestrator)</li>
            <li>✓ `app/agent/router.py` (LLMWorkflowRouter)</li>
            <li>✓ `data/workflows.xlsx` (Strictly preserved official workbook)</li>
          </ul>
        </div>
        <div className="bg-blue-50 border border-blue-200 rounded-xl p-4 text-xs">
          <span className="font-mono font-bold text-blue-800 uppercase block mb-1">
            Standard Extension Pattern
          </span>
          <p className="text-blue-900 leading-relaxed font-sans">
            Extensions plug cleanly into the catalog, tool registry, and step resolver without altering execution mechanics, state serialization, or reporting.
          </p>
        </div>
      </div>

      {/* 6 Steps Checklist */}
      <div className="space-y-6">
        <h2 className="text-xl font-bold text-charcoal-900 font-mono uppercase tracking-wide">
          The 6-Step Implementation Checklist (WF011 Case Study)
        </h2>
        {extensionChecklist.map((item) => (
          <div key={item.step} className="bg-cream-50 rounded-2xl p-6 border border-charcoal-100 shadow-warm">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-2">
              <div className="flex items-center space-x-3">
                <span className="w-7 h-7 rounded-lg bg-brand-blue text-cream-50 text-xs font-mono font-bold flex items-center justify-center">
                  {item.step}
                </span>
                <h3 className="font-bold text-base text-charcoal-900">{item.title}</h3>
              </div>
              <code className="text-[11px] font-mono bg-cream-200 text-charcoal-700 px-2 py-0.5 rounded border border-charcoal-200/60">
                {item.file}
              </code>
            </div>
            <p className="text-xs sm:text-sm text-charcoal-600 mb-3 pl-10">
              {item.desc}
            </p>
            <div className="ml-10 rounded-xl bg-charcoal-900 p-3 text-cream-50 font-mono text-[11px] overflow-x-auto border border-charcoal-800">
              <pre><code>{item.code}</code></pre>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
