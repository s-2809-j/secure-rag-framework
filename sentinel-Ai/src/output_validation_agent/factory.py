"""
Factory responsible for constructing OutputValidationAgent instances.
"""

from __future__ import annotations

from src.llm.gemini_client import   GeminiLLMClient

from src.output_validation_agent.output_validation_agent import (
    OutputValidationAgent,
)

from src.output_validation_agent.policies.output_policy_engine import (
    OutputPolicyEngine,
)

from src.output_validation_agent.risk.output_risk_engine import (
    OutputRiskEngine,
)

from src.output_validation_agent.sanitizer.response_sanitizer import (
    ResponseSanitizer,
)

from src.output_validation_agent.validators.hallucination_validator import (
    HallucinationValidator,
)

from src.output_validation_agent.validators.prompt_leakage_validator import (
    PromptLeakageValidator,
)

from src.output_validation_agent.validators.pii_validator import (
    PIIValidator,
)

from src.output_validation_agent.validators.safety_policy_validator import (
    SafetyPolicyValidator,
)

from src.output_validation_agent.validators.support.models import (
    HallucinationConfig,
)

from src.output_validation_agent.validators.support.sentence_splitter import (
    SentenceSplitter,
)

from src.output_validation_agent.validators.support.scores.semantic_similarity import (
    SemanticSimilarityScorer,
)

from src.output_validation_agent.validators.support.scores.lexical_scores import (
    KeywordOverlapScorer,
    EntityOverlapScorer,
    NumericConsistencyScorer,
    CitationMatchScorer,
)

from src.output_validation_agent.validators.support.scoring import (
    SupportScoreAggregator,
    EscalationPolicy,
)

from src.output_validation_agent.validators.tier2_judge import (
    Tier2Judge,
)

from src.output_validation_agent.validators.result_aggregator import (
    ResultAggregator,
)

from src.output_validation_agent.validators.safety.parser import (
    SafetyParser,
)

from src.knowledge_base.embedder import Embedder


class OutputValidationAgentFactory:
    """
    Factory responsible for constructing a fully configured
    OutputValidationAgent.
    """

    @staticmethod
    def create_agent(
        llm: GeminiLLMClient | None = None,
    ) -> OutputValidationAgent:
        """
        Create a fully configured OutputValidationAgent.

        Parameters
        ----------
        llm
            Optional GeminiLLMClient. If omitted, a production
            GeminiLLMClient is created automatically.
        """

        llm = llm or GeminiLLMClient()

        embedder = Embedder()

        config = HallucinationConfig()

        splitter = SentenceSplitter()

        semantic_scorer = SemanticSimilarityScorer(
            embedder=embedder,
        )

        keyword_scorer = KeywordOverlapScorer()

        entity_scorer = EntityOverlapScorer()

        numeric_scorer = NumericConsistencyScorer()

        citation_scorer = CitationMatchScorer()

        support_score_aggregator = (
            SupportScoreAggregator()
        )

        escalation_policy = EscalationPolicy()

        tier2_judge = Tier2Judge(
            llm=llm,
        )

        result_aggregator = ResultAggregator()

        safety_parser = SafetyParser()

        validators = [
            HallucinationValidator(
                splitter=splitter,
                semantic_scorer=semantic_scorer,
                keyword_scorer=keyword_scorer,
                entity_scorer=entity_scorer,
                numeric_scorer=numeric_scorer,
                citation_scorer=citation_scorer,
                support_score_aggregator=support_score_aggregator,
                escalation_policy=escalation_policy,
                tier2_judge=tier2_judge,
                result_aggregator=result_aggregator,
                config=config,
            ),
            PromptLeakageValidator(),
            PIIValidator(),
            SafetyPolicyValidator(
                llm_client=llm,
                parser=safety_parser,
            ),
        ]

        policy_engine = OutputPolicyEngine()

        risk_engine = OutputRiskEngine()

        sanitizer = ResponseSanitizer()

        return OutputValidationAgent(
            validators=validators,
            policy_engine=policy_engine,
            risk_engine=risk_engine,
            sanitizer=sanitizer,
        )