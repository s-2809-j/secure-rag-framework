from __future__ import annotations

import logging
from pathlib import Path

from .corruption_validator import CorruptionValidator
from .extension_validator import ExtensionValidator
from .malware_validator import MalwareValidator
from .mime_validator import MimeValidator
from .size_validator import SizeValidator


class FileGuard:
    """
    Orchestrates all file-level validation.
    """

    def __init__(
        self,
        extension_validator: ExtensionValidator,
        mime_validator: MimeValidator,
        size_validator: SizeValidator,
        corruption_validator: CorruptionValidator,
        malware_validator: MalwareValidator,
    ) -> None:
        self._logger = logging.getLogger(__name__)

        self._extension_validator = extension_validator
        self._mime_validator = mime_validator
        self._size_validator = size_validator
        self._corruption_validator = corruption_validator
        self._malware_validator = malware_validator

    def validate(self, file_path: Path) -> None:
        """
        Execute all file-level validation.
        """

        self._logger.info(
            "Starting validation for '%s'.",
            file_path.name,
        )

        self._extension_validator.validate(file_path)
        self._logger.debug("Extension validation passed.")

        self._mime_validator.validate(file_path)
        self._logger.debug("MIME validation passed.")

        self._size_validator.validate(file_path)
        self._logger.debug("Size validation passed.")

        self._corruption_validator.validate(file_path)
        self._logger.debug("Corruption validation passed.")

        self._malware_validator.validate(file_path)
        self._logger.debug("Malware validation passed.")

        self._logger.info(
            "File validation completed successfully for '%s'.",
            file_path.name,
        )