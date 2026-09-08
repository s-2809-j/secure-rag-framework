"""
Factory for creating Knowledge Ingestion Pipeline instances.
"""

from __future__ import annotations

from src.knowledge_base.chunker import TextChunker
from src.knowledge_base.embedder import Embedder
from src.knowledge_base.vector_store import VectorStore

from .knowledge_ingestion_pipeline import KnowledgeIngestionPipeline


class KnowledgeIngestionFactory:
    """
    Factory responsible for constructing a fully configured
    KnowledgeIngestionPipeline.
    """

    @staticmethod
    def create_agent(
        *,
        chunker: TextChunker | None = None,
        embedder: Embedder | None = None,
        vector_store: VectorStore | None = None,
    ) -> KnowledgeIngestionPipeline:
        """
        Build a KnowledgeIngestionPipeline.

        Custom components may be supplied for testing or
        advanced configuration. Otherwise production defaults
        are created.
        """

        chunker = chunker or TextChunker()
        embedder = embedder or Embedder()
        vector_store = vector_store or VectorStore()

        return KnowledgeIngestionPipeline(
            chunker=chunker,
            embedder=embedder,
            vector_store=vector_store,
        )