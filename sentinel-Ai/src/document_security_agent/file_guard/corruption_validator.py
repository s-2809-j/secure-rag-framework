from __future__ import annotations

from pathlib import Path

from src.document_security_agent.exceptions import (
    FileCorruptionError,
)


class CorruptionValidator:
    """
    Performs basic corruption checks.
    """

    def validate(self, file_path: Path) -> None:
        
        try:
            with open(file_path, "rb") as file:
                file.read(1)

        except Exception as exc:
            raise FileCorruptionError(
                f"Unable to read uploaded file: {file_path.name}"
            ) from exc