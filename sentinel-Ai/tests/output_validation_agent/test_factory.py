from __future__ import annotations

import unittest

from src.llm.gemini_client import GeminiLLMClient

from src.output_validation_agent.factory import (
    OutputValidationAgentFactory,
)

from src.output_validation_agent.output_validation_agent import (
    OutputValidationAgent,
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


class OutputValidationFactoryTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):

        cls.llm = GeminiLLMClient()

    def setUp(self):

        self.agent = (
            OutputValidationAgentFactory.create_agent(
                self.llm
            )
        )

    ############################################################
    # Factory Creation
    ############################################################

    def test_returns_output_validation_agent(self):

        self.assertIsInstance(
            self.agent,
            OutputValidationAgent,
        )

    ############################################################
    # Validators
    ############################################################

    def test_registers_four_validators(self):

        validators = self.agent._validators

        self.assertEqual(
            len(validators),
            4,
        )

    def test_contains_hallucination_validator(self):

        self.assertTrue(

            any(

                isinstance(
                    validator,
                    HallucinationValidator,
                )

                for validator in self.agent._validators

            )

        )

    def test_contains_prompt_leakage_validator(self):

        self.assertTrue(

            any(

                isinstance(
                    validator,
                    PromptLeakageValidator,
                )

                for validator in self.agent._validators

            )

        )

    def test_contains_pii_validator(self):

        self.assertTrue(

            any(

                isinstance(
                    validator,
                    PIIValidator,
                )

                for validator in self.agent._validators

            )

        )

    def test_contains_safety_policy_validator(self):

        self.assertTrue(

            any(

                isinstance(
                    validator,
                    SafetyPolicyValidator,
                )

                for validator in self.agent._validators

            )

        )

    ############################################################
    # Shared Components
    ############################################################

    def test_policy_engine_exists(self):

        self.assertIsNotNone(
            self.agent._policy_engine
        )

    def test_risk_engine_exists(self):

        self.assertIsNotNone(
            self.agent._risk_engine
        )

    def test_response_sanitizer_exists(self):

        self.assertIsNotNone(
            self.agent._sanitizer
        )


if __name__ == "__main__":

    unittest.main()