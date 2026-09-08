from __future__ import annotations

from pathlib import Path

import filetype

from src.document_security_agent.constants import SUPPORTED_MIME_TYPES
from src.document_security_agent.exceptions import (
    UnsupportedFileTypeError,
)


class MimeValidator:
    

    def validate(self, file_path: Path) -> None:
     

        extension = file_path.suffix.lower()

        expected_mime = SUPPORTED_MIME_TYPES.get(extension)

        if expected_mime is None:
            raise UnsupportedFileTypeError(
                f"No MIME mapping configured for '{extension}'."
            )

        detected = filetype.guess(file_path)

        if detected is None:
            # filetype cannot identify TXT/Markdown
            if extension in {".txt", ".md"}:
                return

            raise UnsupportedFileTypeError(
                f"Unable to determine MIME type for '{file_path.name}'."
            )

        if detected.mime != expected_mime:
            raise UnsupportedFileTypeError(
                f"MIME mismatch. Expected '{expected_mime}', "
                f"found '{detected.mime}'."
            )