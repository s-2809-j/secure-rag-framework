from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class SafetyDecision(str, Enum):
    """
    Decision returned by the Tier-2 Safety Judge.
    """

    SAFE = "SAFE"
    SANITIZE = "SANITIZE"
    BLOCK = "BLOCK"


@dataclass(frozen=True)
class SafetyEvaluation:
    """
    Structured result returned after Tier-2 safety evaluation.
    """

    decision: SafetyDecision

    confidence: float

    reason: str

    triggered_rules: list[str]


__all__ = [
    "SafetyDecision",
    "SafetyEvaluation",
]