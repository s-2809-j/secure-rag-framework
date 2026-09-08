from __future__ import annotations

from abc import ABC,abstractmethod
import re
from src.input_security_agent.models import(
    AttackCategory,
    DetectionMatch,
    SecurityContext,
    ValidationResult


)

class BaseDetector(ABC):


    def __init__(self,detector_name: str) -> None:

        self._detector_name = detector_name

    @property
    def detector_name(self) ->  str:
        return self._detector_name
    
    @abstractmethod
    def detect(self,
               context: SecurityContext,
               )-> ValidationResult:
        raise NotImplementedError
    
    def _safe_result(
            self,
            confidence: float = 0.0,
            reason: str = "No malicious patterns detected.",            
    )-> ValidationResult:
        
        return ValidationResult(
            detector_name= self.detector_name,
            category=AttackCategory.BENIGN,
            is_flagged=False,
            confidence=confidence,
            reason=reason,
        )
    
    def _flagged_result(
            self,
            *,
            category: AttackCategory,
            confidence: float,
            reason : str,
            matches : list[DetectionMatch] | None = None,

    )-> ValidationResult:
        
        return ValidationResult(
            detector_name= self.detector_name,
            category=category,
            is_flagged=True,
            confidence= confidence,
            reason= reason,
            matches= matches or[],
        )
    def _match_patterns(self,query : str,patterns: dict[str, str],*,ignore_case: bool = True,
        ) -> list[DetectionMatch]:

        matches: list[DetectionMatch] = []
        flags = re.IGNORECASE if ignore_case else 0

        for pattern_name, pattern in patterns.items():

            for match in re.finditer(
                pattern,
                query,
                flags=flags,
                ):

                matches.append(
                    DetectionMatch(
                    matched_text=match.group(),
                    pattern_name=pattern_name,
                    start=match.start(),
                    end=match.end(),
                )
            )

        return matches
    
    def _calculate_confidence(
    self,
    matches: list[DetectionMatch],
    ) -> float:
        return min(
        1.0,
        0.60 + (0.10 * len(matches)),
        )

        