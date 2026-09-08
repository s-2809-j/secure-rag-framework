from __future__ import annotations

from pathlib import Path

from src.document_security_agent.constants import SUPPORTED_EXTENSIONS
from src.document_security_agent.exceptions import (
    UnsupportedFileTypeError,
)


class ExtensionValidator:


    def validate(self, file_path: Path) -> None:
       

        extension = file_path.suffix.lower()

        if extension not in SUPPORTED_EXTENSIONS:
            raise UnsupportedFileTypeError(
                f"Unsupported file extension: {extension}"
            )