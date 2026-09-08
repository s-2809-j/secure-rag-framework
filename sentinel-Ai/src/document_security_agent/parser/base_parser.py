from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from src.document_security_agent.models import (
    DocumentParseResult,
)


class BaseParser(ABC):
    """
    Abstract base class for document parsers.
    """

    @abstractmethod
    def parse(
        self,
        file_path: Path,
    ) -> DocumentParseResult:
        """
        Parse the document and return the extracted text.
        """
        raise NotImplementedError