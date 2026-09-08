from __future__ import annotations


class DocumentSecurityError(Exception):
    """Base exception for all document security errors."""


class UnsupportedFileTypeError(DocumentSecurityError):
    """Raised when the uploaded file type is not supported."""


class FileSizeExceededError(DocumentSecurityError):
    """Raised when the uploaded file exceeds the allowed size."""


class FileCorruptionError(DocumentSecurityError):
    """Raised when the uploaded file is corrupted or unreadable."""


class MalwareDetectedError(DocumentSecurityError):
    """Raised when malware is detected in an uploaded file."""


class DocumentParseError(DocumentSecurityError):
    """Raised when document parsing fails."""