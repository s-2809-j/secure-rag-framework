from __future__ import annotations

import logging

from src.input_security_agent.models import (
    AttackCategory,
    PolicyEvaluation,
    ValidationResult,
)

logger = logging.getLogger(__name__)


class RulePolicyEngine:

    _POLICY_RULES = {
        AttackCategory.PROMPT_INJECTION: "POLICY_001",
        AttackCategory.JAILBREAK: "POLICY_002",
        AttackCategory.SYSTEM_PROMPT_LEAKAGE: "POLICY_003",
        AttackCategory.MALICIOUS_INSTRUCTION: "POLICY_004",
        AttackCategory.PII: "POLICY_005",
    }

    def evaluate(
        self,
        results: list[ValidationResult],
    ) -> PolicyEvaluation:

        logger.info("Evaluating security policies.")

        triggered_rules: list[str] = []
        explanations: list[str] = []

        for result in results:

            if not result.is_flagged:
                continue

            rule = self._POLICY_RULES.get(result.category)

            if rule is None:
                continue

            triggered_rules.append(rule)

            explanations.append(
                f"{result.detector_name}: {result.reason}"
            )

        allowed = len(triggered_rules) == 0

        logger.info(
            "Policy evaluation completed."
        )

        return PolicyEvaluation(
            allowed=allowed,
            triggered_rules=triggered_rules,
            explanation="\n".join(explanations),
        )