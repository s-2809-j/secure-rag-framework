from __future__ import annotations

from dataclasses import FrozenInstanceError

from src.output_validation_agent.models import (
    OutputCategory,
    OutputRiskLevel,
    PolicyEvaluation,
    RiskAssessment,
    ValidationContext,
    ValidationDecision,
    ValidationResult,
)


def test_output_category() -> None:
    print("\n[TEST] OutputCategory")

    assert OutputCategory.SAFE.value == "safe"
    assert OutputCategory.HALLUCINATION.value == "hallucination"
    assert OutputCategory.PROMPT_LEAKAGE.value == "prompt_leakage"
    assert OutputCategory.PII.value == "pii"
    assert OutputCategory.POLICY_VIOLATION.value == "policy_violation"
    assert OutputCategory.UNSUPPORTED_CLAIM.value == "unsupported_claim"

    print("PASS")


def test_output_risk_level() -> None:
    print("\n[TEST] OutputRiskLevel")

    assert OutputRiskLevel.LOW.value == "low"
    assert OutputRiskLevel.MEDIUM.value == "medium"
    assert OutputRiskLevel.HIGH.value == "high"
    assert OutputRiskLevel.CRITICAL.value == "critical"

    print("PASS")


def test_validation_context() -> None:
    print("\n[TEST] ValidationContext")

    context = ValidationContext(
        user_query="Capital of France?",
        llm_response="Paris",
        retrieved_chunks=[],
    )

    assert context.user_query == "Capital of France?"
    assert context.llm_response == "Paris"
    assert context.retrieved_chunks == []
    assert context.metadata == {}

    print("PASS")


def test_validation_result() -> None:
    print("\n[TEST] ValidationResult")

    result = ValidationResult(
        validator_name="HallucinationValidator",
        passed=True,
        category=OutputCategory.SAFE,
        score=0.02,
        reason="Supported by retrieved evidence.",
    )

    assert result.validator_name == "HallucinationValidator"
    assert result.passed is True
    assert result.category == OutputCategory.SAFE
    assert result.score == 0.02
    assert result.reason == "Supported by retrieved evidence."
    assert result.details == {}

    print("PASS")


def test_policy_evaluation() -> None:
    print("\n[TEST] PolicyEvaluation")

    policy = PolicyEvaluation(
        allowed=True,
        should_sanitize=False,
        block_response=False,
        reason="Safe response.",
    )

    assert policy.allowed
    assert not policy.should_sanitize
    assert not policy.block_response
    assert policy.reason == "Safe response."

    print("PASS")


def test_risk_assessment() -> None:
    print("\n[TEST] RiskAssessment")

    risk = RiskAssessment(
        overall_score=0.12,
        confidence=0.96,
        risk_level=OutputRiskLevel.LOW,
        summary="Low risk.",
    )

    assert risk.overall_score == 0.12
    assert risk.confidence == 0.96
    assert risk.risk_level == OutputRiskLevel.LOW
    assert risk.summary == "Low risk."

    print("PASS")


def test_validation_decision() -> None:
    print("\n[TEST] ValidationDecision")

    result = ValidationResult(
        validator_name="HallucinationValidator",
        passed=True,
        category=OutputCategory.SAFE,
        score=0.01,
        reason="Verified",
    )

    policy = PolicyEvaluation(
        allowed=True,
        should_sanitize=False,
        block_response=False,
        reason="Allowed",
    )

    risk = RiskAssessment(
        overall_score=0.01,
        confidence=0.99,
        risk_level=OutputRiskLevel.LOW,
        summary="Low Risk",
    )

    decision = ValidationDecision(
        approved=True,
        original_response="Paris is the capital of France.",
        validation_results=[result],
        policy_evaluation=policy,
        risk_assessment=risk,
        request_id="REQ-001",
    )

    assert decision.approved
    assert decision.request_id == "REQ-001"
    assert len(decision.validation_results) == 1

    print("PASS")


def test_frozen_dataclasses() -> None:
    print("\n[TEST] Frozen Dataclasses")

    context = ValidationContext(
        user_query="Hello",
        llm_response="Hi",
        retrieved_chunks=[],
    )

    try:
        context.user_query = "Modified"
        raise AssertionError("ValidationContext should be immutable.")
    except FrozenInstanceError:
        pass

    result = ValidationResult(
        validator_name="Validator",
        passed=True,
        category=OutputCategory.SAFE,
        score=0.0,
        reason="Safe",
    )

    try:
        result.score = 1.0
        raise AssertionError("ValidationResult should be immutable.")
    except FrozenInstanceError:
        pass

    print("PASS")


def main() -> None:
    print("=" * 70)
    print("Output Validation Agent Models Test")
    print("=" * 70)

    test_output_category()
    test_output_risk_level()
    test_validation_context()
    test_validation_result()
    test_policy_evaluation()
    test_risk_assessment()
    test_validation_decision()
    test_frozen_dataclasses()

    print("\n" + "=" * 70)
    print("ALL MODEL TESTS PASSED")
    print("=" * 70)


if __name__ == "__main__":
    main()