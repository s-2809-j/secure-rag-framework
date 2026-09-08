from __future__ import annotations

from src.input_security_agent.detectors.base import BaseDetector
from src.input_security_agent.models import (
    AttackCategory,
    SecurityContext,
    ValidationResult,
)


class SystemPromptDetector(BaseDetector):
   

    _PATTERNS: dict[str, str] = {
        "SYSTEM_PROMPT": r"\bsystem\s+prompt\b",
        "HIDDEN_INSTRUCTIONS": r"\bhidden\s+instructions?\b",
        "DEVELOPER_MESSAGE": r"\bdeveloper\s+message\b",
        "DEVELOPER_INSTRUCTIONS": r"\bdeveloper\s+instructions?\b",
        "INITIAL_INSTRUCTIONS": r"\binitial\s+instructions?\b",
        "INTERNAL_PROMPT": r"\binternal\s+prompt\b",
        "REVEAL_PROMPT": r"\breveal\s+(your\s+)?(prompt|instructions?)\b",
        "SHOW_PROMPT": r"\bshow\s+(me\s+)?(your\s+)?(prompt|instructions?)\b",
        "PRINT_PROMPT": r"\bprint\s+(your\s+)?(prompt|instructions?)\b",
        "REPEAT_ABOVE": r"\brepeat\s+everything\s+above\b",
    }

    def __init__(self) -> None:
        super().__init__("SystemPromptDetector")

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
            category=AttackCategory.SYSTEM_PROMPT_LEAKAGE,
            confidence=self._calculate_confidence(matches),
            reason="Attempt to reveal system prompt detected.",
            matches=matches,
        )