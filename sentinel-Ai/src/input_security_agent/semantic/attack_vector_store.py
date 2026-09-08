"""
Attack Vector Store.

Thin subclass of the shared VectorStore that pins the collection
name/path used for the semantic attack index. This guarantees that
AttackIndexBuilder (which writes into this collection) and
SimilarityDetector (which searches it) always resolve to the exact
same ChromaDB collection, without either one needing to pass the
name/path around manually.
"""

from __future__ import annotations

from src.knowledge_base.vector_store import VectorStore

ATTACK_INDEX_DB_PATH = "chroma_db/attack_index"
ATTACK_INDEX_COLLECTION_NAME = "sentinel_attack_index"


class AttackVectorStore(VectorStore):
    """VectorStore fixed to the shared attack-index collection."""

    def __init__(self) -> None:
        super().__init__(
            db_path=ATTACK_INDEX_DB_PATH,
            collection_name=ATTACK_INDEX_COLLECTION_NAME,
        )