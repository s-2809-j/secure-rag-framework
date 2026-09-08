"""
Exceptions for the Assistant Agent.

The Assistant Agent coordinates multiple subsystems such as
the Input Security Agent, Retriever, LLM, Document Security
Agent, and Knowledge Ingestion Pipeline.

These exceptions represent orchestration failures rather than
low-level implementation errors.
"""

from __future__ import annotations


class AssistantAgentError(Exception):
    """
    Base exception for all Assistant Agent errors.
    """


class ResponseGenerationError(AssistantAgentError):
    """
    Raised when the Assistant Agent fails to generate
    a chat response.
    """


class DocumentAnalysisError(AssistantAgentError):
    """
    Raised when document analysis fails.
    """


class DocumentUploadError(AssistantAgentError):
    """
    Raised when a validated document cannot be uploaded
    into the Knowledge Base.
    """


class WorkflowValidationError(AssistantAgentError):
    """
    Raised when an invalid workflow request is made.

    Examples:
        - Missing upload intent.
        - Invalid workflow parameters.
        - Unsupported operation.
    """