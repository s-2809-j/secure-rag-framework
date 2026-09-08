from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from src.knowledge_base.models import RetrievedChunk


class OutputCategory(str, Enum):
    """
    Categories of output validation findings.
    """

    SAFE = "safe"
    HALLUCINATION = "hallucination"
    PROMPT_LEAKAGE = "prompt_leakage"
    PII = "pii"
    POLICY_VIOLATION = "policy_violation"
    UNSUPPORTED_CLAIM = "unsupported_claim"


class OutputRiskLevel(str, Enum):
    """
    Overall output risk level.
    """

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass(slots=True, frozen=True)
class ValidationContext:
    """
    Context supplied to every output validator.
    """

    user_query: str

    llm_response: str

    retrieved_chunks: list[RetrievedChunk]

    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class ValidationResult:
    """
    Result produced by a single output validator.

    This object is intentionally generic so that every validator
    (Hallucination, Prompt Leakage, PII, Policy, etc.)
    returns the same contract.
    """

    # Name of the validator that produced this result.
    validator_name: str

    # Whether the validator passed.
    passed: bool

    # Category assigned by the validator.
    category: OutputCategory

    # Risk score produced by the validator.
    # Range: 0.0 (safe) → 1.0 (highest risk)
    score: float

    # Human-readable explanation.
    reason: str

    # Optional structured information used by downstream
    # policy engines, risk engines and debugging.
    details: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class PolicyEvaluation:
    """
    Result produced by the output policy engine.
    """

    allowed: bool

    should_sanitize: bool

    block_response: bool

    reason: str


@dataclass(slots=True, frozen=True)
class RiskAssessment:
    """
    Final risk assessment produced after combining
    all validator outputs.
    """

    # Overall risk score.
    overall_score: float

    # Confidence in the overall assessment.
    confidence: float

    # Assigned risk level.
    risk_level: OutputRiskLevel

    # Human-readable summary.
    summary: str

@dataclass(slots=True, frozen=True)
class ValidationDecision:
    """
    Final decision returned by the Output Validation Agent.
    """

    approved: bool

    original_response: str

    # final_response was added later in the project to support
    # sanitized outputs. Make this field optional for backward
    # compatibility with older unit tests that construct
    # ValidationDecision without specifying final_response.
    final_response: str = ""

    validation_results: list[ValidationResult] = field(default_factory=list)

    policy_evaluation: PolicyEvaluation | None = None

    risk_assessment: RiskAssessment | None = None

    request_id: str = ""