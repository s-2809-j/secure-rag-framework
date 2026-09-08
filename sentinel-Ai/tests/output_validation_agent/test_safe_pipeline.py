from __future__ import annotations

import os
import unittest
from typing import ClassVar

from src.knowledge_base.models import RetrievedChunk

from src.llm.gemini_client import GeminiLLMClient

from src.output_validation_agent.factory import (
    OutputValidationAgentFactory,
)

from src.output_validation_agent.models import (
    ValidationContext,
    ValidationDecision,
    OutputRiskLevel,
    OutputCategory,
)


class TestSafePipeline(unittest.TestCase):
    """
    Production Integration Tests
    ============================

    Purpose
    -------
    Verify that a completely safe LLM response successfully passes through the
    entire Output Validation pipeline.

    This test intentionally uses the REAL production components:

        GeminiLLMClient
                │
                ▼
        OutputValidationAgentFactory
                │
                ▼
        HallucinationValidator
                │
                ▼
        PromptLeakageValidator
                │
                ▼
        PIIValidator
                │
                ▼
        SafetyPolicyValidator
                │
                ▼
        OutputPolicyEngine
                │
                ▼
        OutputRiskEngine
                │
                ▼
        ResponseSanitizer

    No validators are mocked.

    The objective is to validate that the complete pipeline behaves correctly
    for benign responses.
    """

    llm: ClassVar[GeminiLLMClient]
    agent = None

    @classmethod
    def setUpClass(cls) -> None:
        """
        Create expensive shared resources only once.

        Loading the Embedder, SentenceTransformer and Gemini LLM client
        repeatedly makes the suite unnecessarily slow.
        """

        required_environment = (
            "LLM_PROVIDER",
            "LLM_MODEL",
            "LLM_BASE_URL",
            "GITHUB_TOKEN",
        )

        missing = [
            variable
            for variable in required_environment
            if not os.getenv(variable)
        ]

        if missing:
            raise unittest.SkipTest(
                "Missing environment variables: "
                + ", ".join(missing)
            )

        cls.llm = GeminiLLMClient()

        cls.agent = OutputValidationAgentFactory.create_agent(
            llm=cls.llm,
        )

    @classmethod
    def tearDownClass(cls) -> None:
        """
        Explicit cleanup.

        Python will eventually collect these objects, but removing the
        references keeps long-running integration suites cleaner.
        """

        cls.agent = None
        cls.llm = None

    # ---------------------------------------------------------
    # Helper Builders
    # ---------------------------------------------------------

    def _chunk(
        self,
        text: str,
        distance: float = 0.05,
    ) -> RetrievedChunk:
        """
        Construct a realistic RetrievedChunk.
        """

        return RetrievedChunk(
            content=text,
            metadata={
                "document": "safe_document.md",
                "chunk_id": "chunk_001",
                "source": "integration_test",
            },
            distance=distance,
        )

    def _safe_context(self) -> ValidationContext:
        """
        Produce a validation context representing a completely
        safe RAG response.

        The retrieved knowledge fully supports the answer.
        """

        chunks = [
            self._chunk(
                (
                    "Paris is the capital and most populous city "
                    "of France. It is located in northern France "
                    "along the River Seine."
                )
            ),
            self._chunk(
                (
                    "France is a country in Western Europe. "
                    "Paris has served as the capital for centuries."
                ),
                distance=0.07,
            ),
        ]

        return ValidationContext(
            user_query="What is the capital of France?",

            llm_response=(
                "The capital of France is Paris."
            ),

            retrieved_chunks=chunks,

            metadata={
                "request_id": "safe-pipeline-001",
                "conversation_id": "integration-suite",
                "test_case": "safe_response",
            },
        )

    def _assert_safe_decision(
        self,
        decision: ValidationDecision,
    ) -> None:
        """
        Common assertions expected from every safe pipeline execution.
        """

        self.assertIsInstance(
            decision,
            ValidationDecision,
        )

        self.assertTrue(
            decision.approved,
            "Safe response should be approved.",
        )

        self.assertEqual(
            decision.original_response,
            decision.final_response,
            "Safe response should not be modified.",
        )

        self.assertFalse(
            decision.policy_evaluation.should_sanitize,
        )

        self.assertTrue(
            decision.policy_evaluation.allowed,
        )

        self.assertFalse(
            decision.policy_evaluation.block_response,
        )

        self.assertEqual(
            decision.request_id,
            "safe-pipeline-001",
        )

        self.assertEqual(
            decision.risk_assessment.risk_level,
            OutputRiskLevel.LOW,
        )

        self.assertGreaterEqual(
            len(decision.validation_results),
            4,
            "Every production validator should execute.",
        )

        validator_names = {
            result.validator_name
            for result in decision.validation_results
        }

        self.assertSetEqual(
            validator_names,
            {
                "HallucinationValidator",
                "PromptLeakageValidator",
                "PIIValidator",
                "SafetyPolicyValidator",
            },
        )

        expected_categories = {
            "HallucinationValidator": OutputCategory.SAFE,
            "PromptLeakageValidator": OutputCategory.PROMPT_LEAKAGE,
            "PIIValidator": OutputCategory.PII,
            "SafetyPolicyValidator": OutputCategory.SAFE,
        }

        for result in decision.validation_results:

            self.assertTrue(
                result.passed,
                f"{result.validator_name} should pass.",
            )

            # Each validator uses its own category to identify the
            # type of check performed. For passing validators the
            # expected category is defined in the map above.
            expected = expected_categories.get(
                result.validator_name,
                OutputCategory.SAFE,
            )

            self.assertEqual(
                result.category,
                expected,
            )

            self.assertLessEqual(
                result.score,
                0.30,
            )

    def test_safe_pipeline(self) -> None:
        """
        End-to-end integration test for a benign LLM response that
        should pass through the full Output Validation pipeline.
        """

        context = self._safe_context()

        decision = self.agent.validate(context)

        # Reuse the standard safe assertions for clarity.
        self._assert_safe_decision(decision)
