from __future__ import annotations

from src.output_validation_agent.validators.hallucination_validator import (
    HallucinationValidator,
)
from src.output_validation_agent.models import ValidationResult
from src.knowledge_base.models import RetrievedChunk
from src.output_validation_agent.validators.support.models import (
    HallucinationAggregationResult,
)
from src.output_validation_agent.exceptions import (
    InvalidValidationContextError,
)
from src.output_validation_agent.validators.support.models import (
    HallucinationConfig,
)

from src.output_validation_agent.models import (
    ValidationContext,
    OutputCategory,
)

from src.output_validation_agent.exceptions import (
    ValidatorExecutionError,
)
from src.output_validation_agent.validators.support.models import (
    HeuristicResult,
    SentenceEvidence,
    Tier2Decision,
)

###############################################################################
# Fake Dependencies
###############################################################################

class FakeSplitter:
    def split(self, text: str):
        return [text]


class FakeSemanticScorer:
    def score(self, sentence, chunks):
        return []


class FakeLexicalScorer:
    def score(self, sentence, chunks):
        return []


class FakeSupportScoreAggregator:
    def compute(self, heuristic_results):
        return 1.0


class FakeTier2Judge:
    def evaluate(
        self,
        sentence,
        evidence_chunks,
        conversation_context,
    ):
        raise AssertionError(
            "Tier2 should not be called."
        )


class FakeResultAggregator:

    def aggregate(
        self,
        sentence_decisions,
    ) -> HallucinationAggregationResult:

        supported = sum(
            d.supported
            for d in sentence_decisions
        )

        unsupported = (
            len(sentence_decisions)
            - supported
        )

        average_score = (
            sum(
                d.support_score
                for d in sentence_decisions
            )
            / len(sentence_decisions)
            if sentence_decisions
            else 0.0
        )

        confidence = (
            sum(
                (
                    d.tier2_decision.confidence
                    if d.tier2_decision
                    else d.support_score
                )
                for d in sentence_decisions
            )
            / len(sentence_decisions)
            if sentence_decisions
            else 0.0
        )

        return HallucinationAggregationResult(
            sentence_decisions=sentence_decisions,
            average_support_score=average_score,
            confidence=confidence,
            supported_sentence_count=supported,
            unsupported_sentence_count=unsupported,
            tier2_usage_count=sum(
                d.used_tier2
                for d in sentence_decisions
            ),
            hallucination_detected=(
                unsupported > 0
            ),
            metadata={},
        )

###############################################################################
# Configurable Fake Components
###############################################################################

class FakeSemanticScorer:

    def __init__(self, score: float = 0.95):
        self._score = score

    def score(self, sentence, chunks):

        return [
            HeuristicResult(
                name="Semantic",
                applicable=True,
                score=self._score,
                confidence=1.0,
            )
        ]


class FakeLexicalScorer:

    def __init__(self, score: float = 0.95):
        self._score = score

    def score(self, sentence, chunks):

        return [
            HeuristicResult(
                name="Lexical",
                applicable=True,
                score=self._score,
                confidence=1.0,
            )
        ]


class FakeSupportScoreAggregator:

    def __init__(self, support_score: float = 0.95):
        self._support_score = support_score

    def compute(self, heuristic_results):

        return self._support_score


class FakeTier2Judge:

    def __init__(
        self,
        supported=True,
    ):

        self.called = False
        self.supported = supported

    def evaluate(
        self,
        sentence,
        evidence_chunks,
        conversation_context,
    ):

        self.called = True

        return Tier2Decision(
            supported=self.supported,
            confidence=0.95,
            reason="Tier2 verification.",
            evidence_indices=[0],
        )

###############################################################################
# Validator Factory
###############################################################################

def create_validator() -> HallucinationValidator:

    config = HallucinationConfig()

    return HallucinationValidator(
        splitter=FakeSplitter(),
        semantic_scorer=FakeSemanticScorer(),
        lexical_scorer=FakeLexicalScorer(),
        support_score_aggregator=FakeSupportScoreAggregator(),
        tier2_judge=FakeTier2Judge(),
        result_aggregator=FakeResultAggregator(),
        config=config,
    )


###############################################################################
# Tests
###############################################################################

def test_constructor() -> None:

    print("\n[TEST] Constructor")

    validator = create_validator()

    assert validator is not None

    print("PASS")


def test_validate_inputs_valid() -> None:

    print("\n[TEST] Valid Input")

    context = ValidationContext(
        user_query="Capital of France?",
        llm_response="Paris is the capital of France.",
        retrieved_chunks=[object()],
    )

    HallucinationValidator._validate_inputs(
        context
    )

    print("PASS")


def test_validate_inputs_empty_response() -> None:

    print("\n[TEST] Empty Response")

    context = ValidationContext(
        user_query="Question",
        llm_response="",
        retrieved_chunks=[object()],
    )

    try:

        HallucinationValidator._validate_inputs(
            context
        )

        raise AssertionError(
            "Expected ValidatorExecutionError."
        )

    except ValidatorExecutionError:

        print("PASS")


def test_validate_inputs_empty_chunks() -> None:

    print("\n[TEST] Empty Chunks")

    context = ValidationContext(
        user_query="Question",
        llm_response="Answer",
        retrieved_chunks=[],
    )

    try:

        HallucinationValidator._validate_inputs(
            context
        )

        raise AssertionError(
            "Expected ValidatorExecutionError."
        )

    except ValidatorExecutionError:

        print("PASS")


def test_validate_inputs_invalid_context() -> None:

    print("\n[TEST] Invalid Context")

    try:

        HallucinationValidator._validate_inputs(
            None
        )

        raise AssertionError(
            "Expected ValidatorExecutionError."
        )

    except ValidatorExecutionError:

        print("PASS")

###############################################################################
# Decision Factory Tests
###############################################################################

from src.output_validation_agent.validators.support.models import (
    HeuristicResult,
    SentenceEvidence,
    Tier2Decision,
)


def create_sentence_evidence() -> SentenceEvidence:

    heuristic = HeuristicResult(
        name="SemanticScorer",
        applicable=True,
        score=0.95,
        confidence=0.98,
    )

    return SentenceEvidence(
        sentence="Paris is the capital of France.",
        heuristic_results=[heuristic],
    )


def create_tier2_decision() -> Tier2Decision:

    return Tier2Decision(
        supported=True,
        confidence=0.97,
        reason="Supported by retrieved evidence.",
        evidence_indices=[0],
    )


def test_create_supported_decision() -> None:

    print("\n[TEST] Supported Decision")

    evidence = create_sentence_evidence()

    decision = (
        HallucinationValidator._create_supported_decision(
            sentence=evidence.sentence,
            support_score=0.96,
            evidence=evidence,
        )
    )

    assert decision.sentence == evidence.sentence
    assert decision.support_score == 0.96
    assert decision.supported is True
    assert decision.used_tier2 is False
    assert decision.tier2_decision is None
    assert decision.evidence == evidence

    print("PASS")


def test_create_unsupported_decision() -> None:

    print("\n[TEST] Unsupported Decision")

    evidence = create_sentence_evidence()

    decision = (
        HallucinationValidator._create_unsupported_decision(
            sentence=evidence.sentence,
            support_score=0.15,
            evidence=evidence,
        )
    )

    assert decision.sentence == evidence.sentence
    assert decision.support_score == 0.15
    assert decision.supported is False
    assert decision.used_tier2 is False
    assert decision.tier2_decision is None
    assert decision.evidence == evidence

    print("PASS")


def test_create_tier2_decision() -> None:

    print("\n[TEST] Tier2 Decision")

    evidence = create_sentence_evidence()

    tier2 = create_tier2_decision()

    decision = (
        HallucinationValidator._create_tier2_decision(
            sentence=evidence.sentence,
            support_score=0.58,
            evidence=evidence,
            tier2=tier2,
        )
    )

    assert decision.sentence == evidence.sentence
    assert decision.support_score == 0.58
    assert decision.supported is True
    assert decision.used_tier2 is True
    assert decision.tier2_decision == tier2
    assert decision.evidence == evidence

    print("PASS")

def create_aggregation_result(
    hallucination_detected: bool,
) -> HallucinationAggregationResult:

    return HallucinationAggregationResult(
        sentence_decisions=[],
        average_support_score=0.92 if not hallucination_detected else 0.35,
        confidence=0.96,
        supported_sentence_count=3 if not hallucination_detected else 1,
        unsupported_sentence_count=0 if not hallucination_detected else 2,
        tier2_usage_count=1,
        hallucination_detected=hallucination_detected,
        metadata={
            "source": "unit-test",
        },
    )

def test_build_validation_result_safe() -> None:

    print("\n[TEST] Build ValidationResult (Safe)")

    validator = create_validator()

    aggregation = create_aggregation_result(
        hallucination_detected=False,
    )

    result = validator._build_validation_result(
        aggregation
    )

    assert result.validator_name == "HallucinationValidator"

    assert result.passed is True

    assert (
        result.category
        == OutputCategory.SAFE
    )

    assert (
        result.reason
        == "No hallucinations detected."
    )

    assert result.score == (
        1.0 - aggregation.average_support_score
    )

    assert (
        result.details[
            "average_support_score"
        ]
        == aggregation.average_support_score
    )

    assert (
        result.details["confidence"]
        == aggregation.confidence
    )

    print("PASS")

def test_build_validation_result_hallucination() -> None:

    print(
        "\n[TEST] Build ValidationResult "
        "(Hallucination)"
    )

    validator = create_validator()

    aggregation = create_aggregation_result(
        hallucination_detected=True,
    )

    result = validator._build_validation_result(
        aggregation
    )

    assert result.validator_name == "HallucinationValidator"

    assert result.passed is False

    assert (
        result.category
        == OutputCategory.HALLUCINATION
    )

    assert (
        result.reason
        == "Unsupported claims detected."
    )

    assert result.score == (
        1.0 - aggregation.average_support_score
    )

    assert (
        result.details[
            "unsupported_sentence_count"
        ]
        == aggregation.unsupported_sentence_count
    )

    print("PASS")



def test_process_sentence_supported() -> None:

    print("\n[TEST] Process Sentence - Supported")

    validator, tier2 = create_process_sentence_validator(
    support_score=0.95,
)

    decision = validator._process_sentence(
        sentence="Paris is the capital of France.",
        evidence_chunks=[
            RetrievedChunk(
                content="Paris is the capital of France.",
                metadata={},
                distance=0.05,
            )
        ],
        conversation_context=None,
    )

    assert decision.supported is True
    assert decision.used_tier2 is False
    assert tier2.called is False

    print("PASS")

def test_process_sentence_unsupported() -> None:

    print("\n[TEST] Process Sentence - Unsupported")

    validator, tier2 = create_process_sentence_validator(
    support_score=0.20,
)

    decision = validator._process_sentence(
        sentence="Moon is made of cheese.",
        evidence_chunks=[
            RetrievedChunk(
                content="Paris is the capital of France.",
                metadata={},
                distance=0.05,
            )
        ],
        conversation_context=None,
    )

    assert decision.supported is False
    assert decision.used_tier2 is False
    assert tier2.called is False

    print("PASS")

def test_process_sentence_tier2() -> None:

    print("\n[TEST] Process Sentence - Tier2")

    validator, tier2 = create_process_sentence_validator(
    support_score=0.75,
)
    decision = validator._process_sentence(
        sentence="Borderline sentence.",
        evidence_chunks=[
            RetrievedChunk(
                content="Paris is the capital of France.",
                metadata={},
                distance=0.05,
            )
        ],
        conversation_context=None,
    )

    assert tier2.called is True
    assert decision.used_tier2 is True
    assert decision.supported is True

    print("PASS")

def test_process_sentence_tier2_disabled() -> None:

    print("\n[TEST] Tier2 Disabled")

    validator, tier2 = create_process_sentence_validator(
    support_score=0.75,
    tier2_enabled=False,
)

    decision = validator._process_sentence(
        sentence="Borderline sentence.",
        evidence_chunks=[
            RetrievedChunk(
                content="Paris is the capital of France.",
                metadata={},
                distance=0.05,
            )
        ],
        conversation_context=None,
    )

    assert tier2.called is False
    assert decision.supported is False
    assert decision.used_tier2 is False

    print("PASS")

###############################################################################
# Process Sentence Validator Factory
###############################################################################

def create_process_sentence_validator(
    support_score: float,
    *,
    tier2_enabled: bool = True,
    tier2_supported: bool = True,
) -> tuple[HallucinationValidator, FakeTier2Judge]:

    tier2 = FakeTier2Judge(
        supported=tier2_supported,
    )

    config = HallucinationConfig(
        enable_tier2=tier2_enabled,
    )

    validator = HallucinationValidator(
        splitter=FakeSplitter(),
        semantic_scorer=FakeSemanticScorer(
            support_score,
        ),
        lexical_scorer=FakeLexicalScorer(
            support_score,
        ),
        support_score_aggregator=FakeSupportScoreAggregator(
            support_score,
        ),
        tier2_judge=tier2,
        result_aggregator=FakeResultAggregator(),
        config=config,
    )

    return validator, tier2

def create_chunks() -> list[RetrievedChunk]:
    return [
        RetrievedChunk(
            content="Paris is the capital of France.",
            metadata={},
            distance=0.05,
        ),
        RetrievedChunk(
            content="France is located in Europe.",
            metadata={},
            distance=0.10,
        ),
    ]

###############################################################################
# Validation Context Helper
###############################################################################

def create_validation_context(
    response: str = (
        "Paris is the capital of France. "
        "France is in Europe."
    ),
) -> ValidationContext:

    return ValidationContext(
        user_query="Where is Paris?",
        llm_response=response,
        retrieved_chunks=create_chunks(),
        metadata={},
    )
def test_validate_supported_response() -> None:

    print("\n[TEST] validate() - Supported Response")

    validator, _ = create_process_sentence_validator(
        support_score=0.95,
    )

    context = create_validation_context()

    result = validator.validate(context)

    assert isinstance(result, ValidationResult)

    assert result.passed is True
    assert result.category == OutputCategory.SAFE

    assert result.validator_name == "HallucinationValidator"

    print("PASS")

def test_validate_unsupported_response() -> None:

    print("\n[TEST] validate() - Unsupported Response")

    validator, _ = create_process_sentence_validator(
        support_score=0.10,
    )

    context = create_validation_context(
        response="The moon is made of cheese."
    )

    result = validator.validate(context)

    assert result.passed is False

    assert (
        result.category
        == OutputCategory.HALLUCINATION
    )

    print("PASS")

def test_validate_tier2_response() -> None:

    print("\n[TEST] validate() - Tier2")

    validator, tier2 = (
        create_process_sentence_validator(
            support_score=0.75,
        )
    )

    context = create_validation_context()

    result = validator.validate(context)

    assert tier2.called is True

    assert result.passed is True

    assert (
        result.category
        == OutputCategory.SAFE
    )

    print("PASS")

def test_validate_invalid_context() -> None:

    print("\n[TEST] validate() - Invalid Context")

    validator, _ = create_process_sentence_validator(
        support_score=0.95,
    )

    try:
        validator.validate(None)

        assert False, (
            "Expected InvalidValidationContextError"
        )

    except InvalidValidationContextError:

        print("PASS")
######################################################
# Main
###############################################################################

def main() -> None:

    print("=" * 70)
    print("Hallucination Validator Tests")
    print("=" * 70)

    test_constructor()
    test_validate_inputs_valid()
    test_validate_inputs_empty_response()
    test_validate_inputs_empty_chunks()
    test_validate_inputs_invalid_context()
    test_create_supported_decision()
    test_create_unsupported_decision()
    test_create_tier2_decision()
    test_build_validation_result_safe()
    test_build_validation_result_hallucination()
    test_process_sentence_supported()
    test_process_sentence_unsupported()
    test_process_sentence_tier2()
    test_process_sentence_tier2_disabled()
    test_validate_supported_response()
    test_validate_unsupported_response()
    test_validate_tier2_response()
    test_validate_invalid_context()

    print("\n" + "=" * 70)
    print("ALL TESTS PASSED")
    print("=" * 70)


if __name__ == "__main__":
    main()