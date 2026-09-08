"""
Versioned response DTOs returned to Spring Boot.
FastAPI never returns raw LangGraph state.
All graph output is translated here before leaving the AI service.
"""

from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, Field


class ChatApiResponse(BaseModel):
    """Response DTO for POST /v1/chat."""

    request_id: str
    success: bool
    message: str
    response_text: Optional[str] = Field(
        None, description="Final validated AI response"
    )
    blocked: bool = Field(False, description="True if security blocked the request")
    risk_score: Optional[float] = Field(None, description="Risk score 0.0 – 1.0")
    workflow: str = "chat"


class DocumentApiResponse(BaseModel):
    """Response DTO for POST /v1/documents/analyze."""

    request_id: str
    success: bool
    message: str
    analysis_result: Optional[Any] = Field(
        None, description="DocumentSecurityDecision payload"
    )
    workflow: str = "document_analysis"


class KnowledgeApiResponse(BaseModel):
    """Response DTO for POST /v1/knowledge/upload."""

    request_id: str
    success: bool
    message: str
    ingestion_result: Optional[Any] = Field(
        None, description="IngestionResult payload"
    )
    workflow: str = "knowledge_upload"


class ErrorApiResponse(BaseModel):
    """Returned on unhandled errors — never leaks internal stack traces."""

    request_id: str
    success: bool = False
    error_code: str
    message: str
    workflow: Optional[str] = None