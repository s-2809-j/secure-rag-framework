"""
Base interface for Tier-2 document security detectors.

Every Tier-2 detector must inherit from this class and implement
the analyze() method.

Tier-2 detectors operate only on chunks that have already been
selected by the Document Escalation Engine.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from src.document_security_agent.models import EscalatedChunk
from src.input_security_agent.models import ValidationResult


class BaseTier2Detector(ABC):
    """
    Abstract base class for all Tier-2 document security detectors.

    Implementations perform deep security analysis on an escalated
    document chunk and return one or more validation results.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """
        Human-readable detector name.

        Returns
        -------
        str
            Detector identifier.
        """
        raise NotImplementedError

    @abstractmethod
    def analyze(
        self,
        chunk: EscalatedChunk,
    ) -> list[ValidationResult]:
        """
        Analyze an escalated document chunk.

        Parameters
        ----------
        chunk
            Chunk selected for Tier-2 analysis.

        Returns
        -------
        list[ValidationResult]
            Validation results produced by this detector.
        """
        raise NotImplementedError