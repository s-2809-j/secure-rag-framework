from __future__ import annotations

import logging
import sys
import time
from pathlib import Path

from annotated_types import Ge

from src.knowledge_base.loader import MarkdownLoader
from src.knowledge_base.chunker import TextChunker
from src.knowledge_base.embedder import Embedder
from src.knowledge_base.vector_store import VectorStore
from src.knowledge_base.retriever import Retriever
from src.assistant_agent.assistant_agent import AssistantAgent
from src.llm.gemini_client import GeminiLLMClient

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s | %(message)s",
)

logger = logging.getLogger(__name__)


def stage(title: str):
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)


def check(condition: bool, message: str):
    if not condition:
        raise AssertionError(message)


def main():

    total_start = time.time()

    try:

        # ------------------------------------------------------------------

        stage("1. INITIALIZING COMPONENTS")

        loader = MarkdownLoader("domain_packs")

        chunker = TextChunker()

        embedder = Embedder()

        vector_store = VectorStore(
            db_path="test_chroma_db",
            collection_name="pipeline_test_collection",
        )

        retriever = Retriever(
            embedder=embedder,
            vector_store=vector_store,
        )

        llm = GeminiLLMClient()

        assistant = AssistantAgent(
            retriever=retriever,
            llm=llm,
        )

        print("PASS  All components initialized.")

        # ------------------------------------------------------------------

        stage("2. LOADING DOCUMENTS")

        start = time.time()

        documents = loader.load()

        check(len(documents) > 0, "No documents were loaded.")

        print(f"Documents Loaded : {len(documents)}")
        print(f"Time             : {time.time()-start:.2f}s")

        # ------------------------------------------------------------------

        stage("3. CHUNKING")

        start = time.time()

        chunks = chunker.chunk_documents(documents)

        check(len(chunks) > 0, "Chunking failed.")

        print(f"Chunks Generated : {len(chunks)}")
        print(f"Time             : {time.time()-start:.2f}s")

        # ------------------------------------------------------------------

        stage("4. EMBEDDING")

        start = time.time()

        embedded_chunks = embedder.embed(chunks)

        check(
            len(embedded_chunks) == len(chunks),
            "Embedding count mismatch.",
        )

        print(f"Embeddings Generated : {len(embedded_chunks)}")

        print(
            f"Embedding Dimension  : {len(embedded_chunks[0].embedding)}"
        )

        print(f"Time                 : {time.time()-start:.2f}s")

        # ------------------------------------------------------------------

        stage("5. VECTOR STORE")

        start = time.time()

        vector_store.store(embedded_chunks)

        print("Chunks stored successfully.")

        print(f"Time : {time.time()-start:.2f}s")

        # ------------------------------------------------------------------

        queries = [
            "What is phishing?",
            "Explain ransomware.",
            "How can an employee report a security incident?",
        ]

        for query in queries:

            stage(f"QUERY : {query}")

            start = time.time()

            retrieved = retriever.retrieve(query)

            check(
                len(retrieved) > 0,
                f"No chunks retrieved for '{query}'",
            )

            print(f"Retrieved : {len(retrieved)} chunks")

            for i, chunk in enumerate(retrieved, start=1):

                print("-" * 60)
                print(f"Chunk {i}")
                print(f"Source   : {chunk.metadata.get('source')}")
                print(f"Distance : {chunk.distance:.4f}")

                preview = chunk.content[:150].replace("\n", " ")

                print(f"Preview  : {preview}")

            print(f"Retrieval Time : {time.time()-start:.2f}s")

            # --------------------------------------------------------------

            stage("ASSISTANT RESPONSE")

            start = time.time()

            response = assistant.generate_response(query)

            check(
                isinstance(response, str),
                "LLM returned invalid response.",
            )

            check(
                len(response.strip()) > 0,
                "Empty response returned.",
            )

            print(response)

            print(f"\nGeneration Time : {time.time()-start:.2f}s")

        # ------------------------------------------------------------------

        stage("PIPELINE SUMMARY")

        print("PASS Loader")
        print("PASS Chunker")
        print("PASS Embedder")
        print("PASS Vector Store")
        print("PASS Retriever")
        print("PASS Assistant Agent")

        print()

        print(
            f"TOTAL EXECUTION TIME : "
            f"{time.time()-total_start:.2f} seconds"
        )

        print()

        print("=" * 80)
        print("ALL PIPELINE TESTS PASSED")
        print("=" * 80)

    except Exception as exc:

        print("\n")
        print("=" * 80)
        print("PIPELINE TEST FAILED")
        print("=" * 80)

        logger.exception(exc)

        sys.exit(1)


if __name__ == "__main__":
    main()
