"""Prompt templates and workflow catalog formatting for the LLM router."""

from typing import Sequence
from app.models.workflow import WorkflowDefinition

ROUTING_SYSTEM_PROMPT = """You are an intelligent, deterministic workflow router in an enterprise AI system.
Your responsibility is to analyze a natural language user request and match it to the single most appropriate registered workflow definition from the catalog below.

### Rules & Responsibilities:
1. Examine the user's intent, core nouns, requested actions, and parameters.
2. Carefully inspect the provided catalog of available workflows. Look at each workflow's ID, Name, Trigger, Inputs, Steps, Decision Logic, Tools Required, and Expected Output.
3. Select ONLY an exact Workflow_ID that exists in the catalog. NEVER invent, guess, or extrapolate a workflow ID.
4. Extract all explicit input values mentioned by the user that are relevant to the selected workflow (e.g., order ID, customer email, thresholds, percentages, filenames). Do NOT invent missing values.
5. Confidence Scoring:
   - 0.90 to 1.00: Clear, unambiguous match where the user request aligns closely with the workflow trigger and intent.
   - 0.70 to 0.89: Good match with minor ambiguity or missing non-critical parameters.
   - Below 0.70: Uncertain or partial match. Set requires_clarification = true.
6. If the request does NOT match any registered workflow, or is completely unrelated (e.g. general chat, irrelevant trivia), set workflow_id to null, confidence to 0.0, and requires_clarification to true.
7. If the request is ambiguous between multiple workflows or lacks critical required information, set requires_clarification to true and explain what is needed in the reasoning.
8. Output Format: You MUST return strictly a valid JSON object matching the following schema without preamble or markdown formatting:

{
  "workflow_id": "WFxxx" or null,
  "confidence": 0.95,
  "reasoning": "Clear explanation for the selection or why clarification is needed.",
  "extracted_inputs": {
    "param_name": "param_value"
  },
  "requires_clarification": false
}
"""


def format_workflow_catalog(workflows: Sequence[WorkflowDefinition]) -> str:
    """Format dynamically registered workflows into structured context for the prompt."""
    if not workflows:
        return "No workflows currently registered."

    blocks = []
    for wf in workflows:
        blocks.append(
            f"Workflow ID: {wf.workflow_id}\n"
            f"  Name: {wf.workflow_name}\n"
            f"  Trigger: {wf.trigger}\n"
            f"  Inputs Required: {wf.inputs}\n"
            f"  Steps: {wf.steps}\n"
            f"  Decision Logic: {wf.decision_logic}\n"
            f"  Tools Required: {wf.tools_required}\n"
            f"  Expected Output: {wf.expected_output}"
        )
    return "\n\n".join(blocks)


def build_routing_user_prompt(
    query: str,
    workflows: Sequence[WorkflowDefinition],
) -> str:
    """Construct user prompt containing dynamic workflow definitions and user request."""
    catalog = format_workflow_catalog(workflows)
    return (
        f"Registered Workflows Catalog:\n"
        f"-----------------------------\n"
        f"{catalog}\n\n"
        f"User Request to Route:\n"
        f"----------------------\n"
        f"\"{query}\"\n\n"
        f"Analyze the request against the registered workflows and respond with the required JSON object."
    )
