"""
Tests for AssistantAgentFactory.
"""

from __future__ import annotations

from src.assistant_agent.assistant_agent import AssistantAgent
from src.assistant_agent.factory import AssistantAgentFactory

from src.knowledge_base.models import RetrievedChunk


# ---------------------------------------------------------------------
# Test Doubles
# ---------------------------------------------------------------------


class FakeRetriever:

    def retrieve(
        self,
        *,
        query: str,
        top_k: int,
        metadata_filter: dict[str, str] | None = None,
    ) -> list[RetrievedChunk]:

        return []


class FakeLLM:

    def generate(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
    ) -> str:

        return "Fake response"


class FakeSecurityAgent:

    pass


class FakeDocumentSecurityAgent:

    pass


class FakeKnowledgeIngestionPipeline:

    pass


class FakeOutputValidationAgent:

    pass


# ---------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------


def test_create_agent_with_required_dependencies() -> None:
    """
    Factory should successfully construct an AssistantAgent
    when only mandatory dependencies are supplied.
    """

    agent = AssistantAgentFactory.create_agent(
        retriever=FakeRetriever(),
        llm=FakeLLM(),
    )

    assert isinstance(agent, AssistantAgent)


def test_create_agent_with_all_dependencies() -> None:
    """
    Factory should preserve user supplied dependencies.
    """

    retriever = FakeRetriever()
    llm = FakeLLM()
    security = FakeSecurityAgent()
    document_security = FakeDocumentSecurityAgent()
    ingestion = FakeKnowledgeIngestionPipeline()
    output_validation = FakeOutputValidationAgent()

    agent = AssistantAgentFactory.create_agent(
        retriever=retriever,
        llm=llm,
        input_security_agent=security,
        document_security_agent=document_security,
        knowledge_ingestion_pipeline=ingestion,
        output_validation_agent=output_validation,
    )

    assert isinstance(agent, AssistantAgent)

    assert agent._retriever is retriever
    assert agent._llm is llm
    assert agent._security_agent is security
    assert agent._document_security_agent is document_security
    assert (
        agent._knowledge_ingestion_pipeline
        is ingestion
    )
    assert (
        agent._output_validation_agent
        is output_validation
    )


def test_factory_creates_default_ingestion_pipeline() -> None:
    """
    Factory should automatically create the default
    KnowledgeIngestionPipeline.
    """

    agent = AssistantAgentFactory.create_agent(
        retriever=FakeRetriever(),
        llm=FakeLLM(),
    )

    assert (
        agent._knowledge_ingestion_pipeline
        is not None
    )


def test_factory_creates_default_output_validation_agent() -> None:
    """
    Factory should automatically create the default
    OutputValidationAgent.
    """

    agent = AssistantAgentFactory.create_agent(
        retriever=FakeRetriever(),
        llm=FakeLLM(),
    )

    assert (
        agent._output_validation_agent
        is not None
    )