from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class Document:
    """
    Raw document loaded from disk before chunking.
    """

    content: str
    metadata: dict[str, Any]


@dataclass(slots=True)
class Chunk:
    """
    Chunk generated from a document and ready for embedding.
    """

    content: str
    metadata: dict[str, Any]


@dataclass(slots=True)
class EmbeddedChunk:
    """
    Chunk together with its vector embedding.
    """

    content: str
    metadata: dict[str, Any]
    embedding: list[float]


@dataclass(slots=True)
class RetrievedChunk:
    """
    Chunk returned from the vector database.
    """

    content: str
    metadata: dict[str, Any]
    distance: float