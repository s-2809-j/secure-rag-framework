from __future__ import annotations

import logging

from src.input_security_agent.detectors.base import BaseDetector
from src.input_security_agent.models import (
    AgentDecision,
    SecurityContext,
)
from src.input_security_agent.policies.rule_policy_engine import (
    RulePolicyEngine,
)
from src.input_security_agent.scoring.risk_scoring_engine import (
    RiskScoringEngine,
)
from src.input_security_agent.preprocessing.input_normalizer import (
    InputNormalizer,
)

logger = logging.getLogger(__name__)


class InputSecurityAgent:
    """
    Orchestrates the complete input security pipeline.
    """

    def __init__(
        self,
        normalizer: InputNormalizer,
        detectors: list[BaseDetector],
        policy_engine: RulePolicyEngine,
        risk_engine: RiskScoringEngine,
    ) -> None:

        if not detectors:
            raise ValueError(
                "At least one detector must be provided."
            )

        self._normalizer = normalizer
        self._detectors = detectors
        self._policy_engine = policy_engine
        self._risk_engine = risk_engine

    def analyze(
        self,
        context: SecurityContext,
    ) -> AgentDecision:

        logger.info(
            "Starting input security analysis."
        )

        # ---------------------------------------------
        # Normalize
        # ---------------------------------------------

        normalized_query = self._normalizer.normalize(
            context.query
        )
        detector_context = SecurityContext(
    query=normalized_query
)
        # ---------------------------------------------
        # Run detectors
        # ---------------------------------------------

        results = []

        logger.info(
            "Executing %d detectors.",
            len(self._detectors),
        )

        for detector in self._detectors:

            results.append(
                detector.detect(
                    detector_context
                )
            )

        # ---------------------------------------------
        # Policy evaluation
        # ---------------------------------------------

        policy = self._policy_engine.evaluate(
            results
        )

        # ---------------------------------------------
        # Risk assessment
        # ---------------------------------------------

        risk = self._risk_engine.assess(
            results
        )

        logger.info(
            "Input security analysis completed."
        )

        return AgentDecision(
            allowed=policy.allowed,
            normalized_context= normalized_query,
            validation_results=results,
            policy_evaluation=policy,
            risk_assessment=risk,
        )