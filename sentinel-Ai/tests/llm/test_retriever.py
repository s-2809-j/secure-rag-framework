from __future__ import annotations

import logging

from src.knowledge_base.embedder import Embedder
from src.knowledge_base.retriever import Retriever
from src.knowledge_base.vector_store import VectorStore


logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s - %(message)s",
)


def print_results(title: str, results) -> None:
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)

    if not results:
        print("No results found.")
        return

    for index, chunk in enumerate(results, start=1):
        print(f"\nResult #{index}")
        print("-" * 40)
        print(f"Content : {chunk.content}")
        print(f"Distance: {chunk.distance:.4f}")
        print(f"Metadata: {chunk.metadata}")


def main() -> None:
    print("Initializing components...\n")

    embedder = Embedder()

    vector_store = VectorStore()
    # print(f"Collection count: {vector_store.collection.count()}")

    # data = vector_store.collection.get()

    # print("IDs:", data["ids"])
    # print("Documents:", data["documents"])
    # print("Metadata:", data["metadatas"])

    retriever = Retriever(
        embedder=embedder,
        vector_store=vector_store,
    )


    # ------------------------------------------------------------------
    # Test 1
    # ------------------------------------------------------------------

    print("\nRunning Test 1: General Search")

    results = retriever.retrieve(
        query="How can a customer reset their password?"
    )

    print_results("General Search", results)

    # ------------------------------------------------------------------
    # Test 2
    # ------------------------------------------------------------------

    print("\nRunning Test 2: Banking Filter")

    results = retriever.retrieve(
        query="password reset",
        metadata_filter={
            "domain": "banking",
        },
    )

    print_results("Banking Domain", results)

    # ------------------------------------------------------------------
    # Test 3
    # ------------------------------------------------------------------

    print("\nRunning Test 3: Enterprise HR Filter")

    results = retriever.retrieve(
        query="annual leave policy",
        metadata_filter={
            "domain": "enterprise_hr",
        },
    )

    print_results("Enterprise HR Domain", results)

    # ------------------------------------------------------------------
    # Test 4
    # ------------------------------------------------------------------

    print("\nRunning Test 4: Unknown Domain")

    results = retriever.retrieve(
        query="password",
        metadata_filter={
            "domain": "unknown",
        },
    )

    print_results("Unknown Domain", results)

    print("\nAll Retriever tests completed successfully.")


if __name__ == "__main__":
    main()