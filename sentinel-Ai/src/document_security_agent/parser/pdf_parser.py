from __future__ import annotations

from pathlib import Path

from pypdf import PdfReader

from src.document_security_agent.exceptions import (
    DocumentParseError,
)
from src.document_security_agent.models import (
    DocumentParseResult,
    FileMetadata,
    ParsedDocument,
)

from .base_parser import BaseParser


class PDFParser(BaseParser):
    """
    Parser for PDF documents.
    """

    def parse(
        self,
        file_path: Path,
    ) -> DocumentParseResult:

        try:
            reader = PdfReader(file_path)

            pages = []

            for page in reader.pages:
                pages.append(page.extract_text() or "")

            metadata = FileMetadata(
                filename=file_path.name,
                extension=".pdf",
                mime_type="application/pdf",
                size_bytes=file_path.stat().st_size,
            )

            document = ParsedDocument(
                metadata=metadata,
                text="\n".join(pages),
                page_count=len(reader.pages),
                parser_name=self.__class__.__name__,
            )

            return DocumentParseResult(
                success=True,
                document=document,
            )

        except Exception as exc:
            raise DocumentParseError(
                f"Failed to parse PDF: {file_path.name}"
            ) from exc