from src.output_validation_agent.exceptions import (
    RiskAssessmentError,
)

from src.output_validation_agent.models import (
    OutputRiskLevel,
    RiskAssessment,
    ValidationResult,
)
from src.output_validation_agent.models import (
    OutputCategory,
)
from src.output_validation_agent.risk.output_risk_engine import (
    OutputRiskEngine,
)
import math

def create_validation_result(
    score: float,
) -> ValidationResult:

    return ValidationResult(
        validator_name="TestValidator",
        passed=True,
        category=OutputCategory.SAFE,
        score=score,
        reason="Test",
        details={},
    )
def test_constructor() -> None:

    print("\n[TEST] Constructor")

    engine = OutputRiskEngine()

    assert isinstance(
        engine,
        OutputRiskEngine,
    )

    print("PASS")

def test_invalid_results_type() -> None:

    print("\n[TEST] Invalid Results Type")

    engine = OutputRiskEngine()

    try:

        engine.assess("invalid")

        assert False

    except RiskAssessmentError:

        print("PASS")

def test_empty_results() -> None:

    print("\n[TEST] Empty Results")

    engine = OutputRiskEngine()

    try:

        engine.assess([])

        assert False

    except RiskAssessmentError:

        print("PASS")

def test_invalid_validation_result() -> None:

    print("\n[TEST] Invalid ValidationResult")

    engine = OutputRiskEngine()

    try:

        engine.assess(
            [object()]
        )

        assert False

    except RiskAssessmentError:

        print("PASS")

def test_low_risk() -> None:

    print("\n[TEST] LOW Risk")

    engine = OutputRiskEngine()

    assessment = engine.assess(
        [
            create_validation_result(0.10),
        ]
    )

    assert isinstance(
        assessment,
        RiskAssessment,
    )

    assert math.isclose(
        assessment.overall_score,
        0.10,
        rel_tol=1e-9,
    )

    assert math.isclose(
        assessment.confidence,
        0.90,
        rel_tol=1e-9,
    )
    assert assessment.risk_level == OutputRiskLevel.LOW
    assert OutputRiskLevel.LOW.value in assessment.summary

    print("PASS")

def test_medium_risk() -> None:

    print("\n[TEST] MEDIUM Risk")

    engine = OutputRiskEngine()

    assessment = engine.assess(
        [
            create_validation_result(0.40),
        ]
    )

    assert math.isclose(
    assessment.overall_score,
    0.40,
    rel_tol=1e-9,
    )

    assert math.isclose(
        assessment.confidence,
        0.60,
        rel_tol=1e-9,
    )
    assert OutputRiskLevel.MEDIUM.value in assessment.summary

    print("PASS")

def test_high_risk() -> None:

    print("\n[TEST] HIGH Risk")

    engine = OutputRiskEngine()

    assessment = engine.assess(
        [
            create_validation_result(0.70),
        ]
    )

    assert math.isclose(
        assessment.overall_score,
        0.70,
        rel_tol=1e-9,
    )

    assert math.isclose(
        assessment.confidence,
        0.30,
        rel_tol=1e-9,
    )  
    assert OutputRiskLevel.HIGH.value in assessment.summary

    print("PASS")

def test_critical_risk() -> None:

    print("\n[TEST] CRITICAL Risk")

    engine = OutputRiskEngine()

    assessment = engine.assess(
        [
            create_validation_result(0.90),
        ]
    )


    assert math.isclose(
        assessment.overall_score,
        0.90,
        rel_tol=1e-9,
    )

    assert math.isclose(
        assessment.confidence,
        0.10,
        rel_tol=1e-9,
    )
    assert OutputRiskLevel.CRITICAL.value in assessment.summary

    print("PASS")

def test_average_score() -> None:

    print("\n[TEST] Average Score")

    engine = OutputRiskEngine()

    assessment = engine.assess(
        [
            create_validation_result(0.20),
            create_validation_result(0.40),
            create_validation_result(0.60),
        ]
    )

    assert math.isclose(
        assessment.overall_score,
        0.40,
        rel_tol=1e-9,
    )

    assert math.isclose(
        assessment.confidence,
        0.60,
        rel_tol=1e-9,
    )
    assert assessment.risk_level == OutputRiskLevel.MEDIUM

    print("PASS")

def test_confidence_floor() -> None:

    print("\n[TEST] Confidence Floor")

    engine = OutputRiskEngine()

    assessment = engine.assess(
        [
            create_validation_result(1.20),
        ]
    )

    assert math.isclose(
        assessment.overall_score,
        1.20,
        rel_tol=1e-9,
    )

    assert math.isclose(
        assessment.confidence,
        0.0,
        abs_tol=1e-9,
    )
    assert assessment.risk_level == OutputRiskLevel.CRITICAL

    print("PASS")

def test_low_medium_boundary() -> None:

    print("\n[TEST] LOW -> MEDIUM Boundary")

    engine = OutputRiskEngine()

    assessment = engine.assess(
        [create_validation_result(0.25)]
    )

    assert assessment.risk_level == OutputRiskLevel.MEDIUM

    print("PASS")

def test_medium_upper_boundary() -> None:

    print("\n[TEST] MEDIUM Upper Boundary")

    engine = OutputRiskEngine()

    assessment = engine.assess(
        [create_validation_result(0.49)]
    )

    assert assessment.risk_level == OutputRiskLevel.MEDIUM

    print("PASS")
def test_medium_high_boundary() -> None:

    print("\n[TEST] MEDIUM -> HIGH Boundary")

    engine = OutputRiskEngine()

    assessment = engine.assess(
        [create_validation_result(0.50)]
    )

    assert assessment.risk_level == OutputRiskLevel.HIGH

    print("PASS")

def test_high_upper_boundary() -> None:

    print("\n[TEST] HIGH Upper Boundary")

    engine = OutputRiskEngine()

    assessment = engine.assess(
        [create_validation_result(0.74)]
    )

    assert assessment.risk_level == OutputRiskLevel.HIGH

    print("PASS")

def test_high_critical_boundary() -> None:

    print("\n[TEST] HIGH -> CRITICAL Boundary")

    engine = OutputRiskEngine()

    assessment = engine.assess(
        [create_validation_result(0.75)]
    )

    assert assessment.risk_level == OutputRiskLevel.CRITICAL

    print("PASS")
def main() -> None:

    print("=" * 70)
    print("output  risk Tests")
    print("=" * 70)

    test_low_medium_boundary()
    test_medium_upper_boundary()
    test_medium_high_boundary()
    test_high_upper_boundary()
    test_high_critical_boundary()

    print("\n" + "=" * 70)
    print("ALL TESTS PASSED")
    print("=" * 70)


if __name__ == "__main__":
    main()
