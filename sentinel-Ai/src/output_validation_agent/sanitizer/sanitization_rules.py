from __future__ import annotations

from asyncio.log import logger
import re
from typing import Callable

from src.output_validation_agent.models import (
    OutputCategory,
    ValidationResult,
)


def _identity(
    response: str,
    _: ValidationResult,
) -> str:
    """
    Return the response unchanged.
    """
    return response


def _remove_unsupported_claims(
    response: str,
    result: ValidationResult,
) -> str:
    """
    Remove unsupported sentences identified by the Hallucination Validator.
    If all sentences are removed, return the original response unchanged
    to prevent data loss — the risk score already signals the issue.
    """

    decisions = result.details.get("sentence_decisions", [])

    sanitized = response

    for decision in decisions:
        if decision.supported:
            continue
        sanitized = sanitized.replace(decision.sentence, "")

    sanitized = " ".join(sanitized.split())

    # Safety net — never return empty string.
    # If sanitization removed everything, the original response
    # is safer than an empty data field reaching the client.
    if not sanitized.strip():
        logger.warning(
            "Sanitization removed entire response — "
            "returning original to prevent data loss."
        )
        return response

    return sanitized


def _redact_pii(
    response: str,
    _: ValidationResult,
) -> str:
    """
    Replace detected PII with a placeholder.

    The PII detector should ideally provide precise spans.
    Until then, use a conservative fallback.
    """

    email_pattern = (
        r"\b[A-Za-z0-9._%+-]+@"
        r"[A-Za-z0-9.-]+\."
        r"[A-Za-z]{2,}\b"
    )

    phone_pattern = (
        r"\b\d{10}\b"
    )

    response = re.sub(
        email_pattern,
        "[REDACTED]",
        response,
    )

    response = re.sub(
        phone_pattern,
        "[REDACTED]",
        response,
    )

    return response


def _redact_prompt_leakage( response: str,
    _: ValidationResult,
    ) -> str:
        """
        Remove responses containing leaked system prompts.

        The Policy Engine should normally block these responses,
        but this provides a safe fallback.
        """

        return (
            "[CONTENT REMOVED "
            "DUE TO SECURITY POLICY]"
        )


def _remove_policy_violation(
    response: str,
    _: ValidationResult,
) -> str:
    """
    Remove policy-violating content.
    """

    return (
        "[CONTENT REMOVED "
        "DUE TO POLICY VIOLATION]"
    )


SANITIZATION_RULES: dict[
    OutputCategory,
    Callable[
        [str, ValidationResult],
        str,
    ],
] = {

    OutputCategory.SAFE:
        _identity,

    OutputCategory.HALLUCINATION:
        _remove_unsupported_claims,

    OutputCategory.UNSUPPORTED_CLAIM:
        _remove_unsupported_claims,

    OutputCategory.PII:
        _redact_pii,

    OutputCategory.PROMPT_LEAKAGE:
        _redact_prompt_leakage,

    OutputCategory.POLICY_VIOLATION:
        _remove_policy_violation,
}