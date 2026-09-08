from __future__ import annotations

from enum import Enum

from src.output_validation_agent.validators.support.models import (
    HallucinationConfig,
    HeuristicResult,
)


class EscalationDecision(str, Enum):
    ACCEPT = "accept"
    REJECT = "reject"
    ESCALATE = "escalate"


class SupportScoreAggregator:
    """
    Computes a weighted support score from Tier-1
    heuristic results.
    """

    _WEIGHTS = {
    "semantic_similarity": "semantic_weight",
    "entity_overlap": "entity_weight",
    "numeric_consistency": "numeric_weight",
    "keyword_overlap": "keyword_weight",
    "citation_match": "citation_weight",
}

    def aggregate(
        self,
        results: list[HeuristicResult],
        config: HallucinationConfig,
    ) -> tuple[float, bool]:

        weighted_score = 0.0
        total_weight = 0.0

        hard_rule = False

        for result in results:

            if not result.applicable:
                continue

            if result.score is None:
                continue
            
            if (
                result.name
                == "numeric_consistency"
                and result.score == 0.0
            ):
                hard_rule = True

            if (
                result.name
                == "entity_overlap"
                and result.score == 0.0
            ):
                hard_rule = True

            weight_name = self._WEIGHTS.get(
                result.name
            )

            if weight_name is None:
                continue

            weight = getattr(
                config,
                weight_name,
            )

            weighted_score += (
                result.score * weight
            )

            total_weight += weight

        if total_weight == 0:
            return 0.0, hard_rule

        return (
            weighted_score / total_weight,
            hard_rule,
        )


class EscalationPolicy:
    """
    Determines whether Tier-2 verification
    is required.
    """

    def decide(
        self,
        support_score: float,
        hard_rule_triggered: bool,
        config: HallucinationConfig,
    ) -> EscalationDecision:

        if hard_rule_triggered:
            return EscalationDecision.ESCALATE

        if (
            support_score
            >= config.high_confidence_threshold
        ):
            return EscalationDecision.ACCEPT

        if (
            support_score
            <= config.low_confidence_threshold
        ):
            return EscalationDecision.REJECT

        return EscalationDecision.ESCALATE