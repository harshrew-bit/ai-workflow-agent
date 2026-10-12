"""Unit and step-by-step tests for WF009 — Employee Task Assignment."""

from pathlib import Path
import pytest

from app.tools.task_assignment import (
    AssignmentSummarizerTool,
    CandidateRankerTool,
    EmployeeSelectorTool,
    SkillsComparatorTool,
    TaskRequirementsAnalyzerTool,
    WorkloadCheckerTool,
    _load_employees_csv,
)


def test_load_sample_employees_csv():
    """Verify loading sample employee dataset."""
    employees = _load_employees_csv(Path("data/sample_employees.csv"))
    assert len(employees) >= 5
    names = [e["name"] for e in employees]
    assert "Alice Chen" in names
    assert "Carlos Rivera" in names


def test_task_requirements_parsing_and_skill_extraction():
    """Verify task description parsing and skill detection."""
    analyzer = TaskRequirementsAnalyzerTool()

    res = analyzer.execute(
        task_description="Build FastAPI endpoint with PostgreSQL database for user auth",
        priority="Urgent",
    )
    reqs = res["task_requirements"]
    assert "fastapi" in reqs["required_skills"]
    assert "postgresql" in reqs["required_skills"]
    assert reqs["priority"] == "Urgent"


def test_task_requirements_missing_desc_raises_error():
    """Verify missing task description raises ValueError."""
    analyzer = TaskRequirementsAnalyzerTool()
    with pytest.raises(ValueError):
        analyzer.execute(task_description="")


def test_skills_comparator_matching():
    """Verify skill matching calculates correct match ratio."""
    comparator = SkillsComparatorTool()

    reqs = {
        "required_skills": ["python", "fastapi", "postgresql"],
        "estimated_hours": 8.0,
    }
    res = comparator.execute(task_requirements=reqs, employee_file_path="data/sample_employees.csv")
    candidates = res["candidates_with_skill_scores"]

    alice = next(c for c in candidates if c["name"] == "Alice Chen")
    assert alice["skill_match_score"] == 1.0
    assert set(alice["matching_skills"]) == {"python", "fastapi", "postgresql"}

    bob = next(c for c in candidates if c["name"] == "Bob Martinez")
    assert bob["skill_match_score"] == 0.0


def test_workload_checker_evaluates_bandwidth():
    """Verify capacity score and bandwidth evaluation."""
    comparator = SkillsComparatorTool()
    workload_checker = WorkloadCheckerTool()

    reqs = {"required_skills": ["python"], "estimated_hours": 10.0}
    cands = comparator.execute(task_requirements=reqs, employee_file_path="data/sample_employees.csv")["candidates_with_skill_scores"]

    res = workload_checker.execute(candidates_with_skill_scores=cands, task_requirements=reqs)
    evaluated = res["candidates_with_workload"]

    carlos = next(c for c in evaluated if c["name"] == "Carlos Rivera")
    assert carlos["available_hours"] == 30.0
    assert carlos["has_bandwidth"] is True

    fiona = next(c for c in evaluated if c["name"] == "Fiona Gallagher")
    assert fiona["available_hours"] == 0.0
    assert fiona["has_bandwidth"] is False


def test_employee_selector_happy_path():
    """Verify best suited employee selection with skills and capacity."""
    analyzer = TaskRequirementsAnalyzerTool()
    comparator = SkillsComparatorTool()
    workload_checker = WorkloadCheckerTool()
    ranker = CandidateRankerTool()
    selector = EmployeeSelectorTool()

    reqs = analyzer.execute(task_description="Build FastAPI service", required_skills=["fastapi", "python"])["task_requirements"]
    cands_skill = comparator.execute(task_requirements=reqs)["candidates_with_skill_scores"]
    cands_workload = workload_checker.execute(candidates_with_skill_scores=cands_skill, task_requirements=reqs)["candidates_with_workload"]
    ranked = ranker.execute(candidates_with_workload=cands_workload, task_requirements=reqs)["ranked_candidates"]

    sel_res = selector.execute(ranked_candidates=ranked, task_requirements=reqs)
    assert sel_res["escalation_required"] is False
    assert sel_res["selected_employee"] is not None
    assert sel_res["selected_employee"]["skill_match_score"] > 0
    assert sel_res["selected_employee"]["available_hours"] > 0


def test_employee_selector_escalates_when_no_matching_skills():
    """Verify escalation when nobody possesses required skills."""
    selector = EmployeeSelectorTool()

    unqualified_cands = [
        {"name": "Dev 1", "role": "Eng", "skill_match_score": 0.0, "available_hours": 20.0, "composite_score": 0.2},
        {"name": "Dev 2", "role": "Eng", "skill_match_score": 0.0, "available_hours": 15.0, "composite_score": 0.15},
    ]

    res = selector.execute(ranked_candidates=unqualified_cands)
    assert res["escalation_required"] is True
    assert res["selected_employee"] is None
    assert "No employee possesses the required skills" in res["escalation_reason"]


def test_employee_selector_escalates_when_all_qualified_are_overloaded():
    """Verify escalation when qualified employees have zero available bandwidth."""
    selector = EmployeeSelectorTool()

    overloaded_cands = [
        {"name": "Dev 1", "role": "Eng", "skill_match_score": 1.0, "available_hours": 0.0, "composite_score": 0.6},
        {"name": "Dev 2", "role": "Eng", "skill_match_score": 0.0, "available_hours": 20.0, "composite_score": 0.2},
    ]

    res = selector.execute(ranked_candidates=overloaded_cands)
    assert res["escalation_required"] is True
    assert res["selected_employee"] is None
    assert "at 100% capacity" in res["escalation_reason"]


def test_step_by_step_wf009_cascading():
    """Verify end-to-end cascading across all 6 WF009 tools."""
    step1 = TaskRequirementsAnalyzerTool().execute(
        task_description="Create React user dashboard with Tailwind",
        required_skills=["react", "typescript"],
        priority="High",
        deadline="Friday",
    )
    reqs = step1["task_requirements"]

    step2 = SkillsComparatorTool().execute(task_requirements=reqs)
    step3 = WorkloadCheckerTool().execute(candidates_with_skill_scores=step2["candidates_with_skill_scores"], task_requirements=reqs)
    step4 = CandidateRankerTool().execute(candidates_with_workload=step3["candidates_with_workload"], task_requirements=reqs)
    step5 = EmployeeSelectorTool().execute(ranked_candidates=step4["ranked_candidates"], task_requirements=reqs)

    step6 = AssignmentSummarizerTool().execute(
        task_requirements=reqs,
        selected_employee=step5["selected_employee"],
        escalation_required=step5["escalation_required"],
        escalation_reason=step5["escalation_reason"],
        ranked_candidates=step4["ranked_candidates"],
    )

    assert step6["assignment_status"] == "ASSIGNED"
    assert step6["is_simulated"] is True
    assert step6["assigned_employee"]["name"] in ["Bob Martinez", "Carlos Rivera"]
