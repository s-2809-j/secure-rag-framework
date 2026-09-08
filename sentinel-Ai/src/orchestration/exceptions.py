"""
Custom exceptions for the Sentinel AI Engine orchestration layer.

This module defines the exception hierarchy used exclusively by the
Sentinel Orchestrator. These exceptions represent failures occurring
while coordinating AI workflows and are intentionally independent of
agent-specific exceptions.

Design Principles
-----------------
- Single responsibility
- Lightweight exception hierarchy
- No framework dependencies
- No business logic
"""

from __future__ import annotations

from typing import Optional

from .models import WorkflowType


class OrchestrationError(Exception):
    """
    Base exception for all orchestration-related failures.
    """

    def __init__(
        self,
        message: str,
        *,
        request_id: str = "",
        workflow: Optional[WorkflowType] = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.request_id = request_id
        self.workflow = workflow

    def __str__(self) -> str:
        return self.message


class InvalidWorkflowError(OrchestrationError):
    """
    Raised when an unsupported workflow is requested.
    """


class WorkflowExecutionError(OrchestrationError):
    """
    Raised when a workflow cannot be completed successfully.
    """


class InvalidRequestError(OrchestrationError):
    """
    Raised when the supplied request object is invalid for the selected
    workflow.
    """


class ResponseConstructionError(OrchestrationError):
    """
    Raised when the orchestrator cannot construct a valid response.
    """