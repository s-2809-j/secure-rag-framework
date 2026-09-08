from __future__ import annotations

import unittest

from src.output_validation_agent.output_validation_agent import (
    OutputValidationAgent,
)

from src.output_validation_agent.models import (
    ValidationContext,
    ValidationResult,
    ValidationDecision,
    PolicyEvaluation,
    RiskAssessment,
    OutputCategory,
    OutputRiskLevel,
)

from src.output_validation_agent.exceptions import (
    ValidatorExecutionError,
    InvalidValidationContextError,
)


########################################################################
# Fake Components
########################################################################

class FakeValidator:
    name = "FakeValidator"

    def __init__(
        self,
        passed: bool = True,
    ) -> None:
        self.called = False
        self.passed = passed

    def validate(
        self,
        context: ValidationContext,
    ) -> ValidationResult:

        self.called = True

        return ValidationResult(
            validator_name=self.name,
            passed=self.passed,
            category=OutputCategory.SAFE,
            score=0.0,
            reason="OK",
        )


class FakeFailingValidator:
    name = "FailingValidator"

    def validate(
        self,
        context: ValidationContext,
    ):

        raise RuntimeError("Validator failed")


class FakePolicyEngine:

    def evaluate(self, results):

        return PolicyEvaluation(
            allowed=True,
            should_sanitize=False,
            block_response=False,
            reason="Allowed",
        )


class FakeSanitizePolicyEngine:

    def evaluate(self, results):

        return PolicyEvaluation(
            allowed=True,
            should_sanitize=True,
            block_response=False,
            reason="Sanitize",
        )


class FakeRiskEngine:

    def assess(self, results):

        return RiskAssessment(
            overall_score=0.0,
            confidence=1.0,
            risk_level=OutputRiskLevel.LOW,
            summary="Safe",
        )


class FakeSanitizer:

    def sanitize(
        self,
        response,
        validation_results,
    ):

        return "[SANITIZED]"


########################################################################
# Tests
########################################################################

class OutputValidationAgentTests(
    unittest.TestCase,
):

    def setUp(self):

        self.validator = FakeValidator()

        self.agent = OutputValidationAgent(
            validators=[self.validator],
            policy_engine=FakePolicyEngine(),
            risk_engine=FakeRiskEngine(),
            sanitizer=FakeSanitizer(),
        )

        self.context = ValidationContext(
            user_query="Hello",
            llm_response="Hi",
            retrieved_chunks=[],
            metadata={},
        )

    ############################################################
    # Constructor
    ############################################################

    def test_empty_validator_list(self):

        with self.assertRaises(ValueError):

            OutputValidationAgent(
                validators=[],
                policy_engine=FakePolicyEngine(),
                risk_engine=FakeRiskEngine(),
                sanitizer=FakeSanitizer(),
            )

    ############################################################
    # validate()
    ############################################################

    def test_validate_returns_decision(self):

        decision = self.agent.validate(
            self.context
        )

        self.assertIsInstance(
            decision,
            ValidationDecision,
        )

    def test_validator_called(self):

        self.agent.validate(
            self.context
        )

        self.assertTrue(
            self.validator.called
        )

    def test_response_not_sanitized(self):

        decision = self.agent.validate(
            self.context
        )

        self.assertEqual(
            decision.final_response,
            "Hi",
        )

    def test_response_sanitized(self):

        agent = OutputValidationAgent(
            validators=[FakeValidator()],
            policy_engine=FakeSanitizePolicyEngine(),
            risk_engine=FakeRiskEngine(),
            sanitizer=FakeSanitizer(),
        )

        decision = agent.validate(
            self.context
        )

        self.assertEqual(
            decision.final_response,
            "[SANITIZED]",
        )

    ############################################################
    # Exceptions
    ############################################################

    def test_invalid_context(self):

        with self.assertRaises(
            InvalidValidationContextError
        ):

            self.agent.validate("invalid")

    def test_validator_exception(self):

        agent = OutputValidationAgent(
            validators=[FakeFailingValidator()],
            policy_engine=FakePolicyEngine(),
            risk_engine=FakeRiskEngine(),
            sanitizer=FakeSanitizer(),
        )

        with self.assertRaises(
            ValidatorExecutionError
        ):

            agent.validate(
                self.context
            )


if __name__ == "__main__":

    unittest.main()