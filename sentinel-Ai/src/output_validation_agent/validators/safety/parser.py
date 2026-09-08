from __future__ import annotations

import json

from src.output_validation_agent.validators.safety.models import (
    SafetyDecision,
    SafetyEvaluation,
)


class SafetyParser:
    """
    Parses and validates the Tier-2 Safety Judge response.
    """

    def parse(
        self,
        response: str,
    ) -> SafetyEvaluation:
        """
        Parse the JSON response returned by the Safety Judge.
        """

        if not isinstance(response, str):
            raise TypeError(
                "Safety judge response must be a string."
            )

        if not response.strip():
            raise ValueError(
                "Safety judge response cannot be empty."
            )

        try:
            payload = json.loads(response)

        except json.JSONDecodeError as exc:
            raise ValueError(
                "Invalid JSON returned by Safety Judge."
            ) from exc

        SafetyParser._validate_payload(
            payload,
        )

        return SafetyEvaluation(
            decision=SafetyDecision(
                payload["decision"],
            ),
            confidence=float(
                payload["confidence"],
            ),
            reason=payload["reason"],
            triggered_rules=list(
                payload["triggered_rules"],
            ),
        )

    @staticmethod
    def _validate_payload(
        payload: dict,
    ) -> None:
        """
        Validate the parsed JSON payload.
        """

        required_fields = (
            "decision",
            "confidence",
            "reason",
            "triggered_rules",
        )

        for field in required_fields:

            if field not in payload:
                raise ValueError(
                    f"Missing required field '{field}'."
                )

        if payload["decision"] not in {
            SafetyDecision.SAFE.value,
            SafetyDecision.SANITIZE.value,
            SafetyDecision.BLOCK.value,
        }:
            raise ValueError(
                "Invalid safety decision."
            )

        confidence = payload["confidence"]

        if not isinstance(
            confidence,
            (float, int),
        ):
            raise ValueError(
                "Confidence must be numeric."
            )
        if not 0.0 <= float(confidence) <= 1.0:
            raise ValueError(
                "Confidence must be between 0.0 and 1.0."
            )

        reason = payload["reason"]

        if not isinstance(reason, str):
            raise ValueError(
                "Reason must be a string."
            )

        if not reason.strip():
            raise ValueError(
                "Reason cannot be empty."
            )

        triggered_rules = payload["triggered_rules"]

        if not isinstance(
            triggered_rules,
            list,
        ):
            raise ValueError(
                "triggered_rules must be a list."
            )

        for rule in triggered_rules:

            if not isinstance(rule, str):
                raise ValueError(
                    "Each triggered rule must be a string."
                )


__all__ = [
    "SafetyParser",
]