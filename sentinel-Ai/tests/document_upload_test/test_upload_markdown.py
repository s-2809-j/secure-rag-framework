"""
Integration test for uploading a Markdown document.

Run:
    python -m tests.assistant_agent.test_upload_markdown
"""

from pathlib import Path
import mimetypes

from src.assistant_agent.assistant_agent import AssistantAgent
from src.assistant_agent.factory import (
    AssistantAgentFactory,
)
from src.document_security_agent.factory.document_security_factory import (
    DocumentSecurityFactory,
)
from src.document_security_agent.models import FileMetadata
from src.input_security_agent.factory.factory import (
    InputSecurityFactory,
)
from src.knowledge_base.embedder import Embedder
from src.knowledge_base.retriever import Retriever
from src.knowledge_base.vector_store import VectorStore
from src.llm.gemini_client import GeminiLLMClient   


TEST_DOCUMENT = Path(
    "tests/resources/doc2.docx"
)


def build_assistant() -> AssistantAgent:

    embedder = Embedder()

    vector_store = VectorStore()

    retriever = Retriever(
        embedder=embedder,
        vector_store=vector_store,
    )

    llm = GeminiLLMClient()

    input_agent = (
        InputSecurityFactory.create_agent()
    )

    document_agent = (
        DocumentSecurityFactory.create_agent()
    )

    return AssistantAgentFactory.create_agent(
        retriever=retriever,
        llm=llm,
        input_security_agent=input_agent,
        document_security_agent=document_agent,
    )


def test_upload_markdown():

    assistant = build_assistant()

    metadata = FileMetadata(
    filename=TEST_DOCUMENT.name,
    extension=TEST_DOCUMENT.suffix,
    mime_type=(
        mimetypes.guess_type(TEST_DOCUMENT)[0]
        or "application/octet-stream"
    ),
    size_bytes=TEST_DOCUMENT.stat().st_size,
    )

    result = assistant.upload_document(
        file_path=str(TEST_DOCUMENT),
        metadata=metadata,
    )

    assert result is not None

    print("[PASS] Markdown uploaded successfully.")


def main():

    print("=" * 70)
    print("Testing Markdown Upload")
    print("=" * 70)

    test_upload_markdown()

    print("=" * 70)
    print("Markdown upload test passed.")
    print("=" * 70)


if __name__ == "__main__":
    main()