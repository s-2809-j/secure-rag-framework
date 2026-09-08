from __future__ import annotations

from src.input_security_agent.models import (
    AttackCategory,
    DetectionMatch,
    ValidationResult as DetectorValidationResult,
)

from src.output_validation_agent.models import (
    OutputCategory,
    ValidationContext,
)

from src.output_validation_agent.validators.pii_validator import (
    PIIValidator,
)


class FakePIIDetector:
    """
    Fake detector used for unit testing.
    """

    def __init__(
        self,
        result: DetectorValidationResult,
    ) -> None:
        self._result = result

    def detect(self, context):
        return self._result


def create_context(
    response: str,
) -> ValidationContext:
    return ValidationContext(
        user_query="Test query",
        llm_response=response,
        retrieved_chunks=[],
    )


def create_safe_detector_result() -> DetectorValidationResult:
    return DetectorValidationResult(
        detector_name="PIIDetector",
        category=AttackCategory.BENIGN,
        is_flagged=False,
        confidence=0.0,
        reason="No PII detected.",
        matches=[],
    )


def create_flagged_detector_result() -> DetectorValidationResult:
    return DetectorValidationResult(
        detector_name="PIIDetector",
        category=AttackCategory.PII,
        is_flagged=True,
        confidence=0.90,
        reason="Sensitive information detected.",
        matches=[
            DetectionMatch(
                matched_text="john@example.com",
                pattern_name="EMAIL",
                start=10,
                end=26,
            ),
            DetectionMatch(
                matched_text="AKIAIOSFODNN7EXAMPLE",
                pattern_name="AWS_ACCESS_KEY",
                start=35,
                end=55,
            ),
        ],
    )


def test_constructor() -> None:
    validator = PIIValidator()

    assert validator is not None
    assert validator.name == "PIIValidator"


def test_empty_response() -> None:
    validator = PIIValidator(
        detector=FakePIIDetector(
            create_safe_detector_result(),
        ),
    )

    result = validator.validate(
        create_context(""),
    )

    assert result.passed is True
    assert result.category == OutputCategory.PII
    assert result.score == 0.0
    assert result.details["match_count"] == 0


def test_safe_response() -> None:
    validator = PIIValidator(
        detector=FakePIIDetector(
            create_safe_detector_result(),
        ),
    )

    result = validator.validate(
        create_context(
            "Paris is the capital of France.",
        ),
    )

    assert result.passed is True
    assert result.category == OutputCategory.PII
    assert result.score == 0.0
    assert result.details["match_count"] == 0


def test_pii_detected() -> None:
    validator = PIIValidator(
        detector=FakePIIDetector(
            create_flagged_detector_result(),
        ),
    )

    result = validator.validate(
        create_context(
            "Email me at john@example.com",
        ),
    )

    assert result.passed is False
    assert result.category == OutputCategory.PII
    assert result.score > 0.0
    assert result.reason == "Sensitive information detected."
    assert result.details["match_count"] == 2
    assert len(result.details["matches"]) == 2


def test_match_structure() -> None:
    validator = PIIValidator(
        detector=FakePIIDetector(
            create_flagged_detector_result(),
        ),
    )

    result = validator.validate(
        create_context(
            "Contact john@example.com",
        ),
    )

    match = result.details["matches"][0]

    assert match["pattern"] == "EMAIL"
    assert match["matched_text"] == "john@example.com"
    assert match["start"] == 10
    assert match["end"] == 26


def test_multiple_matches() -> None:
    validator = PIIValidator(
        detector=FakePIIDetector(
            create_flagged_detector_result(),
        ),
    )

    result = validator.validate(
        create_context(
            (
                "Email: john@example.com\n"
                "AWS Key: AKIAIOSFODNN7EXAMPLE"
            ),
        ),
    )

    assert result.passed is False
    assert result.details["match_count"] == 2
    assert len(result.details["matches"]) == 2


def test_detector_metadata() -> None:
    validator = PIIValidator(
        detector=FakePIIDetector(
            create_flagged_detector_result(),
        ),
    )

    result = validator.validate(
        create_context(
            "john@example.com",
        ),
    )

    assert result.details["detector"] == "PIIDetector"
    assert result.details["confidence"] == 0.90


def test_validation_result_structure() -> None:
    validator = PIIValidator(
        detector=FakePIIDetector(
            create_flagged_detector_result(),
        ),
    )

    result = validator.validate(
        create_context(
            "john@example.com",
        ),
    )

    assert result.validator_name == "PIIValidator"
    assert result.category == OutputCategory.PII
    assert result.passed is False
    assert isinstance(result.score, float)
    assert isinstance(result.reason, str)
    assert isinstance(result.details, dict)


def test_safe_details_structure() -> None:
    validator = PIIValidator(
        detector=FakePIIDetector(
            create_safe_detector_result(),
        ),
    )

    result = validator.validate(
        create_context(
            "Hello world",
        ),
    )

    assert result.details == {
        "match_count": 0,
        "matches": [],
    }


def test_flagged_details_structure() -> None:
    validator = PIIValidator(
        detector=FakePIIDetector(
            create_flagged_detector_result(),
        ),
    )

    result = validator.validate(
        create_context(
            "john@example.com",
        ),
    )

    details = result.details

    assert "match_count" in details
    assert "matches" in details
    assert "detector" in details
    assert "confidence" in details

    assert isinstance(details["matches"], list)
    assert details["match_count"] == len(details["matches"])