"""
Exceptions used by the Knowledge Ingestion Pipeline.
"""


class KnowledgeIngestionError(Exception):
    """
    Base exception for all ingestion-related failures.
    """


class DocumentLoadingError(KnowledgeIngestionError):
    """
    Raised when a document cannot be loaded.
    """


class ChunkingError(KnowledgeIngestionError):
    """
    Raised when document chunking fails.
    """


class EmbeddingGenerationError(KnowledgeIngestionError):
    """
    Raised when embedding generation fails.
    """


class VectorStoreError(KnowledgeIngestionError):
    """
    Raised when writing to the vector database fails.
    """