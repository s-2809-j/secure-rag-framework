"""
Models used by the Assistant Agent.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class AssistantResponseStatus(str, Enum):
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"


@dataclass(slots=True)
class AssistantResponse:
    """
    Response returned by generate_response().
    """

    status: AssistantResponseStatus
    response: str
    sources: list[dict[str, Any]] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class DocumentAnalysisResponse:
    """
    Response returned by analyze_document().
    """

    success: bool
    decision: Any
    message: str = ""


@dataclass(slots=True)
class DocumentUploadResponse:
    """
    Response returned by upload_document().
    """

    success: bool
    message: str
    document_id: str | None = None
    chunk_count: int = 0