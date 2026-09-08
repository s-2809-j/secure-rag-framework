from __future__ import annotations

from pathlib import Path

from src.document_security_agent.exceptions import (
    UnsupportedFileTypeError,
)
from src.document_security_agent.models import (
    DocumentParseResult,
)

from .base_parser import BaseParser


class DocumentParser:
    """
    Delegates document parsing to the appropriate parser.
    """

    def __init__(
        self,
        parsers: dict[str, BaseParser],
    ) -> None:
        """
        Parameters
        ----------
        parsers
            Mapping of parser name to parser instance.
        """

        self._parsers = parsers

    def parse(
        self,
        file_path: Path,
    ) -> DocumentParseResult:
        """
        Parse a document using the appropriate parser.
        """

        extension = file_path.suffix.lower()

        parser = self._parsers.get(extension)

        if parser is None:
            raise UnsupportedFileTypeError(
                f"No parser registered for '{extension}'."
            )

        return parser.parse(file_path)