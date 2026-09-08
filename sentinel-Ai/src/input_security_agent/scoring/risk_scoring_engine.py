from __future__ import annotations

import logging

from src.input_security_agent.models import (
    RiskAssessment,
    RiskLevel,
    ValidationResult,
)

logger = logging.getLogger(__name__)


class RiskScoringEngine:
    """
    Calculates the overall security risk based on detector results.
    """

    def assess(
        self,
        results: list[ValidationResult],
    ) -> RiskAssessment:

        logger.info("Calculating overall security risk.")

        flagged_results = [
            result
            for result in results
            if result.is_flagged
        ]

        if not flagged_results:

            logger.info(
                "No security threats detected."
            )

            return RiskAssessment(
                risk_score=0.0,
                risk_level=RiskLevel.LOW,
                contributing_results=[],
                explanation="No threats detected.",
            )

        highest = max(
            flagged_results,
            key=lambda result: result.confidence,
        )

        score = highest.confidence

        risk_level = self._determine_risk_level(
            score
        )

        explanation = (
            f"Highest confidence detector: "
            f"{highest.detector_name} "
            f"({score:.2f})"
        )

        logger.info(
            "Risk assessment completed."
        )

        return RiskAssessment(
            risk_score=score,
            risk_level=risk_level,
            contributing_results=flagged_results,
            explanation=explanation,
        )

    @staticmethod
    def _determine_risk_level(
        score: float,
    ) -> RiskLevel:

        if score >= 0.75:
            return RiskLevel.CRITICAL

        if score >= 0.50:
            return RiskLevel.HIGH

        if score >= 0.25:
            return RiskLevel.MEDIUM

        return RiskLevel.LOW