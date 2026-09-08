from __future__ import annotations

import os

import pytest

from src.output_validation_agent.models import (
    OutputCategory,
    OutputRiskLevel,
    ValidationDecision,
)
from tests.output_validation_agent.integration_support import (
    INTEGRATION_SCENARIOS,
    build_agent,
    build_chunks,
    build_context,
)


def test_safe_response_factory_integration() -> None:
    required_environment = (
        "LLM_PROVIDER",
        "LLM_MODEL",
        "LLM_BASE_URL",
        "GITHUB_TOKEN",
    )
    missing = [
        variable
        for variable in required_environment
        if not os.getenv(variable)
    ]
    if missing:
        pytest.skip(
            "Missing environment variables: " + ", ".join(missing)
        )

    scenario = INTEGRATION_SCENARIOS["safe_response"]
    scenario_input = scenario["input"]
    expected = scenario["expected"]

    agent = build_agent()
    chunks = build_chunks(scenario_input["retrieved_texts"])
    context = build_context(
        user_query=scenario_input["user_query"],
        llm_response=scenario_input["llm_response"],
        retrieved_chunks=chunks,
        metadata={"request_id": "safe-response-factory-integration"},
    )

    decision = agent.validate(context)

    assert isinstance(decision, ValidationDecision)
    assert decision.approved is expected["approved"]
    assert decision.original_response == scenario_input["llm_response"]
    assert decision.final_response == scenario_input["llm_response"]
    assert decision.request_id == "safe-response-factory-integration"

    assert decision.policy_evaluation is not None
    assert decision.policy_evaluation.allowed is expected["policy"]["allowed"]
    assert (
        decision.policy_evaluation.should_sanitize
        is expected["policy"]["should_sanitize"]
    )
    assert (
        decision.policy_evaluation.block_response
        is expected["policy"]["block_response"]
    )

    assert decision.risk_assessment is not None
    assert decision.risk_assessment.risk_level == OutputRiskLevel.LOW
    assert decision.risk_assessment.risk_level.value == expected["risk_level"]

    assert len(decision.validation_results) == 4
    validator_names = {
        result.validator_name
        for result in decision.validation_results
    }
    assert validator_names == {
        "HallucinationValidator",
        "PromptLeakageValidator",
        "PIIValidator",
        "SafetyPolicyValidator",
    }

    categories_by_validator = {
        result.validator_name: result.category
        for result in decision.validation_results
    }
    assert categories_by_validator["HallucinationValidator"] == OutputCategory.SAFE
    assert (
        categories_by_validator["PromptLeakageValidator"]
        == OutputCategory.PROMPT_LEAKAGE
    )
    assert categories_by_validator["PIIValidator"] == OutputCategory.PII
    assert categories_by_validator["SafetyPolicyValidator"] == OutputCategory.SAFE

    for result in decision.validation_results:
        assert result.passed is True

def test_hallucination_triggers_sanitization_integration() -> None:
    """
    Verify that a hallucinated response is detected by the production
    Output Validation pipeline and sanitized before being returned.

    This integration test exercises the complete production wiring:

        OutputValidationAgentFactory
            ↓
        HallucinationValidator
            ↓
        OutputPolicyEngine
            ↓
        OutputRiskEngine
            ↓
        ResponseSanitizer
            ↓
        ValidationDecision
    """

    required_environment = (
        "LLM_PROVIDER",
        "LLM_MODEL",
        "LLM_BASE_URL",
        "GITHUB_TOKEN",
    )

    missing = [
        variable
        for variable in required_environment
        if not os.getenv(variable)
    ]

    if missing:
        pytest.skip(
            "Missing environment variables: "
            + ", ".join(missing)
        )

    scenario = INTEGRATION_SCENARIOS[
        "hallucination_detected"
    ]

    scenario_input = scenario["input"]
    expected = scenario["expected"]

    agent = build_agent()

    chunks = build_chunks(
        scenario_input["retrieved_texts"]
    )

    context = build_context(
        user_query=scenario_input["user_query"],
        llm_response=scenario_input["llm_response"],
        retrieved_chunks=chunks,
        metadata={
            "request_id":
                "hallucination-sanitization-integration"
        },
    )

    decision = agent.validate(context)

    #
    # ------------------------------------------------------------------
    # ValidationDecision
    # ------------------------------------------------------------------
    #

    assert isinstance(
        decision,
        ValidationDecision,
    )

    assert (
        decision.request_id
        == "hallucination-sanitization-integration"
    )

    assert (
        decision.original_response
        == scenario_input["llm_response"]
    )

    assert (
        decision.approved
        is expected["approved"]
    )

    #
    # ------------------------------------------------------------------
    # Policy evaluation
    # ------------------------------------------------------------------
    #

    assert (
        decision.policy_evaluation
        is not None
    )

    assert (
        decision.policy_evaluation.allowed
        is expected["policy"]["allowed"]
    )

    assert (
        decision.policy_evaluation.should_sanitize
        is expected["policy"]["should_sanitize"]
    )

    assert (
        decision.policy_evaluation.block_response
        is expected["policy"]["block_response"]
    )

    #
    # ------------------------------------------------------------------
    # Validator results
    # ------------------------------------------------------------------
    #

    assert (
        len(decision.validation_results)
        == 4
    )

    validator_names = {
        result.validator_name
        for result in decision.validation_results
    }

    assert validator_names == {
        "HallucinationValidator",
        "PromptLeakageValidator",
        "PIIValidator",
        "SafetyPolicyValidator",
    }

    hallucination_result = next(
        result
        for result in decision.validation_results
        if result.validator_name
        == "HallucinationValidator"
    )

    assert (
        hallucination_result.category
        == OutputCategory.HALLUCINATION
    )

    assert (
        hallucination_result.details
        is not None
    )

    assert (
        "sentence_decisions"
        in hallucination_result.details
    )

    #
    # ------------------------------------------------------------------
    # Sanitization
    # ------------------------------------------------------------------
    #

    assert (
        decision.final_response
        != decision.original_response
    )

    assert (
        "made of cheese"
        not in decision.final_response
    )

    #
    # ------------------------------------------------------------------
    # Risk assessment
    # ------------------------------------------------------------------
    #

    assert (
        decision.risk_assessment
        is not None
    )

    assert (
        decision.risk_assessment.overall_score
        >= 0.0
    )

    assert (
        decision.risk_assessment.confidence
        >= 0.0
    )

    assert (
        decision.risk_assessment.risk_level
        in (
            OutputRiskLevel.LOW,
            OutputRiskLevel.MEDIUM,
            OutputRiskLevel.HIGH,
            OutputRiskLevel.CRITICAL,
        )
    )

def test_prompt_leakage_blocks_response_integration() -> None:
    """
    Verify that prompt leakage is detected by the production
    Output Validation pipeline and the response is blocked.

    This integration test exercises the complete production wiring:

        OutputValidationAgentFactory
            ↓
        PromptLeakageValidator
            ↓
        OutputPolicyEngine
            ↓
        OutputRiskEngine
            ↓
        ValidationDecision
    """

    required_environment = (
        "LLM_PROVIDER",
        "LLM_MODEL",
        "LLM_BASE_URL",
        "GITHUB_TOKEN",
    )

    missing = [
        variable
        for variable in required_environment
        if not os.getenv(variable)
    ]

    if missing:
        pytest.skip(
            "Missing environment variables: "
            + ", ".join(missing)
        )

    scenario = INTEGRATION_SCENARIOS[
        "prompt_leakage_detected"
    ]

    scenario_input = scenario["input"]
    expected = scenario["expected"]

    agent = build_agent()

    chunks = build_chunks(
        scenario_input["retrieved_texts"]
    )

    context = build_context(
        user_query=scenario_input["user_query"],
        llm_response=scenario_input["llm_response"],
        retrieved_chunks=chunks,
        metadata={
            "request_id":
                "prompt-leakage-blocking-integration"
        },
    )

    decision = agent.validate(context)

    #
    # ------------------------------------------------------------------
    # ValidationDecision
    # ------------------------------------------------------------------
    #

    assert isinstance(
        decision,
        ValidationDecision,
    )

    assert (
        decision.request_id
        == "prompt-leakage-blocking-integration"
    )

    assert (
        decision.original_response
        == scenario_input["llm_response"]
    )

    assert (
        decision.approved
        is expected["approved"]
    )

    #
    # ------------------------------------------------------------------
    # Policy evaluation
    # ------------------------------------------------------------------
    #

    assert decision.policy_evaluation is not None

    assert (
        decision.policy_evaluation.allowed
        is expected["policy"]["allowed"]
    )

    assert (
        decision.policy_evaluation.should_sanitize
        is expected["policy"]["should_sanitize"]
    )

    assert (
        decision.policy_evaluation.block_response
        is expected["policy"]["block_response"]
    )

    #
    # ------------------------------------------------------------------
    # Validator results
    # ------------------------------------------------------------------
    #

    assert (
        len(decision.validation_results)
        == 4
    )

    validator_names = {
        result.validator_name
        for result in decision.validation_results
    }

    assert validator_names == {
        "HallucinationValidator",
        "PromptLeakageValidator",
        "PIIValidator",
        "SafetyPolicyValidator",
    }

    prompt_result = next(
        result
        for result in decision.validation_results
        if result.validator_name
        == "PromptLeakageValidator"
    )

    assert (
        prompt_result.category
        == OutputCategory.PROMPT_LEAKAGE
    )

    assert prompt_result.passed is False

    assert (
        prompt_result.details["match_count"]
        > 0
    )

    assert (
        len(prompt_result.details["matches"])
        == prompt_result.details["match_count"]
    )

    #
    # ------------------------------------------------------------------
    # Blocking behaviour
    # ------------------------------------------------------------------
    #

    assert (
        decision.final_response
        == decision.original_response
    )

    #
    # ------------------------------------------------------------------
    # Risk assessment
    # ------------------------------------------------------------------
    #

    assert (
        decision.risk_assessment
        is not None
    )

    assert (
        decision.risk_assessment.overall_score
        >= 0.0
    )

    assert (
        decision.risk_assessment.confidence
        >= 0.0
    )

    assert (
        decision.risk_assessment.risk_level
        in (
            OutputRiskLevel.LOW,
            OutputRiskLevel.MEDIUM,
            OutputRiskLevel.HIGH,
            OutputRiskLevel.CRITICAL,
        )
    )

def test_pii_blocks_response_integration() -> None:
    """
    Verify that PII is detected by the production Output Validation
    pipeline and the response is blocked.

    This integration test exercises the complete production wiring:

        OutputValidationAgentFactory
            ↓
        PIIValidator
            ↓
        OutputPolicyEngine
            ↓
        OutputRiskEngine
            ↓
        ValidationDecision
    """

    required_environment = (
        "LLM_PROVIDER",
        "LLM_MODEL",
        "LLM_BASE_URL",
        "GITHUB_TOKEN",
    )

    missing = [
        variable
        for variable in required_environment
        if not os.getenv(variable)
    ]

    if missing:
        pytest.skip(
            "Missing environment variables: "
            + ", ".join(missing)
        )

    scenario = INTEGRATION_SCENARIOS[
        "pii_detected"
    ]

    scenario_input = scenario["input"]
    expected = scenario["expected"]

    agent = build_agent()

    chunks = build_chunks(
        scenario_input["retrieved_texts"]
    )

    context = build_context(
        user_query=scenario_input["user_query"],
        llm_response=scenario_input["llm_response"],
        retrieved_chunks=chunks,
        metadata={
            "request_id":
                "pii-blocking-integration"
        },
    )

    decision = agent.validate(context)

    #
    # ---------------------------------------------------------------
    # ValidationDecision
    # ---------------------------------------------------------------
    #

    assert isinstance(
        decision,
        ValidationDecision,
    )

    assert (
        decision.request_id
        == "pii-blocking-integration"
    )

    assert (
        decision.original_response
        == scenario_input["llm_response"]
    )

    assert (
        decision.approved
        is expected["approved"]
    )

    #
    # ---------------------------------------------------------------
    # Policy Evaluation
    # ---------------------------------------------------------------
    #

    assert decision.policy_evaluation is not None

    assert (
        decision.policy_evaluation.allowed
        is expected["policy"]["allowed"]
    )

    assert (
        decision.policy_evaluation.should_sanitize
        is expected["policy"]["should_sanitize"]
    )

    assert (
        decision.policy_evaluation.block_response
        is expected["policy"]["block_response"]
    )

    #
    # ---------------------------------------------------------------
    # Validator Results
    # ---------------------------------------------------------------
    #

    assert len(decision.validation_results) == 4

    validator_names = {
        result.validator_name
        for result in decision.validation_results
    }

    assert validator_names == {
        "HallucinationValidator",
        "PromptLeakageValidator",
        "PIIValidator",
        "SafetyPolicyValidator",
    }

    pii_result = next(
        result
        for result in decision.validation_results
        if result.validator_name
        == "PIIValidator"
    )

    assert (
        pii_result.category
        == OutputCategory.PII
    )

    assert pii_result.passed is False

    assert pii_result.details is not None

    #
    # ---------------------------------------------------------------
    # Blocking Behaviour
    # ---------------------------------------------------------------
    #

    assert (
        decision.final_response
        == decision.original_response
    )

    #
    # ---------------------------------------------------------------
    # Risk Assessment
    # ---------------------------------------------------------------
    #

    assert (
        decision.risk_assessment
        is not None
    )

    assert (
        decision.risk_assessment.overall_score
        >= 0.0
    )

    assert (
        decision.risk_assessment.confidence
        >= 0.0
    )

    assert (
        decision.risk_assessment.risk_level
        in (
            OutputRiskLevel.LOW,
            OutputRiskLevel.MEDIUM,
            OutputRiskLevel.HIGH,
            OutputRiskLevel.CRITICAL,
        )
    )

def test_safety_policy_blocks_response_integration() -> None:
    """
    Verify that the production Safety Policy Validator detects
    unsafe content and blocks the response.

    This integration test exercises:

        OutputValidationAgentFactory
            ↓
        SafetyPolicyValidator
            ↓
        OutputPolicyEngine
            ↓
        OutputRiskEngine
            ↓
        ValidationDecision
    """

    required_environment = (
        "LLM_PROVIDER",
        "LLM_MODEL",
        "LLM_BASE_URL",
        "GITHUB_TOKEN",
    )

    missing = [
        variable
        for variable in required_environment
        if not os.getenv(variable)
    ]

    if missing:
        pytest.skip(
            "Missing environment variables: "
            + ", ".join(missing)
        )

    scenario = INTEGRATION_SCENARIOS[
        "safety_policy_violation"
    ]

    scenario_input = scenario["input"]
    expected = scenario["expected"]

    agent = build_agent()

    chunks = build_chunks(
        scenario_input["retrieved_texts"]
    )

    context = build_context(
        user_query=scenario_input["user_query"],
        llm_response=scenario_input["llm_response"],
        retrieved_chunks=chunks,
        metadata={
            "request_id":
                "safety-policy-blocking-integration"
        },
    )

    decision = agent.validate(context)

    #
    # ---------------------------------------------------------------
    # ValidationDecision
    # ---------------------------------------------------------------
    #

    assert isinstance(
        decision,
        ValidationDecision,
    )

    assert (
        decision.request_id
        == "safety-policy-blocking-integration"
    )

    assert (
        decision.original_response
        == scenario_input["llm_response"]
    )

    assert (
        decision.approved
        is expected["approved"]
    )

    #
    # ---------------------------------------------------------------
    # Policy Evaluation
    # ---------------------------------------------------------------
    #

    assert decision.policy_evaluation is not None

    assert (
        decision.policy_evaluation.allowed
        is expected["policy"]["allowed"]
    )

    assert (
        decision.policy_evaluation.should_sanitize
        is expected["policy"]["should_sanitize"]
    )

    assert (
        decision.policy_evaluation.block_response
        is expected["policy"]["block_response"]
    )

    #
    # ---------------------------------------------------------------
    # Validator Results
    # ---------------------------------------------------------------
    #

    assert len(decision.validation_results) == 4

    validator_names = {
        result.validator_name
        for result in decision.validation_results
    }

    assert validator_names == {
        "HallucinationValidator",
        "PromptLeakageValidator",
        "PIIValidator",
        "SafetyPolicyValidator",
    }

    safety_result = next(
        result
        for result in decision.validation_results
        if result.validator_name
        == "SafetyPolicyValidator"
    )

    assert (
        safety_result.category
        == OutputCategory.POLICY_VIOLATION
    )

    assert safety_result.passed is False

    assert safety_result.details is not None

    #
    # ---------------------------------------------------------------
    # Blocking Behaviour
    # ---------------------------------------------------------------
    #

    assert (
        decision.final_response
        == decision.original_response
    )

    #
    # ---------------------------------------------------------------
    # Risk Assessment
    # ---------------------------------------------------------------
    #

    assert (
        decision.risk_assessment
        is not None
    )

    assert (
        decision.risk_assessment.overall_score
        >= 0.0
    )

    assert (
        decision.risk_assessment.confidence
        >= 0.0
    )

    assert (
        decision.risk_assessment.risk_level
        in (
            OutputRiskLevel.LOW,
            OutputRiskLevel.MEDIUM,
            OutputRiskLevel.HIGH,
            OutputRiskLevel.CRITICAL,
        )
    )

def test_multiple_validators_triggered_integration() -> None:
    """
    Verify that when multiple validators are triggered simultaneously,
    the policy engine correctly applies precedence:
    BLOCK > SANITIZE > ALLOW.

    Scenario: hallucination + prompt_leakage
    Expected: BLOCK takes precedence (prompt_leakage is BLOCK category)
    Response is NOT approved and NOT sanitized (blocked).

    This integration test exercises:

        OutputValidationAgentFactory
            ↓
        HallucinationValidator + PromptLeakageValidator
            ↓
        OutputPolicyEngine (precedence logic)
            ↓
        OutputRiskEngine
            ↓
        ValidationDecision
    """

    required_environment = (
        "LLM_PROVIDER",
        "LLM_MODEL",
        "LLM_BASE_URL",
        "GITHUB_TOKEN",
    )

    missing = [
        variable
        for variable in required_environment
        if not os.getenv(variable)
    ]

    if missing:
        pytest.skip(
            "Missing environment variables: "
            + ", ".join(missing)
        )

    scenario = INTEGRATION_SCENARIOS[
        "multiple_validators_triggered"
    ]

    scenario_input = scenario["input"]
    expected = scenario["expected"]

    agent = build_agent()

    chunks = build_chunks(
        scenario_input["retrieved_texts"]
    )

    context = build_context(
        user_query=scenario_input["user_query"],
        llm_response=scenario_input["llm_response"],
        retrieved_chunks=chunks,
        metadata={
            "request_id":
                "multiple-validators-integration"
        },
    )

    decision = agent.validate(context)

    #
    # ------------------------------------------------------------------
    # ValidationDecision
    # ------------------------------------------------------------------
    #

    assert isinstance(
        decision,
        ValidationDecision,
    )

    assert (
        decision.request_id
        == "multiple-validators-integration"
    )

    assert (
        decision.original_response
        == scenario_input["llm_response"]
    )

    # BLOCK precedence: approved must be False
    assert (
        decision.approved
        is expected["approved"]
    )

    #
    # ------------------------------------------------------------------
    # Policy evaluation: BLOCK takes precedence
    # ------------------------------------------------------------------
    #

    assert decision.policy_evaluation is not None

    assert (
        decision.policy_evaluation.allowed
        is expected["policy"]["allowed"]
    )

    # No sanitization when blocked
    assert (
        decision.policy_evaluation.should_sanitize
        is expected["policy"]["should_sanitize"]
    )

    assert (
        decision.policy_evaluation.block_response
        is expected["policy"]["block_response"]
    )

    #
    # ------------------------------------------------------------------
    # Validator results: both validators triggered
    # ------------------------------------------------------------------
    #

    assert len(decision.validation_results) == 4

    validator_names = {
        result.validator_name
        for result in decision.validation_results
    }

    assert validator_names == {
        "HallucinationValidator",
        "PromptLeakageValidator",
        "PIIValidator",
        "SafetyPolicyValidator",
    }

    # Hallucination fails (SANITIZE)
    hallucination_result = next(
        result
        for result in decision.validation_results
        if result.validator_name
        == "HallucinationValidator"
    )

    assert (
        hallucination_result.category
        == OutputCategory.HALLUCINATION
    )

    assert hallucination_result.passed is False

    # Prompt leakage fails (BLOCK)
    prompt_result = next(
        result
        for result in decision.validation_results
        if result.validator_name
        == "PromptLeakageValidator"
    )

    assert (
        prompt_result.category
        == OutputCategory.PROMPT_LEAKAGE
    )

    assert prompt_result.passed is False

    #
    # ------------------------------------------------------------------
    # Blocking behavior: BLOCK precedence wins
    # ------------------------------------------------------------------
    #

    # Response unchanged because blocked, not sanitized
    assert (
        decision.final_response
        == decision.original_response
    )

    #
    # ------------------------------------------------------------------
    # Risk assessment
    # ------------------------------------------------------------------
    #

    assert decision.risk_assessment is not None

    assert (
        decision.risk_assessment.overall_score >= 0.0
    )

    assert (
        decision.risk_assessment.confidence >= 0.0
    )

    assert (
        decision.risk_assessment.risk_level
        in (
            OutputRiskLevel.LOW,
            OutputRiskLevel.MEDIUM,
            OutputRiskLevel.HIGH,
            OutputRiskLevel.CRITICAL,
        )
    )


def test_mixed_severity_findings_integration() -> None:
    """
    Verify that mixed-severity findings (hallucination + PII)
    result in BLOCK precedence.

    Scenario: hallucination (SANITIZE) + PII (BLOCK)
    Expected: BLOCK takes precedence, response is blocked

    This integration test exercises:

        OutputValidationAgentFactory
            ↓
        HallucinationValidator + PIIValidator
            ↓
        OutputPolicyEngine (precedence: BLOCK > SANITIZE)
            ↓
        OutputRiskEngine
            ↓
        ValidationDecision
    """

    required_environment = (
        "LLM_PROVIDER",
        "LLM_MODEL",
        "LLM_BASE_URL",
        "GITHUB_TOKEN",
    )

    missing = [
        variable
        for variable in required_environment
        if not os.getenv(variable)
    ]

    if missing:
        pytest.skip(
            "Missing environment variables: "
            + ", ".join(missing)
        )

    scenario = INTEGRATION_SCENARIOS[
        "mixed_severity_findings"
    ]

    scenario_input = scenario["input"]
    expected = scenario["expected"]

    agent = build_agent()

    chunks = build_chunks(
        scenario_input["retrieved_texts"]
    )

    context = build_context(
        user_query=scenario_input["user_query"],
        llm_response=scenario_input["llm_response"],
        retrieved_chunks=chunks,
        metadata={
            "request_id":
                "mixed-severity-integration"
        },
    )

    decision = agent.validate(context)

    #
    # ------------------------------------------------------------------
    # ValidationDecision
    # ------------------------------------------------------------------
    #

    assert isinstance(
        decision,
        ValidationDecision,
    )

    assert (
        decision.request_id
        == "mixed-severity-integration"
    )

    assert (
        decision.original_response
        == scenario_input["llm_response"]
    )

    # BLOCK precedence: approved must be False
    assert (
        decision.approved
        is expected["approved"]
    )

    #
    # ------------------------------------------------------------------
    # Policy evaluation: BLOCK overrides SANITIZE
    # ------------------------------------------------------------------
    #

    assert decision.policy_evaluation is not None

    assert (
        decision.policy_evaluation.allowed
        is expected["policy"]["allowed"]
    )

    # No sanitization when blocked
    assert (
        decision.policy_evaluation.should_sanitize
        is expected["policy"]["should_sanitize"]
    )

    assert (
        decision.policy_evaluation.block_response
        is expected["policy"]["block_response"]
    )

    #
    # ------------------------------------------------------------------
    # Validator results: hallucination + PII both failed
    # ------------------------------------------------------------------
    #

    assert len(decision.validation_results) == 4

    validator_names = {
        result.validator_name
        for result in decision.validation_results
    }

    assert validator_names == {
        "HallucinationValidator",
        "PromptLeakageValidator",
        "PIIValidator",
        "SafetyPolicyValidator",
    }

    # Hallucination fails (SANITIZE)
    hallucination_result = next(
        result
        for result in decision.validation_results
        if result.validator_name
        == "HallucinationValidator"
    )

    assert (
        hallucination_result.category
        == OutputCategory.HALLUCINATION
    )

    assert hallucination_result.passed is False

    # PII fails (BLOCK)
    pii_result = next(
        result
        for result in decision.validation_results
        if result.validator_name
        == "PIIValidator"
    )

    assert (
        pii_result.category
        == OutputCategory.PII
    )

    assert pii_result.passed is False

    #
    # ------------------------------------------------------------------
    # Blocking behavior: BLOCK > SANITIZE
    # ------------------------------------------------------------------
    #

    # Response unchanged because blocked, not sanitized
    assert (
        decision.final_response
        == decision.original_response
    )

    #
    # ------------------------------------------------------------------
    # Risk assessment
    # ------------------------------------------------------------------
    #

    assert decision.risk_assessment is not None

    assert (
        decision.risk_assessment.overall_score >= 0.0
    )

    assert (
        decision.risk_assessment.confidence >= 0.0
    )

    assert (
        decision.risk_assessment.risk_level
        in (
            OutputRiskLevel.LOW,
            OutputRiskLevel.MEDIUM,
            OutputRiskLevel.HIGH,
            OutputRiskLevel.CRITICAL,
        )
    )


def test_sanitization_required_integration() -> None:
    """
    Verify that multi-sentence responses with mixed
    supported/unsupported content are sanitized correctly,
    retaining only the supported sentences.

    Scenario: "Paris is the capital of France. The moon is made of cheese."
    Retrieved: Paris facts only (moon is absent)
    Expected: First sentence supported, second unsupported.
              Sanitization removes the unsupported sentence.
              approved=True, should_sanitize=True, final_response differs

    This integration test exercises:

        OutputValidationAgentFactory
            ↓
        HallucinationValidator (multi-sentence scoring)
            ↓
        OutputPolicyEngine (SANITIZE decision)
            ↓
        OutputRiskEngine
            ↓
        ResponseSanitizer (remove unsupported claims)
            ↓
        ValidationDecision
    """

    required_environment = (
        "LLM_PROVIDER",
        "LLM_MODEL",
        "LLM_BASE_URL",
        "GITHUB_TOKEN",
    )

    missing = [
        variable
        for variable in required_environment
        if not os.getenv(variable)
    ]

    if missing:
        pytest.skip(
            "Missing environment variables: "
            + ", ".join(missing)
        )

    scenario = INTEGRATION_SCENARIOS[
        "sanitization_required"
    ]

    scenario_input = scenario["input"]
    expected = scenario["expected"]

    agent = build_agent()

    chunks = build_chunks(
        scenario_input["retrieved_texts"]
    )

    context = build_context(
        user_query=scenario_input["user_query"],
        llm_response=scenario_input["llm_response"],
        retrieved_chunks=chunks,
        metadata={
            "request_id":
                "sanitization-required-integration"
        },
    )

    decision = agent.validate(context)

    #
    # ------------------------------------------------------------------
    # ValidationDecision
    # ------------------------------------------------------------------
    #

    assert isinstance(
        decision,
        ValidationDecision,
    )

    assert (
        decision.request_id
        == "sanitization-required-integration"
    )

    assert (
        decision.original_response
        == scenario_input["llm_response"]
    )

    # Approved after sanitization
    assert (
        decision.approved
        is expected["approved"]
    )

    #
    # ------------------------------------------------------------------
    # Policy evaluation: sanitization required
    # ------------------------------------------------------------------
    #

    assert decision.policy_evaluation is not None

    assert (
        decision.policy_evaluation.allowed
        is expected["policy"]["allowed"]
    )

    # Sanitization is required
    assert (
        decision.policy_evaluation.should_sanitize
        is expected["policy"]["should_sanitize"]
    )

    # Not blocked
    assert (
        decision.policy_evaluation.block_response
        is expected["policy"]["block_response"]
    )

    #
    # ------------------------------------------------------------------
    # Validator results: hallucination detected on part of response
    # ------------------------------------------------------------------
    #

    assert len(decision.validation_results) == 4

    validator_names = {
        result.validator_name
        for result in decision.validation_results
    }

    assert validator_names == {
        "HallucinationValidator",
        "PromptLeakageValidator",
        "PIIValidator",
        "SafetyPolicyValidator",
    }

    hallucination_result = next(
        result
        for result in decision.validation_results
        if result.validator_name
        == "HallucinationValidator"
    )

    assert (
        hallucination_result.category
        == OutputCategory.HALLUCINATION
    )

    # Hallucination detected (one sentence unsupported)
    assert hallucination_result.passed is False

    assert (
        "sentence_decisions"
        in hallucination_result.details
    )

    #
    # ------------------------------------------------------------------
    # Sanitization: unsupported sentences removed
    # ------------------------------------------------------------------
    #

    # Final response differs from original (sanitized)
    assert (
        decision.final_response
        != decision.original_response
    )

    # Unsupported claim removed
    assert (
        "made of cheese"
        not in decision.final_response
    )

    # Supported claim retained
    assert (
        "Paris"
        in decision.final_response
        or
        "capital"
        in decision.final_response
    )

    #
    # ------------------------------------------------------------------
    # Risk assessment
    # ------------------------------------------------------------------
    #

    assert decision.risk_assessment is not None

    assert (
        decision.risk_assessment.overall_score >= 0.0
    )

    assert (
        decision.risk_assessment.confidence >= 0.0
    )

    assert (
        decision.risk_assessment.risk_level
        in (
            OutputRiskLevel.LOW,
            OutputRiskLevel.MEDIUM,
            OutputRiskLevel.HIGH,
            OutputRiskLevel.CRITICAL,
        )
    )


def test_tier2_escalation_integration() -> None:
    """
    Verify that Tier-2 escalation is triggered when Tier-1
    heuristics produce a confidence score in the "escalation zone"
    (between low_confidence_threshold and high_confidence_threshold).

    Scenario: partial support (neither clearly supported nor hallucinated)
    Expected: Tier-2 judge is invoked (used_tier2=True)

    This integration test exercises:

        OutputValidationAgentFactory
            ↓
        HallucinationValidator (with escalation policy)
            ↓
        Tier2Judge (LLM-based re-evaluation)
            ↓
        OutputPolicyEngine
            ↓
        OutputRiskEngine
            ↓
        ValidationDecision
    """

    required_environment = (
        "LLM_PROVIDER",
        "LLM_MODEL",
        "LLM_BASE_URL",
        "GITHUB_TOKEN",
    )

    missing = [
        variable
        for variable in required_environment
        if not os.getenv(variable)
    ]

    if missing:
        pytest.skip(
            "Missing environment variables: "
            + ", ".join(missing)
        )

    scenario = INTEGRATION_SCENARIOS[
        "tier2_escalation"
    ]

    scenario_input = scenario["input"]
    expected = scenario["expected"]

    agent = build_agent()

    chunks = build_chunks(
        scenario_input["retrieved_texts"]
    )

    context = build_context(
        user_query=scenario_input["user_query"],
        llm_response=scenario_input["llm_response"],
        retrieved_chunks=chunks,
        metadata={
            "request_id":
                "tier2-escalation-integration"
        },
    )

    decision = agent.validate(context)

    #
    # ------------------------------------------------------------------
    # ValidationDecision
    # ------------------------------------------------------------------
    #

    assert isinstance(
        decision,
        ValidationDecision,
    )

    assert (
        decision.request_id
        == "tier2-escalation-integration"
    )

    assert (
        decision.original_response
        == scenario_input["llm_response"]
    )

    #
    # ------------------------------------------------------------------
    # Validator results: Tier-2 was used
    # ------------------------------------------------------------------
    #

    assert len(decision.validation_results) == 4

    validator_names = {
        result.validator_name
        for result in decision.validation_results
    }

    assert validator_names == {
        "HallucinationValidator",
        "PromptLeakageValidator",
        "PIIValidator",
        "SafetyPolicyValidator",
    }

    hallucination_result = next(
        result
        for result in decision.validation_results
        if result.validator_name
        == "HallucinationValidator"
    )

    assert (
        hallucination_result.category
        == OutputCategory.HALLUCINATION
        or
        hallucination_result.category
        == OutputCategory.UNSUPPORTED_CLAIM
    )

    assert (
        "sentence_decisions"
        in hallucination_result.details
    )

    sentence_decisions = hallucination_result.details[
        "sentence_decisions"
    ]

    # At least one sentence should have used Tier-2
    tier2_used = any(
        decision.used_tier2
        for decision in sentence_decisions
        if hasattr(decision, "used_tier2")
    )

    assert (
        tier2_used
        is expected["tier2_expected"]
    )

    #
    # ------------------------------------------------------------------
    # Risk assessment
    # ------------------------------------------------------------------
    #

    assert decision.risk_assessment is not None

    assert (
        decision.risk_assessment.overall_score >= 0.0
    )

    assert (
        decision.risk_assessment.confidence >= 0.0
    )

    assert (
        decision.risk_assessment.risk_level
        in (
            OutputRiskLevel.LOW,
            OutputRiskLevel.MEDIUM,
            OutputRiskLevel.HIGH,
            OutputRiskLevel.CRITICAL,
        )
    )


def test_tier2_disabled_integration() -> None:
    """
    Verify that when Tier-2 escalation is disabled in the
    HallucinationConfig, the validator falls back to Tier-1
    decisions only (used_tier2=False for all sentences).

    Scenario: partial support with tier2 disabled
    Expected: Tier-1 decision only, no Tier-2 invocation

    LIMITATION: The standard factory has enable_tier2=True hardcoded.
    This test documents the expected behavior when tier2_expected=False,
    but since the factory cannot be configured via the integration test
    setup, the test is skipped to prevent false negatives.

    To properly test tier2_disabled:
    1. Modify OutputValidationAgentFactory to accept a HallucinationConfig
    2. Or create a separate fixture/builder with enable_tier2=False
    3. Or mock the HallucinationConfig inside build_agent()
    """

    required_environment = (
        "LLM_PROVIDER",
        "LLM_MODEL",
        "LLM_BASE_URL",
        "GITHUB_TOKEN",
    )

    missing = [
        variable
        for variable in required_environment
        if not os.getenv(variable)
    ]

    if missing:
        pytest.skip(
            "Missing environment variables: "
            + ", ".join(missing)
        )

    scenario = INTEGRATION_SCENARIOS[
        "tier2_disabled"
    ]

    scenario_input = scenario["input"]
    expected = scenario["expected"]

    # SKIP: Standard factory has enable_tier2=True hardcoded.
    # This test cannot verify the disabled path without
    # factory modifications. Document the expected behavior only.
    pytest.skip(
        "tier2_disabled test requires factory modification "
        "to accept HallucinationConfig parameter. "
        "Expected behavior: all used_tier2 flags should be False. "
        "See docstring for implementation path."
    )