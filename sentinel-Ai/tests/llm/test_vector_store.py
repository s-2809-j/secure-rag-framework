from src.knowledge_base.embedder import Embedder
from src.knowledge_base.models import Chunk
from src.knowledge_base.vector_store import VectorStore

chunks = [
    Chunk(
        content="Customers can reset their password.",
        metadata={
            "chunk_id": "chunk_001",
            "domain": "banking",
        },
    ),
    Chunk(
        content="Employees are entitled to annual leave.",
        metadata={
            "chunk_id": "chunk_002",
            "domain": "enterprise_hr",
        },
    ),
]

embedder = Embedder()
embedded_chunks = embedder.embed(chunks)

store = VectorStore()
store.store(embedded_chunks)

print("Embedded chunks stored successfully.")
print("Collection count:", store._collection.count())