"""End-to-end workflow orchestrator connecting router, registry, engine, and tools."""

from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Union

from app.agent.router import LLMWorkflowRouter, RoutingDecision, WorkflowRouter
from app.engine.base import GenericWorkflowEngine
from app.engine.resolver import ConfigurableStepResolver, StepResolver, create_default_step_resolver
from app.models.execution import ExecutionStatus
from app.models.report import ExecutionReport, StepReport
from app.models.workflow import WorkflowDefinition
from app.registry.registry import WorkflowRegistry
from app.tools import create_default_tool_registry
from app.tools.registry import ToolRegistry


class WorkflowOrchestrator:
    """Application-level orchestrator driving the end-to-end workflow lifecycle:

    User Request → LLM Router → Workflow Registry → Step Resolver → Generic Engine → Tools → Execution Report.
    """

    def __init__(
        self,
        registry: Optional[WorkflowRegistry] = None,
        router: Optional[WorkflowRouter] = None,
        engine: Optional[GenericWorkflowEngine] = None,
        tool_registry: Optional[ToolRegistry] = None,
        step_resolver: Optional[StepResolver] = None,
        workbook_path: Optional[Union[str, Path]] = None,
        default_inputs: Optional[Dict[str, Any]] = None,
    ) -> None:
        wb_path = (
            Path(workbook_path)
            if workbook_path
            else Path(__file__).parent.parent / "data" / "workflows.xlsx"
        )

        self.registry = (
            registry if registry is not None else WorkflowRegistry.from_excel(wb_path)
        )
        self.router = router if router is not None else LLMWorkflowRouter()
        self.tool_registry = (
            tool_registry
            if tool_registry is not None
            else create_default_tool_registry()
        )
        self.step_resolver = (
            step_resolver
            if step_resolver is not None
            else create_default_step_resolver()
        )
        self.engine = (
            engine
            if engine is not None
            else GenericWorkflowEngine(
                tool_registry=self.tool_registry,
                step_resolver=self.step_resolver,
            )
        )
        self.default_inputs = dict(default_inputs or {})

    def run(self, user_request: str, **runtime_inputs: Any) -> ExecutionReport:
        """Execute a natural-language workflow request through the full orchestration pipeline."""
        clean_request = (user_request or "").strip()

        # 1. Ask router to select workflow
        routing_decision = self.router.route(
            clean_request,
            self.registry.list_all(),
        )

        # 2. Check for clarification, low confidence, or missing selection
        if routing_decision.requires_clarification or not routing_decision.workflow_id:
            return ExecutionReport(
                request=user_request,
                selected_workflow_id=routing_decision.workflow_id,
                selected_workflow_name=None,
                routing_confidence=routing_decision.confidence,
                routing_reasoning=routing_decision.reasoning,
                status="needs_clarification",
                steps=[],
                final_output=None,
                errors=[routing_decision.reasoning] if routing_decision.reasoning else [],
                clarification_required=True,
            )

        # 3. Validate selected ID against registry
        workflow = self.registry.get_or_none(routing_decision.workflow_id)
        if workflow is None:
            err = (
                f"Selected workflow ID '{routing_decision.workflow_id}' was not found in the workflow registry."
            )
            return ExecutionReport(
                request=user_request,
                selected_workflow_id=routing_decision.workflow_id,
                selected_workflow_name=None,
                routing_confidence=routing_decision.confidence,
                routing_reasoning=routing_decision.reasoning,
                status="failed",
                steps=[],
                final_output=None,
                errors=[err],
                clarification_required=True,
            )

        # 4. Prepare execution inputs
        merged_inputs = dict(self.default_inputs)
        merged_inputs.update(routing_decision.extracted_inputs)
        merged_inputs.update(runtime_inputs)

        # For WF002, the decision threshold is fixed at 10% by definition in data/workflows.xlsx.
        # Prevent any runtime input or router-extracted argument from overriding it.
        if workflow.workflow_id == "WF002":
            merged_inputs.pop("threshold", None)
            merged_inputs.pop("threshold_percentage", None)

        # 5. Execute via generic execution engine
        exec_result = self.engine.execute(workflow, **merged_inputs)

        # 6. Format step reports
        step_reports: List[StepReport] = []
        for s in exec_result.step_results:
            summary = None
            if s.status == ExecutionStatus.COMPLETED and s.output is not None:
                if isinstance(s.output, dict):
                    if "summary" in s.output:
                        summary = str(s.output["summary"])
                    elif "total_loaded" in s.output:
                        summary = f"Loaded {s.output['total_loaded']} inventory records."
                    elif "low_stock_count" in s.output:
                        summary = f"Identified {s.output['low_stock_count']} low-stock items."
                    elif "restock_items" in s.output:
                        summary = f"Calculated reorders for {len(s.output['restock_items'])} items."
                    else:
                        summary = f"Step output completed with {len(s.output)} fields."
                else:
                    summary = str(s.output)[:120]

            step_reports.append(
                StepReport(
                    step_number=s.step_number,
                    step_name=s.step_name,
                    status=s.status.value,
                    output_summary=summary,
                    output=s.output,
                    error=s.error,
                )
            )

        # 7. Determine overall report status
        if exec_result.status == ExecutionStatus.COMPLETED:
            overall_status = "success"
            errors = []
        else:
            completed_steps = sum(1 for s in step_reports if s.status == "completed")
            overall_status = "partial_failure" if completed_steps > 0 else "failed"
            errors = [exec_result.error] if exec_result.error else []

        return ExecutionReport(
            request=user_request,
            selected_workflow_id=workflow.workflow_id,
            selected_workflow_name=workflow.workflow_name,
            routing_confidence=routing_decision.confidence,
            routing_reasoning=routing_decision.reasoning,
            status=overall_status,
            steps=step_reports,
            final_output=exec_result.output,
            errors=errors,
            clarification_required=False,
        )
