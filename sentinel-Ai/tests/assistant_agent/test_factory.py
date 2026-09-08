"""
Integration tests for AssistantAgentFactory.

Run:
    python -m tests.assistant_agent.test_factory
"""

from annotated_types import Ge

from src.assistant_agent.assistant_agent import AssistantAgent
from src.assistant_agent.factory import (
    AssistantAgentFactory,
)

from src.knowledge_base.embedder import Embedder
from src.knowledge_base.vector_store import VectorStore
from src.knowledge_base.retriever import Retriever

from src.llm.gemini_client import GeminiLLMClient

from src.input_security_agent.factory import (
    InputSecurityFactory,
)

from src.document_security_agent.factory.document_security_factory import (
    DocumentSecurityFactory,
)


def test_create_assistant_agent() -> None:

    print("=" * 70)
    print("Testing AssistantAgentFactory")
    print("=" * 70)

    #
    # Infrastructure
    #

    embedder = Embedder()

    vector_store = VectorStore()

    retriever = Retriever(
        embedder=embedder,
        vector_store=vector_store,
    )

    llm =  GeminiLLMClient()

    #
    # Security Agents
    #

    input_security_agent = (
        InputSecurityFactory.create_agent()
    )

    document_security_agent = (
        DocumentSecurityFactory.create_agent()
    )

    #
    # Factory Under Test
    #

    assistant = AssistantAgentFactory.create_agent(
        retriever=retriever,
        llm=llm,
        input_security_agent=input_security_agent,
        document_security_agent=document_security_agent,
    )

    assert assistant is not None
    assert isinstance(assistant, AssistantAgent)

    print("[PASS] AssistantAgent created successfully.")

    assert assistant._retriever is retriever
    print("[PASS] Retriever injected.")

    assert assistant._llm is llm
    print("[PASS] GeminiLLMClient injected.")

    assert assistant._security_agent is input_security_agent
    print("[PASS] InputSecurityAgent injected.")

    assert (
        assistant._document_security_agent
        is document_security_agent
    )
    print("[PASS] DocumentSecurityAgent injected.")

    assert (
        assistant._knowledge_ingestion_pipeline
        is not None
    )
    print("[PASS] KnowledgeIngestionPipeline initialized.")


def main():

    test_create_assistant_agent()

    print()
    print("=" * 70)
    print("All AssistantAgentFactory tests passed.")
    print("=" * 70)


if __name__ == "__main__":
    main()