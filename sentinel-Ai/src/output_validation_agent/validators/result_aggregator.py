from __future__ import annotations

import logging
from statistics import mean

from .support.models import (
    HallucinationAggregationResult,
    SentenceDecision,
)
from ..exceptions import (
    InvalidValidationResultError,
)

logger = logging.getLogger(__name__)


class ResultAggregator:
    """
    Aggregates sentence-level validation decisions into a
    HallucinationAggregationResult.

    Responsibilities
    ----------------
    - Validate sentence decisions.
    - Compute aggregate support statistics.
    - Compute overall confidence.
    - Count supported and unsupported sentences.
    - Count Tier-2 usage.
    - Produce the aggregated hallucination result.

    This class is deterministic and stateless.
    """

    def aggregate(
        self,
        sentence_decisions: list[SentenceDecision],
    ) -> HallucinationAggregationResult:
        """
        Aggregate sentence decisions into a HallucinationAggregationResult.
        """

        logger.info(
            "Aggregating %d sentence decisions.",
            len(sentence_decisions),
        )

        self._validate_inputs(sentence_decisions)

        supported_count = self._count_supported(
            sentence_decisions
        )

        unsupported_count = self._count_unsupported(
            sentence_decisions
        )

        tier2_count = self._count_tier2_usage(
            sentence_decisions
        )

        average_support = self._compute_average_support(
            sentence_decisions
        )

        confidence = self._compute_confidence(
            sentence_decisions
        )

        return self._build_aggregation_result(
            sentence_decisions=sentence_decisions,
            average_support=average_support,
            confidence=confidence,
            supported_count=supported_count,
            unsupported_count=unsupported_count,
            tier2_count=tier2_count,
        )

    ####################################################################
    # Input Validation
    ####################################################################

    @staticmethod
    def _validate_inputs(
        sentence_decisions: list[SentenceDecision],
    ) -> None:

        if not isinstance(sentence_decisions, list):
            raise InvalidValidationResultError(
                "Sentence decisions must be a list."
            )

        if not sentence_decisions:
            raise InvalidValidationResultError(
                "Sentence decisions cannot be empty."
            )

        for decision in sentence_decisions:

            if not isinstance(
                decision,
                SentenceDecision,
            ):
                raise InvalidValidationResultError(
                    "Invalid SentenceDecision."
                )

            if (
                decision.used_tier2
                and decision.tier2_decision is None
            ):
                raise InvalidValidationResultError(
                    "SentenceDecision indicates Tier-2 was used "
                    "but no Tier2Decision was provided."
        )

    ####################################################################
    # Statistics
    ####################################################################

    @staticmethod
    def _compute_average_support(
        sentence_decisions: list[SentenceDecision],
    ) -> float:

        scores = [
            decision.support_score
            for decision in sentence_decisions
        ]

        return float(mean(scores))

    @staticmethod
    def _compute_confidence(
        sentence_decisions: list[SentenceDecision],
    ) -> float:

        confidences: list[float] = []

        for decision in sentence_decisions:

            if (
                decision.used_tier2
                and decision.tier2_decision is not None
            ):
                confidences.append(
                    decision.tier2_decision.confidence
                )
            else:
                confidences.append(
                    decision.support_score
                )
            

        return float(mean(confidences))

    ####################################################################
    # Counters
    ####################################################################

    @staticmethod
    def _count_supported(
        sentence_decisions: list[SentenceDecision],
    ) -> int:

        return sum(
            1
            for decision in sentence_decisions
            if decision.supported
        )

    @staticmethod
    def _count_unsupported(
        sentence_decisions: list[SentenceDecision],
    ) -> int:

        return sum(
            1
            for decision in sentence_decisions
            if not decision.supported
        )

    @staticmethod
    def _count_tier2_usage(
        sentence_decisions: list[SentenceDecision],
    ) -> int:

        return sum(
            1
            for decision in sentence_decisions
            if decision.used_tier2
        )

    ####################################################################
    # Metadata
    ####################################################################

    @staticmethod
    def _build_summary(
        sentence_decisions: list[SentenceDecision],
    ) -> dict[str, object]:

        total_sentences = len(sentence_decisions)

        supported = sum(
            1
            for decision in sentence_decisions
            if decision.supported
        )

        unsupported = total_sentences - supported

        tier2 = sum(
            1
            for decision in sentence_decisions
            if decision.used_tier2
        )

        support_ratio = (
            supported / total_sentences
            if total_sentences
            else 0.0
        )

        return {
            "total_sentences": total_sentences,
            "supported_sentences": supported,
            "unsupported_sentences": unsupported,
            "tier2_invocations": tier2,
            "support_ratio": support_ratio,
        }

    ####################################################################
    # Aggregation Result Factory
    ####################################################################

    def _build_aggregation_result(
        self,
        sentence_decisions: list[SentenceDecision],
        average_support: float,
        confidence: float,
        supported_count: int,
        unsupported_count: int,
        tier2_count: int,
    ) -> HallucinationAggregationResult:

        metadata = self._build_summary(
            sentence_decisions
        )

        return HallucinationAggregationResult(
            sentence_decisions=sentence_decisions,
            average_support_score=average_support,
            confidence=confidence,
            supported_sentence_count=supported_count,
            unsupported_sentence_count=unsupported_count,
            tier2_usage_count=tier2_count,
            hallucination_detected=(
                unsupported_count > 0
            ),
            metadata=metadata,
        )