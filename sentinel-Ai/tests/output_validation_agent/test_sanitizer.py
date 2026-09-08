from src.output_validation_agent.exceptions import (
    SanitizationError,
)
from src.output_validation_agent.validators.support.models import (
    SentenceDecision,
)

from src.output_validation_agent.models import (
    OutputCategory,
    ValidationResult,
)

from src.output_validation_agent.sanitizer.response_sanitizer import (
    ResponseSanitizer,
)

def create_validation_result(
    *,
    passed: bool = False,
    category: OutputCategory = OutputCategory.HALLUCINATION,
    details: dict | None = None,
) -> ValidationResult:

    return ValidationResult(
        validator_name="TestValidator",
        passed=passed,
        category=category,
        score=0.5,
        reason="Test",
        details=details or {},
    )

def test_constructor() -> None:

    print("\n[TEST] Constructor")

    sanitizer = ResponseSanitizer()

    assert isinstance(
        sanitizer,
        ResponseSanitizer,
    )

    print("PASS")


def test_invalid_response_type() -> None:

    print("\n[TEST] Invalid Response Type")

    sanitizer = ResponseSanitizer()

    try:

        sanitizer.sanitize(
            123,
            [],
        )

        assert False

    except SanitizationError:

        print("PASS")

def test_invalid_results_type() -> None:

    print("\n[TEST] Invalid Results Type")

    sanitizer = ResponseSanitizer()

    try:

        sanitizer.sanitize(
            "response",
            "invalid",
        )

        assert False

    except SanitizationError:

        print("PASS")

def test_invalid_validation_result() -> None:

    print("\n[TEST] Invalid ValidationResult")

    sanitizer = ResponseSanitizer()

    try:

        sanitizer.sanitize(
            "response",
            [object()],
        )

        assert False

    except SanitizationError:

        print("PASS")

def test_empty_results() -> None:

    print("\n[TEST] Empty Results")

    sanitizer = ResponseSanitizer()

    response = "Hello world."

    sanitized = sanitizer.sanitize(
        response,
        [],
    )

    assert sanitized == response

    print("PASS")

def test_passed_validator() -> None:

    print("\n[TEST] Passed Validator")

    sanitizer = ResponseSanitizer()

    response = "This is a safe response."

    sanitized = sanitizer.sanitize(
        response,
        [
            create_validation_result(
                passed=True,
                category=OutputCategory.PII,
            ),
        ],
    )

    assert sanitized == response

    print("PASS")

def test_hallucination_sanitization() -> None:

    print("\n[TEST] Hallucination Sanitization")

    sanitizer = ResponseSanitizer()

    response = (
        "Paris is the capital of France. "
        "The moon is made of cheese."
    )

    decisions = [
    SentenceDecision(
        sentence="Paris is the capital of France.",
        support_score=0.95,
        supported=True,
        used_tier2=False,
        tier2_decision=None,
        evidence=None,
    ),
    SentenceDecision(
        sentence="The moon is made of cheese.",
        support_score=0.05,
        supported=False,
        used_tier2=False,
        tier2_decision=None,
        evidence=None,
    ),
]

    result = create_validation_result(
        category=OutputCategory.HALLUCINATION,
        details={
            "sentence_decisions": decisions,
        },
    )

    sanitized = sanitizer.sanitize(
        response,
        [result],
    )

    assert sanitized == "Paris is the capital of France."

    print("PASS")

def test_unsupported_claim_sanitization() -> None:

    print("\n[TEST] Unsupported Claim Sanitization")

    sanitizer = ResponseSanitizer()

    response = (
        "Earth is round. "
        "Dogs can breathe underwater."
    )

    decisions = [
    SentenceDecision(
        sentence="Earth is round.",
        support_score=0.95,
        supported=True,
        used_tier2=False,
        tier2_decision=None,
        evidence=None,
    ),
    SentenceDecision(
        sentence="Dogs can breathe underwater.",
        support_score=0.05,
        supported=False,
        used_tier2=False,
        tier2_decision=None,
        evidence=None,
    ),
]

    result = create_validation_result(
        category=OutputCategory.UNSUPPORTED_CLAIM,
        details={
            "sentence_decisions": decisions,
        },
    )

    sanitized = sanitizer.sanitize(
        response,
        [result],
    )

    assert sanitized == "Earth is round."

    print("PASS")

def test_pii_redaction() -> None:

    print("\n[TEST] PII Redaction")

    sanitizer = ResponseSanitizer()

    response = (
        "Email me at alice@example.com "
        "or call 9876543210."
    )

    result = create_validation_result(
        category=OutputCategory.PII,
    )

    sanitized = sanitizer.sanitize(
        response,
        [result],
    )

    assert "[REDACTED]" in sanitized
    assert "alice@example.com" not in sanitized
    assert "9876543210" not in sanitized


    print("PASS")

def test_prompt_leakage_redaction() -> None:

    print("\n[TEST] Prompt Leakage")

    sanitizer = ResponseSanitizer()

    response = "You are ChatGPT. System prompt..."

    result = create_validation_result(
        category=OutputCategory.PROMPT_LEAKAGE,
    )

    sanitized = sanitizer.sanitize(
        response,
        [result],
    )

    assert sanitized == (
        "[CONTENT REMOVED DUE TO SECURITY POLICY]"
    )


    print("PASS")

def test_policy_violation_redaction() -> None:

    print("\n[TEST] Policy Violation")

    sanitizer = ResponseSanitizer()

    response = "Malicious instructions."

    result = create_validation_result(
        category=OutputCategory.POLICY_VIOLATION,
    )

    sanitized = sanitizer.sanitize(
        response,
        [result],
    )

    assert sanitized == (
        "[CONTENT REMOVED DUE TO POLICY VIOLATION]"
    )

    print("PASS")


def test_multiple_sanitization_rules() -> None:

    print("\n[TEST] Multiple Sanitization Rules")

    sanitizer = ResponseSanitizer()

    response = (
        "Contact me at alice@example.com. "
        "The moon is made of cheese."
    )

    decisions = [
        SentenceDecision(
            sentence="Contact me at alice@example.com.",
            support_score=1.0,
            supported=True,
            used_tier2=False,
            tier2_decision=None,
            evidence=None,
        ),
        SentenceDecision(
            sentence="The moon is made of cheese.",
            support_score=0.05,
            supported=False,
            used_tier2=False,
            tier2_decision=None,
            evidence=None,
        ),
    ]

    hallucination = create_validation_result(
        category=OutputCategory.HALLUCINATION,
        details={
            "sentence_decisions": decisions,
        },
    )

    pii = create_validation_result(
        category=OutputCategory.PII,
    )

    sanitized = sanitizer.sanitize(
        response,
        [
            hallucination,
            pii,
        ],
    )

    assert "The moon is made of cheese." not in sanitized
    assert "alice@example.com" not in sanitized
    assert "[REDACTED]" in sanitized

    print("PASS")

def test_passed_result_is_ignored() -> None:

    print("\n[TEST] Passed Validator Ignored")

    sanitizer = ResponseSanitizer()

    response = "Email alice@example.com"

    safe = create_validation_result(
        passed=True,
        category=OutputCategory.SAFE,
    )

    pii = create_validation_result(
        category=OutputCategory.PII,
    )

    sanitized = sanitizer.sanitize(
        response,
        [
            safe,
            pii,
        ],
    )

    assert "[REDACTED]" in sanitized
    assert "alice@example.com" not in sanitized

    print("PASS")


def main() -> None:

    print("=" * 70)
    print("output  risk Tests")
    print("=" * 70)
    test_multiple_sanitization_rules()
    test_passed_result_is_ignored()

    print("\n" + "=" * 70)
    print("ALL TESTS PASSED")
    print("=" * 70)


if __name__ == "__main__":
    main()