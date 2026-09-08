

"""
Integration test for AssistantAgent.upload_document().

Run:
    python -m tests.assistant_agent.test_upload_document
"""

from __future__ import annotations

from pathlib import Path

from src.assistant_agent.factory import AssistantAgentFactory
from src.document_security_agent.document_security_agent import (
    DocumentSecurityAgent,
)
from src.document_security_agent.models import FileMetadata
from src.input_security_agent.input_security_agent import (
    InputSecurityAgent,
)
from src.knowledge_base.ingestion.factory import (
    KnowledgeIngestionFactory,
)
from src.knowledge_base.retriever import Retriever
from src.llm.gemini_client import GeminiLLMClient


def main() -> None:
    """
    Integration test for secure document upload.
    """

    # ---------------------------------------------------------
    # Test document
    # ---------------------------------------------------------

    file_path = Path("domain_packs/banking/documents/account_policies.md")

    if not file_path.exists():
        raise FileNotFoundError(
            f"Test document not found: {file_path}"
        )

    metadata = FileMetadata(
        filename=file_path.name,
        extension=file_path.suffix,
        mime_type="text/markdown",
        size_bytes=file_path.stat().st_size,
        checksum=None,
    )

    # ---------------------------------------------------------
    # Initialize dependencies
    # ---------------------------------------------------------

    print("\nInitializing components...")

    retriever = Retriever()

    llm = GeminiLLMClient()

    input_security_agent = InputSecurityAgent()

    document_security_agent = DocumentSecurityAgent()

    knowledge_ingestion_pipeline = (
        KnowledgeIngestionFactory.create()
    )

    assistant = AssistantAgentFactory.create(
        retriever=retriever,
        llm=llm,
        input_security_agent=input_security_agent,
        document_security_agent=document_security_agent,
        knowledge_ingestion_pipeline=knowledge_ingestion_pipeline,
    )

    print("AssistantAgent initialized successfully.")

    # ---------------------------------------------------------
    # Upload document
    # ---------------------------------------------------------

    print("\nUploading document...\n")

    result = assistant.upload_document(
        file_path=str(file_path),
        metadata=metadata,
    )

    # ---------------------------------------------------------
    # Results
    # ---------------------------------------------------------

    print("\n========== UPLOAD RESULT ==========")

    print(result)

    print("\nDocument uploaded successfully.")

    # ---------------------------------------------------------
    # Optional Retrieval Verification
    # ---------------------------------------------------------

    print("\n========== RETRIEVAL TEST ==========\n")

    response = assistant.generate_response(
        "Summarize the uploaded document."
    )

    print(response)

    print("\n========== TEST PASSED ==========")


if __name__ == "__main__":
    main()