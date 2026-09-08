from __future__ import annotations

from src.output_validation_agent.models import (
    OutputCategory,
    ValidationContext,
)
from src.output_validation_agent.validators.prompt_leakage_validator import (
    PromptLeakageValidator,
)


def create_context(response: str) -> ValidationContext:
    """
    Create a minimal ValidationContext for validator testing.
    """

    return ValidationContext(
        user_query="Test query",
        retrieved_chunks=[],
        llm_response=response,
    )


def test_constructor() -> None:
    validator = PromptLeakageValidator()

    assert validator is not None
    assert validator.name == "PromptLeakageValidator"


def test_empty_response() -> None:
    validator = PromptLeakageValidator()

    result = validator.validate(create_context(""))

    assert result.passed is True
    assert result.category == OutputCategory.PROMPT_LEAKAGE
    assert result.score == 0.0
    assert result.details["match_count"] == 0


def test_benign_response() -> None:
    validator = PromptLeakageValidator()

    result = validator.validate(
        create_context(
            "Paris is the capital of France."
        )
    )

    assert result.passed is True
    assert result.category == OutputCategory.PROMPT_LEAKAGE
    assert result.score == 0.0
    assert result.details["match_count"] == 0


def test_system_prompt_detection() -> None:
    validator = PromptLeakageValidator()

    result = validator.validate(
        create_context(
            "Here is the system prompt used by the assistant."
        )
    )

    assert result.passed is False
    assert result.category == OutputCategory.PROMPT_LEAKAGE
    assert result.score > 0
    assert result.details["match_count"] >= 1


def test_developer_instruction_detection() -> None:
    validator = PromptLeakageValidator()

    result = validator.validate(
        create_context(
            "The developer instruction says never reveal secrets."
        )
    )

    assert result.passed is False
    assert result.category == OutputCategory.PROMPT_LEAKAGE
    assert result.details["match_count"] >= 1


def test_chain_of_thought_detection() -> None:
    validator = PromptLeakageValidator()

    result = validator.validate(
        create_context(
            "Here is my chain of thought before answering."
        )
    )

    assert result.passed is False
    assert result.category == OutputCategory.PROMPT_LEAKAGE
    assert result.details["match_count"] >= 1


def test_tool_trace_detection() -> None:
    validator = PromptLeakageValidator()

    result = validator.validate(
        create_context(
            "tool_call completed successfully."
        )
    )

    assert result.passed is False
    assert result.category == OutputCategory.PROMPT_LEAKAGE
    assert result.details["match_count"] >= 1


def test_hidden_prompt_detection() -> None:
    validator = PromptLeakageValidator()

    result = validator.validate(
        create_context(
            "This is a hidden prompt. Do not reveal it."
        )
    )

    assert result.passed is False
    assert result.category == OutputCategory.PROMPT_LEAKAGE
    assert result.details["match_count"] >= 1


def test_multiple_matches() -> None:
    validator = PromptLeakageValidator()

    result = validator.validate(
        create_context(
            (
                "The system prompt contains a developer instruction. "
                "Here is the chain of thought."
            )
        )
    )

    assert result.passed is False
    assert result.score == 1.0
    assert result.details["match_count"] >= 3


def test_details_structure() -> None:
    validator = PromptLeakageValidator()

    result = validator.validate(
        create_context(
            "system prompt"
        )
    )

    assert "match_count" in result.details
    assert "matches" in result.details

    match = result.details["matches"][0]

    assert "rule" in match
    assert "type" in match
    assert "matched_text" in match
    assert "start" in match
    assert "end" in match
    assert "description" in match