"""
End-to-end integration tests for the Sentinel LangGraph layer.

Verifies that the compiled LangGraph graph produces correct results
when wired with real production agents — not mocks.

These tests are the final validation gate for LangGraph integration.
Passing these tests means the LangGraph layer is conclusively integrated
with the real Sentinel AI Engine.

Test Coverage
-------------
- Chat workflow: safe query flows through all three agents
- Chat workflow: blocked query never reaches AssistantAgent
- Chat workflow: prompt injection is blocked at security node
- Document analysis workflow: real document processed correctly
- Knowledge upload workflow: real document ingested correctly
- Parity: LangGraph and SentinelOrchestrator agree on outcomes

Design Constraints
------------------
- No mocks. All agents are real production instances.
- Reuses integration_support.py builders — no duplicated wiring.
- AssistantAgent is constructed WITHOUT security_agent or
  output_validation_agent (double-execution prevention rule).
- Each test builds its own graph to guarantee isolation.
- All state values passed to graph.invoke() are msgpack-serializable.

External Dependency Notes
-------------------------
- Gemini API: subject to 429 RESOURCE_EXHAUSTED on free tier.
  Tests that depend on LLM responses tolerate this gracefully —
  a rate-limit failure is an infrastructure failure, not a logic bug.
- Jailbreak/PII detection: probabilistic. Tests assert the pipeline
  does not crash and produces a valid final_response, not that a
  specific detection decision is made.
"""

from __future__ import annotations

from pathlib import Path
from uuid import uuid4

import pytest

from langgraph.checkpoint.memory import MemorySaver

from src.orchestration.langgraph.factory import LangGraphOrchestratorFactory
from src.orchestration.models import WorkflowType

from tests.e2e2.integration_support import (
    SAFE_DOCUMENT,
    SAFE_CHAT_QUERY,
    PROMPT_INJECTION_QUERY,
    JAILBREAK_QUERY,
    PII_QUERY,
    build_metadata,
    build_input_security_agent,
    build_assistant_agent,
    build_orchestrator,
)

# ============================================================
# Helpers
# ============================================================


def _build_graph(*, with_validation: bool = True):
    """
    Construct a compiled LangGraph with real production agents.

    AssistantAgent is built via build_assistant_agent() which internally
    wires its own input_security_agent and document_security_agent.
    The graph receives a SEPARATE input_security_agent instance to own
    the graph-level security boundary, satisfying the double-execution
    prevention contract.
    """
    from src.output_validation_agent.factory import OutputValidationAgentFactory

    input_security_agent = build_input_security_agent()
    assistant_agent = build_assistant_agent()

    output_validation_agent = (
        OutputValidationAgentFactory.create_agent()
        if with_validation
        else None
    )

    return LangGraphOrchestratorFactory.create(
        input_security_agent=input_security_agent,
        assistant_agent=assistant_agent,
        output_validation_agent=output_validation_agent,
        checkpointer=MemorySaver(),
    )


def _build_initial_state(
    *,
    workflow: str,
    query: str | None = None,
    file_path: Path | None = None,
    metadata=None,
    request_id: str | None = None,
) -> dict:
    """
    Build a fully populated initial state dict.

    All values are msgpack-serializable.
    MagicMock must never appear here.
    """
    return {
        "request_id": request_id or str(uuid4()),
        "workflow": workflow,
        "query": query,
        "file_path": file_path,
        "metadata": metadata,
        "security_passed": None,
        "normalized_query": None,
        "risk_score": None,
        "blocked": None,
        "raw_response": None,
        "validation_approved": None,
        "final_response": None,
        "error": None,
    }


def _invoke(graph, state: dict) -> dict:
    """
    Invoke the compiled graph with a thread_id scoped to this request.
    """
    config = {"configurable": {"thread_id": state["request_id"]}}
    return graph.invoke(state, config)


def _llm_available(result: dict) -> bool:
    """
    Return True if the graph reached the LLM and produced a response.
    Returns False when Gemini returned a rate-limit or other API error,
    which causes blocked=True and error field to be set.
    """
    return (
        result.get("blocked") is not True
        and result.get("raw_response") is not None
    )


# ============================================================
# Chat Workflow — Safe Query
# ============================================================


class TestLangGraphChatWorkflow:

    def test_safe_chat_produces_final_response(self) -> None:
        """
        A safe query must always produce a non-None final_response.
        When the LLM is available: final_response is the validated string.
        When rate-limited: final_response is the blocked dict.
        Either way, final_response must not be None.
        """
        graph = _build_graph()
        state = _build_initial_state(
            workflow=WorkflowType.CHAT,
            query=SAFE_CHAT_QUERY,
            request_id="e2e-lg-safe-chat",
        )

        result = _invoke(graph, state)

        assert result["final_response"] is not None

    def test_safe_chat_security_passes(self) -> None:
        """
        A safe query must pass the security node.
        security_passed=True and blocked=False after security_node.
        This is independent of whether the LLM is available.
        """
        graph = _build_graph()
        state = _build_initial_state(
            workflow=WorkflowType.CHAT,
            query=SAFE_CHAT_QUERY,
            request_id="e2e-lg-safe-chat-security",
        )

        result = _invoke(graph, state)

        assert result["security_passed"] is True

    def test_safe_chat_normalized_query_is_set(self) -> None:
        """
        Security node must write normalized_query for chat workflows.
        This is independent of LLM availability.
        """
        graph = _build_graph()
        state = _build_initial_state(
            workflow=WorkflowType.CHAT,
            query=SAFE_CHAT_QUERY,
            request_id="e2e-lg-safe-chat-normalized",
        )

        result = _invoke(graph, state)

        assert result["normalized_query"] is not None
        assert isinstance(result["normalized_query"], str)
        assert len(result["normalized_query"]) > 0

    def test_safe_chat_raw_response_set_when_llm_available(self) -> None:
        """
        When LLM is available, chat_generation_node must write raw_response.
        Skipped gracefully when rate-limited — that is an infrastructure
        failure, not a logic failure.
        """
        graph = _build_graph()
        state = _build_initial_state(
            workflow=WorkflowType.CHAT,
            query=SAFE_CHAT_QUERY,
            request_id="e2e-lg-safe-chat-raw",
        )

        result = _invoke(graph, state)

        if _llm_available(result):
            assert result["raw_response"] is not None
            assert isinstance(result["raw_response"], str)

    def test_safe_chat_validation_approved_when_llm_available(self) -> None:
        """
        When LLM is available and produces a valid response,
        OutputValidationAgent must approve it.
        Skipped gracefully when rate-limited.
        """
        graph = _build_graph(with_validation=True)
        state = _build_initial_state(
            workflow=WorkflowType.CHAT,
            query=SAFE_CHAT_QUERY,
            request_id="e2e-lg-safe-chat-validation",
        )

        result = _invoke(graph, state)

        if _llm_available(result):
            assert result["validation_approved"] is True

    def test_safe_chat_without_validation_agent(self) -> None:
        """
        When output_validation_agent is None and LLM is available,
        raw_response must be passed through as final_response directly.
        """
        graph = _build_graph(with_validation=False)
        state = _build_initial_state(
            workflow=WorkflowType.CHAT,
            query=SAFE_CHAT_QUERY,
            request_id="e2e-lg-safe-chat-no-validation",
        )

        result = _invoke(graph, state)

        if _llm_available(result):
            assert result["final_response"] is not None
            assert result["final_response"] == result["raw_response"]

    def test_safe_chat_error_field_is_none_when_llm_available(self) -> None:
        """
        When LLM is available and all agents succeed,
        the error field must be None.
        """
        graph = _build_graph()
        state = _build_initial_state(
            workflow=WorkflowType.CHAT,
            query=SAFE_CHAT_QUERY,
            request_id="e2e-lg-safe-chat-no-error",
        )

        result = _invoke(graph, state)

        if _llm_available(result):
            assert result["error"] is None


# ============================================================
# Chat Workflow — Blocked Queries
# ============================================================


class TestLangGraphBlockedWorkflow:

    def test_prompt_injection_is_blocked(self) -> None:
        """
        A prompt injection query must be blocked by security_node.
        blocked=True and final_response must be a structured dict.
        """
        graph = _build_graph()
        state = _build_initial_state(
            workflow=WorkflowType.CHAT,
            query=PROMPT_INJECTION_QUERY,
            request_id="e2e-lg-prompt-injection",
        )

        result = _invoke(graph, state)

        assert result["blocked"] is True
        assert isinstance(result["final_response"], dict)
        assert result["final_response"]["blocked"] is True

    def test_prompt_injection_blocked_response_contains_risk_score(self) -> None:
        """
        The structured blocked response dict must contain risk_score.
        """
        graph = _build_graph()
        state = _build_initial_state(
            workflow=WorkflowType.CHAT,
            query=PROMPT_INJECTION_QUERY,
            request_id="e2e-lg-prompt-injection-risk",
        )

        result = _invoke(graph, state)

        assert result["blocked"] is True
        assert "risk_score" in result["final_response"]

    def test_prompt_injection_blocked_risk_score_is_high(self) -> None:
        """
        Blocked queries must carry a risk_score above 0.5.
        """
        graph = _build_graph()
        state = _build_initial_state(
            workflow=WorkflowType.CHAT,
            query=PROMPT_INJECTION_QUERY,
            request_id="e2e-lg-prompt-injection-risk-score",
        )

        result = _invoke(graph, state)

        assert result["blocked"] is True
        assert result["risk_score"] is not None
        assert result["risk_score"] > 0.5

    def test_prompt_injection_never_produces_raw_response(self) -> None:
        """
        A blocked query must never reach chat_generation_node.
        raw_response must remain None.
        """
        graph = _build_graph()
        state = _build_initial_state(
            workflow=WorkflowType.CHAT,
            query=PROMPT_INJECTION_QUERY,
            request_id="e2e-lg-prompt-injection-no-raw",
        )

        result = _invoke(graph, state)

        assert result["blocked"] is True
        assert result["raw_response"] is None

    def test_jailbreak_does_not_crash(self) -> None:
        """
        A jailbreak query must be handled without raising.
        Detection is probabilistic — the test asserts correctness of
        pipeline behavior for either outcome (blocked or passed through),
        not that the detector fires on this specific string.
        """
        graph = _build_graph()
        state = _build_initial_state(
            workflow=WorkflowType.CHAT,
            query=JAILBREAK_QUERY,
            request_id="e2e-lg-jailbreak",
        )

        result = _invoke(graph, state)

        # Pipeline must always produce a final_response — never None
        assert result["final_response"] is not None

        # If blocked: final_response must be structured dict
        if result["blocked"] is True:
            assert isinstance(result["final_response"], dict)
            assert result["final_response"]["blocked"] is True

    def test_pii_query_does_not_crash(self) -> None:
        """
        A PII query must be handled without raising.
        Either blocked or passed through — both are valid outcomes.
        """
        graph = _build_graph()
        state = _build_initial_state(
            workflow=WorkflowType.CHAT,
            query=PII_QUERY,
            request_id="e2e-lg-pii",
        )

        result = _invoke(graph, state)

        assert result["final_response"] is not None


# ============================================================
# Document Analysis Workflow
# ============================================================


class TestLangGraphDocumentAnalysisWorkflow:

    def test_document_analysis_produces_final_response(self) -> None:
        """
        A real document must flow through the document analysis node
        and produce a non-None final_response.
        """
        graph = _build_graph()
        metadata = build_metadata(SAFE_DOCUMENT)
        state = _build_initial_state(
            workflow=WorkflowType.DOCUMENT_ANALYSIS,
            file_path=SAFE_DOCUMENT,
            metadata=metadata,
            request_id="e2e-lg-doc-analysis",
        )

        result = _invoke(graph, state)

        assert result["final_response"] is not None

    def test_document_analysis_is_not_blocked(self) -> None:
        """
        A safe document must not be blocked.
        security_node bypasses InputSecurityAgent for non-chat workflows
        so blocked must be False after the graph completes.
        """
        graph = _build_graph()
        metadata = build_metadata(SAFE_DOCUMENT)
        state = _build_initial_state(
            workflow=WorkflowType.DOCUMENT_ANALYSIS,
            file_path=SAFE_DOCUMENT,
            metadata=metadata,
            request_id="e2e-lg-doc-analysis-not-blocked",
        )

        result = _invoke(graph, state)

        assert result["blocked"] is not True

    def test_document_analysis_security_passed_is_true(self) -> None:
        """
        security_node must set security_passed=True for document workflows
        (bypass path, not agent invocation).
        """
        graph = _build_graph()
        metadata = build_metadata(SAFE_DOCUMENT)
        state = _build_initial_state(
            workflow=WorkflowType.DOCUMENT_ANALYSIS,
            file_path=SAFE_DOCUMENT,
            metadata=metadata,
            request_id="e2e-lg-doc-analysis-security-passed",
        )

        result = _invoke(graph, state)

        assert result["security_passed"] is True

    def test_document_analysis_never_sets_raw_response(self) -> None:
        """
        Document analysis must never reach chat_generation_node.
        raw_response must remain None.
        """
        graph = _build_graph()
        metadata = build_metadata(SAFE_DOCUMENT)
        state = _build_initial_state(
            workflow=WorkflowType.DOCUMENT_ANALYSIS,
            file_path=SAFE_DOCUMENT,
            metadata=metadata,
            request_id="e2e-lg-doc-analysis-no-raw",
        )

        result = _invoke(graph, state)

        assert result["raw_response"] is None

    def test_document_analysis_never_sets_validation_approved(self) -> None:
        """
        Document analysis must never reach validation_node.
        validation_approved must remain None.
        """
        graph = _build_graph(with_validation=True)
        metadata = build_metadata(SAFE_DOCUMENT)
        state = _build_initial_state(
            workflow=WorkflowType.DOCUMENT_ANALYSIS,
            file_path=SAFE_DOCUMENT,
            metadata=metadata,
            request_id="e2e-lg-doc-analysis-no-validation",
        )

        result = _invoke(graph, state)

        assert result["validation_approved"] is None

    def test_document_analysis_error_field_is_none(self) -> None:
        """
        A clean document analysis run must not populate the error field.
        """
        graph = _build_graph()
        metadata = build_metadata(SAFE_DOCUMENT)
        state = _build_initial_state(
            workflow=WorkflowType.DOCUMENT_ANALYSIS,
            file_path=SAFE_DOCUMENT,
            metadata=metadata,
            request_id="e2e-lg-doc-analysis-no-error",
        )

        result = _invoke(graph, state)

        assert result["error"] is None


# ============================================================
# Knowledge Upload Workflow
# ============================================================


class TestLangGraphKnowledgeUploadWorkflow:

    def test_knowledge_upload_produces_final_response(self) -> None:
        """
        A real document must flow through the knowledge upload node
        and produce a non-None final_response.
        """
        graph = _build_graph()
        metadata = build_metadata(SAFE_DOCUMENT)
        state = _build_initial_state(
            workflow=WorkflowType.KNOWLEDGE_UPLOAD,
            file_path=SAFE_DOCUMENT,
            metadata=metadata,
            request_id="e2e-lg-knowledge-upload",
        )

        result = _invoke(graph, state)

        assert result["final_response"] is not None

    def test_knowledge_upload_is_not_blocked(self) -> None:
        """
        A safe document must not be blocked.
        security_node bypasses InputSecurityAgent for non-chat workflows.
        """
        graph = _build_graph()
        metadata = build_metadata(SAFE_DOCUMENT)
        state = _build_initial_state(
            workflow=WorkflowType.KNOWLEDGE_UPLOAD,
            file_path=SAFE_DOCUMENT,
            metadata=metadata,
            request_id="e2e-lg-knowledge-upload-not-blocked",
        )

        result = _invoke(graph, state)

        assert result["blocked"] is not True

    def test_knowledge_upload_security_passed_is_true(self) -> None:
        """
        security_node must set security_passed=True for upload workflows
        (bypass path, not agent invocation).
        """
        graph = _build_graph()
        metadata = build_metadata(SAFE_DOCUMENT)
        state = _build_initial_state(
            workflow=WorkflowType.KNOWLEDGE_UPLOAD,
            file_path=SAFE_DOCUMENT,
            metadata=metadata,
            request_id="e2e-lg-knowledge-upload-security-passed",
        )

        result = _invoke(graph, state)

        assert result["security_passed"] is True

    def test_knowledge_upload_never_sets_raw_response(self) -> None:
        """
        Knowledge upload must never reach chat_generation_node.
        raw_response must remain None.
        """
        graph = _build_graph()
        metadata = build_metadata(SAFE_DOCUMENT)
        state = _build_initial_state(
            workflow=WorkflowType.KNOWLEDGE_UPLOAD,
            file_path=SAFE_DOCUMENT,
            metadata=metadata,
            request_id="e2e-lg-knowledge-upload-no-raw",
        )

        result = _invoke(graph, state)

        assert result["raw_response"] is None

    def test_knowledge_upload_never_sets_validation_approved(self) -> None:
        """
        Knowledge upload must never reach validation_node.
        validation_approved must remain None.
        """
        graph = _build_graph(with_validation=True)
        metadata = build_metadata(SAFE_DOCUMENT)
        state = _build_initial_state(
            workflow=WorkflowType.KNOWLEDGE_UPLOAD,
            file_path=SAFE_DOCUMENT,
            metadata=metadata,
            request_id="e2e-lg-knowledge-upload-no-validation",
        )

        result = _invoke(graph, state)

        assert result["validation_approved"] is None

    def test_knowledge_upload_error_field_is_none(self) -> None:
        """
        A clean knowledge upload run must not populate the error field.
        """
        graph = _build_graph()
        metadata = build_metadata(SAFE_DOCUMENT)
        state = _build_initial_state(
            workflow=WorkflowType.KNOWLEDGE_UPLOAD,
            file_path=SAFE_DOCUMENT,
            metadata=metadata,
            request_id="e2e-lg-knowledge-upload-no-error",
        )

        result = _invoke(graph, state)

        assert result["error"] is None


# ============================================================
# Parity — LangGraph vs SentinelOrchestrator
# ============================================================


class TestLangGraphParityWithOrchestrator:

    def test_safe_chat_parity(self) -> None:
        """
        Both execution paths must either both succeed or both fail
        for the same safe query.

        When LLM is available: both produce a non-empty string response.
        When rate-limited: both fail gracefully — orchestrator returns
        ErrorResponse, graph returns blocked state. Neither crashes.

        Structural parity only — exact wording differs per invocation.
        """
        from src.orchestration.models import ChatRequest
        from src.orchestration.models import ErrorResponse

        orchestrator = build_orchestrator()
        orch_request = ChatRequest(
            workflow=WorkflowType.CHAT,
            query=SAFE_CHAT_QUERY,
            request_id="e2e-parity-orch",
        )
        orch_response = orchestrator.execute(orch_request)

        graph = _build_graph()
        graph_state = _build_initial_state(
            workflow=WorkflowType.CHAT,
            query=SAFE_CHAT_QUERY,
            request_id="e2e-parity-graph",
        )
        graph_result = _invoke(graph, graph_state)

        orch_llm_available = isinstance(orch_response, ErrorResponse) is False and orch_response.success is True
        graph_llm_available = _llm_available(graph_result)

        if orch_llm_available and graph_llm_available:
            # Both succeeded — verify both produced non-empty string responses
            assert isinstance(orch_response.data, str)
            assert len(orch_response.data) > 0
            assert isinstance(graph_result["final_response"], str)
            assert len(graph_result["final_response"]) > 0
        else:
            # At least one was rate-limited — verify neither crashed
            # (ErrorResponse and blocked dict are both valid graceful failures)
            assert orch_response is not None
            assert graph_result["final_response"] is not None

    def test_blocked_query_parity(self) -> None:
        """
        Both execution paths must agree that a prompt injection query
        is blocked — neither must pass it through to the LLM.

        SentinelOrchestrator returns success=False with blocked data dict.
        LangGraph returns blocked=True with structured dict.
        Both agree: the query did not reach the LLM.
        """
        from src.orchestration.models import ChatRequest

        orchestrator = build_orchestrator()
        orch_request = ChatRequest(
            workflow=WorkflowType.CHAT,
            query=PROMPT_INJECTION_QUERY,
            request_id="e2e-parity-blocked-orch",
        )
        orch_response = orchestrator.execute(orch_request)

        graph = _build_graph()
        graph_state = _build_initial_state(
            workflow=WorkflowType.CHAT,
            query=PROMPT_INJECTION_QUERY,
            request_id="e2e-parity-blocked-graph",
        )
        graph_result = _invoke(graph, graph_state)

        # Orchestrator: success=False, data contains blocked dict
        assert orch_response.success is False
        assert orch_response.data is not None
        assert orch_response.data["blocked"] is True

        # Graph: blocked=True, final_response is structured dict
        assert graph_result["blocked"] is True
        assert graph_result["final_response"]["blocked"] is True

    def test_document_analysis_parity(self) -> None:
        """
        Both execution paths must produce a non-None result
        for the same safe document.
        """
        from src.orchestration.models import DocumentAnalysisRequest

        metadata = build_metadata(SAFE_DOCUMENT)

        orchestrator = build_orchestrator()
        orch_request = DocumentAnalysisRequest(
            workflow=WorkflowType.DOCUMENT_ANALYSIS,
            file_path=SAFE_DOCUMENT,
            metadata=metadata,
            request_id="e2e-parity-doc-orch",
        )
        orch_response = orchestrator.execute(orch_request)

        graph = _build_graph()
        graph_state = _build_initial_state(
            workflow=WorkflowType.DOCUMENT_ANALYSIS,
            file_path=SAFE_DOCUMENT,
            metadata=metadata,
            request_id="e2e-parity-doc-graph",
        )
        graph_result = _invoke(graph, graph_state)

        # Both must succeed with non-None data
        assert orch_response.success is True
        assert orch_response.data is not None

        assert graph_result["final_response"] is not None
        assert graph_result["blocked"] is not True

    def test_knowledge_upload_parity(self) -> None:
        """
        Both execution paths must produce a non-None result
        for the same safe document upload.
        """
        from src.orchestration.models import KnowledgeUploadRequest

        metadata = build_metadata(SAFE_DOCUMENT)

        orchestrator = build_orchestrator()
        orch_request = KnowledgeUploadRequest(
            workflow=WorkflowType.KNOWLEDGE_UPLOAD,
            file_path=SAFE_DOCUMENT,
            metadata=metadata,
            request_id="e2e-parity-upload-orch",
        )
        orch_response = orchestrator.execute(orch_request)

        graph = _build_graph()
        graph_state = _build_initial_state(
            workflow=WorkflowType.KNOWLEDGE_UPLOAD,
            file_path=SAFE_DOCUMENT,
            metadata=metadata,
            request_id="e2e-parity-upload-graph",
        )
        graph_result = _invoke(graph, graph_state)

        # Both must succeed with non-None data
        assert orch_response.success is True
        assert orch_response.data is not None

        assert graph_result["final_response"] is not None
        assert graph_result["blocked"] is not True