"""End-to-end workflow orchestrator connecting router, registry, engine, and tools."""

from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Union

from app.agent.normalization import (
    detect_query_ambiguity,
    extract_deterministic_inputs,
    merge_execution_inputs,
)
from app.agent.offline_router import (
    OfflineWorkflowRouter,
    detect_multi_workflow_intents,
)
from app.agent.provider import is_live_llm_configured
from app.agent.router import LLMWorkflowRouter, RoutingDecision, WorkflowRouter
from app.engine.base import GenericWorkflowEngine
from app.engine.resolver import ConfigurableStepResolver, StepResolver, create_default_step_resolver
from app.models.execution import ExecutionStatus
from app.models.report import ExecutionReport, StepReport
from app.models.workflow import WorkflowDefinition
from app.registry.registry import WorkflowRegistry
from app.tools import create_default_tool_registry
from app.tools.registry import ToolRegistry


def _is_path_like_key(key: str) -> bool:
    """True for input names that point at the filesystem (e.g. vendor_csv_path, file_path)."""
    lowered = key.lower()
    return any(token in lowered for token in ("path", "file", "csv"))


def _format_step_summary(s: Any) -> Optional[str]:
    """Extract or construct human-readable summary for a completed workflow step."""
    summary = None
    if s.status == ExecutionStatus.COMPLETED and s.output is not None:
        if isinstance(s.output, dict):
            if "summary" in s.output and s.output["summary"]:
                summary = str(s.output["summary"])
            elif "total_loaded" in s.output:
                summary = f"Loaded {s.output['total_loaded']} inventory records."
            elif "low_stock_count" in s.output:
                summary = f"Identified {s.output['low_stock_count']} low-stock items."
            elif "restock_items" in s.output:
                summary = f"Calculated reorders for {len(s.output['restock_items'])} items."
            else:
                list_keys = [k for k, v in s.output.items() if isinstance(v, list)]
                if list_keys:
                    summary = f"Processed {len(s.output[list_keys[0]])} items ({', '.join(s.output.keys())})."
                else:
                    summary = f"Completed step ({', '.join(s.output.keys())})."
        else:
            summary = str(s.output)[:120]
    return summary


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
        if router is not None:
            self.router = router
        elif is_live_llm_configured():
            self.router = LLMWorkflowRouter()
        else:
            self.router = OfflineWorkflowRouter()

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

        # 0. Check for multi-objective / multi-workflow requests
        multi_intents = detect_multi_workflow_intents(clean_request, self.registry.list_all())
        if len(multi_intents) >= 2:
            sub_reports: List[ExecutionReport] = []
            combined_steps: List[StepReport] = []
            combined_errors: List[str] = []
            step_num_offset = 0

            for wf, sub_clause in multi_intents:
                # Isolate parameter extraction strictly to the sub-clause and target workflow
                sub_extracted = extract_deterministic_inputs(sub_clause, wf.workflow_id)
                sub_merged, _ = merge_execution_inputs(
                    default_inputs=self.default_inputs,
                    router_extracted={},
                    query_extracted=sub_extracted,
                    runtime_inputs=runtime_inputs,
                    workflow_id=wf.workflow_id,
                )
                sub_exec = self.engine.execute(wf, **sub_merged)

                wf_steps: List[StepReport] = []
                for s in sub_exec.step_results:
                    summary = _format_step_summary(s)
                    st_rep = StepReport(
                        step_number=s.step_number,
                        step_name=s.step_name,
                        status=s.status.value,
                        output_summary=summary,
                        output=s.output,
                        error=s.error,
                    )
                    wf_steps.append(st_rep)
                    combined_steps.append(
                        StepReport(
                            step_number=step_num_offset + s.step_number,
                            step_name=f"[{wf.workflow_id}] {s.step_name}",
                            status=s.status.value,
                            output_summary=summary,
                            output=s.output,
                            error=s.error,
                        )
                    )
                step_num_offset += len(sub_exec.step_results)

                sub_status = "success"
                sub_errors: List[str] = []
                for s in sub_exec.step_results:
                    if s.status == ExecutionStatus.FAILED and s.error:
                        sub_errors.append(f"Step {s.step_number} ({s.step_name}): {s.error}")
                if sub_errors:
                    sub_status = "partial_failure" if sub_exec.output else "failed"
                    combined_errors.extend(sub_errors)

                sub_rep = ExecutionReport(
                    request=sub_clause,
                    selected_workflow_id=wf.workflow_id,
                    selected_workflow_name=wf.workflow_name,
                    routing_confidence=0.95,
                    routing_reasoning=f"Multi-objective intent matched clause '{sub_clause}' to {wf.workflow_id}.",
                    status=sub_status,
                    steps=wf_steps,
                    final_output=sub_exec.output,
                    errors=sub_errors,
                    clarification_required=False,
                    routing_mode="multi_workflow",
                )
                sub_reports.append(sub_rep)

            all_success = all(sr.status == "success" for sr in sub_reports)
            any_success = any(sr.status == "success" for sr in sub_reports)
            if all_success:
                overall_status = "success"
            elif any_success:
                overall_status = "partial_failure"
            else:
                overall_status = "failed"

            wf_ids_str = ", ".join(wf.workflow_id for wf, _ in multi_intents)
            wf_names_str = " + ".join(wf.workflow_name for wf, _ in multi_intents)

            final_composite_output = {
                "workflow_reports": {sr.selected_workflow_id: sr.model_dump() for sr in sub_reports},
                "reports": [sr.model_dump() for sr in sub_reports],
                "summary": f"Executed {len(sub_reports)} workflows ({wf_ids_str}) with status '{overall_status}'.",
            }
            for sr in sub_reports:
                if isinstance(sr.final_output, dict):
                    for k, v in sr.final_output.items():
                        if k not in final_composite_output:
                            final_composite_output[k] = v

            return ExecutionReport(
                request=user_request,
                selected_workflow_id=wf_ids_str,
                selected_workflow_name=wf_names_str,
                routing_confidence=0.95,
                routing_reasoning=f"Executed multi-objective request across workflows: {wf_ids_str}.",
                status=overall_status,
                steps=combined_steps,
                final_output=final_composite_output,
                errors=combined_errors,
                clarification_required=False,
                routing_mode="multi_workflow",
            )

        # 1. Ask router to select workflow for single-objective request
        routing_decision = self.router.route(
            clean_request,
            self.registry.list_all(),
        )

        # Fallback to deterministic offline router if live LLM router was inactive / unconfigured
        if (
            routing_decision.requires_clarification
            and "Live LLM provider is not configured" in (routing_decision.reasoning or "")
        ):
            offline_router = OfflineWorkflowRouter()
            routing_decision = offline_router.route(clean_request, self.registry.list_all())

        # Check if historical data is provided in runtime inputs
        has_historical_data = bool(
            runtime_inputs.get("historical_vendor_csv_path")
            or runtime_inputs.get("prior_vendor_csv_path")
            or runtime_inputs.get("historical_data")
        )
        if (
            routing_decision.requires_clarification
            and routing_decision.workflow_id == "WF002"
            and has_historical_data
            and "historical price comparison" in (routing_decision.reasoning or "").lower()
        ):
            routing_decision.requires_clarification = False

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
                routing_mode=routing_decision.routing_mode,
            )

        # 2b. Check semantic ambiguity (e.g. directional vs absolute variance, historical comparison)
        is_ambiguous, ambiguity_reason = detect_query_ambiguity(
            clean_request, routing_decision.workflow_id, has_historical_data=has_historical_data
        )
        if is_ambiguous:
            return ExecutionReport(
                request=user_request,
                selected_workflow_id=routing_decision.workflow_id,
                selected_workflow_name=workflow.workflow_name if (workflow := self.registry.get_or_none(routing_decision.workflow_id)) else None,
                routing_confidence=routing_decision.confidence,
                routing_reasoning=ambiguity_reason or routing_decision.reasoning,
                status="needs_clarification",
                steps=[],
                final_output=None,
                errors=[ambiguity_reason] if ambiguity_reason else [],
                clarification_required=True,
                routing_mode=routing_decision.routing_mode,
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
                routing_mode=routing_decision.routing_mode,
            )

        # 4. Prepare execution inputs with authoritative precedence contract.
        # Router-extracted values are LLM-controlled and untrusted. File-path inputs are
        # dropped from router and query text so untrusted input can never read an arbitrary local file;
        # paths must come from explicit CLI/runtime arguments or configured defaults.
        query_extracted = extract_deterministic_inputs(clean_request, workflow.workflow_id)
        merged_inputs, ignored_path_inputs = merge_execution_inputs(
            default_inputs=self.default_inputs,
            router_extracted=routing_decision.extracted_inputs,
            query_extracted=query_extracted,
            runtime_inputs=runtime_inputs,
            workflow_id=workflow.workflow_id,
        )
        reasoning = routing_decision.reasoning
        if ignored_path_inputs:
            note = (
                "Ignored router-supplied file path input(s): "
                + ", ".join(ignored_path_inputs)
                + ". Pass file paths explicitly."
            )
            reasoning = f"{reasoning} {note}".strip()

        # 5. Execute via generic execution engine
        exec_result = self.engine.execute(workflow, **merged_inputs)

        # 6. Format step reports
        step_reports: List[StepReport] = []
        for s in exec_result.step_results:
            summary = _format_step_summary(s)
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
        needs_clarification = exec_result.status == ExecutionStatus.NEEDS_CLARIFICATION
        if exec_result.status == ExecutionStatus.COMPLETED:
            overall_status = "success"
            errors = []
        elif needs_clarification:
            overall_status = "needs_clarification"
            errors = [exec_result.error] if exec_result.error else []
        else:
            completed_steps = sum(1 for s in step_reports if s.status == "completed")
            overall_status = "partial_failure" if completed_steps > 0 else "failed"
            errors = [exec_result.error] if exec_result.error else []

        return ExecutionReport(
            request=user_request,
            selected_workflow_id=workflow.workflow_id,
            selected_workflow_name=workflow.workflow_name,
            routing_confidence=routing_decision.confidence,
            routing_reasoning=reasoning,
            status=overall_status,
            steps=step_reports,
            final_output=exec_result.output,
            errors=errors,
            clarification_required=needs_clarification,
            routing_mode=routing_decision.routing_mode,
        )
