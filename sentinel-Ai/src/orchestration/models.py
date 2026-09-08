"""
Defines the public request and response models for the Sentinel AI Engine
orchestration layer.

This module contains lightweight data contracts exchanged between the
Sentinel Orchestrator and the AI workflows. These models intentionally
exclude any application-specific concepts such as authentication,
authorization, user management, persistence, billing, or business logic.

The orchestration layer operates solely on AI-related requests and
responses, making these models reusable across different integration
points (FastAPI, Spring Boot, CLI, MCP, LangGraph, etc.).

Design Principles
-----------------
- Immutable request models
- Lightweight response models
- Standard library only
- Strong typing
- Stable public contracts
- No business logic
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path
from typing import Any
from uuid import uuid4
from src.common.models import FileMetadata

class WorkflowType(StrEnum):
    """
    Supported workflows handled by the Sentinel AI Engine.
    """

    CHAT = "chat"
    DOCUMENT_ANALYSIS = "document_analysis"
    KNOWLEDGE_UPLOAD = "knowledge_upload"


@dataclass(frozen=True, slots=True)
class BaseRequest:
    """
    Base class for every request entering the Sentinel AI Engine.

    Attributes
    ----------
    request_id:
        Unique correlation identifier propagated across the complete
        AI workflow for tracing and logging.

    session_id:
        Conversation thread identifier used by the LangGraph checkpointer
        to scope memory state across turns within the same session.

    workflow:
        Identifies the workflow that should be executed.
    """

    workflow: WorkflowType
    request_id: str = field(default_factory=lambda: str(uuid4()), kw_only=True)
    session_id: str = field(default_factory=lambda: str(uuid4()), kw_only=True)


@dataclass(frozen=True, slots=True)
class ChatRequest(BaseRequest):
    """
    Represents a user query for conversational AI processing.

    The application backend is responsible for authentication,
    authorization, session handling, and conversation persistence.
    Sentinel receives only the AI query.
    """

    query: str


@dataclass(frozen=True, slots=True)
class FileRequest(BaseRequest):
    """
    Base class for workflows operating on a document.
    """

    file_path: Path
    metadata: FileMetadata


@dataclass(frozen=True, slots=True)
class DocumentAnalysisRequest(FileRequest):
    """
    Request for secure document analysis.

    This workflow invokes the Document Security Agent before any
    downstream AI processing.
    """

    pass


@dataclass(frozen=True, slots=True)
class KnowledgeUploadRequest(FileRequest):
    """
    Request for secure knowledge ingestion.

    Authorization to upload documents into the knowledge base must
    already be verified by the application backend before this request
    reaches the Sentinel AI Engine.
    """

    pass


@dataclass(slots=True)
class SentinelResponse:
    """
    Represents a successful workflow execution.

    Attributes
    ----------
    success:
        Indicates whether the workflow completed successfully.

    workflow:
        Workflow that generated this response.

    request_id:
        Correlation identifier copied from the originating request.

    message:
        Human-readable summary of the execution result.

    data:
        Workflow-specific response payload.
    """

    success: bool
    workflow: WorkflowType
    request_id: str
    message: str
    data: Any | None = None


@dataclass(slots=True)
class ErrorResponse:
    """
    Represents a standardized orchestration error.

    This model is returned whenever the orchestration layer cannot
    successfully complete a workflow.
    """

    success: bool = False
    request_id: str = ""
    workflow: WorkflowType | None = None
    error_code: str = ""
    message: str = ""
    details: Any | None = None