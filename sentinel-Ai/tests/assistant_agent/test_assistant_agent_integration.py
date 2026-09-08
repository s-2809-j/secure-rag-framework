"""
Integration tests for AssistantAgent.
"""

from __future__ import annotations

from src.input_security_agent.models import (
    AgentDecision,
    AttackCategory,
    PolicyEvaluation as InputPolicyEvaluation,
    RiskAssessment as InputRiskAssessment,
    RiskLevel,
    ValidationResult as InputValidationResult,
)

from src.output_validation_agent.models import (
    OutputCategory,
    OutputRiskLevel,
    PolicyEvaluation as OutputPolicyEvaluation,
    RiskAssessment as OutputRiskAssessment,
    ValidationDecision,
)

from tests.assistant_agent.integration_support import (
    build_agent,
    build_chunk,
)


# ============================================================
# Helper Builders
# ============================================================


def build_security_decision() -> AgentDecision:

    detector_result = InputValidationResult(
        detector_name="PromptInjectionDetector",
        category=AttackCategory.BENIGN,
        is_flagged=False,
        confidence=0.99,
        reason="Safe query.",
    )

    policy = InputPolicyEvaluation(
        allowed=True,
        triggered_rules=[],
        explanation="Allowed.",
    )

    risk = InputRiskAssessment(
        risk_score=0.01,
        risk_level=RiskLevel.LOW,
        contributing_results=[
            detector_result,
        ],
        explanation="Low risk.",
    )

    return AgentDecision(
        allowed=True,
        normalized_context="What is the password policy?",
        validation_results=[
            detector_result,
        ],
        policy_evaluation=policy,
        risk_assessment=risk,
    )


def build_output_decision() -> ValidationDecision:

    policy = OutputPolicyEvaluation(
        allowed=True,
        should_sanitize=False,
        block_response=False,
        reason="Safe.",
    )

    risk = OutputRiskAssessment(
        overall_score=0.01,
        confidence=0.99,
        risk_level=OutputRiskLevel.LOW,
        summary="Safe.",
    )

    return ValidationDecision(
        approved=True,
        original_response=(
            "Passwords must contain at least 12 characters."
        ),
        final_response=(
            "Passwords must contain at least 12 characters."
        ),
        validation_results=[],
        policy_evaluation=policy,
        risk_assessment=risk,
        request_id="integration-test",
    )


# ============================================================
# Happy Path
# ============================================================


def test_safe_query_integration() -> None:

    agent = build_agent(
        security_decision=build_security_decision(),
        retrieved_chunks=[
            build_chunk(
                "Passwords must contain at least 12 characters."
            ),
        ],
        llm_response=(
            "Passwords must contain at least 12 characters."
        ),
        output_validation_decision=build_output_decision(),
    )

    response = agent.generate_response(
        "What is the password policy?"
    )

    assert (
        response
        == "Passwords must contain at least 12 characters."
    )


# ============================================================
# Empty Retrieval
# ============================================================


def test_empty_retrieval_returns_default_message() -> None:

    agent = build_agent(
        security_decision=build_security_decision(),
        retrieved_chunks=[],
        llm_response="",
        output_validation_decision=build_output_decision(),
    )

    response = agent.generate_response(
        "Unknown question"
    )

    assert response == (
        "I couldn't find any relevant information "
        "in the knowledge base to answer your question."
    )


# ============================================================
# Sanitized Response
# ============================================================


def test_output_validation_returns_sanitized_response() -> None:

    decision = build_output_decision()

    decision = ValidationDecision(
        approved=True,
        original_response="Unsafe response",
        final_response="Sanitized response",
        validation_results=decision.validation_results,
        policy_evaluation=decision.policy_evaluation,
        risk_assessment=decision.risk_assessment,
        request_id="integration-test",
    )

    agent = build_agent(
        security_decision=build_security_decision(),
        retrieved_chunks=[
            build_chunk(
                "Some secure content."
            ),
        ],
        llm_response="Unsafe response",
        output_validation_decision=decision,
    )

    response = agent.generate_response(
        "Question"
    )

    assert response == "Sanitized response"


# ============================================================
# Blocked Response
# ============================================================


def test_output_validation_returns_blocked_response() -> None:

    decision = build_output_decision()

    decision = ValidationDecision(
        approved=False,
        original_response="Unsafe",
        final_response="Response blocked.",
        validation_results=decision.validation_results,
        policy_evaluation=decision.policy_evaluation,
        risk_assessment=decision.risk_assessment,
        request_id="integration-test",
    )

    agent = build_agent(
        security_decision=build_security_decision(),
        retrieved_chunks=[
            build_chunk(
                "Secure content."
            ),
        ],
        llm_response="Unsafe",
        output_validation_decision=decision,
    )

    response = agent.generate_response(
        "Question"
    )

    assert response == "Response blocked."