"""Unit and step-by-step tests for WF010 — Workflow Performance Report."""

from pathlib import Path
import pytest

from app.tools.performance_report import (
    ErrorIdentifierTool,
    ExecutionTimeCalculatorTool,
    LogLoaderTool,
    RateCalculatorTool,
    RecommendationsGeneratorTool,
    SlowStepsIdentifierTool,
    _load_logs_csv,
)


def test_load_sample_workflow_logs():
    """Verify loading sample execution logs CSV."""
    logs = _load_logs_csv(Path("data/sample_workflow_logs.csv"))
    assert len(logs) >= 25
    wids = {l["workflow_id"] for l in logs}
    assert "WF001" in wids
    assert "WF003" in wids


def test_rate_calculator_flags_failure_above_10_percent():
    """Verify rate calculator flags workflows with failure rate strictly > 10%."""
    calc = RateCalculatorTool()
    logs = _load_logs_csv(Path("data/sample_workflow_logs.csv"))

    res = calc.execute(raw_logs=logs, failure_threshold=10.0)
    w_rates = res["workflow_rates"]

    assert "WF003" in res["flagged_high_failure_workflows"]
    assert w_rates["WF003"]["failure_rate_percent"] > 10.0
    assert w_rates["WF003"]["is_failure_flagged"] is True

    # WF001 has 0% failure
    assert w_rates["WF001"]["failure_rate_percent"] == 0.0
    assert w_rates["WF001"]["is_failure_flagged"] is False


def test_execution_time_calculator_flags_slow_workflows():
    """Verify time calculator flags workflows exceeding time threshold."""
    time_calc = ExecutionTimeCalculatorTool()
    logs = _load_logs_csv(Path("data/sample_workflow_logs.csv"))

    res = time_calc.execute(raw_logs=logs, time_threshold_seconds=5.0)
    w_times = res["workflow_times"]

    assert "WF003" in res["flagged_slow_workflows"]
    assert w_times["WF003"]["avg_execution_time_seconds"] > 5.0

    # WF001 is fast (< 1s)
    assert w_times["WF001"]["avg_execution_time_seconds"] < 1.0
    assert "WF001" not in res["flagged_slow_workflows"]


def test_error_identifier_ranks_frequent_errors():
    """Verify grouping and ranking of frequent errors."""
    err_tool = ErrorIdentifierTool()
    logs = _load_logs_csv(Path("data/sample_workflow_logs.csv"))

    res = err_tool.execute(raw_logs=logs)
    errors = res["frequent_errors"]

    assert len(errors) > 0
    top_err = errors[0]
    assert top_err["count"] >= 1
    assert "affected_workflows" in top_err


def test_slow_steps_identifier_finds_bottlenecks():
    """Verify slow steps identification."""
    step_tool = SlowStepsIdentifierTool()
    logs = _load_logs_csv(Path("data/sample_workflow_logs.csv"))

    res = step_tool.execute(raw_logs=logs, slow_step_threshold_seconds=4.0)
    flagged = res["flagged_slow_steps"]

    assert len(flagged) > 0
    step_names = [s["step_name"] for s in flagged]
    assert "clean_dataset_producer" in step_names


def test_empty_logs_handling():
    """Verify calculators handle empty log lists gracefully without zero-division errors."""
    rate_calc = RateCalculatorTool()
    time_calc = ExecutionTimeCalculatorTool()

    r_res = rate_calc.execute(raw_logs=[])
    assert r_res["overall_success_rate"] == 0.0
    assert r_res["overall_failure_rate"] == 0.0
    assert r_res["flagged_high_failure_workflows"] == []

    t_res = time_calc.execute(raw_logs=[])
    assert t_res["overall_avg_time"] == 0.0
    assert t_res["flagged_slow_workflows"] == []


def test_step_by_step_wf010_cascading():
    """Verify end-to-end cascading across all 6 WF010 tools."""
    step1 = LogLoaderTool().execute(log_file_path="data/sample_workflow_logs.csv")
    logs = step1["raw_logs"]

    step2 = RateCalculatorTool().execute(raw_logs=logs, failure_threshold=10.0)
    step3 = ExecutionTimeCalculatorTool().execute(raw_logs=logs, time_threshold_seconds=5.0)
    step4 = ErrorIdentifierTool().execute(raw_logs=logs)
    step5 = SlowStepsIdentifierTool().execute(raw_logs=logs, slow_step_threshold_seconds=4.0)

    step6 = RecommendationsGeneratorTool().execute(
        workflow_rates=step2["workflow_rates"],
        workflow_times=step3["workflow_times"],
        frequent_errors=step4["frequent_errors"],
        slow_steps=step5["slow_steps"],
        flagged_high_failure_workflows=step2["flagged_high_failure_workflows"],
        flagged_slow_workflows=step3["flagged_slow_workflows"],
        overall_success_rate=step2["overall_success_rate"],
        overall_failure_rate=step2["overall_failure_rate"],
        overall_avg_time=step3["overall_avg_time"],
    )

    assert step6["is_simulated"] is True
    assert "WF003" in step6["flagged_high_failure_workflows"]
    assert "WF003" in step6["flagged_slow_workflows"]
    assert len(step6["recommendations"]) > 0
