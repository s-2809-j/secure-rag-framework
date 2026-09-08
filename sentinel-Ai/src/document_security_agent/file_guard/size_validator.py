from __future__ import annotations

from pathlib import Path

from src.document_security_agent.constants import MAX_FILE_SIZE_BYTES
from src.document_security_agent.exceptions import (
    FileSizeExceededError,
)


class SizeValidator:


    def validate(self, file_path: Path) -> None:
       

        size = file_path.stat().st_size

        if size > MAX_FILE_SIZE_BYTES:
            raise FileSizeExceededError(
                f"File size ({size} bytes) exceeds "
                f"maximum allowed ({MAX_FILE_SIZE_BYTES} bytes)."
            )