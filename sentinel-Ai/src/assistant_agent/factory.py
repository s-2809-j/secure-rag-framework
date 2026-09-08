
"""
Factory for constructing AssistantAgent instances.
"""

from __future__ import annotations

from typing import Optional

from src.assistant_agent.assistant_agent import AssistantAgent
from src.document_security_agent.document_security_agent import DocumentSecurityAgent
from src.input_security_agent.input_security_agent import InputSecurityAgent
from src.knowledge_base.ingestion.factory import KnowledgeIngestionFactory
from src.knowledge_base.ingestion.knowledge_ingestion_pipeline import KnowledgeIngestionPipeline
from src.knowledge_base.retriever import Retriever
from src.llm.gemini_client import GeminiLLMClient
from src.output_validation_agent.output_validation_agent import OutputValidationAgent


class AssistantAgentFactory:
    """
    Factory responsible for creating AssistantAgent instances.

    Boundary contract
    -----------------
    - LangGraph owns InputSecurityAgent and OutputValidationAgent.
      Neither is constructed here when operating under the graph.
    - KnowledgeIngestionPipeline is NOT a graph boundary — the factory
      may construct it automatically when omitted.
    - DocumentSecurityAgent is required for document workflows.
      Callers must supply it explicitly.
    """

    @staticmethod
    def create_agent(
        *,
        retriever: Retriever,
        llm: GeminiLLMClient,
        input_security_agent: Optional[InputSecurityAgent] = None,
        document_security_agent: Optional[DocumentSecurityAgent] = None,
        knowledge_ingestion_pipeline: Optional[KnowledgeIngestionPipeline] = None,
        output_validation_agent: Optional[OutputValidationAgent] = None,
    ) -> AssistantAgent:
        """
        Create a fully configured AssistantAgent.

        Parameters
        ----------
        retriever:
            Required. Used by generate_response() for RAG retrieval.

        llm:
            Required. GeminiLLMClient used for response generation.

        input_security_agent:
            Must be None when AssistantAgent is used under LangGraph.
            The graph owns input security at the orchestration boundary.

        document_security_agent:
            Required for analyze_document() and upload_document().
            AssistantAgent raises DocumentAnalysisError / DocumentUploadError
            immediately if this is None and either method is called.

        knowledge_ingestion_pipeline:
            Optional. If None, KnowledgeIngestionFactory.create_agent()
            is called automatically — the graph does not own this boundary.

        output_validation_agent:
            Must be None when AssistantAgent is used under LangGraph.
            The graph owns output validation at the orchestration boundary.
            Unlike KnowledgeIngestionPipeline, this is NOT auto-constructed
            here because the graph always supplies its own instance.
        """

        if knowledge_ingestion_pipeline is None:
            knowledge_ingestion_pipeline = (
                KnowledgeIngestionFactory.create_agent()
            )

        # output_validation_agent is intentionally NOT auto-constructed.
        # When operating under LangGraph, it must remain None so the graph
        # owns the validation boundary exclusively. Callers who need
        # standalone AssistantAgent validation must pass it explicitly.

        return AssistantAgent(
            retriever=retriever,
            llm=llm,
            security_agent=input_security_agent,
            document_security_agent=document_security_agent,
            knowledge_ingestion_pipeline=knowledge_ingestion_pipeline,
            output_validation_agent=output_validation_agent,
        )    