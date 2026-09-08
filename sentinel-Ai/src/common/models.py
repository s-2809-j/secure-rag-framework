from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class FileMetadata:
    """
    Metadata describing an uploaded document.
    Shared across Sentinel modules.
    """

    filename: str
    extension: str
    mime_type: str
    size_bytes: int
    checksum: str | None = None