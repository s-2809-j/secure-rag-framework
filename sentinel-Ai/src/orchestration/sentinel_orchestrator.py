"""
Central workflow orchestrator for the Sentinel AI Engine.

The SentinelOrchestrator is the single entry point into the AI Engine.
Its responsibility is to coordinate AI workflows by delegating work to
specialized agents while returning standardized responses.

The orchestrator intentionally contains no AI logic, security logic,
retrieval logic, or document processing logic.

Fix Log
-------
- OutputValidationAgent added as optional constructor parameter (was imported but never injected)
- InputSecurityAgent now called at orchestrator boundary in _execute_chat (was bypassed)
- DocumentSecurityAgent now called at orchestrator boundary in _execute_document_analysis (was bypassed)
- Security check ownership moved from AssistantAgent to orchestrator boundary (correct architecture)
"""

from __future__ import annotations

import logging
import threading
from typing import Optional
from urllib import request

from src.assistant_agent.assistant_agent import AssistantAgent
from src.document_security_agent.document_security_agent import DocumentSecurityAgent
from src.input_security_agent.input_security_agent import InputSecurityAgent
from src.input_security_agent.models import SecurityContext
from src.output_validation_agent.output_validation_agent import OutputValidationAgent
from src.output_validation_agent.models import ValidationContext

from .exceptions import (
    InvalidRequestError,
    InvalidWorkflowError,
    WorkflowExecutionError,
)
from .models import (
    BaseRequest,
    ChatRequest,
    DocumentAnalysisRequest,
    ErrorResponse,
    KnowledgeUploadRequest,
    SentinelResponse,
    WorkflowType,
)

logger = logging.getLogger(__name__)

# FIX 7A — Thread-safe LangGraph invocation lock.
# Acquired around graph.invoke() in _execute_chat to prevent concurrent
# requests with the same thread_id from corrupting MemorySaver state.
_graph_lock = threading.Lock()


class SentinelOrchestrator:
    """
    Coordinates all AI workflows inside the Sentinel AI Engine.

    The orchestrator acts as the single public entry point into
    the AI Engine while delegating workflow execution to specialized agents.

    Agent Execution Boundaries
    --------------------------
    - InputSecurityAgent  : called at orchestrator boundary before AssistantAgent (chat workflow)
    - DocumentSecurityAgent: called at orchestrator boundary before AssistantAgent (document workflows)
    - AssistantAgent      : called for generation, analysis, and ingestion
    - OutputValidationAgent: called at orchestrator boundary after AssistantAgent (chat workflow)
    """

    def __init__(
        self,
        *,
        input_security_agent: InputSecurityAgent,
        document_security_agent: DocumentSecurityAgent,
        assistant_agent: AssistantAgent,
        output_validation_agent: Optional[OutputValidationAgent] = None,
    ) -> None:
        self._input_security_agent = input_security_agent
        self._document_security_agent = document_security_agent
        self._assistant_agent = assistant_agent
        self._output_validation_agent = output_validation_agent

        logger.info("SentinelOrchestrator initialized successfully.")

    def execute(
        self,
        request: BaseRequest,
    ) -> SentinelResponse | ErrorResponse:
        """
        Execute the requested workflow.
        """

        logger.info(
            "Executing workflow '%s' (request_id=%s)",
            request.workflow,
            request.request_id,
        )

        try:
            if request.workflow == WorkflowType.CHAT:
                return self._execute_chat(request)

            if request.workflow == WorkflowType.DOCUMENT_ANALYSIS:
                return self._execute_document_analysis(request)

            if request.workflow == WorkflowType.KNOWLEDGE_UPLOAD:
                return self._execute_knowledge_upload(request)

            raise InvalidWorkflowError(
                f"Unsupported workflow '{request.workflow}'.",
                workflow=request.workflow,
                request_id=request.request_id,
            )

        except Exception as exc:
            # FIX 6D — Log the actual exception; never surface it in the response.
            logger.exception(
                "Workflow '%s' failed. request_id=%s",
                request.workflow,
                request.request_id,
            )

            return ErrorResponse(
                workflow=request.workflow,
                request_id=request.request_id,
                error_code=type(exc).__name__,
                # FIX 6D — Static user-safe message; no exception text, paths, or IDs.
                message="An internal error occurred. Please try again.",
            )

    # ------------------------------------------------------------------
    # Chat Workflow
    # ------------------------------------------------------------------

    def _execute_chat(
        self,
        request: BaseRequest,
    ) -> SentinelResponse:

        if not isinstance(request, ChatRequest):
            raise InvalidRequestError(
                "Expected ChatRequest.",
                workflow=request.workflow,
                request_id=request.request_id,
            )

        # ----------------------------------------------------------
        # Step 1: Input security check at orchestrator boundary.
        # The orchestrator owns the security gate — AssistantAgent
        # must be constructed WITHOUT its own security_agent so that
        # security is not executed twice.
        # ----------------------------------------------------------
        # ----------------------------------------------------------
        logger.debug("Performing input security check.")
        security_context = SecurityContext(query=request.query)
        security_decision = self._input_security_agent.analyze(security_context)

        if not security_decision.allowed:
            logger.warning(
                "Chat request blocked by InputSecurityAgent. "
                "risk_score=%.2f request_id=%s",
                security_decision.risk_assessment.risk_score,
                request.request_id,
            )
            return SentinelResponse(
                success=False,
                workflow=request.workflow,
                request_id=request.request_id,
                message="Request blocked by security policy.",
                data={
                    "blocked": True,
                    "reason": "Input security policy violation.",
                    "risk_score": security_decision.risk_assessment.risk_score,
                },
            )

        # ----------------------------------------------------------
        # Step 2: Generate response using normalized query.
        # FIX 7A — Acquire lock to prevent concurrent MemorySaver
        # state corruption from requests sharing the same thread_id.
        # ----------------------------------------------------------

        _graph_lock.acquire()
        try:
            raw_response, retrieved_chunks = self._assistant_agent.generate_response(
            query=security_decision.normalized_context,
        )   
        finally:
            _graph_lock.release()

        # ----------------------------------------------------------
        # Step 3: Output validation (optional — skipped if not wired).
        # ----------------------------------------------------------

        if self._output_validation_agent is None:
            logger.debug(
                "OutputValidationAgent not configured. Skipping validation."
            )
            return SentinelResponse(
                success=True,
                workflow=request.workflow,
                request_id=request.request_id,
                message="Chat workflow completed successfully.",
                data=raw_response,
            )

        validation_context = ValidationContext(
            user_query=security_decision.normalized_context,
            llm_response=raw_response,
            retrieved_chunks=[],
            metadata={
                "request_id": request.request_id,
            },
        )

        validation_decision = self._output_validation_agent.validate(
            validation_context
        )

        logger.info(
            "Output validation completed. approved=%s request_id=%s",
            validation_decision.approved,
            request.request_id,
        )

        return SentinelResponse(
            success=True,
            workflow=request.workflow,
            request_id=request.request_id,
            message="Chat workflow completed successfully.",
            data=validation_decision.final_response,
        )

    # ------------------------------------------------------------------
    # Document Analysis Workflow
    # ------------------------------------------------------------------

    def _execute_document_analysis(
    self,
    request: BaseRequest,
) -> SentinelResponse:

        if not isinstance(request, DocumentAnalysisRequest):
            raise InvalidRequestError(
                "Expected DocumentAnalysisRequest.",
                workflow=request.workflow,
                request_id=request.request_id,
            )

        security_decision = self._document_security_agent.analyze(
            file_path=str(request.file_path),
            metadata=request.metadata,
        )

        if not security_decision.allowed:
            logger.warning(
                "Document blocked by DocumentSecurityAgent. request_id=%s",
                request.request_id,
            )
            return SentinelResponse(
                success=False,
                workflow=request.workflow,
                request_id=request.request_id,
                message="Document blocked by security policy.",
                data={
                    "blocked": True,
                    "reason": "Document security policy violation.",
                    "risk_score": getattr(security_decision, 'risk_score', None),
                },
            )

        result = self._assistant_agent.analyze_document(
            file_path=request.file_path,
            metadata=request.metadata,
            security_decision=security_decision,
        )

        return SentinelResponse(
            success=True,
            workflow=request.workflow,
            request_id=request.request_id,
            message="Document analysis completed successfully.",
            data=result,
        )

    # ------------------------------------------------------------------
    # Knowledge Upload Workflow
    # ------------------------------------------------------------------

    def _execute_knowledge_upload(
        self,
        request: BaseRequest,
    ) -> SentinelResponse:

        if not isinstance(request, KnowledgeUploadRequest):
            raise InvalidRequestError(
                "Expected KnowledgeUploadRequest.",
                workflow=request.workflow,
                request_id=request.request_id,
            )

        security_decision = self._document_security_agent.analyze(
            file_path=str(request.file_path),
            metadata=request.metadata,
        )

        if not security_decision.allowed:
            logger.warning(
                "Document blocked by DocumentSecurityAgent. request_id=%s",
                request.request_id,
            )
            return SentinelResponse(
                success=False,
                workflow=request.workflow,
                request_id=request.request_id,
                message="Document blocked by security policy.",
                data={
                    "blocked": True,
                    "reason": "Document security policy violation.",
                    "risk_score": getattr(security_decision, 'risk_score', None),
                },
            )

        result = self._assistant_agent.upload_document(
            file_path=request.file_path,
            metadata=request.metadata,
            security_decision=security_decision,
        )

        return SentinelResponse(
            success=True,
            workflow=request.workflow,
            request_id=request.request_id,
            message="Knowledge upload completed successfully.",
            data=result,
        )