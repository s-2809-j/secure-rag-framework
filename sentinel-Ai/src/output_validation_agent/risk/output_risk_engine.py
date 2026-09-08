from __future__ import annotations

import logging

from src.output_validation_agent.exceptions import (
    RiskAssessmentError,
)
from src.output_validation_agent.models import (
    OutputRiskLevel,
    RiskAssessment,
    ValidationResult,
)

logger = logging.getLogger(__name__)


class OutputRiskEngine:
    """
    Computes the overall risk assessment for the generated response.
    """

    def assess(
        self,
        results: list[ValidationResult],
    ) -> RiskAssessment:
        """
        Compute the overall output risk assessment.
        """

        logger.info(
            "Computing output risk assessment."
        )

        self._validate_results(results)

        overall_score = self._compute_score(results)

        confidence = self._compute_confidence(
            overall_score,
        )

        risk_level = self._determine_risk_level(
            overall_score,
        )

        logger.info(
            "Output risk assessment completed. "
            "Score=%.2f Confidence=%.2f Risk=%s",
            overall_score,
            confidence,
            risk_level.value,
        )

        return RiskAssessment(
            overall_score=overall_score,
            confidence=confidence,
            risk_level=risk_level,
            summary=(
                f"Risk level: {risk_level.value} "
                f"(score={overall_score:.2f})"
            ),
        )

    @staticmethod
    def _validate_results(
        results: list[ValidationResult],
    ) -> None:
        """
        Validate the supplied validation results.
        """

        if not isinstance(results, list):
            
            raise RiskAssessmentError(
                "Expected a list of ValidationResult objects."
            )

        if not results:
            raise RiskAssessmentError(
                "No validation results were provided."
            )

        for result in results:
            if not isinstance(
                result,
                ValidationResult,
            ):
                raise RiskAssessmentError(
                    "Expected ValidationResult."
                )

    @staticmethod
    def _compute_score(
        results: list[ValidationResult],
    ) -> float:
        """
        Compute the overall risk score.

        Currently uses a simple arithmetic mean.
        """

        return (
            sum(
                result.score
                for result in results
            )
            / len(results)
        )

    @staticmethod
    def _compute_confidence(
        overall_score: float,
    ) -> float:
        """
        Compute the confidence score.

        Confidence is inversely proportional to risk.
        """

        return max(
            0.0,
            1.0 - overall_score,
        )

    @staticmethod
    def _determine_risk_level(
        overall_score: float,
    ) -> OutputRiskLevel:
        """
        Determine the overall risk level.
        """

        if overall_score < 0.25:
            return OutputRiskLevel.LOW

        if overall_score < 0.50:
            return OutputRiskLevel.MEDIUM

        if overall_score < 0.75:
            return OutputRiskLevel.HIGH

        return OutputRiskLevel.CRITICAL