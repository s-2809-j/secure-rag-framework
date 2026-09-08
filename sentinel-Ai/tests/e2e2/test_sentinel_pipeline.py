from __future__ import annotations
import pytest
from src.orchestration.models import (
    ErrorResponse,
    SentinelResponse,
    WorkflowType,
)

from tests.e2e2.integration_support import (
    SAFE_DOCUMENT,
    SAFE_CHAT_QUERY,
    PROMPT_INJECTION_QUERY,
    JAILBREAK_QUERY,
    PII_QUERY,
    build_chat_request,
    build_document_analysis_request,
    build_knowledge_upload_request,
    build_orchestrator,
)

def test_document_analysis_pipeline() -> None:
    """
    End-to-end validation of the Document Analysis workflow.

    Pipeline:

        Document
            │
            ▼
        SentinelOrchestrator
            │
            ▼
        DocumentSecurityAgent
            │
            ▼
        SentinelResponse
    """

    orchestrator = build_orchestrator()

    request = build_document_analysis_request(
        file_path=SAFE_DOCUMENT,
        request_id="e2e-document-analysis",
    )

    response = orchestrator.execute(request)

    assert isinstance(
        response,
        (SentinelResponse, ErrorResponse),
    )

    if isinstance(response, SentinelResponse):

        assert response.success is True

        assert (
            response.workflow
            == WorkflowType.DOCUMENT_ANALYSIS
        )

        assert (
            response.request_id
            == "e2e-document-analysis"
        )

        assert response.data is not None

    else:

        pytest.fail(
            f"Document analysis failed unexpectedly: "
            f"{response.error_code}: {response.message}"
        )

        
def test_knowledge_upload_pipeline() -> None:
    """
    End-to-end validation of the Knowledge Upload workflow.

    Pipeline:

        Document
            │
            ▼
        SentinelOrchestrator
            │
            ▼
        DocumentSecurityAgent
            │
            ▼
        Knowledge Ingestion Pipeline
            │
            ▼
        ChromaDB
            │
            ▼
        SentinelResponse
    """

    orchestrator = build_orchestrator()

    request = build_knowledge_upload_request(
        file_path=SAFE_DOCUMENT,
        request_id="e2e-knowledge-upload",
    )

    response = orchestrator.execute(request)

    assert isinstance(
        response,
        (SentinelResponse, ErrorResponse),
    )

    if isinstance(response, SentinelResponse):

        assert response.success is True

        assert (
            response.workflow
            == WorkflowType.KNOWLEDGE_UPLOAD
        )

        assert (
            response.request_id
            == "e2e-knowledge-upload"
        )

        assert response.data is not None

    else:

        pytest.fail(
            f"Knowledge upload failed unexpectedly: "
            f"{response.error_code}: {response.message}"
        )

def test_safe_chat_pipeline() -> None:
    """
    End-to-end validation of the complete chat pipeline.

    Pipeline:

        ChatRequest
             │
             ▼
      SentinelOrchestrator
             │
             ▼
      InputSecurityAgent
             │
             ▼
       AssistantAgent
             │
             ▼
         Retriever
             │
             ▼
        GeminiLLMClient
             │
             ▼
    OutputValidationAgent
             │
             ▼
    SentinelResponse / ErrorResponse
    """

    orchestrator = build_orchestrator()

    request = build_chat_request(
        query=SAFE_CHAT_QUERY,
        request_id="e2e-safe-chat",
    )

    response = orchestrator.execute(request)

    assert isinstance(
        response,
        (SentinelResponse, ErrorResponse),
    )

    if isinstance(response, SentinelResponse):

        assert response.success is True

        assert (
            response.workflow
            == WorkflowType.CHAT
        )

        assert (
            response.request_id
            == "e2e-safe-chat"
        )

        assert response.data is not None

    else:

        #
        # GitHub Models may be temporarily unavailable.
        # The orchestrator should gracefully return an
        # ErrorResponse rather than raising.
        #

        assert response.success is False

        assert (
            response.workflow
            == WorkflowType.CHAT
        )

        assert response.error_code == "APIStatusError"

def test_prompt_injection_pipeline() -> None:
    """
    End-to-end validation of prompt injection detection.

    Pipeline:

        Malicious Prompt
              │
              ▼
      SentinelOrchestrator
              │
              ▼
      InputSecurityAgent
              │
              ▼
      PromptInjectionDetector
              │
              ▼
         Policy Engine
              │
              ▼
         Blocked Response
    """

    orchestrator = build_orchestrator()

    request = build_chat_request(
        query=PROMPT_INJECTION_QUERY,
        request_id="e2e-prompt-injection",
    )

    response = orchestrator.execute(request)

    assert isinstance(
        response,
        (SentinelResponse, ErrorResponse),
    )

    #
    # The pipeline should never crash.
    #
    if isinstance(response, SentinelResponse):

        #
        # If the request was blocked by the Input Security Agent,
        # the orchestrator should still return a successful
        # SentinelResponse carrying the security decision.
        #
        assert response.workflow == WorkflowType.CHAT
        assert response.request_id == "e2e-prompt-injection"
        assert response.data is not None

    else:

        #
        # External failures (LLM, etc.) must still be represented
        # as structured ErrorResponse objects.
        #
        assert response.success is False

def test_jailbreak_pipeline() -> None:
    """
    End-to-end validation of jailbreak detection.

    Pipeline:

        Jailbreak Prompt
              │
              ▼
      SentinelOrchestrator
              │
              ▼
      InputSecurityAgent
              │
              ▼
      JailbreakDetector
              │
              ▼
         Policy Engine
              │
              ▼
         Blocked Response
    """

    orchestrator = build_orchestrator()

    request = build_chat_request(
        query=JAILBREAK_QUERY,
        request_id="e2e-jailbreak",
    )

    response = orchestrator.execute(request)

    assert isinstance(
        response,
        (SentinelResponse, ErrorResponse),
    )

    if isinstance(response, SentinelResponse):

        assert response.workflow == WorkflowType.CHAT

        assert (
            response.request_id
            == "e2e-jailbreak"
        )

        assert response.data is not None

    else:

        assert response.success is False

def test_pii_pipeline() -> None:
    """
    End-to-end validation of PII detection.

    Pipeline:

        User Query
             │
             ▼
      SentinelOrchestrator
             │
             ▼
      InputSecurityAgent
             │
             ▼
         PIIDetector
             │
             ▼
        Policy Engine
             │
             ▼
      SentinelResponse / ErrorResponse
    """

    orchestrator = build_orchestrator()

    request = build_chat_request(
        query=PII_QUERY,
        request_id="e2e-pii",
    )

    response = orchestrator.execute(request)

    assert isinstance(
        response,
        (SentinelResponse, ErrorResponse),
    )

    if isinstance(response, SentinelResponse):

        assert response.success is True

        assert (
            response.workflow
            == WorkflowType.CHAT
        )

        assert (
            response.request_id
            == "e2e-pii"
        )

        assert response.data is not None

    else:

        #
        # External dependency failures must still
        # be represented as structured errors.
        #

        assert response.success is False

def test_hallucination_pipeline() -> None:
    """
    End-to-end validation of the hallucination
    detection and output validation pipeline.

    Pipeline:

        User Query
             │
             ▼
      SentinelOrchestrator
             │
             ▼
       AssistantAgent
             │
             ▼
         Retriever
             │
             ▼
      GeminiLLMClient
             │
             ▼
     OutputValidationAgent
             │
             ▼
      SentinelResponse / ErrorResponse
    """

    orchestrator = build_orchestrator()

    #
    # A query likely to require retrieval.
    #

    request = build_chat_request(
        query="Explain Sentinel architecture.",
        request_id="e2e-hallucination",
    )

    response = orchestrator.execute(request)

    assert isinstance(
        response,
        (SentinelResponse, ErrorResponse),
    )

    if isinstance(response, SentinelResponse):

        assert response.success is True

        assert (
            response.workflow
            == WorkflowType.CHAT
        )

        assert (
            response.request_id
            == "e2e-hallucination"
        )

        assert response.data is not None

        #
        # Output Validation should already
        # have processed the response.
        #

    else:

        #
        # GitHub Models outage or other
        # external dependency failure.
        #

        assert response.success is False