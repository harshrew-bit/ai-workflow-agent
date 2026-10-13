"""Domain tools for WF009 — Employee Task Assignment.

Steps:
1. Understand task requirements
2. compare employee skills
3. check current workload
4. rank candidates
5. select employee
6. generate assignment summary
"""

import csv
from pathlib import Path
import re
from typing import Any, Dict, List, Optional, Tuple, Union

from pydantic import BaseModel, Field

from app.tools.base import BaseTool, ToolMetadata
from app.tools.base import ClarificationRequired


class TaskRequirement(BaseModel):
    """Normalized task requirement model."""
    description: str
    required_skills: List[str]
    priority: str = "Medium"
    deadline: str = "Next Sprint"
    estimated_hours: float = 8.0


class EmployeeCandidate(BaseModel):
    """Employee record with skills and capacity."""
    employee_id: str
    name: str
    role: str
    skills: List[str]
    current_workload_hours: float
    max_capacity_hours: float = 40.0
    active_tasks_count: int = 0


def _load_employees_csv(file_path: Path) -> List[Dict[str, Any]]:
    """Load employee data from CSV."""
    if not file_path.exists():
        raise FileNotFoundError(f"Employee file not found at '{file_path}'")

    employees: List[Dict[str, Any]] = []
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

            emp_id = row_dict.get("employee_id") or f"EMP-{len(employees)+1:03d}"
            name = row_dict.get("name") or "Unknown"
            role = row_dict.get("role") or "Engineer"
            skills_raw = row_dict.get("skills", "")
            skills = [s.strip().lower() for s in skills_raw.split(",") if s.strip()]

            try:
                curr_hours = float(row_dict.get("current_workload_hours", "0"))
            except ValueError:
                curr_hours = 0.0

            try:
                max_hours = float(row_dict.get("max_capacity_hours", "40"))
            except ValueError:
                max_hours = 40.0

            try:
                tasks_cnt = int(row_dict.get("active_tasks_count", "0"))
            except ValueError:
                tasks_cnt = 0

            employees.append({
                "employee_id": emp_id,
                "name": name,
                "role": role,
                "skills": skills,
                "current_workload_hours": curr_hours,
                "max_capacity_hours": max_hours,
                "active_tasks_count": tasks_cnt,
            })
    return employees


class TaskRequirementsAnalyzerTool(BaseTool):
    """Step 1 Tool: Understand task requirements."""

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="task_requirements_analyzer",
            description="Parse and understand task requirements, skills, priority, and deadline.",
        )

    def execute(
        self,
        task_description: Optional[str] = None,
        required_skills: Optional[Union[List[str], str]] = None,
        priority: Optional[str] = None,
        deadline: Optional[str] = None,
        estimated_hours: Optional[float] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        desc = (task_description or "").strip()
        if not desc:
            raise ClarificationRequired(
                "Required input 'task_description' is missing. Please describe the task to assign."
            )

        parsed_skills: List[str] = []
        if required_skills:
            if isinstance(required_skills, str):
                parsed_skills = [s.strip().lower() for s in re.split(r"[,;\n]+", required_skills) if s.strip()]
            else:
                parsed_skills = [str(s).strip().lower() for s in required_skills if str(s).strip()]
        else:
            # Extract common tech skills mentioned in task description
            known_skills = [
                "python", "fastapi", "django", "react", "typescript", "javascript",
                "postgresql", "postgres", "sql", "aws", "docker", "kubernetes",
                "terraform", "pytest", "selenium", "playwright", "redis", "kafka",
                "css", "nextjs", "tailwind", "ci/cd", "devops", "qa"
            ]
            desc_lower = desc.lower()
            for s in known_skills:
                if re.search(rf"\b{re.escape(s)}\b", desc_lower):
                    parsed_skills.append("postgresql" if s == "postgres" else s)

        # Required skills are mandatory. Never fabricate a skill: ask the user instead.
        if not parsed_skills:
            raise ClarificationRequired(
                "Required input 'required_skills' is missing. "
                "Please specify the skills the task requires (e.g. python, fastapi, postgresql)."
            )

        # Priority determination
        p_val = (priority or "").strip().capitalize()
        if not p_val:
            if any(w in desc.lower() for w in ["urgent", "asap", "critical", "blocker", "p0", "immediately"]):
                p_val = "Urgent"
            elif any(w in desc.lower() for w in ["high", "important", "p1"]):
                p_val = "High"
            else:
                p_val = "Medium"

        # Deadline determination
        d_val = (deadline or "").strip()
        if not d_val:
            if "urgent" in p_val.lower():
                d_val = "Immediate (Within 24 Hours)"
            else:
                d_val = "End of Current Sprint"

        hours = float(estimated_hours) if estimated_hours is not None else 8.0

        task_req = {
            "description": desc,
            "required_skills": parsed_skills,
            "priority": p_val,
            "deadline": d_val,
            "estimated_hours": hours,
        }

        return {
            "task_requirements": task_req,
            "summary": (
                f"Task parsed: '{desc[:50]}...' with {len(parsed_skills)} required skill(s) "
                f"({', '.join(parsed_skills)}), Priority: {p_val}, Deadline: {d_val}."
            ),
        }


class SkillsComparatorTool(BaseTool):
    """Step 2 Tool: compare employee skills."""

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="skills_comparator",
            description="Compare candidate employee skill sets against required task skills.",
        )

    def execute(
        self,
        task_requirements: Optional[Dict[str, Any]] = None,
        employee_file_path: Optional[str] = None,
        employee_list: Optional[List[Dict[str, Any]]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        reqs = task_requirements or {}
        req_skills = reqs.get("required_skills", [])

        if not req_skills:
            raise ClarificationRequired(
                "Required input 'required_skills' is missing. "
                "Please provide the skills needed for this task."
            )

        if employee_list:
            employees = employee_list
        elif employee_file_path:
            employees = _load_employees_csv(Path(employee_file_path))
        else:
            default_path = Path("data/sample_employees.csv")
            if default_path.exists():
                employees = _load_employees_csv(default_path)
            else:
                raise ValueError("No employee dataset available to compare skills.")

        candidates_evaluated: List[Dict[str, Any]] = []
        for emp in employees:
            emp_skills = set(emp.get("skills", []))
            matching = [s for s in req_skills if s in emp_skills]
            missing = [s for s in req_skills if s not in emp_skills]

            # Calculate match ratio
            match_score = len(matching) / len(req_skills) if req_skills else 0.0

            cand_rec = dict(emp)
            cand_rec["skill_match_score"] = round(match_score, 2)
            cand_rec["matching_skills"] = matching
            cand_rec["missing_skills"] = missing
            candidates_evaluated.append(cand_rec)

        qualified_count = sum(1 for c in candidates_evaluated if c["skill_match_score"] > 0)
        return {
            "candidates_with_skill_scores": candidates_evaluated,
            "qualified_skill_count": qualified_count,
            "summary": f"Compared {len(candidates_evaluated)} employee(s); {qualified_count} have one or more matching skills.",
        }


class WorkloadCheckerTool(BaseTool):
    """Step 3 Tool: check current workload."""

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="workload_checker",
            description="Evaluate employee current workload, max capacity, and remaining bandwidth.",
        )

    def execute(
        self,
        candidates_with_skill_scores: Optional[List[Dict[str, Any]]] = None,
        task_requirements: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        candidates = candidates_with_skill_scores or []
        reqs = task_requirements or {}
        est_hours = reqs.get("estimated_hours", 8.0)

        evaluated: List[Dict[str, Any]] = []
        available_count = 0

        for c in candidates:
            curr = c.get("current_workload_hours", 0.0)
            max_cap = c.get("max_capacity_hours", 40.0)
            avail = max(0.0, max_cap - curr)
            utilization = (curr / max_cap) if max_cap > 0 else 1.0

            # Capacity score: 1.0 means 100% free, 0.0 means at or over capacity
            cap_score = max(0.0, min(1.0, 1.0 - utilization))
            has_capacity = (avail >= est_hours) and (curr < max_cap)

            if has_capacity:
                available_count += 1

            c_rec = dict(c)
            c_rec["available_hours"] = round(avail, 1)
            c_rec["utilization_percent"] = round(utilization * 100, 1)
            c_rec["capacity_score"] = round(cap_score, 2)
            c_rec["has_bandwidth"] = has_capacity
            evaluated.append(c_rec)

        return {
            "candidates_with_workload": evaluated,
            "available_candidates_count": available_count,
            "summary": f"Evaluated workload across {len(evaluated)} candidate(s); {available_count} have sufficient bandwidth.",
        }


class CandidateRankerTool(BaseTool):
    """Step 4 Tool: rank candidates."""

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="candidate_ranker",
            description="Rank employee candidates based on skills, workload, priority, and deadline.",
        )

    def execute(
        self,
        candidates_with_workload: Optional[List[Dict[str, Any]]] = None,
        task_requirements: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        candidates = candidates_with_workload or []
        reqs = task_requirements or {}
        priority = reqs.get("priority", "Medium").lower()

        # Weighting based on priority
        if priority in ["urgent", "high"]:
            skill_w = 0.50
            cap_w = 0.50
        else:
            skill_w = 0.65
            cap_w = 0.35

        ranked: List[Dict[str, Any]] = []
        for c in candidates:
            s_score = c.get("skill_match_score", 0.0)
            c_score = c.get("capacity_score", 0.0)

            # Combined score
            composite = round((s_score * skill_w) + (c_score * cap_w), 3)

            # Explain ranking factors
            m_skills = ", ".join(c.get("matching_skills", [])) or "None"
            avail_h = c.get("available_hours", 0.0)
            util = c.get("utilization_percent", 0.0)

            explanation = (
                f"Skill match: {s_score*100:.0f}% ({m_skills}); "
                f"Workload: {util:.0f}% used ({avail_h}h available); "
                f"Ranking: all required skills first, then available capacity; composite score (reference only): {composite:.3f}."
            )

            c_rec = dict(c)
            c_rec["composite_score"] = composite
            c_rec["ranking_explanation"] = explanation
            ranked.append(c_rec)

        # Decision (final): only candidates with every required skill are qualified.
        # Qualified candidates rank first, ordered by available capacity. The composite score
        # is reference-only and does not drive ranking.
        ranked.sort(
            key=lambda x: (
                _is_fully_qualified(x),
                x.get("available_hours", 0.0),
                x.get("capacity_score", 0.0),
            ),
            reverse=True,
        )

        return {
            "ranked_candidates": ranked,
            "top_candidate": ranked[0] if ranked else None,
            "summary": f"Ranked {len(ranked)} candidate(s): fully qualified first, then by available capacity.",
        }


def _is_fully_qualified(candidate: Dict[str, Any]) -> bool:
    """A candidate is fully qualified only if they hold EVERY required skill.

    Uses the explicit missing_skills list when present (always the case inside the workflow);
    otherwise falls back to a skill score of 1.0. A partial score never qualifies.
    """
    if "missing_skills" in candidate:
        return not candidate["missing_skills"]
    return candidate.get("skill_match_score", 0.0) >= 1.0


class EmployeeSelectorTool(BaseTool):
    """Step 5 Tool: select employee."""

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="employee_selector",
            description="Select best suited employee or trigger escalation if no candidate satisfies criteria.",
        )

    def execute(
        self,
        ranked_candidates: Optional[List[Dict[str, Any]]] = None,
        task_requirements: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        candidates = ranked_candidates or []
        reqs = task_requirements or {}

        # Decision Logic:
        # Prefer employees with required skills and available capacity;
        # Escalate if no suitable employee exists.
        # Only fully qualified candidates (every required skill) with available capacity are viable.
        # A partially qualified employee is never assigned, regardless of capacity or priority.
        viable_candidates = [
            c for c in candidates
            if _is_fully_qualified(c)
            and c.get("skill_match_score", 0.0) > 0.0
            and c.get("available_hours", 0.0) > 0.0
        ]

        if viable_candidates:
            selected = viable_candidates[0]
            return {
                "selected_employee": selected,
                "escalation_required": False,
                "escalation_reason": None,
                "summary": f"Selected candidate '{selected['name']}' ({selected['role']}) with composite score {selected['composite_score']:.3f}.",
            }
        else:
            # Check why no one was viable
            fully_qualified = [c for c in candidates if _is_fully_qualified(c)]
            if not fully_qualified:
                reason = (
                    "No employee possesses the required skills for this task "
                    "(every required skill must be present); partially qualified employees are never assigned."
                )
            else:
                reason = "All employees who possess every required skill are currently at 100% capacity with no available bandwidth."

            return {
                "selected_employee": None,
                "escalation_required": True,
                "escalation_reason": reason,
                "summary": f"Escalation required: {reason}",
            }


class AssignmentSummarizerTool(BaseTool):
    """Step 6 Tool: generate assignment summary."""

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="assignment_summarizer",
            description="Compile final task assignment recommendation and explanation.",
        )

    def execute(
        self,
        task_requirements: Optional[Dict[str, Any]] = None,
        selected_employee: Optional[Dict[str, Any]] = None,
        escalation_required: bool = False,
        escalation_reason: Optional[str] = None,
        ranked_candidates: Optional[List[Dict[str, Any]]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        reqs = task_requirements or {}
        candidates = ranked_candidates or []

        if escalation_required or not selected_employee:
            summary_text = (
                f"[ESCALATION REQUIRED] Task '{reqs.get('description', '')}' could not be assigned. "
                f"Reason: {escalation_reason or 'No suitable employee available.'}"
            )
            return {
                "assignment_status": "ESCALATED",
                "escalation_required": True,
                "escalation_reason": escalation_reason,
                "assigned_employee": None,
                "task_requirements": reqs,
                "ranked_candidates": candidates[:5],
                "is_simulated": True,
                "summary": summary_text,
            }

        emp = selected_employee
        summary_text = (
            f"Recommended Assignment: {emp.get('name')} ({emp.get('role')}) for task '{reqs.get('description', '')}'. "
            f"Composite Suitability: {emp.get('composite_score', 0):.3f}. "
            f"Priority: {reqs.get('priority')}, Deadline: {reqs.get('deadline')}."
        )

        return {
            "assignment_status": "ASSIGNED",
            "escalation_required": False,
            "escalation_reason": None,
            "assigned_employee": {
                "employee_id": emp.get("employee_id"),
                "name": emp.get("name"),
                "role": emp.get("role"),
                "composite_score": emp.get("composite_score"),
                "skill_match_score": emp.get("skill_match_score"),
                "matching_skills": emp.get("matching_skills"),
                "current_workload_hours": emp.get("current_workload_hours"),
                "available_hours": emp.get("available_hours"),
                "ranking_explanation": emp.get("ranking_explanation"),
            },
            "task_requirements": reqs,
            "top_candidates": [
                {
                    "name": c.get("name"),
                    "role": c.get("role"),
                    "composite_score": c.get("composite_score"),
                    "skill_match": f"{c.get('skill_match_score', 0)*100:.0f}%",
                    "available_hours": c.get("available_hours"),
                }
                for c in candidates[:4]
            ],
            "is_simulated": True,
            "summary": summary_text,
        }
