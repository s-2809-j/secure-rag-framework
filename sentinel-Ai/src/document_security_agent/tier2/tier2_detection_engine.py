"""
Tier-2 Detection Engine.

Runs deep security analysis on document chunks selected by the
Document Escalation Engine.
"""

from __future__ import annotations
from src.document_security_agent.models import EscalatedChunk
import logging

from src.document_security_agent.tier2.base import BaseTier2Detector
from .exceptions import Tier2EngineError

from src.document_security_agent.models import (
    EscalationReport,
    Tier2ChunkResult,
    Tier2DetectionReport,
)
from src.input_security_agent.models import ValidationResult

logger = logging.getLogger(__name__)


class Tier2DetectionEngine:
    """
    Executes Tier-2 detectors on escalated document chunks.
    """

    def __init__(
        self,
        detectors: list[BaseTier2Detector],
    ) -> None:
        self._detectors = detectors

    def analyze(
        self,
        escalation_report: EscalationReport,
    ) -> Tier2DetectionReport:
        """
        Perform Tier-2 analysis on escalated chunks.

        Parameters
        ----------
        escalation_report
            Chunks selected by the escalation engine.

        Returns
        -------
        Tier2DetectionReport
            Consolidated Tier-2 detection results.
        """

        logger.info("Starting Tier-2 detection.")

        chunk_results: list[Tier2ChunkResult] = []

        try:

            for escalated_chunk in escalation_report.escalated_chunks:

                validation_results = self._run_detectors(
                    escalated_chunk
                )

                chunk_results.append(
                    Tier2ChunkResult(
                        chunk=escalated_chunk.chunk,
                        validation_results=validation_results,
                    )
                )

            logger.info(
                "Tier-2 detection completed. %d chunk(s) analyzed.",
                len(chunk_results),
            )

            return Tier2DetectionReport(
                metadata=escalation_report.metadata,
                chunk_results=chunk_results,
            )

        except Exception as exc:
            logger.exception(
                "Tier-2 Detection Engine failed."
            )

            raise Tier2EngineError(
                str(exc)
            ) from exc

    def _run_detectors(
        self,
        escalated_chunk: EscalatedChunk,
    ) -> list[ValidationResult]:
        """
        Execute every registered Tier-2 detector.
        """

        validation_results: list[ValidationResult] = []

        for detector in self._detectors:

            logger.info(
                "Running Tier-2 detector: %s",
                detector.name,
            )

            results = detector.analyze(escalated_chunk)

            for result in results:
                logger.info(
                    "  -> %s: is_flagged=%s category=%s "
                    "confidence=%.2f",
                    detector.name,
                    result.is_flagged,
                    result.category.value,
                    result.confidence,
                )

            validation_results.extend(results)

        return validation_results