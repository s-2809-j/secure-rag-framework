from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from src.input_security_agent.exceptions import (
    InvalidValidationResultError,
)


class AttackCategory(str, Enum):
    PROMPT_INJECTION = "prompt_injection"
    JAILBREAK = "jailbreak"
    SYSTEM_PROMPT_LEAKAGE = "system_prompt_leakage"
    PII = "pii"
    MALICIOUS_INSTRUCTION = "malicious_instruction"
    BENIGN = "benign"


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass(frozen=True, slots=True)
class SecurityContext:
    """
    Input supplied for security validation.
    """

    query: str


@dataclass(frozen=True, slots=True)
class DetectionMatch:
    """
    Represents a single detector match.
    """

    matched_text: str
    pattern_name: str
    start: int | None = None
    end: int | None = None


@dataclass(frozen=True, slots=True)
class   ValidationResult:
    """
    Output produced by a detector.
    """

    detector_name: str
    category: AttackCategory
    is_flagged: bool
    confidence: float
    reason: str | None = None
    matches: list[DetectionMatch] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not 0.0 <= self.confidence <= 1.0:
            raise InvalidValidationResultError(
                f"confidence must be between 0 and 1 (got {self.confidence})"
            )

        if self.is_flagged and self.category == AttackCategory.BENIGN:
            raise InvalidValidationResultError(
                "Flagged results cannot have BENIGN category."
            )

        if (
            not self.is_flagged
            and self.category != AttackCategory.BENIGN
        ):
            raise InvalidValidationResultError(
                "Non-flagged results must have BENIGN category."
            )


@dataclass(frozen=True, slots=True)
class RiskAssessment:
    """
    Overall risk assessment.
    """

    risk_score: float
    risk_level: RiskLevel
    contributing_results: list[ValidationResult]
    explanation: str


@dataclass(frozen=True, slots=True)
class PolicyEvaluation:
    """
    Output from the policy engine.
    """

    allowed: bool
    triggered_rules: list[str]
    explanation: str


@dataclass(frozen=True, slots=True)
class AgentDecision:
    """
    Final decision returned by InputSecurityAgent.
    """

    allowed: bool
    normalized_context: str
    validation_results: list[ValidationResult]
    policy_evaluation: PolicyEvaluation
    risk_assessment: RiskAssessment