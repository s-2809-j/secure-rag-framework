from __future__ import annotations

from src.input_security_agent.input_security_agent import InputSecurityAgent

from src.input_security_agent.preprocessing.input_normalizer import (
    InputNormalizer,
)

from src.input_security_agent.detectors.prompt_injection_detector import (
    PromptInjectionDetector,
)
from src.input_security_agent.detectors.jailbreak_detector import (
    JailbreakDetector,
)
from src.input_security_agent.detectors.pii_detector import (
    PIIDetector,
)
from src.input_security_agent.detectors.malicious_instruction_detector import (
    MaliciousInstructionDetector,
)
from src.input_security_agent.detectors.system_prompt_detector import (
    SystemPromptDetector,
)

from src.input_security_agent.semantic.attack_vector_store import (
    AttackVectorStore,
)
from src.input_security_agent.semantic.similarity_detector import (
    SimilarityDetector,
)

from src.input_security_agent.policies.rule_policy_engine import (
    RulePolicyEngine,
)
from src.input_security_agent.scoring.risk_scoring_engine import (
    RiskScoringEngine,
)

from src.knowledge_base.embedder import Embedder


class InputSecurityFactory:
    """
    Factory responsible for constructing fully configured
    InputSecurityAgent instances.
    """

    @staticmethod
    def create_agent() -> InputSecurityAgent:

        normalizer = InputNormalizer()

        embedder = Embedder()

        attack_vector_store = AttackVectorStore()

        similarity_detector = SimilarityDetector(
            embedder=embedder,
            vector_store=attack_vector_store,
        )

        detectors = [
            PromptInjectionDetector(),
            JailbreakDetector(),
            PIIDetector(),
            MaliciousInstructionDetector(),
            SystemPromptDetector(),
            similarity_detector,
        ]

        policy_engine = RulePolicyEngine()

        risk_engine = RiskScoringEngine()

        return InputSecurityAgent(
            normalizer=normalizer,
            detectors=detectors,
            policy_engine=policy_engine,
            risk_engine=risk_engine,
        )