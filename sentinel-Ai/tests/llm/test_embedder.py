# from src.rag.embedder import Embedder
# from src.rag.models import Chunk


# chunks = [
#     Chunk(
#         content="Customers can reset their password.",
#         metadata={
#             "chunk_id": "chunk_001",
#             "domain": "banking",
#         },
#     ),
#     Chunk(
#         content="Employees are entitled to annual leave.",
#         metadata={
#             "chunk_id": "chunk_002",
#             "domain": "enterprise_hr",
#         },
#     ),
# ]

# embedder = Embedder()

# embedded_chunks = embedder.embed(chunks)

# print(f"Embedded chunks: {len(embedded_chunks)}")

# for chunk in embedded_chunks:
#     print(chunk.metadata["chunk_id"])
#     print(len(chunk.embedding))
#     print(chunk.embedding[:5])

from src.knowledge_base.embedder import Embedder

embedder = Embedder()

query = "What is the password reset policy?"

embedding = embedder.embed_query(query)

print(type(embedding))
print(len(embedding))
print(embedding[:5])