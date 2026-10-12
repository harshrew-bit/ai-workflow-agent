"""WF011: Supplier Delivery Risk Assessment domain tools and extension registration."""

from __future__ import annotations

import csv
from datetime import date, datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple, Union
from pydantic import BaseModel, Field

from app.engine.context import ExecutionContext
from app.models.workflow import WorkflowDefinition
from app.registry.registry import WorkflowRegistry
from app.tools.base import BaseTool, ToolMetadata
from app.tools.registry import ToolRegistry

if TYPE_CHECKING:
    from app.engine.resolver import ConfigurableStepResolver


class DeliveryRecord(BaseModel):
    """Normalized supplier delivery record."""

    delivery_id: str
    supplier_id: str
    supplier_name: str
    order_date: str
    promised_delivery_date: str
    actual_delivery_date: str
    quantity_ordered: int = 0
    quantity_delivered: int = 0
    delay_days: int = 0
    is_late: bool = False
    status: str = "DELIVERED"


class SupplierRiskMetrics(BaseModel):
    """Aggregated delivery performance metrics for a supplier."""

    supplier_id: str
    supplier_name: str
    total_shipments: int
    on_time_shipments: int
    late_shipments: int
    late_delivery_rate: float
    total_delay_days: int
    average_delay_days: float
    max_delay_days: int


class SupplierRiskEvaluation(BaseModel):
    """Risk classification and evidence evaluation for a supplier."""

    supplier_id: str
    supplier_name: str
    risk_level: str  # LOW, MEDIUM, HIGH
    risk_score: float  # 0.0 to 100.0
    late_delivery_rate: float
    average_delay_days: float
    max_delay_days: int
    total_shipments: int
    evidence: str
    recommended_action: str


def parse_iso_date(date_str: str) -> Optional[date]:
    """Parse YYYY-MM-DD date safely, returning None on failure."""
    if not date_str or not isinstance(date_str, str):
        return None
    try:
        return datetime.strptime(date_str.strip(), "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None


def calculate_supplier_metrics(
    records: List[DeliveryRecord],
) -> Dict[str, SupplierRiskMetrics]:
    """Aggregate delivery records into per-supplier metrics."""
    by_supplier: Dict[str, List[DeliveryRecord]] = {}
    for r in records:
        by_supplier.setdefault(r.supplier_id, []).append(r)

    metrics_map: Dict[str, SupplierRiskMetrics] = {}
    for supp_id, supp_records in by_supplier.items():
        supp_name = supp_records[0].supplier_name
        total = len(supp_records)
        late_records = [r for r in supp_records if r.is_late]
        late_count = len(late_records)
        on_time = total - late_count
        late_rate = late_count / total if total > 0 else 0.0

        delay_days_list = [r.delay_days for r in late_records]
        total_delay = sum(delay_days_list)
        avg_delay = (total_delay / late_count) if late_count > 0 else 0.0
        max_delay = max(delay_days_list) if delay_days_list else 0

        metrics_map[supp_id] = SupplierRiskMetrics(
            supplier_id=supp_id,
            supplier_name=supp_name,
            total_shipments=total,
            on_time_shipments=on_time,
            late_shipments=late_count,
            late_delivery_rate=round(late_rate, 4),
            total_delay_days=total_delay,
            average_delay_days=round(avg_delay, 2),
            max_delay_days=max_delay,
        )
    return metrics_map


def evaluate_supplier_risk(
    metrics: SupplierRiskMetrics,
) -> SupplierRiskEvaluation:
    """Evaluate risk score and tier using documented deterministic rules.

    Scoring formula:
        Risk Score = (late_rate * 60.0) + min(avg_delay_days * 8.0, 40.0)
        Scale: 0.0 to 100.0

    Thresholds:
        HIGH RISK:   score >= 50.0 OR late_rate >= 0.35 OR avg_delay_days >= 7.0
        MEDIUM RISK: score >= 25.0 OR late_rate >= 0.15 OR avg_delay_days >= 3.0
        LOW RISK:    otherwise
    """
    late_rate = metrics.late_delivery_rate
    avg_delay = metrics.average_delay_days

    # Deterministic risk score calculation
    score_from_rate = late_rate * 60.0
    score_from_delay = min(avg_delay * 8.0, 40.0)
    composite_score = min(100.0, max(0.0, score_from_rate + score_from_delay))
    composite_score = round(composite_score, 1)

    # Risk level categorization
    if composite_score >= 50.0 or late_rate >= 0.35 or avg_delay >= 7.0:
        level = "HIGH"
        action = "Initiate formal vendor review; identify backup sources; freeze new POs if critical."
        reason = (
            f"Exceeds high-risk threshold: late rate {late_rate:.1%} ({metrics.late_shipments}/{metrics.total_shipments}), "
            f"average delay {avg_delay:.1f} days (max {metrics.max_delay_days} days), risk score {composite_score}/100."
        )
    elif composite_score >= 25.0 or late_rate >= 0.15 or avg_delay >= 3.0:
        level = "MEDIUM"
        action = "Monitor lead times weekly; request buffer stock for critical assemblies."
        reason = (
            f"Moderate delivery variance: late rate {late_rate:.1%} ({metrics.late_shipments}/{metrics.total_shipments}), "
            f"average delay {avg_delay:.1f} days, risk score {composite_score}/100."
        )
    else:
        level = "LOW"
        action = "Maintain preferred supplier status; standard periodic review schedule."
        reason = (
            f"Stable delivery track record: late rate {late_rate:.1%} ({metrics.late_shipments}/{metrics.total_shipments}), "
            f"average delay {avg_delay:.1f} days, risk score {composite_score}/100."
        )

    return SupplierRiskEvaluation(
        supplier_id=metrics.supplier_id,
        supplier_name=metrics.supplier_name,
        risk_level=level,
        risk_score=composite_score,
        late_delivery_rate=late_rate,
        average_delay_days=avg_delay,
        max_delay_days=metrics.max_delay_days,
        total_shipments=metrics.total_shipments,
        evidence=reason,
        recommended_action=action,
    )


# --- Step Tools for WF011 ---


class SupplierDeliveryLoaderTool(BaseTool):
    """Step 1: Load supplier delivery records from CSV or runtime context."""

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="supplier_delivery_loader",
            description="Loads raw supplier delivery records from CSV or runtime inputs",
        )

    def execute(self, **kwargs: Any) -> Dict[str, Any]:
        raw_deliveries = kwargs.get("deliveries")
        csv_path = (
            kwargs.get("supplier_csv_path")
            or kwargs.get("delivery_file_path")
            or kwargs.get("csv_path")
        )

        records: List[Dict[str, Any]] = []

        if raw_deliveries is not None and isinstance(raw_deliveries, list):
            for item in raw_deliveries:
                if isinstance(item, dict):
                    records.append(item)
        elif csv_path:
            p = Path(csv_path)
            if not p.exists():
                raise FileNotFoundError(f"Supplier delivery CSV file not found at: {csv_path}")
            with open(p, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                records = [dict(row) for row in reader]
        else:
            default_p = Path(__file__).parent.parent.parent / "data" / "sample_supplier_deliveries.csv"
            if default_p.exists():
                with open(default_p, "r", encoding="utf-8") as f:
                    reader = csv.DictReader(f)
                    records = [dict(row) for row in reader]
            else:
                records = []

        return {
            "raw_records": records,
            "total_loaded": len(records),
            "summary": f"Loaded {len(records)} raw supplier delivery record(s).",
        }


class DeliveryRecordValidatorTool(BaseTool):
    """Step 2: Validate delivery records, parse dates, calculate delay days."""

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="delivery_record_validator",
            description="Validates delivery records, computes delay days, and identifies invalid rows",
        )

    def execute(self, **kwargs: Any) -> Dict[str, Any]:
        raw_records = kwargs.get("raw_records") or []
        last_out = kwargs.get("last_output")
        if not raw_records and isinstance(last_out, dict):
            raw_records = last_out.get("raw_records", [])

        valid_records: List[DeliveryRecord] = []
        invalid_records: List[Dict[str, Any]] = []

        required_keys = ["supplier_id", "supplier_name", "promised_delivery_date", "actual_delivery_date"]

        for idx, row in enumerate(raw_records, start=1):
            missing = [k for k in required_keys if not str(row.get(k, "")).strip()]
            if missing:
                invalid_records.append({
                    "row_index": idx,
                    "record": row,
                    "reason": f"Missing required fields: {', '.join(missing)}",
                })
                continue

            promised = parse_iso_date(str(row.get("promised_delivery_date", "")))
            actual = parse_iso_date(str(row.get("actual_delivery_date", "")))

            if not promised or not actual:
                invalid_records.append({
                    "row_index": idx,
                    "record": row,
                    "reason": "Invalid date format; expected YYYY-MM-DD",
                })
                continue

            delay_days = (actual - promised).days
            is_late = delay_days > 0

            try:
                qty_ord = int(row.get("quantity_ordered", 0))
                qty_del = int(row.get("quantity_delivered", qty_ord))
            except (ValueError, TypeError):
                qty_ord = 0
                qty_del = 0

            record = DeliveryRecord(
                delivery_id=str(row.get("delivery_id", f"DEL-{idx}")).strip(),
                supplier_id=str(row.get("supplier_id", "")).strip(),
                supplier_name=str(row.get("supplier_name", "")).strip(),
                order_date=str(row.get("order_date", "")).strip(),
                promised_delivery_date=str(row.get("promised_delivery_date", "")).strip(),
                actual_delivery_date=str(row.get("actual_delivery_date", "")).strip(),
                quantity_ordered=qty_ord,
                quantity_delivered=qty_del,
                delay_days=delay_days,
                is_late=is_late,
                status=str(row.get("status", "DELIVERED")).strip(),
            )
            valid_records.append(record)

        return {
            "validated_records": [r.model_dump() for r in valid_records],
            "valid_count": len(valid_records),
            "invalid_count": len(invalid_records),
            "invalid_records": invalid_records,
            "summary": (
                f"Validated {len(raw_records)} record(s): {len(valid_records)} valid, "
                f"{len(invalid_records)} malformed or incomplete."
            ),
        }


class DeliveryMetricsCalculatorTool(BaseTool):
    """Step 3: Calculate supplier delivery performance metrics."""

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="delivery_metrics_calculator",
            description="Aggregates supplier delivery records into late rates and delay statistics",
        )

    def execute(self, **kwargs: Any) -> Dict[str, Any]:
        val_records_data = kwargs.get("validated_records")
        last_out = kwargs.get("last_output")
        if not val_records_data and isinstance(last_out, dict):
            val_records_data = last_out.get("validated_records", [])

        records = [DeliveryRecord(**r) for r in (val_records_data or [])]
        metrics_map = calculate_supplier_metrics(records)

        return {
            "supplier_metrics": {k: v.model_dump() for k, v in metrics_map.items()},
            "suppliers_count": len(metrics_map),
            "summary": f"Calculated delivery performance metrics for {len(metrics_map)} supplier(s).",
        }


class SupplierRiskEvaluatorTool(BaseTool):
    """Step 4: Evaluate supplier risk levels and evidence."""

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="supplier_risk_evaluator",
            description="Evaluates risk scores, applies thresholds, and categorizes suppliers as LOW, MEDIUM, or HIGH risk",
        )

    def execute(self, **kwargs: Any) -> Dict[str, Any]:
        metrics_data = kwargs.get("supplier_metrics")
        last_out = kwargs.get("last_output")
        if not metrics_data and isinstance(last_out, dict):
            metrics_data = last_out.get("supplier_metrics", {})

        evaluations: List[SupplierRiskEvaluation] = []
        for supp_id, m_dict in (metrics_data or {}).items():
            metrics = SupplierRiskMetrics(**m_dict)
            ev = evaluate_supplier_risk(metrics)
            evaluations.append(ev)

        # Sort: High risk first, then by risk score descending
        risk_rank = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
        evaluations.sort(key=lambda x: (risk_rank.get(x.risk_level, 3), -x.risk_score))

        high_count = sum(1 for e in evaluations if e.risk_level == "HIGH")
        med_count = sum(1 for e in evaluations if e.risk_level == "MEDIUM")
        low_count = sum(1 for e in evaluations if e.risk_level == "LOW")

        return {
            "evaluations": [e.model_dump() for e in evaluations],
            "high_risk_count": high_count,
            "medium_risk_count": med_count,
            "low_risk_count": low_count,
            "summary": (
                f"Evaluated {len(evaluations)} supplier(s): {high_count} HIGH risk, "
                f"{med_count} MEDIUM risk, {low_count} LOW risk."
            ),
        }


class SupplierRiskReporterTool(BaseTool):
    """Step 5: Generate final structured supplier risk report."""

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="supplier_risk_reporter",
            description="Compiles final structured supplier delivery risk assessment report",
        )

    def execute(self, **kwargs: Any) -> Dict[str, Any]:
        evals_data = kwargs.get("evaluations")
        high_cnt = kwargs.get("high_risk_count", 0)
        med_cnt = kwargs.get("medium_risk_count", 0)
        low_cnt = kwargs.get("low_risk_count", 0)

        last_out = kwargs.get("last_output")
        if not evals_data and isinstance(last_out, dict):
            evals_data = last_out.get("evaluations", [])
            high_cnt = last_out.get("high_risk_count", high_cnt)
            med_cnt = last_out.get("medium_risk_count", med_cnt)
            low_cnt = last_out.get("low_risk_count", low_cnt)

        evals_data = evals_data or []
        high_risk_suppliers = [
            e["supplier_name"] for e in evals_data if e.get("risk_level") == "HIGH"
        ]

        summary = (
            f"Assessed {len(evals_data)} supplier(s). Identified {high_cnt} HIGH risk supplier(s) "
            f"requiring operational mitigation."
        )

        return {
            "total_suppliers_assessed": len(evals_data),
            "risk_distribution": {
                "high": high_cnt,
                "medium": med_cnt,
                "low": low_cnt,
            },
            "supplier_evaluations": evals_data,
            "high_risk_suppliers": high_risk_suppliers,
            "summary": summary,
            "is_simulated": True,
        }


# --- Demonstration Extension Registration ---


def get_wf011_definition() -> WorkflowDefinition:
    """Return the official demonstration WorkflowDefinition for WF011."""
    return WorkflowDefinition(
        Workflow_ID="WF011",
        Workflow_Name="Supplier Delivery Risk Assessment",
        Trigger="Periodic supplier audit, purchase order review, or vendor delivery risk evaluation",
        Inputs="Supplier delivery records or CSV file; optional delivery risk thresholds",
        Steps="Load supplier delivery records -> Validate delivery records -> Calculate supplier delivery metrics -> Evaluate supplier risk levels -> Generate supplier risk report",
        Decision_Logic="Calculate late delivery rate and average delay days. Flag HIGH risk if risk score >= 50.0, late rate >= 35%, or average delay >= 7.0 days; MEDIUM risk if risk score >= 25.0, late rate >= 15%, or average delay >= 3.0 days; LOW risk otherwise.",
        Tools_Required="supplier_delivery_loader, delivery_record_validator, delivery_metrics_calculator, supplier_risk_evaluator, supplier_risk_reporter",
        Expected_Output="Structured supplier delivery risk assessment report with supplier evaluations, risk scores, late rates, average delay days, and recommended mitigation actions.",
    )


def register_wf011_extension(
    registry: Optional[WorkflowRegistry] = None,
    tool_registry: Optional[ToolRegistry] = None,
    step_resolver: Optional[ConfigurableStepResolver] = None,
) -> WorkflowDefinition:
    """Register WF011 into the provided registry, tool_registry, and step_resolver.

    Demonstrates extending the system with an 11th workflow without modifying
    the generic execution engine or existing workflows.
    """
    wf011 = get_wf011_definition()

    # 1. Register tools if tool_registry provided
    if tool_registry is not None:
        tool_registry.register(SupplierDeliveryLoaderTool(), allow_overwrite=True)
        tool_registry.register(DeliveryRecordValidatorTool(), allow_overwrite=True)
        tool_registry.register(DeliveryMetricsCalculatorTool(), allow_overwrite=True)
        tool_registry.register(SupplierRiskEvaluatorTool(), allow_overwrite=True)
        tool_registry.register(SupplierRiskReporterTool(), allow_overwrite=True)

    # 2. Register step bindings if step_resolver provided
    if step_resolver is not None:
        step_resolver.bind(
            workflow_id="WF011",
            step_name="Load supplier delivery records",
            tool_name="supplier_delivery_loader",
        )
        step_resolver.bind(
            workflow_id="WF011",
            step_name="Validate delivery records",
            tool_name="delivery_record_validator",
        )
        step_resolver.bind(
            workflow_id="WF011",
            step_name="Calculate supplier delivery metrics",
            tool_name="delivery_metrics_calculator",
        )
        step_resolver.bind(
            workflow_id="WF011",
            step_name="Evaluate supplier risk levels",
            tool_name="supplier_risk_evaluator",
        )
        step_resolver.bind(
            workflow_id="WF011",
            step_name="Generate supplier risk report",
            tool_name="supplier_risk_reporter",
        )

    # 3. Register workflow definition if registry provided
    if registry is not None:
        registry.register(wf011, allow_overwrite=True)

    return wf011
