from __future__ import annotations

from src.document_security_agent.models import ParsedDocument
from src.input_security_agent.preprocessing.input_normalizer import (
    InputNormalizer,
)


class DocumentNormalizer:
    """
    Normalizes parsed document text.

    This class reuses the existing InputNormalizer
    to avoid duplicating normalization logic.
    """

    def __init__(
        self,
        input_normalizer: InputNormalizer,
    ) -> None:
        self._input_normalizer = input_normalizer

    def doc_normalize(
        self,
        document: ParsedDocument,
    ) -> ParsedDocument:
        """
        Normalize the document text.

        Parameters
        ----------
        document
            Parsed document.

        Returns
        -------
        ParsedDocument
            Document with normalized text.
        """

        normalized_text = self._input_normalizer.normalize(
            document.text
        )

        return ParsedDocument(
            metadata=document.metadata,
            text=normalized_text,
            page_count=document.page_count,
            parser_name=document.parser_name,
        )