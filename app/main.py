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

            unmatched_i = report.final_output.get("unmatched_internal_records", [])
            if unmatched_i:
                lines.append(f"  Unmatched Internal SKUs: {len(unmatched_i)} record(s)")
                for item in unmatched_i:
                    lines.append(
                        f"    - {item.get('sku', '')}: "
                        f"{item.get('reason', 'No matching vendor price record')}"
                    )


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

        # WF008: SEO Keyword Classification
        if "keyword_records" in report.final_output:
            records = report.final_output.get("keyword_records", [])
            lines.append(f"\n  SEO Keyword Classification ({len(records)} unique keywords processed):")
            lines.append(
                f"  {'KEYWORD':<34} {'INTENT':<15} {'CATEGORY':<24} {'PRIORITY':<10} {'TARGET PAGE':<28}"
            )
            lines.append("  " + "-" * 115)
            for r in records[:10]:
                kw = r.get("keyword", "")[:32]
                intent = r.get("intent", "").upper()
                cat = r.get("category", "")[:22]
                pri = r.get("priority", "")
                target = r.get("target_page", "")[:26]
                lines.append(f"  {kw:<34} {intent:<15} {cat:<24} {pri:<10} {target:<28}")
            lines.append("")
            lines.append(f"  High Priority:   {report.final_output.get('high_priority_count', 0)} keyword(s)")
            lines.append(f"  Medium Priority: {report.final_output.get('medium_priority_count', 0)} keyword(s)")
            lines.append(f"  Low Priority:    {report.final_output.get('low_priority_count', 0)} keyword(s)")

            ic = report.final_output.get("intent_counts", {})
            if ic:
                lines.append(f"  Intent Distribution: {ic.get('transactional', 0)} Transactional, {ic.get('commercial', 0)} Commercial, {ic.get('informational', 0)} Informational, {ic.get('navigational', 0)} Navigational")

            if report.final_output.get("is_simulated"):
                lines.append("  [Notice: SEO keyword classification generated via deterministic rule set (SIMULATED)]")
            lines.append("")

        # WF009: Employee Task Assignment
        if "assignment_status" in report.final_output:
            status = report.final_output.get("assignment_status")
            reqs = report.final_output.get("task_requirements", {})
            lines.append("\n  Task Assignment Decision:")
            lines.append(f"    Task:             {reqs.get('description')}")
            lines.append(f"    Required Skills:  {', '.join(reqs.get('required_skills', []))}")
            lines.append(f"    Priority / Due:   {reqs.get('priority')} (Deadline: {reqs.get('deadline')})")
            lines.append(f"    Status:           {status}")

            if status == "ASSIGNED":
                assigned = report.final_output.get("assigned_employee", {})
                lines.append("\n  Recommended Assignee:")
                lines.append(f"    Employee:         {assigned.get('name')} ({assigned.get('employee_id')}) — {assigned.get('role')}")
                lines.append(f"    Suitability:      {assigned.get('composite_score', 0):.3f} composite score")
                lines.append(f"    Matching Skills:  {', '.join(assigned.get('matching_skills', []))}")
                lines.append(f"    Workload:         {assigned.get('current_workload_hours')}h logged ({assigned.get('available_hours')}h available)")
                lines.append(f"    Reasoning:        {assigned.get('ranking_explanation')}")
            else:
                lines.append(f"\n  [!] Escalation Reason: {report.final_output.get('escalation_reason')}")
                lines.append("  Recommendation: Reassign lower-priority tasks or bring in external contractor.")

            top_cands = report.final_output.get("top_candidates", [])
            if top_cands:
                lines.append("\n  Candidate Evaluation Ranking:")
                lines.append(f"    {'CANDIDATE':<22} {'ROLE':<26} {'SKILL MATCH':<14} {'AVAILABLE':<12} {'COMPOSITE':<10}")
                lines.append("    " + "-" * 88)
                for tc in top_cands:
                    c_name = tc.get("name", "")[:20]
                    c_role = tc.get("role", "")[:24]
                    sm = tc.get("skill_match", "")
                    av = f"{tc.get('available_hours', 0)}h"
                    comp = f"{tc.get('composite_score', 0):.3f}"
                    lines.append(f"    {c_name:<22} {c_role:<26} {sm:<14} {av:<12} {comp:<10}")

            if report.final_output.get("is_simulated"):
                lines.append("\n  [Notice: Employee assignment recommendation evaluated without external HR modifications (SIMULATED)]")
            lines.append("")

        # WF010: Workflow Performance Report
        if "workflow_performance" in report.final_output:
            ov = report.final_output.get("overall_metrics", {})
            w_rates = report.final_output.get("workflow_performance", {})
            w_times = report.final_output.get("workflow_timings", {})
            lines.append("\n  Workflow Performance & Reliability Summary:")
            lines.append(f"    Overall Success Rate: {ov.get('success_rate_percent', 0):.1f}%")
            lines.append(f"    Overall Failure Rate: {ov.get('failure_rate_percent', 0):.1f}%")
            lines.append(f"    Overall Average Time: {ov.get('avg_execution_time_seconds', 0):.2f}s")
            lines.append(f"    Monitored Workflows:  {ov.get('total_workflows_monitored', 0)}")

            flagged_fail = report.final_output.get("flagged_high_failure_workflows", [])
            flagged_slow = report.final_output.get("flagged_slow_workflows", [])
            if flagged_fail:
                lines.append(f"    [!] Flagged High Failure (>10%): {', '.join(flagged_fail)}")
            if flagged_slow:
                lines.append(f"    [!] Flagged Slow Latency (>5.0s): {', '.join(flagged_slow)}")

            lines.append("\n  Workflow Health Matrix:")
            lines.append(
                f"    {'WORKFLOW':<8} {'NAME':<30} {'RUNS':<8} {'SUCCESS':<10} {'FAILURE':<10} {'AVG TIME':<10} {'STATUS':<12}"
            )
            lines.append("    " + "-" * 92)
            for wid, r_data in w_rates.items():
                t_data = w_times.get(wid, {})
                w_name = r_data.get("workflow_name", wid)[:28]
                tot = r_data.get("total_runs", 0)
                s_pct = f"{r_data.get('success_rate_percent', 0):.1f}%"
                f_pct = f"{r_data.get('failure_rate_percent', 0):.1f}%"
                avg_t = f"{t_data.get('avg_execution_time_seconds', 0):.2f}s"
                status_label = "HEALTHY"
                if r_data.get("is_failure_flagged") and t_data.get("is_slow_flagged"):
                    status_label = "CRITICAL"
                elif r_data.get("is_failure_flagged"):
                    status_label = "HIGH FAILURE"
                elif t_data.get("is_slow_flagged"):
                    status_label = "SLOW"

                lines.append(f"    {wid:<8} {w_name:<30} {tot:<8} {s_pct:<10} {f_pct:<10} {avg_t:<10} {status_label:<12}")

            recs = report.final_output.get("recommendations", [])
            if recs:
                lines.append("\n  Key Improvement Recommendations:")
                for rc in recs:
                    lines.append(f"    - [{rc.get('priority')}] {rc.get('workflow_id')}: {rc.get('action')}")

            if report.final_output.get("is_simulated"):
                lines.append("\n  [Notice: Performance metrics computed from local execution logs, not production telemetry (SIMULATED)]")
            lines.append("")

        # WF011: Supplier Delivery Risk Assessment
        if "supplier_evaluations" in report.final_output:
            supp_evals = report.final_output.get("supplier_evaluations", [])
            dist = report.final_output.get("risk_distribution", {})
            lines.append(f"\n  Supplier Delivery Risk Assessment ({len(supp_evals)} suppliers assessed):")
            lines.append(
                f"    {'SUPPLIER NAME':<30} {'RISK LEVEL':<12} {'SCORE':<8} {'LATE RATE':<12} {'AVG DELAY':<12} {'RECOMMENDED ACTION':<32}"
            )
            lines.append("    " + "-" * 110)
            for se in supp_evals:
                s_name = se.get("supplier_name", "")[:28]
                r_level = se.get("risk_level", "LOW")
                r_score = f"{se.get('risk_score', 0):.1f}"
                l_rate = f"{se.get('late_delivery_rate', 0):.1%}"
                a_delay = f"{se.get('average_delay_days', 0):.1f}d"
                act = se.get("recommended_action", "")[:30]
                lines.append(f"    {s_name:<30} {r_level:<12} {r_score:<8} {l_rate:<12} {a_delay:<12} {act:<32}")
            lines.append("")
            lines.append(f"  Risk Breakdown: {dist.get('high', 0)} High Risk, {dist.get('medium', 0)} Medium Risk, {dist.get('low', 0)} Low Risk")
            high_supps = report.final_output.get("high_risk_suppliers", [])
            if high_supps:
                lines.append(f"  [!] High Risk Suppliers Flagged: {', '.join(high_supps)}")
            if report.final_output.get("is_simulated"):
                lines.append("  [Notice: Supplier delivery risk assessment evaluated from simulated delivery logs (SIMULATED)]")
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
        "--keyword-csv",
        default=None,
        help="Keyword CSV path (WF008)",
    )
    parser.add_argument(
        "--keywords",
        default=None,
        help="Direct keywords list or text (WF008)",
    )
    parser.add_argument(
        "--task-desc",
        default=None,
        help="Task description (WF009)",
    )
    parser.add_argument(
        "--skills",
        default=None,
        help="Required skills for task (WF009)",
    )
    parser.add_argument(
        "--employee-csv",
        default=None,
        help="Employee CSV path (WF009)",
    )
    parser.add_argument(
        "--task-priority",
        default=None,
        help="Task priority (WF009)",
    )
    parser.add_argument(
        "--deadline",
        default=None,
        help="Task deadline (WF009)",
    )
    parser.add_argument(
        "--log-csv",
        default=None,
        help="Workflow execution log CSV path (WF010)",
    )
    parser.add_argument(
        "--failure-threshold",
        type=float,
        default=10.0,
        help="Failure rate alert threshold percentage (WF010, default 10.0)",
    )
    parser.add_argument(
        "--time-threshold",
        type=float,
        default=5.0,
        help="Average execution time alert threshold in seconds (WF010, default 5.0)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output raw JSON execution report",
    )

    parser.add_argument(
        "--mock-route",
        default=None,
        help="Simulate router selection with a workflow ID (e.g. 'WF001' to 'WF011')",
    )
    parser.add_argument(
        "--enable-wf011",
        action="store_true",
        help="Enable demonstration extension WF011 (Supplier Delivery Risk Assessment)",
    )
    parser.add_argument(
        "--supplier-csv",
        default=None,
        help="Supplier delivery records CSV path (WF011)",
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

    if args.enable_wf011 or args.mock_route == "WF011":
        from app.tools.supplier_risk import register_wf011_extension
        register_wf011_extension(
            registry=orchestrator.registry,
            tool_registry=orchestrator.tool_registry,
            step_resolver=orchestrator.step_resolver,
        )

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

    # WF008 inputs
    if args.keyword_csv:
        runtime_inputs["keyword_file_path"] = args.keyword_csv
    if args.keywords:
        runtime_inputs["keywords"] = args.keywords

    # WF009 inputs
    if args.task_desc:
        runtime_inputs["task_description"] = args.task_desc
    elif args.mock_route == "WF009" and not args.task_desc:
        runtime_inputs["task_description"] = "Build secure REST API endpoint for user profile export in FastAPI with PostgreSQL"
        runtime_inputs["required_skills"] = "python, fastapi, postgresql"
        runtime_inputs["priority"] = "Urgent"
    if args.skills:
        runtime_inputs["required_skills"] = args.skills
    if args.employee_csv:
        runtime_inputs["employee_file_path"] = args.employee_csv
    if args.task_priority:
        runtime_inputs["priority"] = args.task_priority
    if args.deadline:
        runtime_inputs["deadline"] = args.deadline

    # WF010 inputs
    if args.log_csv:
        runtime_inputs["log_file_path"] = args.log_csv
    if args.failure_threshold is not None:
        runtime_inputs["failure_threshold"] = args.failure_threshold
    if args.time_threshold is not None:
        runtime_inputs["time_threshold_seconds"] = args.time_threshold

    # WF011 inputs
    if args.supplier_csv:
        runtime_inputs["supplier_csv_path"] = args.supplier_csv

    report = orchestrator.run(args.request, **runtime_inputs)

    if args.json:
        print(report.model_dump_json(indent=2))
    else:
        print(format_report_for_display(report))

    if report.status in ("failed", "partial_failure"):
        sys.exit(1)


if __name__ == "__main__":
    main()
