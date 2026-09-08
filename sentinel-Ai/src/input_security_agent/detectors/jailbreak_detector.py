from __future__ import annotations

from src.input_security_agent.detectors.base import BaseDetector
from src.input_security_agent.models import (
    AttackCategory,
    SecurityContext,
    ValidationResult,
)


class JailbreakDetector(BaseDetector):

    _PATTERNS: dict[str, str] = {
        "NO_RESTRICTIONS": r"\bno\s+restrictions\b",
        "NO_LIMITATIONS": r"\bno\s+limitations\b",
        "UNRESTRICTED": r"\bunrestricted\b",
        "DEVELOPER_MODE": r"\bdeveloper\s+mode\b",
        "DAN": r"\bdan\b",
        "NO_ETHICS": r"\bno\s+ethical\s+(guidelines|constraints)\b",
        "IGNORE_POLICIES": r"\bignore\s+(all\s+)?(policies|safety)\b",
        "ANSWER_ANYTHING": r"\banswer\s+anything\b",
        "YOU_ARE_FREE": r"\byou\s+are\s+free\b",
        "NO_RULES": r"\bno\s+rules\b",
    }

    def __init__(self) -> None:
        super().__init__("JailbreakDetector")

    def detect(
        self,
        context: SecurityContext,
    ) -> ValidationResult:


        matches = self._match_patterns(
            context.query,
            self._PATTERNS,
        )

        if not matches:
            return self._safe_result()

    

        return self._flagged_result(
            category=AttackCategory.JAILBREAK,
            confidence=self._calculate_confidence(matches),
            reason="Jailbreak pattern(s) detected.",
            matches=matches,
        )