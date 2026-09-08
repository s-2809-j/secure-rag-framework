from __future__ import annotations

from pathlib import Path

from src.document_security_agent.models import (
    DocumentParseResult,
    FileMetadata,
    ParsedDocument,
)

from .base_parser import BaseParser


class TxtParser(BaseParser):
    """
    Parser for plain text files.
    """

    def parse(
        self,
        file_path: Path,
    ) -> DocumentParseResult:

        text = file_path.read_text(
            encoding="utf-8",
            errors="ignore",
        )

        metadata = FileMetadata(
            filename=file_path.name,
            extension=file_path.suffix.lower(),
            mime_type="text/plain",
            size_bytes=file_path.stat().st_size,
        )

        document = ParsedDocument(
            metadata=metadata,
            text=text,
            page_count=1,
            parser_name=self.__class__.__name__,
        )

        return DocumentParseResult(
            success=True,
            document=document,
        )