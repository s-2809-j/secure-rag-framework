from __future__ import annotations

from src.input_security_agent.detectors.base import BaseDetector
from src.input_security_agent.models import (
    AttackCategory,
    SecurityContext,
    ValidationResult,
)


class PIIDetector(BaseDetector):
    """
    Detects personally identifiable information (PII)
    and common secret formats using rule-based patterns.
    """

    _PATTERNS: dict[str, str] = {
        "EMAIL":
            r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",

        "PHONE":
            r"\b(?:\+?\d{1,3}[- ]?)?\d{10}\b",

        "CREDIT_CARD":
            r"\b(?:\d{4}[- ]?){3}\d{4}\b",

        "AWS_ACCESS_KEY":
            r"\bAKIA[0-9A-Z]{16}\b",

        "GITHUB_TOKEN":
            r"\bgh[pousr]_[A-Za-z0-9]{36,255}\b",

        "JWT":
            r"\beyJ[A-Za-z0-9_-]+\.[A-Za-z0-9._-]+\.[A-Za-z0-9._-]+\b",
    }

    def __init__(self) -> None:
        super().__init__("PIIDetector")

    def detect(
        self,
        context: SecurityContext,
    ) -> ValidationResult:

        matches = self._match_patterns(
            context.query,
            self._PATTERNS,
            ignore_case=False,
        )

        if not matches:
            return self._safe_result()

        return self._flagged_result(
            category=AttackCategory.PII,
            confidence=self._calculate_confidence(matches),
            reason="Sensitive information detected.",
            matches=matches,
        )