"""Custom exceptions for the workflow registry and loader."""


class WorkflowRegistryError(Exception):
    """Base exception for all workflow registry and loader errors."""

    pass


class WorkbookNotFoundError(WorkflowRegistryError, FileNotFoundError):
    """Raised when the Excel workbook file does not exist at the specified path."""

    pass


class InvalidWorkbookError(WorkflowRegistryError):
    """Raised when the workbook file is corrupted, unreadable, or not a valid Excel file."""

    pass


class MissingSheetError(InvalidWorkbookError):
    """Raised when a required sheet is missing from the workbook."""

    pass


class MissingColumnError(InvalidWorkbookError):
    """Raised when one or more required columns are missing from a workbook sheet."""

    pass


class DuplicateWorkflowIDError(WorkflowRegistryError):
    """Raised when a duplicate workflow ID is detected in the workbook or registry."""

    pass


class WorkflowValidationError(WorkflowRegistryError):
    """Raised when workflow data fails validation (missing ID, empty fields, or invalid format)."""

    pass


class WorkflowNotFoundError(WorkflowRegistryError, KeyError):
    """Raised when a requested workflow ID is not found in the registry."""

    pass
