"""
Document Escalation Engine.

This module selects document chunks that require Tier-2 security
analysis based on Tier-1 detection results.
"""

from __future__ import annotations

import logging

from .escalation_rules import (
    DEFAULT_ESCALATION_RULES,
    EscalationRules,
)
from .exceptions import EscalationEngineError

from src.document_security_agent.models import (
    ChunkDetectionResult,
    EscalatedChunk,
    EscalationPriority,
    EscalationReport,
    Tier1DetectionReport,
)

from src.input_security_agent.models import ValidationResult

logger = logging.getLogger(__name__)


class DocumentEscalationEngine:
    """
    Determines which document chunks should proceed
    to Tier-2 security analysis.
    """

    def __init__(
        self,
        rules: EscalationRules = DEFAULT_ESCALATION_RULES,
    ) -> None:
        self._rules = rules

    def escalate(
        self,
        report: Tier1DetectionReport,
    ) -> EscalationReport:
        """
        Escalate flagged chunks for Tier-2 analysis.
        """

        logger.info("Starting document escalation.")

        escalated_chunks: list[EscalatedChunk] = []

        try:

            for chunk_result in report.chunk_results:

                if not self._should_escalate(chunk_result):
                    continue

                flagged_results = self._get_flagged_results(
                    chunk_result
                )

                priority = self._determine_priority(
                    flagged_results
                )

                reasons = self._build_reasons(
                    flagged_results
                )

                escalated_chunks.append(
                    EscalatedChunk(
                        chunk=chunk_result.chunk,
                        priority=priority,
                        reasons=reasons,
                        validation_results=flagged_results,
                    )
                )

            logger.info(
                "Escalation complete. %d chunks selected.",
                len(escalated_chunks),
            )

            return EscalationReport(
    metadata=report.metadata,
    total_chunks=len(report.chunk_results),
    escalated_chunks=escalated_chunks,
)

        except Exception as exc:
            logger.exception(
                "Escalation engine failed."
            )
            raise EscalationEngineError(
                str(exc)
            ) from exc

    def _should_escalate(
        self,
        chunk_result: ChunkDetectionResult,
    ) -> bool:
        """
        Returns True if any detector flagged the chunk.
        """

        return any(
            result.is_flagged
            for result in chunk_result.validation_results
        )

    def _get_flagged_results(
        self,
        chunk_result: ChunkDetectionResult,
    ) -> list[ValidationResult]:
        """
        Returns only flagged validation results.
        """

        return [
            result
            for result in chunk_result.validation_results
            if result.is_flagged
        ]

    def _determine_priority(
    self,
    results: list[ValidationResult],
) -> EscalationPriority:
        """
        Assign escalation priority using the highest
        detector confidence.
        """

        highest = max(
            result.confidence
            for result in results
        )

        if highest >= self._rules.high_confidence_threshold:
            return EscalationPriority.HIGH

        if highest >= self._rules.medium_confidence_threshold:
            return EscalationPriority.MEDIUM

        return EscalationPriority.LOW
    @staticmethod
    def _build_reasons(
        results: list[ValidationResult],
    ) -> list[str]:
        """
        Build human-readable escalation reasons.
        """

        reasons: list[str] = []

        for result in results:

            if result.reason:
                reasons.append(result.reason)
            else:
                reasons.append(
                    f"{result.detector_name} detected "
                    f"{result.category.value}"
                )

        return reasons