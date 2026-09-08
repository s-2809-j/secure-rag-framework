from __future__ import annotations

import logging

from langchain_text_splitters import (
    RecursiveCharacterTextSplitter,
)

from src.document_security_agent.models import (
    Chunk,
    ChunkedDocument,
    ParsedDocument,
)

logger = logging.getLogger(__name__)


class DocumentChunker:
    """
    Splits a parsed document into smaller chunks for
    downstream security analysis.
    """

    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
    ) -> None:

        if chunk_size <= 0:
            raise ValueError(
                "chunk_size must be greater than zero."
            )

        if chunk_overlap < 0:
            raise ValueError(
                "chunk_overlap cannot be negative."
            )

        if chunk_overlap >= chunk_size:
            raise ValueError(
                "chunk_overlap must be smaller than chunk_size."
            )

        self._splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            is_separator_regex=False,
        )

        logger.info(
            "DocumentChunker initialized "
            "(chunk_size=%d, overlap=%d)",
            chunk_size,
            chunk_overlap,
        )

    def chunk(
        self,
        document: ParsedDocument,
    ) -> ChunkedDocument:
        """
        Split a parsed document into chunks.
        """

        logger.info(
            "Chunking document '%s'",
            document.metadata.filename,
        )

        chunk_texts = self._splitter.split_text(
            document.text
        )

        chunks: list[Chunk] = []

        cursor = 0

        for index, chunk_text in enumerate(chunk_texts):

            start = document.text.find(
                chunk_text,
                cursor,
            )

            if start == -1:
                logger.warning(
        "Unable to reconstruct offsets "
        "for chunk %d.",
        index,
    )

            end = start + len(chunk_text)

            cursor = end

            chunks.append(
                Chunk(
                    id=index,
                    text=chunk_text,
                    start_offset=start,
                    end_offset=end,
                )
            )

        logger.info(
            "Generated %d chunks.",
            len(chunks),
        )

        return ChunkedDocument(
            metadata=document.metadata,
            chunks=chunks,
            page_count=document.page_count,
            parser_name=document.parser_name,
            warnings=document.warnings.copy(),
        )