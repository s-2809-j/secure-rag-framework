"""
Tier-2 Semantic Detector.

Performs semantic similarity analysis on escalated document chunks
by reusing the existing SimilarityDetector.
"""

from __future__ import annotations

import logging

from src.document_security_agent.models import EscalatedChunk
from src.document_security_agent.tier2.base import BaseTier2Detector

from src.input_security_agent.semantic.similarity_detector import (
    SimilarityDetector,
)

from src.input_security_agent.models import (
    SecurityContext,
    ValidationResult,
)

logger = logging.getLogger(__name__)


class SemanticDetector(BaseTier2Detector):
    """
    Tier-2 semantic detector.

    Delegates semantic similarity analysis to the existing
    SimilarityDetector.
    """

    def __init__(
        self,
        similarity_detector: SimilarityDetector,
    ) -> None:

        if similarity_detector is None:
            raise ValueError(
                "similarity_detector cannot be None."
            )

        self._similarity_detector = similarity_detector

    @property
    def name(self) -> str:
        return "SemanticDetector"

    def analyze(
        self,
        chunk: EscalatedChunk,
    ) -> list[ValidationResult]:

        logger.info(
            "Running semantic analysis on chunk %d.",
            chunk.chunk.id,
        )

        context = SecurityContext(
            query=chunk.chunk.text,
        )

        result = self._similarity_detector.detect(
            context
        )

        return [result]