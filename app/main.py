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

        # WF005: Customer Order Status
        if "order_found" in report.final_output or "request_another_identifier" in report.final_output:
            orders_list = report.final_output.get("orders", [])
            if orders_list:
                lines.append("\n  Order Status & Fulfillment Details:")
                for ord_info in orders_list:
                    lines.append(f"    Order ID:           {ord_info.get('order_id')}")
                    lines.append(f"    Order Status:       {ord_info.get('order_status')}")
                    lines.append(f"    Order Date:         {ord_info.get('order_date')}")
                    lines.append(f"    Items:              {ord_info.get('items')}")
                    lines.append(f"    Total Amount:       ${ord_info.get('total_amount', 0):.2f} {ord_info.get('currency', 'USD')}")
                    lines.append(f"    Shipment Status:    {ord_info.get('shipment_status')}")
                    lines.append(f"    Carrier:            {ord_info.get('carrier')}")
                    lines.append(f"    Tracking Number:    {ord_info.get('tracking_number')}")
                    lines.append(f"    Estimated Delivery: {ord_info.get('estimated_delivery')}")
                    lines.append(f"    Current Location:   {ord_info.get('last_location')}")
                    lines.append("")
                if report.final_output.get("is_simulated"):
                    lines.append("  [Notice: Order & fulfillment data retrieved from local simulated records (SIMULATED)]")
                    lines.append("")
            else:
                lines.append(f"\n  [!] {report.final_output.get('summary')}")
                if report.final_output.get("is_simulated"):
                    lines.append("  [Notice: Order query executed against local simulated records (SIMULATED)]")
                lines.append("")

        # WF006: Duplicate Product Detection
        if "duplicate_candidates" in report.final_output:
            candidates = report.final_output.get("duplicate_candidates", [])
            lines.append(f"\n  Duplicate Product Analysis ({len(candidates)} candidate pairs found):")
            lines.append(
                f"  {'PRIMARY PRODUCT / SKU':<36} {'DUPLICATE CANDIDATE / SKU':<36} {'SIMILARITY':<12} {'CONFIDENCE':<12}"
            )
            lines.append("  " + "-" * 98)
            for c in candidates:
                p1 = f"{c.get('primary_name', '')[:22]} ({c.get('primary_sku', '')})"
                p2 = f"{c.get('duplicate_name', '')[:22]} ({c.get('duplicate_sku', '')})"
                score_str = f"{c.get('similarity_score', 0):.0%}"
                conf_str = c.get("confidence", "").upper()
                lines.append(f"  {p1:<36} {p2:<36} {score_str:<12} {conf_str:<12}")
            lines.append("")
            lines.append(f"  Definite Duplicates (Exact SKU):    {report.final_output.get('definite_duplicates_count', 0)}")
            lines.append(f"  Likely Duplicates (High Overlap):   {report.final_output.get('likely_duplicates_count', 0)}")
            lines.append(f"  Possible Duplicates (Review Req):   {report.final_output.get('possible_duplicates_count', 0)}")
            lines.append("")
            methodology = report.final_output.get("methodology")
            if methodology:
                lines.append(f"  LIMITATIONS & METHODOLOGY: {methodology}")
                lines.append("")

        # WF007: Marketing Campaign Brief
        if "execution_checklist" in report.final_output and "campaign_goal" in report.final_output:
            lines.append(f"\n  Campaign Goal:       {report.final_output.get('campaign_goal')}")
            lines.append(f"  Schedule/Timeline:   {report.final_output.get('timeline')}")
            lines.append(f"  Target Audience:     {report.final_output.get('target_audience')}")
            lines.append(f"  Promotion:           {report.final_output.get('promotion')}")
            featured_p = report.final_output.get("featured_products", [])
            if featured_p:
                lines.append(f"  Featured Products:   {', '.join(featured_p)}")

            messaging = report.final_output.get("messaging", {})
            if messaging:
                lines.append(f"\n  Headline:            {messaging.get('primary_headline')}")
                lines.append(f"  Value Callout:       {messaging.get('promotional_callout')}")

            channels = report.final_output.get("channels", [])
            if channels:
                lines.append("\n  Channel Strategy:")
                for ch in channels:
                    lines.append(f"    - {ch.get('channel')}: {ch.get('role')}")

            checklist = report.final_output.get("execution_checklist", [])
            if checklist:
                lines.append("\n  Execution Checklist:")
                for item in checklist:
                    lines.append(f"    [ ] {item.get('phase')}: {item.get('task')}")
            if report.final_output.get("is_simulated"):
                lines.append("\n  [Notice: Campaign brief generated via offline deterministic synthesis (SIMULATED)]")
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
        help="Natural language user request",
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
        help="Target audience (WF004, WF007)",
    )
    parser.add_argument(
        "--order-id",
        default=None,
        help="Order ID for order status lookup (WF005)",
    )
    parser.add_argument(
        "--customer-email",
        default=None,
        help="Customer email for order status lookup (WF005)",
    )
    parser.add_argument(
        "--catalog-csv",
        default=None,
        help="Catalog CSV path for duplicate detection (WF006)",
    )
    parser.add_argument(
        "--campaign-goal",
        default=None,
        help="Marketing campaign goal (WF007)",
    )
    parser.add_argument(
        "--dates",
        default=None,
        help="Campaign dates or timeline (WF007)",
    )
    parser.add_argument(
        "--promotion",
        default=None,
        help="Campaign promotion details (WF007)",
    )
    parser.add_argument(
        "--products",
        default=None,
        help="Featured campaign products (WF007)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output raw JSON execution report",
    )

    parser.add_argument(
        "--mock-route",
        default=None,
        help="Simulate router selection with a workflow ID (e.g. 'WF001' to 'WF007')",
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
    if args.order_id:
        runtime_inputs["order_id"] = args.order_id
    if args.customer_email:
        runtime_inputs["customer_email"] = args.customer_email
    if args.catalog_csv:
        runtime_inputs["catalog_csv_path"] = args.catalog_csv
    if args.campaign_goal:
        runtime_inputs["campaign_goal"] = args.campaign_goal
    elif args.mock_route == "WF007" and not args.campaign_goal:
        runtime_inputs["campaign_goal"] = "Launch New Sustainable Workspace Collection"
        runtime_inputs["dates"] = "2026-11-01 to 2026-11-30"
        runtime_inputs["target_audience"] = "Remote Professionals"
        runtime_inputs["promotion"] = "15% off launch bundles with code ECO15"
        runtime_inputs["product_list"] = ["Bamboo Desk Organizer", "Ergonomic Hemp Chair"]
    if args.dates:
        runtime_inputs["dates"] = args.dates
    if args.promotion:
        runtime_inputs["promotion"] = args.promotion
    if args.products:
        runtime_inputs["product_list"] = args.products

    report = orchestrator.run(args.request, **runtime_inputs)

    if args.json:
        print(report.model_dump_json(indent=2))
    else:
        print(format_report_for_display(report))

    if report.status in ("failed", "partial_failure"):
        sys.exit(1)


if __name__ == "__main__":
    main()
