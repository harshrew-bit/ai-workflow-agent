"""Domain tools for WF010 — Workflow Performance Report.

Steps:
1. Load execution logs
2. calculate success/failure rate
3. calculate average execution time
4. identify frequent errors
5. identify slow steps
6. generate recommendations
"""

import csv
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from pydantic import BaseModel, Field

from app.tools.base import BaseTool, ToolMetadata


def _load_logs_csv(file_path: Path) -> List[Dict[str, Any]]:
    """Load workflow execution logs from CSV file."""
    if not file_path.exists():
        raise FileNotFoundError(f"Workflow logs file not found at '{file_path}'")

    logs: List[Dict[str, Any]] = []
    with file_path.open("r", encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        headers: Optional[List[str]] = None
        for raw_row in reader:
            if not raw_row or not any(field.strip() for field in raw_row):
                continue
            if raw_row[0].strip().startswith("#"):
                continue
            if headers is None:
                headers = [h.strip().lower() for h in raw_row]
                continue

            row_dict: Dict[str, Any] = {}
            for h, val in zip(headers, raw_row):
                row_dict[h] = val.strip()

            wid = row_dict.get("workflow_id", "WF000")
            wname = row_dict.get("workflow_name", "Unknown Workflow")
            step = row_dict.get("step_name", "unknown_step")
            status = row_dict.get("status", "SUCCESS").upper()
            err_msg = row_dict.get("error_message", "")

            try:
                exec_time = float(row_dict.get("execution_time_seconds", "0.0"))
            except ValueError:
                exec_time = 0.0

            logs.append({
                "log_id": row_dict.get("log_id", f"LOG-{len(logs)+1}"),
                "workflow_id": wid,
                "workflow_name": wname,
                "step_name": step,
                "execution_time_seconds": exec_time,
                "status": status,
                "error_message": err_msg,
                "timestamp": row_dict.get("timestamp", ""),
            })
    return logs


class LogLoaderTool(BaseTool):
    """Step 1 Tool: Load execution logs."""

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="log_loader",
            description="Load workflow execution telemetry logs from CSV or input records.",
        )

    def execute(
        self,
        log_file_path: Optional[str] = None,
        logs_data: Optional[List[Dict[str, Any]]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        records: List[Dict[str, Any]] = []

        if logs_data:
            records = logs_data
        elif log_file_path:
            records = _load_logs_csv(Path(log_file_path))
        else:
            default_path = Path("data/sample_workflow_logs.csv")
            if default_path.exists():
                records = _load_logs_csv(default_path)
            else:
                raise ValueError("No execution logs provided and default sample file not found.")

        return {
            "raw_logs": records,
            "total_logs": len(records),
            "summary": f"Loaded {len(records)} workflow execution log record(s).",
        }


class RateCalculatorTool(BaseTool):
    """Step 2 Tool: calculate success/failure rate."""

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="rate_calculator",
            description="Calculate success and failure rates per workflow and flag failure rates exceeding 10%.",
        )

    def execute(
        self,
        raw_logs: Optional[List[Dict[str, Any]]] = None,
        failure_threshold: float = 10.0,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        logs = raw_logs or []
        if not logs:
            return {
                "workflow_rates": {},
                "overall_success_rate": 0.0,
                "overall_failure_rate": 0.0,
                "flagged_high_failure_workflows": [],
                "summary": "No logs available to calculate success/failure rates.",
            }

        grouped: Dict[str, Dict[str, Any]] = {}
        total_success = 0
        total_failures = 0

        for r in logs:
            wid = r.get("workflow_id", "WF000")
            wname = r.get("workflow_name", wid)
            status = r.get("status", "SUCCESS").upper()

            if wid not in grouped:
                grouped[wid] = {
                    "workflow_id": wid,
                    "workflow_name": wname,
                    "total_runs": 0,
                    "success_count": 0,
                    "failure_count": 0,
                }

            grouped[wid]["total_runs"] += 1
            if status == "SUCCESS":
                grouped[wid]["success_count"] += 1
                total_success += 1
            else:
                grouped[wid]["failure_count"] += 1
                total_failures += 1

        flagged_workflows: List[str] = []
        for wid, data in grouped.items():
            tot = data["total_runs"]
            succ = data["success_count"]
            fail = data["failure_count"]
            s_rate = (succ / tot * 100) if tot > 0 else 0.0
            f_rate = (fail / tot * 100) if tot > 0 else 0.0
            data["success_rate_percent"] = round(s_rate, 1)
            data["failure_rate_percent"] = round(f_rate, 1)
            # Flag if strictly greater than failure threshold (10.0%)
            data["is_failure_flagged"] = f_rate > failure_threshold
            if f_rate > failure_threshold:
                flagged_workflows.append(wid)

        tot_all = len(logs)
        ov_succ_rate = round((total_success / tot_all * 100), 1) if tot_all > 0 else 0.0
        ov_fail_rate = round((total_failures / tot_all * 100), 1) if tot_all > 0 else 0.0

        summary_msg = (
            f"Overall Success Rate: {ov_succ_rate}% ({total_success}/{tot_all}), "
            f"Failure Rate: {ov_fail_rate}% ({total_failures}/{tot_all}). "
            f"Workflows exceeding {failure_threshold}% failure threshold: "
            f"{', '.join(flagged_workflows) if flagged_workflows else 'None'}."
        )

        return {
            "workflow_rates": grouped,
            "overall_success_rate": ov_succ_rate,
            "overall_failure_rate": ov_fail_rate,
            "flagged_high_failure_workflows": flagged_workflows,
            "summary": summary_msg,
        }


class ExecutionTimeCalculatorTool(BaseTool):
    """Step 3 Tool: calculate average execution time."""

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="execution_time_calculator",
            description="Calculate average execution times and flag workflows exceeding time threshold.",
        )

    def execute(
        self,
        raw_logs: Optional[List[Dict[str, Any]]] = None,
        time_threshold_seconds: float = 5.0,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        logs = raw_logs or []
        if not logs:
            return {
                "workflow_times": {},
                "overall_avg_time": 0.0,
                "flagged_slow_workflows": [],
                "summary": "No logs available to calculate execution times.",
            }

        grouped_times: Dict[str, List[float]] = {}
        workflow_names: Dict[str, str] = {}
        all_times: List[float] = []

        for r in logs:
            wid = r.get("workflow_id", "WF000")
            workflow_names[wid] = r.get("workflow_name", wid)
            t = r.get("execution_time_seconds", 0.0)
            if wid not in grouped_times:
                grouped_times[wid] = []
            grouped_times[wid].append(t)
            all_times.append(t)

        metrics: Dict[str, Dict[str, Any]] = {}
        flagged_slow: List[str] = []

        for wid, times in grouped_times.items():
            avg_t = sum(times) / len(times) if times else 0.0
            max_t = max(times) if times else 0.0
            min_t = min(times) if times else 0.0
            is_slow = avg_t > time_threshold_seconds

            if is_slow:
                flagged_slow.append(wid)

            metrics[wid] = {
                "workflow_id": wid,
                "workflow_name": workflow_names.get(wid, wid),
                "avg_execution_time_seconds": round(avg_t, 2),
                "min_execution_time_seconds": round(min_t, 2),
                "max_execution_time_seconds": round(max_t, 2),
                "is_slow_flagged": is_slow,
            }

        overall_avg = round(sum(all_times) / len(all_times), 2) if all_times else 0.0

        summary_msg = (
            f"Overall Avg Execution Time: {overall_avg:.2f}s. "
            f"Workflows exceeding {time_threshold_seconds}s threshold: "
            f"{', '.join(flagged_slow) if flagged_slow else 'None'}."
        )

        return {
            "workflow_times": metrics,
            "overall_avg_time": overall_avg,
            "flagged_slow_workflows": flagged_slow,
            "summary": summary_msg,
        }


class ErrorIdentifierTool(BaseTool):
    """Step 4 Tool: identify frequent errors."""

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="error_identifier",
            description="Aggregate and rank frequent error occurrences across workflow runs.",
        )

    def execute(
        self,
        raw_logs: Optional[List[Dict[str, Any]]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        logs = raw_logs or []
        failed_logs = [r for r in logs if r.get("status") != "SUCCESS"]

        error_counts: Dict[str, Dict[str, Any]] = {}
        for f in failed_logs:
            err = (f.get("error_message") or "").strip()
            if not err:
                err = f"Unspecified failure in step '{f.get('step_name')}'"

            wid = f.get("workflow_id", "WF000")
            if err not in error_counts:
                error_counts[err] = {
                    "error_message": err,
                    "count": 0,
                    "affected_workflows": set(),
                }
            error_counts[err]["count"] += 1
            error_counts[err]["affected_workflows"].add(wid)

        ranked_errors = [
            {
                "error_message": data["error_message"],
                "count": data["count"],
                "affected_workflows": sorted(list(data["affected_workflows"])),
            }
            for data in error_counts.values()
        ]
        ranked_errors.sort(key=lambda x: x["count"], reverse=True)

        summary_msg = (
            f"Identified {len(failed_logs)} failure(s) across {len(ranked_errors)} distinct error type(s)."
        )

        return {
            "frequent_errors": ranked_errors,
            "total_errors_found": len(failed_logs),
            "summary": summary_msg,
        }


class SlowStepsIdentifierTool(BaseTool):
    """Step 5 Tool: identify slow steps."""

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="slow_steps_identifier",
            description="Isolate specific steps with high average latency across executions.",
        )

    def execute(
        self,
        raw_logs: Optional[List[Dict[str, Any]]] = None,
        slow_step_threshold_seconds: float = 4.0,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        logs = raw_logs or []
        step_times: Dict[Tuple[str, str], List[float]] = {}
        workflow_names: Dict[str, str] = {}

        for r in logs:
            wid = r.get("workflow_id", "WF000")
            step = r.get("step_name", "unknown")
            workflow_names[wid] = r.get("workflow_name", wid)
            t = r.get("execution_time_seconds", 0.0)

            key = (wid, step)
            if key not in step_times:
                step_times[key] = []
            step_times[key].append(t)

        slow_steps_list: List[Dict[str, Any]] = []
        for (wid, step), times in step_times.items():
            avg_t = sum(times) / len(times) if times else 0.0
            max_t = max(times) if times else 0.0
            slow_steps_list.append({
                "workflow_id": wid,
                "workflow_name": workflow_names.get(wid, wid),
                "step_name": step,
                "run_count": len(times),
                "avg_time_seconds": round(avg_t, 2),
                "max_time_seconds": round(max_t, 2),
                "is_slow": avg_t > slow_step_threshold_seconds,
            })

        slow_steps_list.sort(key=lambda x: x["avg_time_seconds"], reverse=True)
        top_slow = [s for s in slow_steps_list if s["is_slow"]]

        return {
            "slow_steps": slow_steps_list,
            "flagged_slow_steps": top_slow,
            "summary": f"Identified {len(top_slow)} step(s) with average latency exceeding {slow_step_threshold_seconds}s.",
        }


class RecommendationsGeneratorTool(BaseTool):
    """Step 6 Tool: generate recommendations."""

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="recommendations_generator",
            description="Generate actionable operational recommendations based on failure rates and latency bottlenecks.",
        )

    def execute(
        self,
        workflow_rates: Optional[Dict[str, Any]] = None,
        workflow_times: Optional[Dict[str, Any]] = None,
        frequent_errors: Optional[List[Dict[str, Any]]] = None,
        slow_steps: Optional[List[Dict[str, Any]]] = None,
        flagged_high_failure_workflows: Optional[List[str]] = None,
        flagged_slow_workflows: Optional[List[str]] = None,
        overall_success_rate: float = 0.0,
        overall_failure_rate: float = 0.0,
        overall_avg_time: float = 0.0,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        high_fail_wfs = flagged_high_failure_workflows or []
        slow_wfs = flagged_slow_workflows or []
        errors = frequent_errors or []
        steps = slow_steps or []
        rates = workflow_rates or {}
        times = workflow_times or {}

        recommendations: List[Dict[str, str]] = []

        # 1. High failure rate recommendations
        for wid in high_fail_wfs:
            r_info = rates.get(wid, {})
            w_name = r_info.get("workflow_name", wid)
            f_rate = r_info.get("failure_rate_percent", 0.0)
            recommendations.append({
                "category": "RELIABILITY",
                "workflow_id": wid,
                "priority": "HIGH",
                "finding": f"{wid} ({w_name}) has an elevated failure rate of {f_rate}% (Threshold: 10.0%).",
                "action": f"Implement retry policies, strict schema validation, or robust error recovery in {wid}.",
            })

        # 2. Slow workflow recommendations
        for wid in slow_wfs:
            t_info = times.get(wid, {})
            w_name = t_info.get("workflow_name", wid)
            avg_t = t_info.get("avg_execution_time_seconds", 0.0)
            recommendations.append({
                "category": "PERFORMANCE",
                "workflow_id": wid,
                "priority": "MEDIUM",
                "finding": f"{wid} ({w_name}) average execution time is {avg_t}s (Threshold: 5.0s).",
                "action": f"Profile step execution in {wid}, optimize file streaming, or add caching for repetitive operations.",
            })

        # 3. Frequent error recommendations
        if errors:
            top_err = errors[0]
            recommendations.append({
                "category": "ERROR_MITIGATION",
                "workflow_id": ", ".join(top_err.get("affected_workflows", [])),
                "priority": "HIGH" if top_err.get("count", 0) > 1 else "MEDIUM",
                "finding": f"Top error ({top_err.get('count')} occurrences): '{top_err.get('error_message')}'.",
                "action": "Add upstream input sanitization or fallback handling for this error type.",
            })

        # 4. Slow step recommendations
        slow_step_candidates = [s for s in steps if s.get("is_slow")]
        if slow_step_candidates:
            slowest = slow_step_candidates[0]
            recommendations.append({
                "category": "BOTTLENECK_OPTIMIZATION",
                "workflow_id": slowest.get("workflow_id", ""),
                "priority": "MEDIUM",
                "finding": f"Step '{slowest.get('step_name')}' in {slowest.get('workflow_id')} averages {slowest.get('avg_time_seconds')}s.",
                "action": "Refactor I/O or parallelize chunk processing to reduce latency.",
            })

        if not recommendations:
            recommendations.append({
                "category": "MAINTENANCE",
                "workflow_id": "ALL",
                "priority": "LOW",
                "finding": "All monitored workflows are operating within healthy failure and latency thresholds.",
                "action": "Continue regular telemetry monitoring and review.",
            })

        summary_msg = (
            f"Generated {len(recommendations)} recommendation(s) across {len(rates)} monitored workflow(s). "
            f"Flagged {len(high_fail_wfs)} high-failure workflow(s) and {len(slow_wfs)} slow workflow(s)."
        )

        return {
            "overall_metrics": {
                "success_rate_percent": overall_success_rate,
                "failure_rate_percent": overall_failure_rate,
                "avg_execution_time_seconds": overall_avg_time,
                "total_workflows_monitored": len(rates),
            },
            "workflow_performance": rates,
            "workflow_timings": times,
            "flagged_high_failure_workflows": high_fail_wfs,
            "flagged_slow_workflows": slow_wfs,
            "frequent_errors": errors[:5],
            "slow_steps": slow_step_candidates[:5],
            "recommendations": recommendations,
            "is_simulated": True,
            "summary": summary_msg,
        }
