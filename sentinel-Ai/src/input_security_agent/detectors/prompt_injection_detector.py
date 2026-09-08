from __future__ import annotations


from src.input_security_agent.detectors.base import BaseDetector
from src.input_security_agent.models import (
    AttackCategory,
    SecurityContext,
    ValidationResult,
)


class PromptInjectionDetector(BaseDetector):
    

    _PATTERNS: dict[str, str] = {
        "IGNORE_PREVIOUS": r"\bignore\s+(all\s+)?previous\s+instructions?\b",
        "DISREGARD_PREVIOUS": r"\bdisregard\s+(all\s+)?previous\s+instructions?\b",
        "FORGET_PREVIOUS": r"\bforget\s+(all\s+)?previous\s+instructions?\b",
        "OVERRIDE_SYSTEM": r"\boverride\s+(the\s+)?system\b",
        "BYPASS_RULES": r"\bbypass\s+(all\s+)?(rules|restrictions|filters)\b",
        "ACT_AS": r"\bact\s+as\b",
        "PRETEND_YOU_ARE": r"\bpretend\s+you\s+are\b",
    }

    def __init__(self) -> None:
        super().__init__("PromptInjectionDetector")

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
            category=AttackCategory.PROMPT_INJECTION,
            confidence=self._calculate_confidence(matches),
            reason="Prompt injection pattern(s) detected.",
            matches=matches,
        )