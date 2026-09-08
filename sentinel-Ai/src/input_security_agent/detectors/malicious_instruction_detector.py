from __future__ import annotations

from src.input_security_agent.detectors.base import BaseDetector
from src.input_security_agent.models import (
    AttackCategory,
    SecurityContext,
    ValidationResult,
)


class MaliciousInstructionDetector(BaseDetector):
    """
    Detects malicious instructions that request harmful,
    destructive, or unauthorized actions.
    """

    _PATTERNS: dict[str, str] = {
        "MALWARE": r"\b(create|write|develop|generate)\s+.*\bmalware\b",
        "RANSOMWARE": r"\bransomware\b",
        "VIRUS": r"\bcomputer\s+virus\b",
        "KEYLOGGER": r"\bkeylogger\b",
        "PHISHING": r"\bphishing\b",
        "STEAL_PASSWORDS": r"\bsteal\s+passwords?\b",
        "STEAL_CREDENTIALS": r"\bsteal\s+credentials?\b",
        "DISABLE_ANTIVIRUS": r"\bdisable\s+antivirus\b",
        "DELETE_SYSTEM_FILES": r"\bdelete\s+system\s+files\b",
        "DATA_EXFILTRATION": r"\bexfiltrate\s+data\b",
    }

    def __init__(self) -> None:
        super().__init__("MaliciousInstructionDetector")

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
            category=AttackCategory.MALICIOUS_INSTRUCTION,
            confidence=self._calculate_confidence(matches),
            reason="Malicious instruction detected.",
            matches=matches,
        )