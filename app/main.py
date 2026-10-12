"""CLI entrypoint for AI Workflow Agent."""

import argparse
import json
import sys
from typing import Any, Dict

from app.orchestrator import WorkflowOrchestrator


def format_report_for_display(report: Any) -> str:
    """Format an ExecutionReport into a clear, clean human-readable terminal output."""
    lines = []
    lines.append("=" * 70)
    lines.append(" AI WORKFLOW AUTOMATION — EXECUTION REPORT")
    lines.append("=" * 70)
    lines.append(f"Request:               {report.request}")
    lines.append(f"Status:                {report.status.upper()}")
    lines.append(f"Selected Workflow:     {report.selected_workflow_id or 'None'} ({report.selected_workflow_name or 'None'})")
    lines.append(f"Routing Confidence:    {report.routing_confidence:.2f}")
    lines.append(f"Routing Reasoning:     {report.routing_reasoning}")
    lines.append("-" * 70)

    if report.status == "needs_clarification":
        lines.append("\n[!] CLARIFICATION REQUIRED:")
        for err in report.errors:
            lines.append(f"    - {err}")
        lines.append("\nNo tools were executed.")
        lines.append("=" * 70)
        return "\n".join(lines)

    lines.append("Step-by-Step Execution:")
    for step in report.steps:
        status_icon = "[✓]" if step.status == "completed" else "[✗]"
        summary_text = f" — {step.output_summary}" if step.output_summary else ""
        error_text = f" [ERROR: {step.error}]" if step.error else ""
        lines.append(f"  {status_icon} Step {step.step_number}: {step.step_name}{summary_text}{error_text}")

    lines.append("-" * 70)
    lines.append("Final Structured Result:")

    if isinstance(report.final_output, dict):
        # Format restock list if present
        restock_items = report.final_output.get("products_requiring_restock")
        if restock_items:
            lines.append("\n  Products Requiring Restock:")
            lines.append(
                f"  {'PRODUCT ID':<12} {'NAME':<30} {'CURRENT':<8} {'MINIMUM':<8} {'REORDER':<8}"
            )
            lines.append("  " + "-" * 68)
            for item in restock_items:
                lines.append(
                    f"  {item.get('product_id', ''):<12} "
                    f"{item.get('product_name', '')[:28]:<30} "
                    f"{item.get('current_stock', 0):<8} "
                    f"{item.get('minimum_stock', 0):<8} "
                    f"{item.get('reorder_quantity', 0):<8}"
                )
            lines.append("")
        summary = report.final_output.get("summary")
        if summary:
            lines.append(f"  Summary: {summary}")
    elif report.final_output is not None:
        lines.append(f"  {report.final_output}")
    else:
        lines.append("  No final output produced.")

    if report.errors:
        lines.append("\nErrors / Warnings:")
        for err in report.errors:
            lines.append(f"  [!] {err}")

    lines.append("=" * 70)
    return "\n".join(lines)


def main() -> None:
    """Run CLI workflow execution."""
    parser = argparse.ArgumentParser(
        description="Run AI Workflow Agent on natural-language requests."
    )
    parser.add_argument(
        "request",
        nargs="?",
        default="Which products need restocking?",
        help="Natural language user request (default: 'Which products need restocking?')",
    )
    parser.add_argument(
        "--csv-path",
        default=None,
        help="Optional custom inventory CSV path",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output raw JSON execution report",
    )

    parser.add_argument(
        "--mock-route",
        default=None,
        help="Simulate router selection with a workflow ID for deterministic offline CLI demo (e.g. 'WF001')",
    )

    args = parser.parse_args()

    router = None
    if args.mock_route:
        from app.agent.provider import FakeLLMProvider
        from app.agent.router import LLMWorkflowRouter
        fake_json = json.dumps({
            "workflow_id": args.mock_route,
            "confidence": 0.95,
            "reasoning": f"Simulated routing selection for {args.mock_route}",
            "extracted_inputs": {},
            "requires_clarification": False,
        })
        router = LLMWorkflowRouter(provider=FakeLLMProvider(default_response=fake_json))

    orchestrator = WorkflowOrchestrator(router=router)

    runtime_inputs = {}
    if args.csv_path:
        runtime_inputs["csv_path"] = args.csv_path

    report = orchestrator.run(args.request, **runtime_inputs)

    if args.json:
        print(report.model_dump_json(indent=2))
    else:
        print(format_report_for_display(report))

    if report.status in ("failed", "partial_failure"):
        sys.exit(1)


if __name__ == "__main__":
    main()
