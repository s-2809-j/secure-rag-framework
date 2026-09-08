from __future__ import annotations

import logging

from src.output_validation_agent.exceptions import (
    SanitizationError,
)
from src.output_validation_agent.models import (
    ValidationResult,
)
from src.output_validation_agent.sanitizer.sanitization_rules import (
    SANITIZATION_RULES,
)

logger = logging.getLogger(__name__)


class ResponseSanitizer:
    """
    Applies sanitization rules to an LLM response.

    Responsibilities
    ----------------
    - Validate sanitizer inputs.
    - Apply sanitization rules corresponding to failed validators.
    - Return the sanitized response.

    This class performs no validation, policy evaluation,
    or risk assessment.
    """

    def sanitize(
        self,
        response: str,
        results: list[ValidationResult],
    ) -> str:
        """
        Sanitize the supplied response.
        """

        logger.info("Sanitizing response.")

        self._validate_inputs(
            response,
            results,
        )

        sanitized = response

        for result in results:

            if result.passed:
                continue

            rule = SANITIZATION_RULES.get(
                result.category
            )

            if rule is None:
                continue

            logger.debug(
                "Applying sanitization rule for '%s'.",
                result.category.value,
            )

            sanitized = rule(
                sanitized,
                result,
            )

        logger.info(
            "Response sanitization completed."
        )

        return sanitized

    @staticmethod
    def _validate_inputs(
        response: str,
        results: list[ValidationResult],
    ) -> None:
        """
        Validate sanitizer inputs.
        """

        if not isinstance(response, str):
            raise SanitizationError(
                "Response must be a string."
            )

        if not isinstance(results, list):
            raise SanitizationError(
                "Results must be a list of ValidationResult."
            )

        for result in results:

            if not isinstance(
                result,
                ValidationResult,
            ):
                raise SanitizationError(
                    "Expected ValidationResult."
                )