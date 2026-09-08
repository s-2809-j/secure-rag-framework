from __future__ import annotations

import logging
from typing import Any

from src.input_security_agent.detectors.pii_detector import PIIDetector
from src.input_security_agent.models import (
    SecurityContext,
)

from src.output_validation_agent.models import (
    OutputCategory,
    ValidationContext,
    ValidationResult,
)

from src.output_validation_agent.validators.base import BaseValidator

logger = logging.getLogger(__name__)


class PIIValidator(BaseValidator):
    """
    Output validator responsible for detecting sensitive
    information present in the generated LLM response.

    This validator reuses the production PIIDetector from the
    Input Security Agent instead of maintaining a separate
    implementation.
    """

    def __init__(
        self,
        detector: PIIDetector | None = None,
    ) -> None:
        super().__init__()

        self._detector = detector or PIIDetector()

    def _validate(
        self,
        context: ValidationContext,
    ) -> ValidationResult:
        """
        Validate the generated response for PII leakage.
        """

        response = context.llm_response.strip()

        if not response:
            return self._build_safe_result()

        security_context = SecurityContext(
            query=response,
        )

        detector_result = self._detector.detect(
            security_context,
        )

        if not detector_result.is_flagged:
            return self._build_safe_result()

        return self._build_flagged_result(
            detector_result,
        )

    def _build_safe_result(
        self,
    ) -> ValidationResult:
        """
        Build a successful validation result.
        """

        return ValidationResult(
            validator_name=self.name,
            passed=True,
            category=OutputCategory.PII,
            score=0.0,
            reason="No sensitive information detected.",
            details={
                "match_count": 0,
                "matches": [],
            },
        )

    def _build_flagged_result(
        self,
        detector_result: Any,
    ) -> ValidationResult:
        """
        Convert the Input Security detector output into an
        Output Validation result.
        """

        matches = []

        for match in detector_result.matches:
            matches.append(
                {
                    "pattern": match.pattern_name,
                    "matched_text": match.matched_text,
                    "start": match.start,
                    "end": match.end,
                }
            )

        score = detector_result.confidence
        return ValidationResult(
            validator_name=self.name,
            passed=False,
            category=OutputCategory.PII,
            score=score,
            reason=detector_result.reason,
            details={
                "match_count": len(matches),
                "matches": matches,
                "detector": detector_result.detector_name,
                "confidence": detector_result.confidence,
            },
        )

    