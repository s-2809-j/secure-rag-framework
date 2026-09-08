"""
Response parser for the Tier-2 LLM Security Detector.
"""

from __future__ import annotations

import json

from src.input_security_agent.models import (
    AttackCategory,
    ValidationResult,
)


class Tier2ResponseParser:
    """
    Parses and validates the JSON response returned by the Tier-2 LLM.
    """

    REQUIRED_FIELDS = {
        "is_flagged",
        "category",
        "confidence",
        "reason",
    }

    @classmethod
    def parse(
        cls,
        response: str,
        detector_name: str,
    ) -> ValidationResult:
        """
        Parse the LLM response into a ValidationResult.

        Parameters
        ----------
        response
            Raw JSON response from the LLM.

        detector_name
            Name of the detector producing the result.

        Returns
        -------
        ValidationResult
            Parsed validation result.

        Raises
        ------
        ValueError
            If the response is malformed or invalid.
        """

        try:
            data = json.loads(response)

        except json.JSONDecodeError as exc:
            raise ValueError(
                "LLM returned invalid JSON."
            ) from exc

        cls._validate(data)

        try:

            category = AttackCategory[
                data["category"]
            ]

        except KeyError as exc:
            raise ValueError(
                f"Unknown attack category: "
                f"{data['category']}"
            ) from exc

        confidence = float(
            data["confidence"]
        )

        if confidence < 0.0 or confidence > 1.0:
            raise ValueError(
                "Confidence must be between 0 and 1."
            )

        return ValidationResult(
            detector_name=detector_name,
            category=category,
            is_flagged=bool(
                data["is_flagged"]
            ),
            confidence=confidence,
            reason=str(
                data["reason"]
            ),
            matches=[],
        )

    @classmethod
    def _validate(
        cls,
        data: dict,
    ) -> None:
        """
        Validate the JSON schema.
        """

        missing = cls.REQUIRED_FIELDS - data.keys()

        if missing:
            raise ValueError(
                f"Missing required fields: "
                f"{sorted(missing)}"
            )