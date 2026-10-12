"""In-memory registry for managing workflow definitions dynamically."""

from pathlib import Path
from typing import Dict, Iterable, List, Optional, Union

from app.models.workflow import WorkflowDefinition
from app.registry.exceptions import DuplicateWorkflowIDError, WorkflowNotFoundError
from app.registry.loader import load_workflows_from_excel


class WorkflowRegistry:
    """Dynamic, generic registry for workflow definitions.

    Enables dynamic registration and lookup of workflows without hardcoding
    individual workflow IDs or chatbot branches. Workflows can be loaded from
    Excel or registered programmatically.
    """

    def __init__(self) -> None:
        self._workflows: Dict[str, WorkflowDefinition] = {}

    def register(
        self,
        workflow: WorkflowDefinition,
        *,
        allow_overwrite: bool = False,
    ) -> None:
        """Register a workflow definition.

        Raises DuplicateWorkflowIDError if the workflow ID is already registered
        and allow_overwrite is False.
        """
        workflow_id = workflow.workflow_id
        if not allow_overwrite and workflow_id in self._workflows:
            raise DuplicateWorkflowIDError(
                f"Workflow with ID '{workflow_id}' is already registered. "
                "Set allow_overwrite=True to replace an existing workflow."
            )
        self._workflows[workflow_id] = workflow

    def register_many(
        self,
        workflows: Iterable[WorkflowDefinition],
        *,
        allow_overwrite: bool = False,
    ) -> None:
        """Register multiple workflow definitions."""
        for wf in workflows:
            self.register(wf, allow_overwrite=allow_overwrite)

    def get(self, workflow_id: str) -> WorkflowDefinition:
        """Retrieve a workflow by ID, raising WorkflowNotFoundError if missing."""
        if workflow_id not in self._workflows:
            raise WorkflowNotFoundError(
                f"Workflow '{workflow_id}' was not found in registry. "
                f"Registered IDs: {sorted(self._workflows.keys())}."
            )
        return self._workflows[workflow_id]

    def get_or_none(self, workflow_id: str) -> Optional[WorkflowDefinition]:
        """Retrieve a workflow by ID, or None if not found."""
        return self._workflows.get(workflow_id)

    def contains(self, workflow_id: str) -> bool:
        """Check whether a workflow ID is registered."""
        return workflow_id in self._workflows

    def __contains__(self, workflow_id: str) -> bool:
        return self.contains(workflow_id)

    def __len__(self) -> int:
        return len(self._workflows)

    def list_all(self) -> List[WorkflowDefinition]:
        """Return a list of all registered workflow definitions."""
        return list(self._workflows.values())

    def list_ids(self) -> List[str]:
        """Return a list of all registered workflow IDs."""
        return list(self._workflows.keys())

    def clear(self) -> None:
        """Clear all registered workflows."""
        self._workflows.clear()

    @classmethod
    def from_excel(cls, filepath: Union[str, Path]) -> "WorkflowRegistry":
        """Factory method to instantiate and populate registry from an Excel workbook."""
        registry = cls()
        workflows = load_workflows_from_excel(filepath)
        registry.register_many(workflows)
        return registry
