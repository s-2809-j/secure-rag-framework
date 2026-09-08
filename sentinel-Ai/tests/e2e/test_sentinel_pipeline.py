import os
from pathlib import Path

import pytest

from src.assistant_agent.factory import AssistantAgentFactory
from src.document_security_agent.factory.document_security_factory import (
    DocumentSecurityFactory,
)
from src.input_security_agent.factory.factory import (
    InputSecurityFactory,
)
from src.knowledge_base.retriever import Retriever
from src.knowledge_base.vector_store import VectorStore
from src.knowledge_base.embedder import Embedder
from src.llm.gemini_client import GeminiLLMClient
from src.orchestration.factory import OrchestratorFactory
from src.orchestration.models import (
    ChatRequest,
    ErrorResponse,
    SentinelResponse,
    WorkflowType,
)


class TestSentinelPipeline:
    """
    End-to-end integration tests for the complete Sentinel AI Engine.
    """

    @pytest.fixture
    def orchestrator(self):
        """Build a fully configured orchestrator with all dependencies."""
        
        # Build LLM client
        llm_client = GeminiLLMClient()
        
        # Build retriever stack (Embedder → VectorStore → Retriever)
        embedder = Embedder()
        vector_store = VectorStore(
            db_path="chroma_db",
            collection_name="sentinel_knowledge_base",
        )
        retriever = Retriever(
            embedder=embedder,
            vector_store=vector_store,
            top_k=5,
        )
        
        # Build security agents
        input_agent = InputSecurityFactory.create_agent()
        doc_agent = DocumentSecurityFactory.create_agent()
        
        # Build assistant agent with all required dependencies
        assistant_agent = AssistantAgentFactory.create_agent(
            retriever=retriever,
            llm=llm_client,
            input_security_agent=input_agent,
            document_security_agent=doc_agent,
        )

        # Build orchestrator with output validation enabled
        return OrchestratorFactory.create(
            input_security_agent=input_agent,
            document_security_agent=doc_agent,
            assistant_agent=assistant_agent,
            enable_output_validation=True,
        )

    def test_chat_workflow_with_output_validation(
        self,
        orchestrator,
    ) -> None:
        """
        Verify that chat workflow executes end-to-end with
        output validation enabled.

        This test requires environment variables:
        - LLM_PROVIDER
        - LLM_MODEL
        - LLM_BASE_URL
        - GITHUB_TOKEN
        """

        required_env = (
            "LLM_PROVIDER",
            "LLM_MODEL",
            "LLM_BASE_URL",
            "GITHUB_TOKEN",
        )

        missing = [
            var for var in required_env if not os.getenv(var)
        ]

        if missing:
            pytest.skip(
                "Missing environment variables: "
                + ", ".join(missing)
            )

        request = ChatRequest(
            query="What is the capital of France?",
            workflow=WorkflowType.CHAT,
            request_id="e2e-test-001",
        )

        response = orchestrator.execute(request)

        # Response should be successful
        assert isinstance(response, SentinelResponse)
        assert response.success is True
        assert response.workflow == WorkflowType.CHAT
        assert response.request_id == "e2e-test-001"

        # Response data should include assistant response + validation
        assert response.data is not None
        assert isinstance(response.data, dict)

        # If output validation is enabled, validation_decision
        # should be present
        if "validation_decision" in response.data:
            validation_decision = response.data[
                "validation_decision"
            ]

            # Decision should have standard fields
            assert hasattr(validation_decision, "approved")
            assert hasattr(
                validation_decision,
                "policy_evaluation",
            )
            assert hasattr(
                validation_decision,
                "risk_assessment",
            )

    def test_chat_workflow_without_output_validation(
        self,
    ) -> None:
        """
        Verify that chat workflow works with output validation disabled
        (legacy behavior).
        """

        required_env = (
            "LLM_PROVIDER",
            "LLM_MODEL",
            "LLM_BASE_URL",
            "GITHUB_TOKEN",
        )

        missing = [
            var for var in required_env if not os.getenv(var)
        ]

        if missing:
            pytest.skip(
                "Missing environment variables: "
                + ", ".join(missing)
            )

        # Build LLM client
        llm_client = GeminiLLMClient()
        
        # Build retriever stack
        embedder = Embedder()
        vector_store = VectorStore(
            db_path="chroma_db",
            collection_name="sentinel_knowledge_base",
        )
        retriever = Retriever(
            embedder=embedder,
            vector_store=vector_store,
            top_k=5,
        )
        
        # Build security agents
        input_agent = InputSecurityFactory.create_agent()
        doc_agent = DocumentSecurityFactory.create_agent()
        
        # Build assistant agent
        assistant_agent = AssistantAgentFactory.create_agent(
            retriever=retriever,
            llm=llm_client,
            input_security_agent=input_agent,
            document_security_agent=doc_agent,
        )

        # Build orchestrator with output validation DISABLED
        orchestrator = OrchestratorFactory.create(
            input_security_agent=input_agent,
            document_security_agent=doc_agent,
            assistant_agent=assistant_agent,
            enable_output_validation=False,
        )

        request = ChatRequest(
            query="What is the capital of France?",
            workflow=WorkflowType.CHAT,
            request_id="e2e-test-002",
        )

        response = orchestrator.execute(request)

        # Response should be successful
        assert isinstance(response, SentinelResponse)
        assert response.success is True

        # With validation disabled, validation_decision
        # should NOT be present
        assert "validation_decision" not in (
            response.data or {}
        )

    def test_invalid_workflow_returns_error(self) -> None:
        """
        Verify that invalid workflows are caught and return
        an ErrorResponse.
        """

        # Build LLM client
        llm_client = GeminiLLMClient()
        
        # Build retriever stack
        embedder = Embedder()
        vector_store = VectorStore(
            db_path="chroma_db",
            collection_name="sentinel_knowledge_base",
        )
        retriever = Retriever(
            embedder=embedder,
            vector_store=vector_store,
            top_k=5,
        )
        
        # Build security agents
        input_agent = InputSecurityFactory.create_agent()
        doc_agent = DocumentSecurityFactory.create_agent()
        
        # Build assistant agent
        assistant_agent = AssistantAgentFactory.create_agent(
            retriever=retriever,
            llm=llm_client,
            input_security_agent=input_agent,
            document_security_agent=doc_agent,
        )

        orchestrator = OrchestratorFactory.create(
            input_security_agent=input_agent,
            document_security_agent=doc_agent,
            assistant_agent=assistant_agent,
        )

        request = ChatRequest(
            query="Test",
            workflow=WorkflowType.CHAT,
        )

        response = orchestrator.execute(request)

        # Should not raise exception, returns response
        assert isinstance(
            response,
            (SentinelResponse, ErrorResponse),
        )