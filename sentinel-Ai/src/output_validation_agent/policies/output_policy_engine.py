from __future__ import annotations

import logging

from src.output_validation_agent.exceptions import (
    PolicyEvaluationError,
)
from src.output_validation_agent.models import (
    OutputCategory,
    PolicyEvaluation,
    ValidationResult,
)
from src.output_validation_agent.policies.policy_rules import (
    ALLOW,
    BLOCK,
    POLICY_RULES,
    SANITIZE,
)

logger = logging.getLogger(__name__)


class OutputPolicyEngine:
    """
    Evaluates validation results and determines whether the
    generated response should be allowed, sanitized, or blocked.
    """

    def evaluate(
        self,
        results: list[ValidationResult],
    ) -> PolicyEvaluation:
        """
        Evaluate validator results and determine the
        response policy.
        """

        logger.info(
            "Evaluating output validation policy."
        )

        if not isinstance(results, list):
            raise PolicyEvaluationError(
                "Expected a list of ValidationResult objects."
            )

        if not results:
            raise PolicyEvaluationError(
                "No validation results were provided."
            )

        should_sanitize = False

        for result in results:

            if not isinstance(result, ValidationResult):
                raise PolicyEvaluationError(
                    "Expected ValidationResult."
                )

            if result.passed:
                continue

            action = POLICY_RULES.get(
                result.category,
            )

            if action is None:
                raise PolicyEvaluationError(
                    f"No policy rule defined for '{result.category.value}'."
                )
            
            if action == BLOCK:

                logger.warning(
                    "Blocking response due to '%s'.",
                    result.category.value,
                )

                return PolicyEvaluation(
                    allowed=False,
                    should_sanitize=False,
                    block_response=True,
                    reason=result.reason,
                )

            if action == SANITIZE:
                should_sanitize = True

        if should_sanitize:

            logger.info(
                "Response requires sanitization."
            )

            return PolicyEvaluation(
                allowed=True,
                should_sanitize=True,
                block_response=False,
                reason="Response contains unsupported content.",
            )

        logger.info(
            "Response approved."
        )

        return PolicyEvaluation(
            allowed=True,
            should_sanitize=False,
            block_response=False,
            reason="All validators passed.",
        )