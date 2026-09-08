from __future__ import annotations

import logging
from typing import Any

from src.output_validation_agent.models import (
    OutputCategory,
    ValidationContext,
    ValidationResult,
)
from src.output_validation_agent.validators.base import BaseValidator
from src.output_validation_agent.validators.rules.prompt_leakage_rules import (
    PROMPT_LEAKAGE_RULES,
)

logger = logging.getLogger(__name__)


class PromptLeakageValidator(BaseValidator):
    """
    Validator responsible for detecting prompt leakage in
    LLM-generated responses.

    This validator is purely rule-based and does not modify
    the generated response.
    """

    def __init__(self) -> None:
        super().__init__()

    def _validate(
        self,
        context: ValidationContext,
    ) -> ValidationResult:
        """
        Detect prompt leakage patterns in the generated response.
        """

        response = context.llm_response.strip()

        if not response:
            return self._build_validation_result([])

        matches = self._scan_response(response)

        return self._build_validation_result(matches)

    def _scan_response(
        self,
        response: str,
    ) -> list[dict[str, Any]]:
        """
        Scan the response against every configured prompt
        leakage rule.
        """

        findings: list[dict[str, Any]] = []

        logger.debug("Scanning response for prompt leakage.")

        for rule in PROMPT_LEAKAGE_RULES:
            for match in rule.pattern.finditer(response):
                findings.append(
                    {
                        "rule": rule.name,
                        "type": rule.category.value,
                        "matched_text": match.group(0),
                        "start": match.start(),
                        "end": match.end(),
                        "description": rule.description,
                    }
                )

        logger.debug(
            "Prompt leakage scan completed with %d findings.",
            len(findings),
        )

        return findings

    def _build_validation_result(
        self,
        matches: list[dict[str, Any]],
    ) -> ValidationResult:
        """
        Build the ValidationResult from the detected findings.
        """

        score = self._calculate_score(len(matches))

        return ValidationResult(
            validator_name=self.name,
            passed=not matches,
            category=OutputCategory.PROMPT_LEAKAGE,
            score=score,
            reason=(
                "No prompt leakage detected."
                if not matches
                else f"Detected {len(matches)} prompt leakage pattern(s)."
            ),
            details={
                "match_count": len(matches),
                "matches": matches,
            },
        )

    @staticmethod
    def _calculate_score(
        match_count: int,
    ) -> float:
        """
        Calculate a deterministic confidence score based on
        the number of matched rules.
        """

        if match_count == 0:
            return 0.0

        if match_count == 1:
            return 0.4

        if match_count == 2:
            return 0.7

        return 1.0