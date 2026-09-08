from src.output_validation_agent.exceptions import (
    PolicyEvaluationError,
)

from src.output_validation_agent.models import (
    OutputCategory,
    ValidationResult,
)

from src.output_validation_agent.policies.output_policy_engine import (
    OutputPolicyEngine,
)

def create_validation_result(
    *,
    passed: bool = True,
    category: OutputCategory = OutputCategory.SAFE,
    reason: str = "Test",
) -> ValidationResult:

    return ValidationResult(
        validator_name="TestValidator",
        passed=passed,
        category=category,
        score=0.0,
        reason=reason,
        details={},
    )
def test_constructor() -> None:

    print("\n[TEST] Constructor")

    engine = OutputPolicyEngine()

    assert isinstance(
        engine,
        OutputPolicyEngine,
    )

    print("PASS")

def test_invalid_results_type() -> None:

    print("\n[TEST] Invalid Results Type")

    engine = OutputPolicyEngine()

    try:

        engine.evaluate("invalid")

        assert False

    except PolicyEvaluationError:

        print("PASS")

def test_empty_results() -> None:

    print("\n[TEST] Empty Results")

    engine = OutputPolicyEngine()

    try:

        engine.evaluate([])

        assert False

    except PolicyEvaluationError:

        print("PASS")


def test_invalid_validation_result() -> None:

    print("\n[TEST] Invalid ValidationResult")

    engine = OutputPolicyEngine()

    try:

        engine.evaluate(
            [object()]
        )

        assert False

    except PolicyEvaluationError:

        print("PASS")


def test_safe_response() -> None:

    print("\n[TEST] Safe Response")

    engine = OutputPolicyEngine()

    result = create_validation_result(
        passed=True,
        category=OutputCategory.SAFE,
    )

    policy = engine.evaluate([result])

    assert policy.allowed is True
    assert policy.should_sanitize is False
    assert policy.block_response is False
    assert policy.reason == "All validators passed."

    print("PASS")

def test_hallucination_sanitize() -> None:

    print("\n[TEST] Hallucination -> Sanitize")

    engine = OutputPolicyEngine()

    result = create_validation_result(
        passed=False,
        category=OutputCategory.HALLUCINATION,
        reason="Hallucination detected.",
    )

    policy = engine.evaluate([result])

    assert policy.allowed is True
    assert policy.should_sanitize is True
    assert policy.block_response is False
    assert (
        policy.reason
        == "Response contains unsupported content."
    )

    print("PASS")


def test_unsupported_claim_sanitize() -> None:

    print("\n[TEST] Unsupported Claim -> Sanitize")

    engine = OutputPolicyEngine()

    result = create_validation_result(
        passed=False,
        category=OutputCategory.UNSUPPORTED_CLAIM,
    )

    policy = engine.evaluate([result])

    assert policy.allowed is True
    assert policy.should_sanitize is True
    assert policy.block_response is False

    print("PASS")

def test_multiple_sanitize_rules() -> None:

    print("\n[TEST] Multiple Sanitize Rules")

    engine = OutputPolicyEngine()

    results = [
        create_validation_result(
            passed=False,
            category=OutputCategory.HALLUCINATION,
        ),
        create_validation_result(
            passed=False,
            category=OutputCategory.UNSUPPORTED_CLAIM,
        ),
    ]

    policy = engine.evaluate(results)

    assert policy.allowed is True
    assert policy.should_sanitize is True
    assert policy.block_response is False

    print("PASS")

def test_prompt_leakage_block() -> None:

    print("\n[TEST] Prompt Leakage -> Block")

    engine = OutputPolicyEngine()

    result = create_validation_result(
        passed=False,
        category=OutputCategory.PROMPT_LEAKAGE,
        reason="Prompt leakage detected.",
    )

    policy = engine.evaluate([result])

    assert policy.allowed is False
    assert policy.should_sanitize is False
    assert policy.block_response is True
    assert policy.reason == "Prompt leakage detected."

    print("PASS")

def test_pii_block() -> None:

    print("\n[TEST] PII -> Block")

    engine = OutputPolicyEngine()

    result = create_validation_result(
        passed=False,
        category=OutputCategory.PII,
        reason="PII detected.",
    )

    policy = engine.evaluate([result])

    assert policy.allowed is False
    assert policy.should_sanitize is False
    assert policy.block_response is True
    assert policy.reason == "PII detected."

    print("PASS")

def test_policy_violation_block() -> None:

    print("\n[TEST] Policy Violation -> Block")

    engine = OutputPolicyEngine()

    result = create_validation_result(
        passed=False,
        category=OutputCategory.POLICY_VIOLATION,
        reason="Policy violation detected.",
    )

    policy = engine.evaluate([result])

    assert policy.allowed is False
    assert policy.should_sanitize is False
    assert policy.block_response is True
    assert policy.reason == "Policy violation detected."

    print("PASS")

def test_block_takes_precedence() -> None:

    print("\n[TEST] Block Takes Precedence")

    engine = OutputPolicyEngine()

    results = [
        create_validation_result(
            passed=False,
            category=OutputCategory.HALLUCINATION,
        ),
        create_validation_result(
            passed=False,
            category=OutputCategory.PII,
            reason="Sensitive information detected.",
        ),
    ]

    policy = engine.evaluate(results)

    assert policy.allowed is False
    assert policy.should_sanitize is False
    assert policy.block_response is True
    assert policy.reason == "Sensitive information detected."

    print("PASS")



def main() -> None:

    print("=" * 70)
    print("output  policy Tests")
    print("=" * 70)

    test_prompt_leakage_block()
    test_pii_block()
    test_policy_violation_block()
    test_block_takes_precedence()

    print("\n" + "=" * 70)
    print("ALL TESTS PASSED")
    print("=" * 70)


if __name__ == "__main__":
    main()