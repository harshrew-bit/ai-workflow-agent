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
        # WF001: Restock list
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

        # WF002: Product Price Validation
        matched_prices = report.final_output.get("matched_products")
        if matched_prices:
            lines.append("\n  Price Validation Results:")
            lines.append(
                f"  {'SKU':<10} {'NAME':<28} {'INTERNAL':<10} {'VENDOR':<10} {'DIFF %':<8} {'STATUS':<20}"
            )
            lines.append("  " + "-" * 88)
            for item in matched_prices:
                status_label = "EXCEPTION (>10%)" if item.get("is_exception") else "COMPLIANT"
                lines.append(
                    f"  {item.get('sku', ''):<10} "
                    f"{item.get('product_name', '')[:26]:<28} "
                    f"${item.get('internal_price', 0):<9.2f} "
                    f"${item.get('vendor_price', 0):<9.2f} "
                    f"{item.get('percentage_difference', 0):<7.1f}% "
                    f"{status_label:<20}"
                )
            lines.append("")
            exceptions = report.final_output.get("exceptions", [])
            lines.append(f"  Exceptions Flagged: {len(exceptions)} item(s)")
            unmatched_v = report.final_output.get("unmatched_vendor_records", [])
            if unmatched_v:
                lines.append(f"  Unmatched Vendor SKUs: {len(unmatched_v)} record(s)")

        # WF003: Vendor File Processing
        cleaned_records = report.final_output.get("cleaned_records")
        if cleaned_records is not None:
            invalid_records = report.final_output.get("invalid_records", [])
            lines.append(f"\n  Valid Records Cleaned: {len(cleaned_records)}")
            lines.append(f"  Invalid Rows Flagged:  {len(invalid_records)}")
            if invalid_records:
                lines.append("\n  Invalid Rows Report:")
                for inv in invalid_records[:10]:
                    row_no = inv.get("row_number", "?")
                    errs = "; ".join(inv.get("errors", []))
                    lines.append(f"    - Row {row_no}: {errs}")
                if len(invalid_records) > 10:
                    lines.append(f"    ... and {len(invalid_records) - 10} more invalid row(s).")
            lines.append("")

        # WF004: Product Description Generator
        if "product_description" in report.final_output and "seo_title" in report.final_output:
            lines.append(f"\n  Product Name:        {report.final_output.get('product_name')}")
            lines.append(f"  SEO Title:           {report.final_output.get('seo_title')}")
            lines.append(f"  Meta Description:    {report.final_output.get('meta_description')}")
            lines.append(f"  Short Description:   {report.final_output.get('short_description')}")
            lines.append(f"\n  Full Product Description:\n  {report.final_output.get('product_description')}")
            missing_attrs = report.final_output.get("missing_attributes", [])
            if missing_attrs:
                lines.append(f"\n  Omitted / Missing Attributes: {', '.join(missing_attrs)} (Not invented)")
            if report.final_output.get("is_simulated"):
                lines.append("  [Notice: Output generated via offline simulated content synthesis]")
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
        help="Optional custom inventory CSV path (WF001)",
    )
    parser.add_argument(
        "--internal-csv",
        default=None,
        help="Optional custom internal prices CSV path (WF002)",
    )
    parser.add_argument(
        "--vendor-csv",
        default=None,
        help="Optional custom vendor prices CSV path (WF002)",
    )
    parser.add_argument(
        "--vendor-file",
        default=None,
        help="Optional vendor file path (WF003)",
    )
    parser.add_argument(
        "--product-name",
        default=None,
        help="Product name for description generation (WF004)",
    )
    parser.add_argument(
        "--category",
        default=None,
        help="Product category (WF004)",
    )
    parser.add_argument(
        "--material",
        default=None,
        help="Product material (WF004)",
    )
    parser.add_argument(
        "--color",
        default=None,
        help="Product color (WF004)",
    )
    parser.add_argument(
        "--target-audience",
        default=None,
        help="Target audience (WF004)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output raw JSON execution report",
    )

    parser.add_argument(
        "--mock-route",
        default=None,
        help="Simulate router selection with a workflow ID for deterministic offline CLI demo (e.g. 'WF001', 'WF002', 'WF003', 'WF004')",
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
    if args.internal_csv:
        runtime_inputs["internal_csv_path"] = args.internal_csv
    if args.vendor_csv:
        runtime_inputs["vendor_csv_path"] = args.vendor_csv
    if args.vendor_file:
        runtime_inputs["file_path"] = args.vendor_file
    if args.product_name:
        runtime_inputs["product_name"] = args.product_name
    elif args.mock_route == "WF004" and not args.product_name:
        # Default sample product name if none provided for demo
        runtime_inputs["product_name"] = "Ergonomic Desk Chair"
        runtime_inputs["category"] = "Office Furniture"
        runtime_inputs["material"] = "Breathable Mesh"
        runtime_inputs["color"] = "Charcoal Black"
        runtime_inputs["target_audience"] = "Remote Professionals"
    if args.category:
        runtime_inputs["category"] = args.category
    if args.material:
        runtime_inputs["material"] = args.material
    if args.color:
        runtime_inputs["color"] = args.color
    if args.target_audience:
        runtime_inputs["target_audience"] = args.target_audience

    report = orchestrator.run(args.request, **runtime_inputs)

    if args.json:
        print(report.model_dump_json(indent=2))
    else:
        print(format_report_for_display(report))

    if report.status in ("failed", "partial_failure"):
        sys.exit(1)


if __name__ == "__main__":
    main()
