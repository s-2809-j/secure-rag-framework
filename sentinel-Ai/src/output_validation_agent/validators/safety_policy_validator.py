from __future__ import annotations

import logging
from src.output_validation_agent.validators.safety.models import (
    SafetyEvaluation,
)
from src.llm.gemini_client import GeminiLLMClient
from src.output_validation_agent.models import (
    OutputCategory,
    ValidationContext,
    ValidationResult,
)
from src.output_validation_agent.exceptions import (
    ValidatorExecutionError,
)
from src.output_validation_agent.validators.base import BaseValidator
from src.output_validation_agent.validators.rules.safety_policy_rules import (
    ESCALATION_RULES,
    EscalationRule,
)
from src.output_validation_agent.validators.safety.models import (
    SafetyDecision,
)
from src.output_validation_agent.validators.safety.parser import (
    SafetyParser,
)
from src.output_validation_agent.validators.safety.prompt import (
    SAFETY_POLICY_SYSTEM_PROMPT,
    SAFETY_POLICY_USER_PROMPT,
)

logger = logging.getLogger(__name__)

_DECISION_SCORES = {
    SafetyDecision.SAFE: 0.0,
    SafetyDecision.SANITIZE: 0.5,
    SafetyDecision.BLOCK: 1.0,
}
class SafetyPolicyValidator(BaseValidator):
    """
    Output Safety Policy Validator.

    Responsibilities
    ----------------
    1. Execute Tier-1 escalation rule matching.
    2. Invoke the Tier-2 Safety Judge when required.
    3. Convert the SafetyEvaluation into a ValidationResult.

    This validator is intentionally an orchestrator and contains
    no policy logic itself.
    """

    def __init__(
        self,
        llm_client: GeminiLLMClient,
        parser: SafetyParser,
        escalation_rules: tuple[
            EscalationRule,
            ...
        ] = ESCALATION_RULES,
    ) -> None:
        super().__init__()

        self._llm_client = llm_client
        self._parser = parser
        self._escalation_rules = escalation_rules

    ####################################################################
    # Public API
    ####################################################################

    def _validate(
        self,
        context: ValidationContext,
    ) -> ValidationResult:
        """
        Execute the complete safety validation pipeline.
        """

        logger.info(
            "Starting Safety Policy Validator."
        )

        self._validate_inputs(context)

        matched_rules = self._find_escalation_matches(
            context.llm_response
        )

        if not matched_rules:

            logger.debug(
                "No Tier-1 escalation indicators detected."
            )

            return self._build_validation_result(
                evaluation=None,
                matched_rules=[],
            )

        logger.info(
            "Tier-1 matched %d escalation rule(s).",
            len(matched_rules),
        )

        evaluation = self._evaluate_tier2(
            response=context.llm_response,
        )

        return self._build_validation_result(
            evaluation=evaluation,
            matched_rules=matched_rules,
        )
        ####################################################################
    # Input Validation
    ####################################################################

    @staticmethod
    def _validate_inputs(
        context: ValidationContext,
    ) -> None:
        """
        Validate validator inputs.
        """

        if not context.llm_response.strip():
            raise ValidatorExecutionError(
                "LLM response cannot be empty."
            )

    ####################################################################
    # Tier-1 Escalation
    ####################################################################

    def _find_escalation_matches(
        self,
        response: str,
    ) -> list[EscalationRule]:
        """
        Execute Tier-1 escalation rule matching.

        A match indicates that the response should be
        evaluated by the Tier-2 Safety Judge. A match does
        not imply that the response violates policy.
        """

        matched_rules: list[
            EscalationRule
        ] = []

        logger.debug(
            "Scanning response using %d escalation rule(s).",
            len(self._escalation_rules),
        )

        for rule in self._escalation_rules:

            if rule.pattern.search(response):

                logger.debug(
                    "Matched escalation rule '%s'.",
                    rule.name,
                )

                matched_rules.append(rule)

        logger.debug(
            "Tier-1 completed with %d match(es).",
            len(matched_rules),
        )

        return matched_rules
        ####################################################################
    # Tier-2 Safety Evaluation
    ####################################################################

    def _evaluate_tier2(
        self,
        response: str,
    ) ->SafetyEvaluation:
        """
        Execute Tier-2 semantic safety evaluation.

        Returns
        -------
        SafetyEvaluation
            Structured evaluation returned by the Tier-2
            Safety Judge.
        """

        logger.info(
            "Invoking Tier-2 Safety Judge."
        )

        user_prompt = (
            SAFETY_POLICY_USER_PROMPT.format(
                response=response,
            )
        )

        llm_response = self._llm_client.generate(
            system_prompt=(
                SAFETY_POLICY_SYSTEM_PROMPT
            ),
            user_prompt=user_prompt,
        )

        logger.debug(
            "Tier-2 Safety Judge completed."
        )

        evaluation = self._parser.parse(
            llm_response,
        )

        logger.info(
            "Tier-2 decision=%s confidence=%.2f",
            evaluation.decision.value,
            evaluation.confidence,
        )

        return evaluation

        ####################################################################
    # Validation Result
    ####################################################################

    @staticmethod
    def _build_validation_result(
        evaluation:SafetyEvaluation | None,
        matched_rules: list[EscalationRule],
    ) -> ValidationResult:
        """
        Convert the Tier-1/Tier-2 evaluation into the generic
        ValidationResult contract.
        """

        ################################################################
        # Tier-1 only (no escalation)
        ################################################################

        if evaluation is None:

            return ValidationResult(
                validator_name="SafetyPolicyValidator",
                passed=True,
                category=OutputCategory.SAFE,
                score=0.0,
                reason=(
                    "No Tier-1 escalation indicators detected."
                ),
                details={
                    "tier1_matches": 0,
                    "matched_rules": [],
                    "tier2_used": False,
                },
            )

        ################################################################
        # Tier-2 decision
        ################################################################

        passed = (
            evaluation.decision == SafetyDecision.SAFE
        )

        if evaluation.decision == SafetyDecision.SAFE:

            category = OutputCategory.SAFE

        else:

            category = (
                OutputCategory.POLICY_VIOLATION
            )

        if evaluation.decision == SafetyDecision.SAFE:

            score = _DECISION_SCORES[evaluation.decision]

        elif (
            evaluation.decision
            == SafetyDecision.SANITIZE
        ):

            score = _DECISION_SCORES[evaluation.decision]

        else:

            score = _DECISION_SCORES[evaluation.decision]

        if evaluation.decision == SafetyDecision.SAFE:

            reason = "No safety policy violations detected."

        elif (
            evaluation.decision
            == SafetyDecision.SANITIZE
        ):

            reason = (
                "Response requires sanitization before release."
            )

        else:

            reason = (
                "Response violates safety policy."
            )

        return ValidationResult(
            validator_name="SafetyPolicyValidator",
            passed=passed,
            category=category,
            score=score,
            reason=reason,
            details={
                "tier1_matches": len(matched_rules),
                "matched_rules": [
                    rule.name
                    for rule in matched_rules
                ],
                "tier2_used": True,
                "tier2_decision": (
                    evaluation.decision.value
                ),
                "tier2_confidence": (
                    evaluation.confidence
                ),
                "tier2_reason": (
                    evaluation.reason
                ),
                "triggered_rules": (
                    evaluation.triggered_rules
                ),
            },
        )
__all__ = [
    "SafetyPolicyValidator",
]