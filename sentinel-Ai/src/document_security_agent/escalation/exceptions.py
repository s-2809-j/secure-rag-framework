"""
Custom exceptions for the Document Escalation subsystem.

These exceptions encapsulate errors that occur while determining which
document chunks should be escalated for Tier-2 security analysis.
"""

from __future__ import annotations


class EscalationError(Exception):
    """
    Base exception for all document escalation errors.
    """

    pass


class PriorityEvaluationError(EscalationError):
    """
    Raised when the escalation priority for a chunk
    cannot be determined.
    """

    pass


class EscalationEngineError(EscalationError):
    """
    Raised when the Document Escalation Engine encounters
    an unexpected processing error.
    """

    pass


class InvalidEscalationResultError(EscalationError):
    """
    Raised when the generated EscalationReport
    is invalid or internally inconsistent.
    """

    pass