"""
Dependency injection for FastAPI.

Critical contract:
- The compiled LangGraph is built ONCE at application startup.
- It is never rebuilt per request.
- Agents are never instantiated per request.
- All request handlers receive the graph via FastAPI Depends().

Dependency construction order
-----------------------------
InputSecurityAgent          (graph boundary — injected into graph directly)
Embedder → VectorStore → Retriever
GeminiLLMClient
DocumentSecurityAgent       (required by AssistantAgent for document workflows)
AssistantAgent              (security_agent=None, output_validation_agent=None)
OutputValidationAgent       (graph boundary — injected into graph directly)
CompiledGraph
"""

from __future__ import annotations

import logging
from functools import lru_cache

from langgraph.graph.state import CompiledStateGraph

from src.assistant_agent.factory import AssistantAgentFactory
from src.document_security_agent.factory.document_security_factory import (
    DocumentSecurityFactory,
)
from src.input_security_agent.factory.factory import InputSecurityFactory
from src.knowledge_base.embedder import Embedder
from src.knowledge_base.retriever import Retriever
from src.knowledge_base.vector_store import VectorStore
from src.llm.gemini_client import GeminiLLMClient
from src.knowledge_base.ingestion.factory import KnowledgeIngestionFactory
from src.orchestration.langgraph.factory import LangGraphOrchestratorFactory
from src.output_validation_agent.factory import OutputValidationAgentFactory

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def _build_compiled_graph() -> CompiledStateGraph:
    """
    Builds and caches the compiled LangGraph exactly once.
    Called during lifespan startup — never during request handling.
    lru_cache(maxsize=1) guarantees single instantiation even under
    concurrent startup conditions.

    Boundary decisions
    ------------------
    - input_security_agent : injected into graph, NOT into AssistantAgent
    - output_validation_agent: injected into graph, NOT into AssistantAgent
    - document_security_agent: injected into AssistantAgent (required for
      document workflows — AssistantAgent raises immediately without it)
    - knowledge_ingestion_pipeline: omitted — AssistantAgentFactory builds
      it automatically (not a graph boundary)
    """
    logger.info("Building compiled LangGraph — this runs once at startup.")

    # ------------------------------------------------------------------
    # Step 1 — InputSecurityAgent.
    # Builds its own Embedder internally via InputSecurityFactory.
    # Injected directly into the graph — never into AssistantAgent.
    # ------------------------------------------------------------------
    input_security_agent = InputSecurityFactory.create_agent()
    logger.info("InputSecurityAgent ready.")

    # ------------------------------------------------------------------
    # Step 2 — Shared infrastructure for AssistantAgent.
    # ------------------------------------------------------------------
    embedder = Embedder()
    vector_store = VectorStore()
    retriever = Retriever(embedder=embedder, vector_store=vector_store)
    llm = GeminiLLMClient()
    logger.info("Retriever and LLM client ready.")

    # ------------------------------------------------------------------
    # Step 3 — DocumentSecurityAgent.
    # Required by AssistantAgent.analyze_document() and upload_document().
    # Without this, both document endpoints raise immediately.
    # ------------------------------------------------------------------
    document_security_agent = DocumentSecurityFactory.create_agent()
    logger.info("DocumentSecurityAgent ready.")

    # ------------------------------------------------------------------
    # Step 4 — AssistantAgent.
    # input_security_agent=None  → graph owns this boundary.
    # output_validation_agent=None → graph owns this boundary.
    #   AssistantAgentFactory no longer auto-constructs OutputValidationAgent
    #   (fix applied to factory.py in this session).
    # knowledge_ingestion_pipeline omitted → factory builds it automatically.
    # ------------------------------------------------------------------
    knowledge_ingestion_pipeline = KnowledgeIngestionFactory.create_agent(
        vector_store=vector_store,
    )

    assistant_agent = AssistantAgentFactory.create_agent(
        retriever=retriever,
        llm=llm,
        document_security_agent=document_security_agent,
        knowledge_ingestion_pipeline=knowledge_ingestion_pipeline,
        input_security_agent=None,
        output_validation_agent=None,
    )
    logger.info("AssistantAgent ready.")

    # ------------------------------------------------------------------
    # Step 5 — OutputValidationAgent.
    # Injected directly into the graph — never into AssistantAgent.
    # Shares the same GeminiLLMClient instance to avoid a second
    # Gemini connection being opened at startup.
    # ------------------------------------------------------------------
    output_validation_agent = OutputValidationAgentFactory.create_agent(llm=llm)
    logger.info("OutputValidationAgent ready.")

    # ------------------------------------------------------------------
    # Step 6 — Compile graph.
    # ------------------------------------------------------------------
    graph = LangGraphOrchestratorFactory.create(
        input_security_agent=input_security_agent,
        assistant_agent=assistant_agent,
        output_validation_agent=output_validation_agent,
    )
    logger.info("Compiled LangGraph ready.")
    return graph


def get_compiled_graph() -> CompiledStateGraph:
    """
    FastAPI dependency — injected into every router handler via Depends().
    Returns the already-built graph from the startup cache.
    Zero agent construction happens here.
    """
    return _build_compiled_graph()